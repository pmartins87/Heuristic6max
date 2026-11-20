"""Regressões de contrato — python -m unittest -v."""
import unittest
from dataclasses import replace
from scenario_contract import *


def base_preflop(**kwargs):
    d = dict(hand_id='hand-001', street=Street.PREFLOP, hero_position=Position.BTN,
             hand_class='AKs', dealt_players=6, active_players=6, effective_stack_bb=100,
             pot_bb=1.5, to_call_bb=0, pot_type=PotType.UNOPENED, facing=Facing.RFI,
             positional_relation=PositionalRelation.IP)
    d.update(kwargs)
    return ScenarioState(**d)


def base_flop(**kwargs):
    d = dict(hand_id='hand-002', street=Street.FLOP, hero_position=Position.BTN,
             hand_class='AKs', dealt_players=6, active_players=2, effective_stack_bb=95,
             pot_bb=6.0, to_call_bb=0, pot_type=PotType.SRP,
             facing=Facing.CHECKED_TO, positional_relation=PositionalRelation.IP,
             opponent_position=Position.BB,
             board=BoardState(BoardFamily.ACE_HIGH, Suits.RAINBOW, Pairing.UNPAIRED, Connectivity.DISCONNECTED),
             hero_hand=HeroHandState(MadeHand.TOP_PAIR, Draw.NONE, 'NON_NUTS', 'TOP'),
             prev_line='PFR_HERO')
    d.update(kwargs)
    return ScenarioState(**d)


class ContractTests(unittest.TestCase):
    def test_169_hand_classes(self):
        hands = all_hand_classes()
        self.assertEqual(len(hands), 169)
        self.assertEqual(len(set(hands)), 169)
        self.assertEqual(sum(combo_count(h) for h in hands), 1326)

    def test_invalid_hands(self):
        for h in ('AAo', 'KAs', 'AKx', 'ABs', 'KKs', ''):
            with self.assertRaises(ContractError): validate_hand_class(h)

    def test_valid_hand_types(self):
        for h in ('AKs', 'AKo', 'QQ', '72o', 'T9s'):
            self.assertEqual(validate_hand_class(h), h)

    def test_preflop_key_changes_with_position(self):
        a = base_preflop()
        self.assertNotEqual(a.key(), replace(a, hero_position=Position.HJ).key())

    def test_preflop_key_changes_with_hand(self):
        a = base_preflop()
        self.assertNotEqual(a.key(), replace(a, hand_class='QQ').key())

    def test_flop_key_changes_with_board(self):
        a = base_flop()
        b = replace(a, board=replace(a.board, suits=Suits.TWO_TONE))
        self.assertNotEqual(a.key(), b.key())

    def test_flop_key_changes_with_prev_line(self):
        a = base_flop()
        self.assertNotEqual(a.key(), replace(a, prev_line='PFR_VILLAIN').key())

    def test_flop_requires_board_and_hand(self):
        with self.assertRaises(ContractError): base_flop(hero_hand=None)
        with self.assertRaises(ContractError): base_flop(board=None)

    def test_preflop_rejects_board(self):
        with self.assertRaises(ContractError): base_preflop(board=base_flop().board)

    def test_requires_positive_pot_and_stack(self):
        for kw in ({'pot_bb':0}, {'effective_stack_bb':0}, {'pot_bb':-1}):
            with self.assertRaises(ContractError): base_preflop(**kw)

    def test_requires_call_when_facing_bet(self):
        with self.assertRaises(ContractError): base_flop(facing=Facing.VS_BET, to_call_bb=0)

    def test_no_call_when_checked_to(self):
        with self.assertRaises(ContractError): base_flop(facing=Facing.CHECKED_TO, to_call_bb=2)

    def test_spr_bucket(self):
        self.assertEqual(spr_band(0.9), 'SPR0_1')
        self.assertEqual(spr_band(5.0), 'SPR4_8')

    def test_mix_stable_across_polling(self):
        s=base_preflop()
        p=Policy('PF.BTN.RFI.001', (WeightedAction(Action.RAISE,0.65,raise_to_bb=2.5), WeightedAction(Action.FOLD,0.35)),
                 'Abertura mista de teste; não é range operacional', 'TEST_ONLY')
        vals={pick_action(p,s) for _ in range(200)}
        self.assertEqual(len(vals),1)

    def test_mix_changes_by_hand(self):
        s=base_preflop()
        u1=stable_uniform(s.hand_id,s.key(),'P1')
        u2=stable_uniform('next-hand',s.key(),'P1')
        self.assertNotEqual(u1,u2)

    def test_refuse_bet_while_facing_bet(self):
        s=base_flop(facing=Facing.VS_BET,to_call_bb=2)
        p=Policy('BAD',(WeightedAction(Action.BET,1.0,.5),),'teste','TEST_ONLY')
        with self.assertRaises(ContractError): validate_policy(p,s)

    def test_refuse_call_when_checked_to(self):
        s=base_flop()
        p=Policy('BAD',(WeightedAction(Action.CALL,1.0),),'teste','TEST_ONLY')
        with self.assertRaises(ContractError): validate_policy(p,s)

    def test_invalid_mixed_weights(self):
        s=base_preflop()
        p=Policy('BAD',(WeightedAction(Action.FOLD,.7),WeightedAction(Action.RAISE,.4,raise_to_bb=2.5)), 'teste','TEST_ONLY')
        with self.assertRaises(ContractError): validate_policy(p,s)

    def test_no_fallback_to_fold(self):
        self.assertIsNone(policy_or_none({},base_preflop()))

    def test_scenario_different_as_shove(self):
        a=base_flop()
        b=base_flop(facing=Facing.VS_SHOVE,to_call_bb=95)
        self.assertNotEqual(a.key(),b.key())

    def test_preflop_raises_are_raise_to_bb(self):
        s=base_preflop()
        p=Policy('BAD',(WeightedAction(Action.RAISE,1.0,size_pot=2.5),),'teste','TEST_ONLY')
        with self.assertRaises(ContractError): validate_policy(p,s)

    def test_legal_rfi_policy(self):
        a=base_preflop()
        p=Policy('EXAMPLE',(WeightedAction(Action.RAISE,1.,raise_to_bb=2.5),), 'somente prova de contrato','TEST_ONLY')
        self.assertEqual(pick_action(p,a).action, Action.RAISE)


if __name__=='__main__':
    unittest.main()
