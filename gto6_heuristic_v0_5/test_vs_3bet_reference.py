import unittest
from dataclasses import replace
from action_ledger import HandLedger, Move, LedgerError, Round
from scenario_contract import (Action, Facing, PotType, Position, PositionalRelation,
    ScenarioState, Street, all_hand_classes, combo_count, pick_action, validate_policy)
from strict_observation import Observation, SeenSeat
from rfi_reference import RANGES as RFI_RANGES
from vs_open_reference import threebet_to_bb, expected_open
from vs_3bet_reference import (RANGES,BY_PAIR,SPECS,aggregate_conditional,
    opener_relation,fourbet_to_bb,policy_for)
from vs_3bet_bridge import prepare_vs_3bet, expected_pot_bb

POSITIONS=('LJ','HJ','CO','BTN','SB','BB')


def make_ledger(pair,stack=100.,threebet_override=None,open_override=None):
    opener,threebettor=pair
    l=HandLedger('VS3_'+opener+'_'+threebettor,{p:stack for p in POSITIONS})
    for p in POSITIONS[:POSITIONS.index(opener)]: l.act(p,Move.FOLD)
    l.act(opener,Move.RAISE,open_override if open_override is not None else expected_open(opener))
    for p in POSITIONS[POSITIONS.index(opener)+1:POSITIONS.index(threebettor)]:
        l.act(p,Move.FOLD)
    l.act(threebettor,Move.RAISE,threebet_override if threebet_override is not None else threebet_to_bb(*pair))
    for p in POSITIONS[POSITIONS.index(threebettor)+1:]:
        l.act(p,Move.FOLD)
    assert l.next_actor==opener,(pair,l.next_actor,l.history_key())
    return l


def obs(l):
    return Observation(l.hand_id,l.street,l.next_actor,True,l.pot_bb,
                       l.to_call(l.next_actor),
                       {p: SeenSeat(s.balance,s.contrib,s.folded,s.allin)
                        for p,s in l.seats.items()},True,True)


class RangeTests(unittest.TestCase):
    def test_exact_15_pairs_169_classes(self):
        pairs={(a,b) for i,a in enumerate(POSITIONS) for b in POSITIONS[i+1:]}
        self.assertEqual(set(RANGES),pairs)
        self.assertEqual(set(BY_PAIR),pairs)
        self.assertEqual(len(SPECS),15)
        for pair,r in RANGES.items():
            self.assertEqual(len(r),169)
            self.assertEqual(set(r),set(all_hand_classes()))
    def test_probability_and_reachability(self):
        for pair,rows in RANGES.items():
            for h,row in rows.items():
                p=RFI_RANGES[Position(pair[0])][h]['RAISE']
                self.assertEqual(row.open_probability,p)
                self.assertAlmostEqual(sum((row.fourbet,row.call,row.fold)), 1 if p>0 else 0)
                self.assertTrue(all(0<=x<=1 for x in (row.fourbet,row.call,row.fold)))
                if p==0:
                    self.assertEqual(row.bucket,'NOT_REACHABLE_FROM_RFI')
    def test_aa_kk_not_folded_and_are_4bet(self):
        for pair,rows in RANGES.items():
            for h in ('AA','KK'):
                self.assertEqual(rows[h].fourbet,1)
                self.assertEqual(rows[h].call,0)
                self.assertEqual(rows[h].fold,0)
    def test_4bet_size_non_shove(self):
        for pair in RANGES:
            fourbet=fourbet_to_bb(*pair)
            three=threebet_to_bb(*pair)
            self.assertGreaterEqual(fourbet,2*three-expected_open(pair[0]))  # minimo 4bet: raise size anterior
            self.assertLess(fourbet,40)
            self.assertGreater(fourbet,three)
    def test_4bet_sizing_ip_oop(self):
        self.assertEqual(opener_relation('BTN','BB'),PositionalRelation.IP)
        self.assertEqual(opener_relation('LJ','BTN'),PositionalRelation.OOP)
        self.assertEqual(opener_relation('SB','BB'),PositionalRelation.OOP)
        self.assertAlmostEqual(fourbet_to_bb('LJ','HJ'),21.20)
        self.assertAlmostEqual(fourbet_to_bb('BTN','BB'),23.58)
    def test_aggregate_conditioned_on_open_not_dealt(self):
        for pair in RANGES:
            self.assertAlmostEqual(sum(aggregate_conditional(*pair,k) for k in ('4BET','CALL','FOLD')),100)
            self.assertGreater(aggregate_conditional(*pair,'4BET'),0)
            self.assertGreater(aggregate_conditional(*pair,'FOLD'),0)
    def test_policy_all_reachable_2535(self):
        count=0
        for pair,rows in RANGES.items():
            for h,row in rows.items():
                s=ScenarioState(hand_id='H_'+h,street=Street.PREFLOP,
                     hero_position=Position(pair[0]),hand_class=h,dealt_players=6,
                     active_players=2,effective_stack_bb=100,
                     pot_bb=expected_pot_bb(*pair),
                     to_call_bb=threebet_to_bb(*pair)-expected_open(pair[0]),
                     pot_type=PotType.THREE_BET,facing=Facing.VS_3BET,
                     positional_relation=opener_relation(*pair),
                     opponent_position=Position(pair[1]))
                policy=policy_for(s)
                if row.open_probability==0:
                    self.assertIsNone(policy,(pair,h))
                else:
                    count+=1
                    self.assertIsNotNone(policy,(pair,h))
                    validate_policy(policy,s)
                    self.assertTrue(all(a.action in (Action.RAISE,Action.CALL,Action.FOLD)
                                        for a in policy.actions))
                    self.assertEqual(pick_action(policy,s),pick_action(policy,s))
        self.assertEqual(count,888)  # snapshot v0.4 de classes com p(RFI raise) > 0


