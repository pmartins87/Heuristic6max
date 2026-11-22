"""Adversarial source-driven snapshots; these are NOT OpenHoldem replays.

The expected decisions come from the independently reviewed F2 two-spot
contract. The actual decisions are evaluated from the native .oppl source,
not a parallel set of if/else poker policy rules.
"""
from dataclasses import replace
import unittest
from strict_symbolic_replay import Snapshot, source, StrictSource, UnsupportedSource


def trips():
    return Snapshot('flop', ('Qs', 'Js'), ('Qh', 'Qc', '6d'),
                    user_open=True, bot_raised_preflop=True, have_trips=True)


def top_pair():
    return Snapshot('flop', ('Ah', '5h'), ('As', '7d', '3c'),
                    user_open=True, bot_raised_preflop=True, have_top_pair=True)


class ExactSourceDecisions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = source()

    def action(self, snapshot):
        return self.policy.execute_section(snapshot.street, snapshot)[0]

    def test_trips_bet_one_third(self):
        self.assertEqual(self.action(trips()), 'BET_THIRD_POT')

    def test_weak_ax_check(self):
        self.assertEqual(self.action(top_pair()), 'CHECK')

    def test_order_of_hole_cards_is_irrelevant(self):
        self.assertEqual(self.action(replace(trips(), hand=('Js', 'Qs'))), 'BET_THIRD_POT')

    def test_order_of_board_cards_is_irrelevant(self):
        self.assertEqual(self.action(replace(trips(), board=('6d', 'Qh', 'Qc'))), 'BET_THIRD_POT')

    def test_preflop_first_in_sets_marker_and_open(self):
        for cards in [('Qs', 'Js'), ('Ah', '5h')]:
            with self.subTest(cards=cards):
                result, state = self.policy.execute_section('preflop',
                    Snapshot('preflop', cards, (), stack_size=100.0))
                self.assertEqual(result, 'RAISE_TO_2_5_BB')
                self.assertTrue(state.user_open)

    def test_preflop_wrong_hand_beeps_without_marker(self):
        result, state = self.policy.execute_section('preflop',
            Snapshot('preflop', ('Qs', 'Ts'), (), stack_size=100.0))
        self.assertEqual(result, 'BEEP_NO_ACTION')
        self.assertFalse(state.user_open)

    def test_preflop_limp_or_raise_is_excluded(self):
        for changes in [{'calls': 1}, {'raises': 1}, {'calls': 2, 'raises': 1}]:
            with self.subTest(changes=changes):
                result, state = self.policy.execute_section('preflop',
                    replace(Snapshot('preflop', ('Qs', 'Js'), (), stack_size=100.0), **changes))
                self.assertEqual(result, 'BEEP_NO_ACTION')
                self.assertFalse(state.user_open)

    def test_preflop_not_button_is_excluded(self):
        self.assertEqual(self.action(replace(
            Snapshot('preflop', ('Qs', 'Js'), (), stack_size=100.0),
            in_button=False)), 'BEEP_NO_ACTION')

    def test_preflop_wrong_stack_is_excluded(self):
        for stack in (94.99, 105.01, 0):
            with self.subTest(stack=stack):
                self.assertEqual(self.action(Snapshot('preflop', ('Qs', 'Js'), (),
                                                       stack_size=stack)), 'BEEP_NO_ACTION')

    def test_flop_guards_fail_closed_in_symbolic_model(self):
        changes = [
            {'user_open': False},
            {'bot_raised_preflop': False},
            {'opponents_preflop_raises': 1},
            {'nplayersdealt': 5},
            {'in_button': False},
            {'position': 'First'},
            {'opponents_on_flop': 2},
            {'opponents_left': 2},
            {'headsupchair': 4},
            {'bigblindchair': 4, 'headsupchair': 5},
            {'no_betting_on_flop': False},
            {'amount_to_call': 0.01},
            {'stack_size': 89.99},
            {'stack_size': 105.01},
            {'have_trips': False},
            {'hand': ('Qs', 'Ts')},
            {'board': ('Qh', 'Jc', '6d')},
            {'board': ('Qh', 'Qc', '6h')},
        ]
        for mod in changes:
            with self.subTest(change=mod):
                self.assertEqual(self.action(replace(trips(), **mod)),
                                 'BEEP_NO_ACTION')

    def test_flop_guards_on_second_case(self):
        changes = [
            {'user_open': False},
            {'amount_to_call': 0.5},
            {'have_top_pair': False},
            {'hand': ('Ah', '6h')},
            {'board': ('As', '7d', '4c')},
            {'opponents_on_flop': 2},
        ]
        for mod in changes:
            with self.subTest(change=mod):
                self.assertEqual(self.action(replace(top_pair(), **mod)),
                                 'BEEP_NO_ACTION')

    def test_cross_spot_hand_and_board_mismatch(self):
        for state in [replace(trips(), board=top_pair().board),
                      replace(top_pair(), board=trips().board)]:
            self.assertEqual(self.action(state), 'BEEP_NO_ACTION')

    def test_turn_and_river_never_return_a_poker_action(self):
        for street in ('turn', 'river'):
            with self.subTest(street=street):
                self.assertEqual(self.action(replace(trips(), street=street)),
                                 'BEEP_NO_ACTION')

    def test_preflop_memory_never_survives_hypothetical_new_hand_in_model(self):
        _, initial = self.policy.execute_section('preflop',
            Snapshot('preflop', ('Qs', 'Js'), (), stack_size=100.0))
        self.assertTrue(initial.user_open)
        next_hand = replace(trips(), user_open=False)
        self.assertEqual(self.action(next_hand), 'BEEP_NO_ACTION')

    def test_unknown_symbol_fails_strict_static_parser(self):
        self.assertRaises(UnsupportedSource, StrictSource,
            '''##f$V2PilotBTNOpenRFIContext##\nWHEN Others RETURN TRUE FORCE
##f$preflop##\nWHEN (UnknownSymbol) Check FORCE
##f$flop##\nWHEN Others Beep FORCE
##f$turn##\nWHEN Others Beep FORCE
##f$river##\nWHEN Others Beep FORCE''')

    def test_source_first_match_has_beep_only_on_out_of_scope(self):
        self.assertEqual(self.action(trips()), 'BET_THIRD_POT')
        self.assertEqual(self.action(top_pair()), 'CHECK')
        self.assertEqual(self.action(replace(trips(), opponents_left=0)),
                         'BEEP_NO_ACTION')


if __name__ == '__main__':
    unittest.main()
