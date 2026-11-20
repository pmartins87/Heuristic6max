import json
import tempfile
import unittest
from pathlib import Path
from scenario_contract import (Action, Facing, Policy, PotType, Position,
    PositionalRelation, ScenarioState, Street, all_hand_classes, combo_count, pick_action,
    validate_policy)
from vs_open_reference import (RANGES, BY_PAIR, SHADOWS, aggregate, expected_open,
    positional_relation, threebet_to_bb, expected_pot_bb, policy_for, SPECS)
from vs_open_bridge import prepare_vs_open
from strict_observation import Observation, SeenSeat
from evidence_ingest import load_verified_fixture
from action_ledger import HandLedger, LedgerError, Move, Round

POSITIONS=('LJ','HJ','CO','BTN','SB','BB')
SEATS={p:100. for p in POSITIONS}


def make_ledger(pair, *, stack=100., open_size=None):
    opener,hero=pair
    l=HandLedger('TEST_'+opener+'_'+hero,{p:stack for p in POSITIONS})
    for p in POSITIONS[:POSITIONS.index(opener)]: l.act(p, Move.FOLD)
    l.act(opener,Move.RAISE,open_size if open_size is not None else expected_open(opener))
    for p in POSITIONS[POSITIONS.index(opener)+1:POSITIONS.index(hero)]:
        l.act(p,Move.FOLD)
    assert l.next_actor==hero, (pair,l.next_actor)
    return l


def make_obs(l):
    return Observation(hand_id=l.hand_id,street=l.street,hero_position=l.next_actor,
        hero_turn=True,pot_bb=l.pot_bb,hero_to_call_bb=l.to_call(l.next_actor),
        seats={p:SeenSeat(s.balance,s.contrib,s.folded,s.allin) for p,s in l.seats.items()},
        complete_history=True,stable_scrape=True)

class ReferenceTests(unittest.TestCase):
    def test_all_15_pairs(self):
        expected={(a,b) for i,a in enumerate(POSITIONS) for b in POSITIONS[i+1:]}
        self.assertEqual(set(RANGES),expected)
        self.assertEqual(set(BY_PAIR),expected)
        self.assertEqual(len(SPECS),15)
    def test_169_hands_all_nodes(self):
        for pair,rows in RANGES.items():
            self.assertEqual(set(rows),set(all_hand_classes()))
            for hand,row in rows.items():
                self.assertAlmostEqual(row.threebet+row.call+row.fold,1)
                self.assertTrue(all(0<=x<=1 for x in (row.threebet,row.call,row.fold)))
    def test_no_sb_flat(self):
        for pair,rows in RANGES.items():
            if pair[1]=='SB':
                self.assertTrue(all(r.call==0 for r in rows.values()))
    def test_no_pure_3bet_aa_folds(self):
        for pair,rows in RANGES.items():
            self.assertEqual(rows['AA'].threebet,1,pair)
            self.assertEqual(rows['AA'].fold,0,pair)
    def test_3bet_increases_against_later_openers_for_bb(self):
        self.assertLess(aggregate('LJ','BB','3BET'),aggregate('CO','BB','3BET'))
        self.assertLess(aggregate('CO','BB','3BET'),aggregate('BTN','BB','3BET'))
        self.assertLess(aggregate('BTN','BB','3BET'),aggregate('SB','BB','3BET'))
    def test_reference_benchmark_bb_reasonable_but_not_exact(self):
        # Não exige equalizar tabela de solver: apenas alerta desvios drásticos.
        b={'LJ':(5.8,20.7),'HJ':(7.5,21.5),'CO':(9.5,24.2),'BTN':(13.4,32.5),'SB':(16.2,41.8)}
        for opp,(target3,targetcall) in b.items():
            self.assertLess(abs(aggregate(opp,'BB','3BET')-target3),3.0,opp)
            self.assertLess(abs(aggregate(opp,'BB','CALL')-targetcall),4.0,opp)
    def test_sizes_and_relation(self):
        self.assertEqual(threebet_to_bb('LJ','HJ'),8.0)
        self.assertEqual(threebet_to_bb('BTN','SB'),10.25)
        self.assertEqual(threebet_to_bb('SB','BB'),9.6)
        self.assertEqual(positional_relation('SB','BB'),PositionalRelation.IP)
        self.assertEqual(positional_relation('BTN','BB'),PositionalRelation.OOP)
    def test_policy_all_classes_each_scenario(self):
        for pair in RANGES:
            opener,hero=pair
            contrib=0.5 if hero=='SB' else 1 if hero=='BB' else 0
            for hand in all_hand_classes():
                s=ScenarioState(hand_id='A1',street=Street.PREFLOP,hero_position=Position(hero),
                    hand_class=hand,dealt_players=6,active_players=6,
                    effective_stack_bb=100,pot_bb=expected_pot_bb(opener),
                    to_call_bb=expected_open(opener)-contrib,pot_type=PotType.SRP,
                    facing=Facing.VS_OPEN,positional_relation=positional_relation(*pair),
                    opponent_position=Position(opener))
                p=policy_for(s)
                self.assertIsNotNone(p,(pair,hand))
                validate_policy(p,s)
                a=pick_action(p,s)
                self.assertIn(a.action,{Action.RAISE,Action.CALL,Action.FOLD})
                self.assertEqual(a,pick_action(p,s))
    def test_shadowed_range_auditable(self):
        self.assertEqual(len(SHADOWS),15)
        self.assertTrue(any(SHADOWS.values()))

