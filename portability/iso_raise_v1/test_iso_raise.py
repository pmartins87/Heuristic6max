"""ISO-1 DRAFT: source-derived postflop execution, guards and ancestor stability.

Not a substitute for OpenHoldem executable replay or EV/strategic review.
"""
from pathlib import Path
import sys
import unittest
import hashlib
import re

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import build_iso as build
import iso_interpreter as iso


class ISOv1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=iso.parse_file()

    def act(self,street='flop',**changes):
        obs=iso.observe(street,**changes)
        return iso.evaluate(self.model,street,obs)

    def test_01_parent_source_and_final_merge_are_reproducible(self):
        self.assertEqual(build.render(),build.COMBINED.read_text(encoding='utf-8'))
        old=build.PARENT.read_text(encoding='utf-8')
        new=build.COMBINED.read_text(encoding='utf-8')
        before=[ln for ln in old.splitlines() if ln.startswith('WHEN ')]
        after=[ln for ln in new.splitlines() if ln.startswith('WHEN ')]
        i=0
        for ln in before:
            while i<len(after) and after[i]!=ln:i+=1
            self.assertLess(i,len(after))
            i+=1

    def test_02_single_reserved_street_headers_and_separate_list(self):
        txt=build.COMBINED.read_text()
        for st in ('preflop','flop','turn','river'):
            self.assertEqual(txt.count(f'##f\x24{st}##'),1)
        self.assertEqual(txt.count('##listH6ISOCORE##'),1)
        self.assertNotIn('listH6ISOCORE',build.PARENT.read_text())
        self.assertEqual(len(self.model.helpers)-len(iso.prev.parse_file().helpers),7)

    def test_03_preflop_intent_is_paired_with_same_guard_action(self):
        pf=build.PREFLOP.read_text()
        acts=[x for x in pf.splitlines() if x.startswith('WHEN (')]
        self.assertEqual(len(acts),15)
        tags=('CO1','CO2','BTN1','BTN2','BTN3')
        for index,tag in enumerate(tags):
            intent,raise_rule,fold=acts[index*3:index*3+3]
            self.assertIn('Set user_H6_ISO'+tag,intent)
            self.assertEqual(intent.split(') Set ')[0],raise_rule.split(') RaiseTo ')[0])
            self.assertIn('Fold FORCE',fold)
            for branch in (intent,raise_rule,fold):
                self.assertIn('Raises = 0',branch)
                self.assertIn('Calls = ',branch)
                self.assertIn('nplayersdealt = 6',branch)
        self.assertEqual([x.split('RaiseTo ')[1].split(' FORCE')[0] for x in acts if 'RaiseTo ' in x],
                         ['4.5','5.5','4.5','5.5','6.5'])

    def test_04_action_count_and_scoped_fallbacks(self):
        self.assertEqual([len(self.model.streets[s]) for s in build.STREETS],[15,14,12])
        for street in build.STREETS:
            rs=self.model.streets[street]
            self.assertEqual(rs[-1].action,'Check')
            self.assertEqual(rs[-1].atoms,('f$H6ISOValid','AmountToCall = 0'))
            self.assertTrue(any(r.action=='Fold' and r.atoms==('f$H6ISOValid','AmountToCall > 0') for r in rs))

    def test_05_both_two_way_and_crowded_scoped(self):
        for street in build.STREETS:
            self.assertEqual(self.act(street,OpponentsLeft=2,AmountToCall=0),'Check')
            self.assertEqual(self.act(street,OpponentsLeft=2,HaveNuts=True),'BetTwoThirdPot')
            self.assertEqual(self.act(street,OpponentsLeft=2,AmountToCall=100,HaveNuts=True),'Call')
            self.assertEqual(self.act(street,OpponentsLeft=2,AmountToCall=100),'Fold')

    def test_06_source_rejects_conflicting_origin(self):
        collisions=[
            {'user_H6_ISOCO1':True},
            {'user_H6_RFIIntent':True},
            {'user_H6_3betIntent':True},
            {'user_H6_VSOpenCallIntent':True},
            {'user_H6_ML2SB':True},
            {'BotCalledBeforeFlop':True},
            {'BotRaisedBeforeFlop':False},
            {'NumberOfRaisesBeforeFlop':1},
            {'NumberOfOpponentsAllin':1},
            {'StackUnknown':True},
            {'nplayersdealt':5}
        ]
        for condition in collisions:
            with self.subTest(condition=condition):
                self.assertIsNone(self.act(**condition))

    def test_07_flop_size_bounded_by_preflop_intent(self):
        self.assertIsNone(self.act(OpponentsOnFlop=4,OpponentsLeft=4))
        self.assertIsNone(self.act(OpponentsOnFlop=0,OpponentsLeft=0))
        self.assertEqual(self.act(OpponentsOnFlop=3,OpponentsLeft=3),'Check')
        # CO2 permits up to 5 callers; BTN1 cannot.
        self.assertEqual(self.act(user_H6_ISOBTN1=False,user_H6_ISOCO2=True,
                                  OpponentsOnFlop=5,OpponentsLeft=5),'Check')

    def test_08_every_monotone_street_topology_has_action(self):
        for n in range(1,6):
            for t in range(1,n+1):
                for river in range(1,t+1):
                    for alive in range(1,river+1):
                        state={'user_H6_ISOBTN1':False,'user_H6_ISOCO2':True,
                               'OpponentsOnFlop':n,'OpponentsOnTurn':t,
                               'OpponentsOnRiver':river,'OpponentsLeft':alive}
                        self.assertEqual(self.act('river',**state),'Check')
                        self.assertEqual(self.act('river',AmountToCall=100,**state),'Fold')

    def test_09_invalid_exit_counts_never_route(self):
        for street,state in (
            ('flop',{'OpponentsOnFlop':2,'OpponentsLeft':3}),
            ('turn',{'OpponentsOnFlop':3,'OpponentsOnTurn':4,'OpponentsLeft':2}),
            ('turn',{'OpponentsOnFlop':2,'OpponentsOnTurn':1,'OpponentsLeft':2}),
            ('river',{'OpponentsOnFlop':3,'OpponentsOnTurn':2,'OpponentsOnRiver':3,'OpponentsLeft':1}),
            ('river',{'OpponentsOnFlop':3,'OpponentsOnTurn':2,'OpponentsOnRiver':1,'OpponentsLeft':2})):
            with self.subTest(street=street,state=state):
                self.assertIsNone(self.act(street,**state))

    def test_10_nuts_never_folds_against_overbets(self):
        for street in build.STREETS:
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=999),'Call')
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=1),'RaiseHalfPot')

    def test_11_price_thresholds_tighten_from_hu_to_crowded(self):
        for street,cap in [('flop',(8.5,6.5,4.5)),('turn',(7.2,5.4,3.5)),('river',(5.5,4.2,2.7))]:
            for alive,limit in enumerate(cap,1):
                state={'user_H6_ISOBTN1':False,'user_H6_ISOCO2':True,
                       'OpponentsOnFlop':3,'OpponentsOnTurn':3,
                       'OpponentsOnRiver':3,'OpponentsLeft':alive,'HaveSet':True}
                self.assertEqual(self.act(street,AmountToCall=limit,**state),'Call')
                self.assertEqual(self.act(street,AmountToCall=limit+.1,**state),'Fold')

    def test_12_invalid_symbols_prices_and_global_fallback_fail(self):
        policy=build.POLICY.read_text()
        for mutation in (
            policy+'\nWHEN Others Fold FORCE',
            policy.replace('HaveNuts','HaveUnknownSuperNuts',1),
            policy.replace('f$H6ISOValid AND AmountToCall > 0) Fold FORCE',
                           'AmountToCall > 0) Fold FORCE')):
            with self.assertRaises(iso.SourceError):
                iso.parse(build.TOPOLOGY.read_text(),mutation)
        for updates in ({'randomhand':1},{'AmountToCall':float('nan')},
                        {'BotRaisedBeforeFlop':1},{'Position':'Unknown'}):
            with self.assertRaises(iso.SourceError):
                self.act(**updates)

    def test_13_source_files_unchanged_after_builder(self):
        before={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in
                [('PARENT',build.PARENT),('HAND',build.HAND),
                 ('PREFLOP',build.PREFLOP),('TOPOLOGY',build.TOPOLOGY),
                 ('POLICY',build.POLICY),('COMBINED',build.COMBINED)]}
        self.assertEqual(build.build()[0],41)
        after={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in
               [('PARENT',build.PARENT),('HAND',build.HAND),
                ('PREFLOP',build.PREFLOP),('TOPOLOGY',build.TOPOLOGY),
                ('POLICY',build.POLICY),('COMBINED',build.COMBINED)]}
        self.assertEqual(before,after)


if __name__=='__main__':
    unittest.main()