class ReplayTests(unittest.TestCase):
    def test_all_15_pairs_legal_and_exact_pot(self):
        for pair in RANGES:
            l=make_ledger(pair)
            self.assertEqual(l.pf_facing(l.next_actor),'VS_3BET')
            self.assertAlmostEqual(l.pot_bb,expected_pot_bb(*pair))
            p=prepare_vs_3bet(l,obs(l),'AA')
            self.assertIsNotNone(p,pair)
            self.assertEqual(p.actions[0].action,Action.RAISE)
            self.assertEqual(p.actions[0].raise_to_bb,fourbet_to_bb(*pair))
    def test_end_to_end_2535_state_classes(self):
        for pair,rows in RANGES.items():
            l=make_ledger(pair)
            seen=obs(l)
            for h,row in rows.items():
                p=prepare_vs_3bet(l,seen,h)
                self.assertEqual(p is None,row.open_probability==0,(pair,h))
                if p is not None:
                    self.assertAlmostEqual(sum(a.weight for a in p.actions),1)
    def test_reject_other_3bet_sizing(self):
        pair=('BTN','BB')
        l=make_ledger(pair,threebet_override=threebet_to_bb(*pair)+1)
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'AA'))
    def test_reject_open_sizing(self):
        pair=('LJ','HJ')
        l=make_ledger(pair,threebet_override=8.,open_override=3.)
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'AA'))
    def test_reject_short_stacks(self):
        l=make_ledger(('BTN','BB'),stack=80.)
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'AA'))
    def test_reject_3bet_plus_caller_multiway(self):
        l=HandLedger('CALLER',{p:100. for p in POSITIONS})
        l.act('LJ',Move.RAISE,2.5)
        l.act('HJ',Move.RAISE,8)
        l.act('CO',Move.CALL)
        l.act('BTN',Move.FOLD)
        l.act('SB',Move.FOLD)
        l.act('BB',Move.FOLD)
        self.assertEqual(l.next_actor,'LJ')
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'AA'))
    def test_reject_3bet_after_call_squeeze(self):
        l=HandLedger('SQUEEZE',{p:100. for p in POSITIONS})
        l.act('LJ',Move.RAISE,2.5)
        l.act('HJ',Move.CALL)
        l.act('CO',Move.RAISE,11)
        for p in ('BTN','SB','BB'):l.act(p,Move.FOLD)
        self.assertEqual(l.next_actor,'LJ')
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'AA'))
    def test_reject_shove_3bet(self):
        l=HandLedger('SHOVE',{p:100. for p in POSITIONS})
        l.act('LJ',Move.RAISE,2.5)
        l.act('HJ',Move.SHOVE)
        for p in ('CO','BTN','SB','BB'): l.act(p,Move.FOLD)
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'AA'))
    def test_reject_other_actions_fourbet_later(self):
        l=make_ledger(('LJ','HJ'))
        l.act('LJ',Move.RAISE,22)
        self.assertEqual(l.pf_facing(l.next_actor),'VS_4BET')
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'AA'))
    def test_reject_bad_pot_snapshot(self):
        l=make_ledger(('CO','BB'))
        s=obs(l)
        with self.assertRaises(LedgerError):
            prepare_vs_3bet(l,replace(s,pot_bb=s.pot_bb+0.1),'AA')
    def test_reject_incomplete_history(self):
        l=make_ledger(('LJ','BTN'))
        with self.assertRaises(LedgerError):
            prepare_vs_3bet(l,replace(obs(l),complete_history=False),'AA')
    def test_reject_bad_hand(self):
        l=make_ledger(('LJ','CO'))
        with self.assertRaises(Exception): prepare_vs_3bet(l,obs(l),'AAo')
    def test_none_is_not_fold(self):
        l=make_ledger(('LJ','HJ'))
        self.assertIsNone(prepare_vs_3bet(l,obs(l),'72o'))
    def test_stable_policy_unchanged(self):
        l=make_ledger(('BTN','BB'))
        self.assertEqual(prepare_vs_3bet(l,obs(l),'AKs'),prepare_vs_3bet(l,obs(l),'AKs'))
    def test_all_policies_remain_draft(self):
        for pair in RANGES:
            l=make_ledger(pair)
            p=prepare_vs_3bet(l,obs(l),'AA')
            self.assertEqual(p.status,'DRAFT')

if __name__=='__main__':unittest.main()