class BridgeTests(unittest.TestCase):
    def test_each_pair_bridge_legit(self):
        for pair in RANGES:
            l=make_ledger(pair)
            p=prepare_vs_open(l,make_obs(l),'AA')
            self.assertIsNotNone(p,pair)
            self.assertEqual(p.actions[0].action,Action.RAISE)
    def test_end_to_end_2535_verified_synthetic_states(self):
        # Teste de contrato: 15 pares × 169 classes usando histórico e snapshot
        # sintéticos coerentes. NÃO substitui replay real de OpenHoldem.
        for pair in RANGES:
            l=make_ledger(pair)
            seen=make_obs(l)
            for hand in all_hand_classes():
                p=prepare_vs_open(l,seen,hand)
                self.assertIsNotNone(p,(pair,hand))
                self.assertTrue(p.actions)
                self.assertAlmostEqual(sum(a.weight for a in p.actions),1)

    def test_unchanged_mixed_action(self):
        l=make_ledger(('BTN','BB'))
        a=prepare_vs_open(l,make_obs(l),'A9s')
        b=prepare_vs_open(l,make_obs(l),'A9s')
        self.assertEqual(a,b)
    def test_reject_limper_isoraise(self):
        l=HandLedger('limp',SEATS)
        l.act('LJ',Move.CALL)
        l.act('HJ',Move.RAISE,2.5)
        self.assertIsNone(prepare_vs_open(l,make_obs(l),'AA'))
    def test_reject_caller_between_open_and_hero(self):
        l=HandLedger('caller',SEATS)
        l.act('LJ',Move.RAISE,2.5)
        l.act('HJ',Move.CALL)
        self.assertIsNone(prepare_vs_open(l,make_obs(l),'AA'))
    def test_reject_open_sizing_unmodelled(self):
        l=make_ledger(('LJ','HJ'),open_size=3.)
        self.assertIsNone(prepare_vs_open(l,make_obs(l),'AA'))
    def test_reject_stack_outside_calibration(self):
        l=make_ledger(('BTN','BB'),stack=80.)
        self.assertIsNone(prepare_vs_open(l,make_obs(l),'AA'))
    def test_reject_bad_observation(self):
        l=make_ledger(('BTN','BB'))
        snap=make_obs(l)
        bad=Observation(snap.hand_id,snap.street,snap.hero_position,snap.hero_turn,snap.pot_bb+1,
                        snap.hero_to_call_bb,snap.seats,True,True)
        with self.assertRaises(LedgerError):prepare_vs_open(l,bad,'AA')
    def test_reject_incomplete_history(self):
        l=make_ledger(('LJ','HJ'))
        snap=make_obs(l)
        bad=Observation(snap.hand_id,snap.street,snap.hero_position,True,snap.pot_bb,snap.hero_to_call_bb,
                        snap.seats,False,True)
        with self.assertRaises(LedgerError):prepare_vs_open(l,bad,'AA')
    def test_atomic_shove_no_reopen_reject(self):
        l=HandLedger('S',{'SB':100.,'BB':10.})
        l.act('SB',Move.RAISE,6.)
        l.act('BB',Move.SHOVE)
        before=(l.pot_bb,l.seats['SB'].balance,l.seats['SB'].contrib,len(l.events),l.next_actor)
        with self.assertRaises(LedgerError):l.act('SB',Move.SHOVE)
        after=(l.pot_bb,l.seats['SB'].balance,l.seats['SB'].contrib,len(l.events),l.next_actor)
        self.assertEqual(before,after)
    def test_verified_fixture_import(self):
        l=make_ledger(('LJ','BTN'))
        obs=make_obs(l)
        events=[dict(actor=e.pid,move=e.move.value,to_bb=e.street_to_bb if e.move==Move.RAISE else None,
                     verified=True,source='MANUAL_VERIFIED') for e in l.events]
        # 'to_bb' for FOLD should be omitted, not null: no difference for ledger.
        obj=dict(hand_id=l.hand_id,seats=SEATS,events=events,
            observation=dict(hand_id=obs.hand_id,street=obs.street.value,hero_position=obs.hero_position,
                hero_turn=True,pot_bb=obs.pot_bb,hero_to_call_bb=obs.hero_to_call_bb,
                seats={p:dict(stack_remaining_bb=s.stack_remaining_bb,street_contribution_bb=s.street_contribution_bb,
                       folded=s.folded,allin=s.allin) for p,s in obs.seats.items()},
                complete_history=True,stable_scrape=True))
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'verified.json'
            path.write_text(json.dumps(obj))
            replay,snapshot=load_verified_fixture(path)
            self.assertEqual(replay.current_spot_key(),l.current_spot_key())
            self.assertIsNotNone(prepare_vs_open(replay,snapshot,'AA'))
            obj['events'][0]['verified']=False
            path.write_text(json.dumps(obj))
            with self.assertRaises(LedgerError):load_verified_fixture(path)

if __name__=='__main__': unittest.main()
