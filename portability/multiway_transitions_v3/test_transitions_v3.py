from __future__ import annotations
from pathlib import Path
import csv, hashlib, sys, unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import build_transitions_v3 as build
import source_interpreter as p

class PartialTransitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model=p.parse_file()
    def action(self,street='flop',**overrides):return p.evaluate(self.model,street,p.observe(street,**overrides))
    def test_branch_counts_and_source_only(self):
        self.assertEqual([len(self.model.rules[s]) for s in p.STREETS],[15,14,12])
        self.assertEqual(len(self.model.helpers),23) # 10 upstream + 13 new
        self.assertEqual(build.build(),(53,41))

    def test_all_physically_possible_partial_paths_are_admitted(self):
        for street in p.STREETS:
            for left in (2,3,4):
                for tup in build.tuples_for(street,left):
                    kwargs={'OpponentsOnFlop':tup[0],'OpponentsLeft':left}
                    if street in ('turn','river'):kwargs['OpponentsOnTurn']=tup[1]
                    if street=='river':kwargs['OpponentsOnRiver']=tup[2]
                    with self.subTest(street=street,t=tup):
                        self.assertEqual(self.action(street,**kwargs),'Check')
                        self.assertEqual(self.action(street,AmountToCall=100,**kwargs),'Fold')
                        self.assertEqual(self.action(street,HaveNuts=True,AmountToCall=100,**kwargs),'Call')

    def test_inconsistent_timelines_never_classified(self):
        contexts=[('turn',{'OpponentsOnFlop':3,'OpponentsOnTurn':4,'OpponentsLeft':2}),
                  ('turn',{'OpponentsOnFlop':5,'OpponentsOnTurn':2,'OpponentsLeft':3}),
                  ('river',{'OpponentsOnFlop':5,'OpponentsOnTurn':4,'OpponentsOnRiver':5,'OpponentsLeft':2}),
                  ('river',{'OpponentsOnFlop':5,'OpponentsOnTurn':4,'OpponentsOnRiver':2,'OpponentsLeft':3}),
                  ('flop',{'OpponentsOnFlop':5,'OpponentsLeft':6})]
        for street,ctx in contexts:
            with self.subTest(street=street,ctx=ctx):self.assertIsNone(self.action(street,**ctx))

    def test_unaffected_domain_never_reclassified(self):
        for street in p.STREETS:
            for initial,left in ((1,1),(2,1),(2,2),(3,3),(4,4),(5,5),(3,1),(4,1),(5,1)):
                d={'OpponentsOnFlop':initial,'OpponentsLeft':left,'OpponentsOnTurn':initial,'OpponentsOnRiver':initial}
                if left<initial:
                    d['OpponentsOnTurn']=left;d['OpponentsOnRiver']=left
                self.assertIsNone(self.action(street,**d))

    def test_origin_consistency_and_bad_source_flags(self):
        for key,value in [('user_H6_RFIIntent',False),('user_H6_3betIntent',True),
                          ('BotRaisedBeforeFlop',False),('BotCalledBeforeFlop',True),
                          ('StackUnknown',True),('NumberOfOpponentsAllin',1),
                          ('nplayersdealt',5),('NumberOfRaisesBeforeFlop',1),
                          ('user_H6_VSOpenCallIntent',True)]:
            with self.subTest(key=key):self.assertIsNone(self.action(**{key:value}))

    def test_caller_history_is_distinct(self):
        c={'user_H6_RFIIntent':False,'user_H6_VSOpenCallIntent':True,
           'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,
           'NumberOfRaisesBeforeFlop':1}
        self.assertEqual(self.action('flop',**c),'Check')
        self.assertEqual(self.action('river',**c),'Check')
        self.assertIsNone(self.action('flop',user_H6_VSOpenCallIntent=True))

    def test_price_tightens_with_remaining_villains(self):
        for left,cap in ((2,7.),(3,5.5),(4,4.5)):
            state={'OpponentsOnFlop':5,'OpponentsLeft':left,'HaveSet':True}
            self.assertEqual(self.action(AmountToCall=cap,**state),'Call')
            self.assertEqual(self.action(AmountToCall=cap+.01,**state),'Fold')

    def test_no_air_autobet_and_nuts_priority_on_overbets(self):
        for s in p.STREETS:
            self.assertEqual(self.action(s,randomhand=0),'Check')
            self.assertEqual(self.action(s,HaveNuts=True,AmountToCall=360),'Call')
            self.assertEqual(self.action(s,HaveNuts=True,AmountToCall=1),'RaiseHalfPot')

    def test_mixed_action_stable_and_boundary(self):
        kwargs={'OpponentsOnFlop':5,'OpponentsLeft':2,'Position':'Last','HaveOverPair':True}
        for _ in range(4):self.assertEqual(self.action('flop',randomhand=.19,**kwargs),'BetThirdPot')
        self.assertEqual(self.action('flop',randomhand=.20,**kwargs),'Check')
        self.assertEqual(self.action('flop',randomhand=.99,**kwargs),'Check')

    def test_parser_rejects_unknown_moves_and_unscoped_fallback(self):
        gates=build.HELPERS.read_text();policy=build.POLICY.read_text()
        for modified in (policy+'\nWHEN Others Fold FORCE',
                         policy.replace('f$H6PartialF AND AmountToCall > 0) Fold FORCE',
                                        'AmountToCall > 0) Fold FORCE'),
                         policy.replace('randomhand < 0.20','Random < 0.20'),
                         policy.replace('randomhand < 0.20','randomhand < 0.99')):
            with self.subTest(x=modified[-60:]),self.assertRaises(p.SourceError):p.parse(gates,modified)

    def test_bad_observations_rejected(self):
        for x in ({'randomhand':1},{'AmountToCall':-1},{'PotSize':0},
                  {'BotRaisedBeforeFlop':1},{'OpponentsLeft':float('nan')},
                  {'IsRiver':True},{'Position':'Unknown'}):
            with self.subTest(x=x),self.assertRaises(p.SourceError):self.action(**x)

    def test_byte_preservation_of_all_old_actions_and_prefix(self):
        old=build.PARENT.read_text();new=build.COMBINED.read_text()
        self.assertTrue(new.startswith(old.split('##f$flop##')[0]))
        before=[x for x in old.splitlines() if x.startswith('WHEN ')]
        after=[x for x in new.splitlines() if x.startswith('WHEN ')]
        i=0
        for rule in before:
            while i<len(after) and after[i]!=rule:i+=1
            self.assertLess(i,len(after),msg=rule[:80]);i+=1
        for s in ('preflop','flop','turn','river'):
            self.assertEqual(new.count(f'##f${s}##'),1)

    def test_topology_csv_is_exhaustive_for_bounded_model(self):
        with build.MATRIX.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),108)
        self.assertEqual(sum(r['PolicyOwner']=='NEW_PARTIAL' for r in rows),53)
        self.assertTrue(all(r['RuntimeStatus']=='STATIC_DRAFT_NOT_OH_VERIFIED' for r in rows))

    def test_generator_deterministic_and_ancestors_untouched(self):
        paths=(build.PARENT,build.COMBINED,build.HELPERS,build.MATRIX)
        before=[hashlib.sha256(f.read_bytes()).digest() for f in paths]
        self.assertEqual(build.build(),(53,41))
        self.assertEqual(before,[hashlib.sha256(f.read_bytes()).digest() for f in paths])

if __name__=='__main__':unittest.main()
