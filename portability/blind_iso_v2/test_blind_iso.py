"""BLISO-2 source-derived static contracts; no runtime OpenHoldem validation."""
from pathlib import Path
import hashlib
import re
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import build_blind_iso as build
import blind_iso_interpreter as interp

SB=[f'SB{n}' for n in range(1,5)]
BB=[x for n in range(1,6) for x in ([f'BB{n}SB',f'BB{n}Other'] if n<5 else [f'BB{n}SB'])]
TAGS=SB+BB


class BlindIsoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=interp.parse_file()

    def act(self,street='flop',**kw):
        return interp.evaluate(self.model,street,interp.observe(street,**kw))

    @staticmethod
    def origin(tag):
        return {**{'user_H6_BISO'+name:False for name in TAGS},
                'user_H6_BISO'+tag:True}

    def test_01_source_merge_is_exact(self):
        self.assertEqual(build.render(),build.COMBINED.read_text(encoding='utf-8'))

    def test_02_parent_WHEN_action_order_preserved(self):
        old=[x for x in build.PARENT.read_text().splitlines() if x.startswith('WHEN ')]
        new=[x for x in build.COMBINED.read_text().splitlines() if x.startswith('WHEN ')]
        i=0
        for original in old:
            while i<len(new) and new[i]!=original:i+=1
            self.assertLess(i,len(new),'ancestor removed or reordered')
            i+=1

    def test_03_single_action_callbacks_and_list(self):
        new=build.COMBINED.read_text()
        for s in ('preflop','flop','turn','river'):
            self.assertEqual(new.count('##f$'+s+'##'),1)
        self.assertEqual(new.count('##listH6BISOCORE##'),1)
        self.assertNotIn('listH6BISOCORE',build.PARENT.read_text())
        self.assertEqual(len(self.model.helpers)-len(interp.prev.parse_file().helpers),9)

    def test_04_preflop_13_intents_match_raise_guards(self):
        rules=[s for s in build.PREFLOP.read_text().splitlines() if s.startswith('WHEN (')]
        self.assertEqual(len(rules),30)
        for tag in TAGS:
            intent=[s for s in rules if 'Set user_H6_BISO'+tag in s]
            self.assertEqual(len(intent),1)
            ix=rules.index(intent[0])
            self.assertEqual(intent[0].split(') Set ')[0],rules[ix+1].split(') RaiseTo ')[0])
            self.assertIn('RaiseTo ',rules[ix+1])
            self.assertIn('Raises = 0',intent[0])
            self.assertIn('nplayersdealt = 6',intent[0])
        self.assertEqual(len([r for r in rules if 'RaiseTo' in r]),13)
        self.assertEqual(len([r for r in rules if 'Fold FORCE' in r]),4)

    def test_05_sb_cases_price_and_fallback(self):
        rules=build.PREFLOP.read_text()
        for n in range(1,5):
            tag='SB'+str(n)
            r=next(x for x in rules.splitlines() if 'Set user_H6_BISO'+tag in x)
            self.assertIn('InSmallBlind',r)
            self.assertIn('AmountToCall = 0.5',r)
            self.assertIn(f'Calls = {n}',r)
            self.assertIn(f'PotSize = {n+1.5}',r)
            self.assertIn('StillToAct = 1',r)
            self.assertIn('Fold FORCE',rules.splitlines()[rules.splitlines().index(r)+2])

    def test_06_bb_cases_price_and_keep_existing_check(self):
        rules=build.PREFLOP.read_text()
        for n in range(1,6):
            for kind in ('SB','Other') if n<5 else ('SB',):
                tag=f'BB{n}{kind}'
                r=next(x for x in rules.splitlines() if 'Set user_H6_BISO'+tag in x)
                self.assertIn('InBigBlind',r)
                self.assertIn('AmountToCall = 0',r)
                self.assertIn('StillToAct = 0',r)
                self.assertIn(f'Calls = {n}',r)
                price=n+(1 if kind=='SB' else 1.5)
                self.assertIn(f'PotSize = {price:g}',r)
        new=build.COMBINED.read_text()
        self.assertLess(new.index('Set user_H6_BISOBB2SB'),new.index('Set user_H6_ML2SB'))
        self.assertLess(new.index('RaiseTo 5 FORCE'),new.index('Set user_H6_ML2SB'))
        self.assertIn('Set user_H6_ML2SB',new)
        self.assertIn('Check FORCE',new)

    def test_07_postflop_actions_and_safe_scoped_fallbacks(self):
        self.assertEqual([len(self.model.streets[x]) for x in build.STREETS],[16,14,13])
        for street in build.STREETS:
            rules=self.model.streets[street]
            self.assertEqual(rules[-1].atoms,('f$H6BISOValid','AmountToCall = 0'))
            self.assertEqual(rules[-1].action,'Check')
            self.assertTrue(any(x.atoms==('f$H6BISOValid','AmountToCall > 0') and x.action=='Fold' for x in rules))

    def test_08_each_tag_single_origin_can_act(self):
        for tag in TAGS:
            with self.subTest(tag=tag):
                d={**self.origin(tag),'OpponentsOnFlop':1,'OpponentsOnTurn':1,
                   'OpponentsOnRiver':1,'OpponentsLeft':1}
                for street in build.STREETS:
                    self.assertEqual(self.act(street,**d),'Check')
                    self.assertEqual(self.act(street,AmountToCall=100,**d),'Fold')

    def test_09_origin_maximum_is_limper_specific(self):
        for tag in TAGS:
            max_players=(int(tag[2:]) +1 if tag.startswith('SB')
                         else int(re.match(r'BB(\d+)',tag).group(1)))
            args=self.origin(tag)
            self.assertEqual(self.act(OpponentsOnFlop=max_players,OpponentsLeft=max_players,**args),'Check')
            if max_players<5:
                self.assertIsNone(self.act(OpponentsOnFlop=max_players+1,OpponentsLeft=max_players+1,**args))

    def test_10_legal_transition_within_street(self):
        args=self.origin('SB4')
        for street,n,t,r,left in (
            ('flop',5,5,5,2),('turn',5,4,4,2),
            ('turn',5,3,3,1),('river',5,4,3,1),
            ('river',5,3,2,1),('river',5,5,5,5)):
            self.assertEqual(self.act(street,OpponentsOnFlop=n,OpponentsOnTurn=t,
                  OpponentsOnRiver=r,OpponentsLeft=left,**args),'Check')

    def test_11_invalid_transition_fails_no_match(self):
        for street,k in [
            ('flop',{'OpponentsOnFlop':2,'OpponentsLeft':3}),
            ('turn',{'OpponentsOnFlop':4,'OpponentsOnTurn':5,'OpponentsLeft':2}),
            ('turn',{'OpponentsOnFlop':3,'OpponentsOnTurn':1,'OpponentsLeft':2}),
            ('river',{'OpponentsOnFlop':4,'OpponentsOnTurn':2,'OpponentsOnRiver':3,'OpponentsLeft':1}),
            ('river',{'OpponentsOnFlop':4,'OpponentsOnTurn':3,'OpponentsOnRiver':1,'OpponentsLeft':2})]:
            self.assertIsNone(self.act(street,**k))

    def test_12_collisions_invalid_3bet_limp_check_and_stale_flags(self):
        for key,value in [
            ('user_H6_BISOSB1',True),('user_H6_ISOBTN1',True),
            ('user_H6_RFIIntent',True),('user_H6_3betIntent',True),
            ('user_H6_VSOpenCallIntent',True),('user_H6_ML2SB',True),
            ('user_H6_LimpSBIntent',True),('BotRaisedBeforeFlop',False),
            ('BotCheckedPreflop',True),('BotCalledBeforeFlop',True),
            ('NumberOfRaisesBeforeFlop',1),('NumberOfOpponentsAllin',1),
            ('StackUnknown',True),('nplayersdealt',5)]:
            with self.subTest(key=key):
                self.assertIsNone(self.act(**{key:value}))

    def test_13_have_nuts_never_folds_overbet(self):
        for street in build.STREETS:
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=1),'RaiseHalfPot')
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=500),'Call')

    def test_14_values_more_conservative_multiway(self):
        cases={'flop':(8,6,4),'turn':(6.8,4.8,3.2),'river':(5.6,3.8,2.3)}
        for street,price in cases.items():
            for alive,cap in enumerate(price,1):
                args={**self.origin('SB4'),'HaveSet':True,
                      'OpponentsOnFlop':4,'OpponentsOnTurn':4,'OpponentsOnRiver':4,
                      'OpponentsLeft':alive}
                self.assertEqual(self.act(street,AmountToCall=cap,**args),'Call')
                self.assertEqual(self.act(street,AmountToCall=cap+.1,**args),'Fold')

    def test_15_sb_bb_value_sizing_is_not_identical(self):
        sb={**self.origin('SB1'),'OpponentsOnFlop':1,'OpponentsLeft':1}
        bb={**self.origin('BB1Other'),'OpponentsOnFlop':1,'OpponentsLeft':1}
        self.assertEqual(self.act(HaveSet=True,**sb),'BetThirdPot')
        self.assertEqual(self.act(HaveSet=True,**bb),'BetHalfPot')
        self.assertEqual(self.act(HaveNuts=True,**sb),'BetTwoThirdPot')

    def test_16_parser_rejects_unknown_symbol_and_broad_default(self):
        top=build.TOPOLOGY.read_text()
        p=build.POLICY.read_text()
        for mutation in [
            p.replace('HaveNuts','HaveFantasyNuts',1),
            p+'\nWHEN Others Fold FORCE',
            p.replace('f$H6BISOValid AND AmountToCall > 0) Fold FORCE',
                      'AmountToCall > 0) Fold FORCE')]:
            with self.assertRaises(interp.SourceError):
                interp.parse(top,mutation)

    def test_17_invalid_observed_inputs_rejected(self):
        for args in [
            {'randomhand':1.0},{'AmountToCall':float('nan')},
            {'BotCheckedPreflop':1},{'Position':'Unknown'},
            {'IsRiver':True}]:
            with self.assertRaises(interp.SourceError):
                self.act(**args)

    def test_18_builder_idempotent_without_ancestor_edit(self):
        files=(build.PARENT,build.HAND,build.PREFLOP,build.TOPOLOGY,
               build.POLICY,build.COMBINED)
        before=[hashlib.sha256(x.read_bytes()).digest() for x in files]
        self.assertEqual(build.build()[0],43)
        self.assertEqual(before,[hashlib.sha256(x.read_bytes()).digest() for x in files])


if __name__=='__main__':
    unittest.main()
