"""Static source parity / guard / integration tests for multiway v2."""
from __future__ import annotations
from pathlib import Path
import csv
import hashlib
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import multiway_interpreter as p
import build_multiway_v2 as b

class Multiway(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m=p.parse_file()

    def action(self,street='flop',**kwargs):
        return p.evaluate(self.m,street,p.observe(**kwargs))

    def test_source_has_74_actions_and_10_unique_helpers(self):
        self.assertEqual([len(self.m.rules[x]) for x in p.STREETS],[29,25,20])
        self.assertEqual(len(self.m.helpers),10)
        self.assertTrue(all(k.startswith('f$H6') for k in self.m.helpers))

    def test_4_5_6_player_pots_have_distinct_domains(self):
        for initial in (3,4,5):
            for street in p.STREETS:
                with self.subTest(initial=initial,street=street):
                    self.assertEqual(self.action(street,OpponentsOnFlop=initial,
                                            OpponentsLeft=initial),'Check')
                    self.assertEqual(self.action(street,OpponentsOnFlop=initial,
                                            OpponentsLeft=initial,AmountToCall=11),'Fold')

    def test_caller_origin_works_for_4_to_6_player_pots(self):
        caller={'user_H6_RFIIntent':False,'user_H6_VSOpenCallIntent':True,
                'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,
                'NumberOfRaisesBeforeFlop':1}
        for initial in (3,4,5):
            self.assertEqual(self.action(OpponentsOnFlop=initial,OpponentsLeft=initial,**caller),'Check')
            self.assertEqual(self.action('turn',OpponentsOnFlop=initial,OpponentsLeft=initial,**caller),'Check')

    def test_3way_to_hu_transition_covers_all_streets(self):
        for street in p.STREETS:
            self.assertEqual(self.action(street,OpponentsOnFlop=2,OpponentsLeft=1),'Check')
            self.assertEqual(self.action(street,OpponentsOnFlop=2,OpponentsLeft=1,AmountToCall=11),'Fold')

    def test_4_to_6_way_to_hu_transitions_are_explicit(self):
        for initial in (3,4,5):
            for street in p.STREETS:
                self.assertEqual(self.action(street,OpponentsOnFlop=initial,OpponentsLeft=1),'Check')
                self.assertEqual(self.action(street,OpponentsOnFlop=initial,OpponentsLeft=1,
                                             HaveNuts=True,AmountToCall=99),'Call')

    def test_unknown_partial_topologies_not_faked(self):
        for initial,left in ((2,2),(3,2),(4,2),(4,3),(5,2),(5,3),(5,4),
                             (1,1),(0,0),(3,0)):
            for street in p.STREETS:
                with self.subTest(initial=initial,left=left,street=street):
                    self.assertIsNone(self.action(street,OpponentsOnFlop=initial,OpponentsLeft=left))

    def test_nuts_very_large_bets_are_never_folded(self):
        for initial,left in ((3,3),(4,4),(5,5),(2,1),(3,1),(4,1),(5,1)):
            for street in p.STREETS:
                self.assertEqual(self.action(street,OpponentsOnFlop=initial,OpponentsLeft=left,
                                             HaveNuts=True,AmountToCall=310),'Call')

    def test_nuts_small_bet_may_raise(self):
        for street in p.STREETS:
            self.assertEqual(self.action(street,HaveNuts=True,AmountToCall=1),'RaiseHalfPot')
            self.assertEqual(self.action(street,OpponentsOnFlop=4,OpponentsLeft=1,
                                         HaveNuts=True,AmountToCall=1),'RaiseHalfPot')

    def test_strong_hand_prices_tighten_with_more_opponents(self):
        for n,max_amount in ((3,6.5),(4,5.5),(5,4.5)):
            data={'OpponentsOnFlop':n,'OpponentsLeft':n,'HaveSet':True}
            self.assertEqual(self.action(AmountToCall=max_amount,**data),'Call')
            self.assertEqual(self.action(AmountToCall=max_amount+.01,**data),'Fold')

    def test_draw_call_prices_shrink_with_crowding(self):
        for initial,at,action in ((3,2,'Call'),(3,2.01,'Fold'),
                                 (4,1.5,'Call'),(4,1.51,'Fold'),(5,.01,'Fold')):
            self.assertEqual(self.action(OpponentsOnFlop=initial,OpponentsLeft=initial,
                                         HaveNutFlushDraw=True,Position='Last',AmountToCall=at),action)

    def test_no_air_cbet_in_crowded_pots(self):
        for initial in (3,4,5):
            for street in p.STREETS:
                self.assertEqual(self.action(street,OpponentsOnFlop=initial,
                                             OpponentsLeft=initial,randomhand=0),'Check')

    def test_overpair_value_has_position_and_crowd_guards(self):
        self.assertEqual(self.action(HaveOverPair=True,Position='Last',randomhand=.19), 'BetThirdPot')
        self.assertEqual(self.action(HaveOverPair=True,Position='Last',randomhand=.20), 'Check')
        self.assertEqual(self.action(HaveOverPair=True,Position='First',randomhand=.01),'Check')
        self.assertEqual(self.action(HaveOverPair=True,OpponentsOnFlop=4,
                                     OpponentsLeft=4,randomhand=.01),'Check')

    def test_srp_pfr_and_caller_conflict_is_not_admitted(self):
        self.assertIsNone(self.action(user_H6_RFIIntent=True,user_H6_VSOpenCallIntent=True))
        self.assertIsNone(self.action(user_H6_3betIntent=True))
        self.assertIsNone(self.action(user_H6_RFIIntent=False))
        self.assertIsNone(self.action(BotRaisedBeforeFlop=False))
        self.assertIsNone(self.action(BotCalledBeforeFlop=True))

    def test_3bet_and_extra_raise_history_excluded(self):
        for raises in (1,2,3,4):
            self.assertIsNone(self.action(NumberOfRaisesBeforeFlop=raises))
        self.assertIsNone(self.action(NumberOfOpponentsAllin=1))
        self.assertIsNone(self.action(StackUnknown=True))
        self.assertIsNone(self.action(nplayersdealt=5))

    def test_caller_with_3bet_history_not_accidentally_admitted(self):
        data={'user_H6_RFIIntent':False,'user_H6_VSOpenCallIntent':True,
              'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,
              'NumberOfRaisesBeforeFlop':2}
        self.assertIsNone(self.action(**data))

    def test_strong_hands_value_bet_without_facing_bet(self):
        for n in (3,4,5):
            self.assertEqual(self.action(OpponentsOnFlop=n,OpponentsLeft=n,HaveNuts=True),'BetTwoThirdPot')
            self.assertEqual(self.action(OpponentsOnFlop=n,OpponentsLeft=n,HaveTwoPair=True),
                             'BetHalfPot' if n==3 else 'BetThirdPot')
        self.assertEqual(self.action(OpponentsOnFlop=5,OpponentsLeft=1,HaveTwoPair=True),'BetThirdPot')

    def test_transition_remembers_original_crowd_strictness(self):
        self.assertEqual(self.action(OpponentsOnFlop=2,OpponentsLeft=1,
                                    HaveSet=True,AmountToCall=7.5),'Call')
        self.assertEqual(self.action(OpponentsOnFlop=5,OpponentsLeft=1,
                                    HaveSet=True,AmountToCall=7.5),'Fold')

    def test_transition_does_not_use_original_hu_domain(self):
        self.assertIsNone(self.action(OpponentsOnFlop=1,OpponentsLeft=1))
        self.assertEqual(self.action(OpponentsOnFlop=2,OpponentsLeft=1),'Check')

    def test_randomhand_is_not_python_rng(self):
        data={'HaveOverPair':True,'Position':'Last'}
        for _ in range(5):
            self.assertEqual(self.action(randomhand=.19,**data),'BetThirdPot')
            self.assertEqual(self.action(randomhand=.20,**data),'Check')

    def test_parser_rejects_unknown_actions_and_unguarded_others(self):
        crowded=p.CROWDED.read_text()
        trans=p.TRANSITION.read_text()
        for change in (crowded+'\nWHEN Others Call FORCE',
                       crowded.replace('WHEN (f$H6CrowdedSRP AND AmountToCall > 0) Fold FORCE',
                                       'WHEN (AmountToCall > 0) Fold FORCE'),
                       crowded.replace('randomhand < 0.20','Random < 0.20'),
                       crowded.replace('randomhand < 0.20','randomhand < 0.99')):
            with self.subTest(change=change[-65:]),self.assertRaises(p.SourceError):p.parse(change,trans)

    def test_invalid_observation_types_or_prices_rejected(self):
        for x in ({'PotSize':0}, {'AmountToCall':float('nan')}, {'randomhand':1.},
                  {'Position':'Unknown'}, {'BotRaisedBeforeFlop':1},
                  {'OpponentsLeft':'3'}):
            with self.subTest(x=x),self.assertRaises(p.SourceError):self.action(**x)

    def test_upstream_action_lines_unchanged_and_preflop_is_byte_identical(self):
        old=b.PREVIOUS.read_text(encoding='utf-8')
        new=b.COMBINED.read_text(encoding='utf-8')
        self.assertTrue(new.startswith(old.split('##f$flop##')[0]))
        assert '##f$preflop##' in old
        old_lines=[x for x in old.splitlines() if x.startswith('WHEN ')]
        new_lines=[x for x in new.splitlines() if x.startswith('WHEN ')]
        position=0
        for x in old_lines:
            while position<len(new_lines) and new_lines[position]!=x:position+=1
            self.assertLess(position,len(new_lines),msg='upstream rule lost or reordered: '+x[:65])
            position+=1

    def test_combined_has_one_street_function_each(self):
        data=b.COMBINED.read_text()
        for s in ('preflop','flop','turn','river'):
            self.assertEqual(data.count(f'##f${s}##'),1)
        self.assertEqual(data.count('##f$H6CrowdedStrong##'),1)
        self.assertEqual(data.count('##f$H6TransitionHU##'),1)

    def test_topology_export_explains_unimplemented_states(self):
        with b.COVERAGE.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),40) # sum(n+1), n=1..5 =20 times two roles
        self.assertEqual(sum(x['ExpectedDomain']=='CROWDED_SRP_V1' for x in rows),6)
        self.assertEqual(sum(x['ExpectedDomain']=='MULTIWAY_TO_HU_V1' for x in rows),8)
        self.assertEqual(sum(x['ExpectedDomain']=='NOT_IN_NEW_LAYER' for x in rows),26)

    def test_regeneration_idempotent_and_parent_immutable(self):
        paths=(b.COMBINED,b.COVERAGE,b.PREVIOUS)
        before=tuple(hashlib.sha256(x.read_bytes()).hexdigest() for x in paths)
        self.assertEqual(b.build(),(74,10))
        self.assertEqual(before,tuple(hashlib.sha256(x.read_bytes()).hexdigest() for x in paths))

if __name__=='__main__':unittest.main()
