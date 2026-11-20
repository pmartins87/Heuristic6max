import unittest
from dataclasses import replace
from rfi_reference import TARGETS, RANGES, aggregate, policy_for, decide
from scenario_contract import (all_hand_classes, Position, ScenarioState, Street,
                               Facing, PotType, PositionalRelation, Action,
                               ContractError, validate_policy, pick_action)


def rfi_scenario(pos=Position.BTN,hand='AKs',stack=100,pot=1.5):
    return ScenarioState(hand_id='12345', street=Street.PREFLOP,
         hero_position=pos, hand_class=hand, dealt_players=6, active_players=6,
         effective_stack_bb=stack, pot_bb=pot,to_call_bb=0.5 if pos==Position.SB else 1.0,
         pot_type=PotType.UNOPENED,facing=Facing.RFI,positional_relation=PositionalRelation.UNKNOWN)

class RfiTests(unittest.TestCase):
    def test_completeness_5_by_169(self):
        for pos in TARGETS:
            self.assertEqual(set(RANGES[pos]),set(all_hand_classes()))

    def test_all_weights_sum_one(self):
        for pos in TARGETS:
            for h in all_hand_classes():
                ws=RANGES[pos][h]
                self.assertAlmostEqual(sum(ws.values()),1,places=9)
                self.assertTrue(all(0<=v<=1 for v in ws.values()))

    def test_aggregate_targets(self):
        for pos, cfg in TARGETS.items():
            for a in ('RAISE','LIMP'):
                self.assertLess(abs(aggregate(pos,a)-100*cfg[a]), 0.5)  # tolerância 0,5 ponto percentual

    def test_sb_only_limp(self):
        for pos in (Position.LJ,Position.HJ,Position.CO,Position.BTN):
            self.assertEqual(aggregate(pos,'LIMP'),0)
        self.assertGreater(aggregate(Position.SB,'LIMP'),0)

    def test_premium_never_folds(self):
        for pos in TARGETS:
            for hand in ('AA','KK','QQ','AKs'):
                self.assertEqual(RANGES[pos][hand]['RAISE'],1.0)

    def test_specific_hand_guardrails(self):
        # Uma calibração apenas de frequência total deixaria estes spots errados.
        self.assertEqual(RANGES[Position.LJ]['A8o']['RAISE'],0)
        self.assertEqual(RANGES[Position.LJ]['QJo']['RAISE'],0)
        self.assertEqual(RANGES[Position.LJ]['76s']['RAISE'],1)
        self.assertEqual(RANGES[Position.BTN]['22']['RAISE'],1)
        self.assertEqual(RANGES[Position.BTN]['K2s']['RAISE'],1)
        self.assertEqual(RANGES[Position.HJ]['KJo']['RAISE'],1)
        self.assertEqual(RANGES[Position.LJ]['KJo']['RAISE'],0.4)

    def test_button_opens_more_than_hj(self):
        self.assertGreater(aggregate(Position.BTN,'RAISE'),aggregate(Position.HJ,'RAISE'))

    def test_no_bb_rfi_policy(self):
        self.assertIsNone(policy_for(rfi_scenario(Position.BB)))

    def test_unsupported_stacks_do_not_fallback(self):
        for st in (15,50,75,90,110,121,200):
            self.assertIsNone(policy_for(rfi_scenario(stack=st)))

    def test_unsupported_pot_type_and_size(self):
        self.assertIsNone(policy_for(rfi_scenario(pot=3.5)))
        self.assertIsNone(policy_for(replace(rfi_scenario(), pot_type=PotType.THREE_BET)))

    def test_reuse_stable_sample(self):
        s=rfi_scenario(hand='K9o')
        p=policy_for(s)
        self.assertIsNotNone(p)
        validate_policy(p,s)
        self.assertEqual(len({pick_action(p,s) for _ in range(100)}),1)

    def test_rl_note_heuristic_not_release(self):
        p=policy_for(rfi_scenario())
        self.assertEqual(p.status,'DRAFT')
        self.assertIn('HEURISTIC',p.provenance)

    def test_actions_are_legal_on_rfi(self):
        for pos in TARGETS:
            for hand in all_hand_classes():
                s=rfi_scenario(pos,hand)
                validate_policy(policy_for(s),s)

if __name__=='__main__': unittest.main()
