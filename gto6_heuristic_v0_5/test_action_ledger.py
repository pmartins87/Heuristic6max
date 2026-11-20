import unittest
from action_ledger import HandLedger, LedgerError, Move, Round

SIX={p:100.0 for p in ('LJ','HJ','CO','BTN','SB','BB')}
HU={'SB':100., 'BB':100.}

class LedgerTests(unittest.TestCase):
    def test_rfi_positions_turn_order(self):
        l=HandLedger('A',SIX)
        self.assertEqual(l.next_actor,'LJ')
        self.assertEqual(l.pf_facing('LJ'),'RFI')
        self.assertAlmostEqual(l.to_call('LJ'),1)
        for p in ('LJ','HJ','CO','BTN','SB'):
            l.act(p, Move.FOLD)
        self.assertIsNone(l.next_actor)  # walk: BB recebe blinds sem agir
        self.assertTrue(l.finished)

    def test_hu_sb_first_then_bb_postflop(self):
        l=HandLedger('HU', HU)
        self.assertEqual(l.next_actor,'SB')
        l.act('SB',Move.RAISE,2.5)
        l.act('BB',Move.CALL)
        self.assertAlmostEqual(l.pot_bb,5)
        l.next_street(Round.FLOP)
        self.assertEqual(l.next_actor,'BB')
        self.assertEqual(l.to_call('BB'),0)

    def test_open_call_3bet(self):
        l=HandLedger('B',SIX)
        l.act('LJ',Move.FOLD)
        l.act('HJ',Move.RAISE,2.5)
        self.assertEqual(l.pf_facing('CO'),'VS_OPEN')
        l.act('CO',Move.RAISE,8.0)
        self.assertEqual(l.pf_facing('BTN'),'VS_3BET')
        self.assertAlmostEqual(l.pot_bb,12.0)
        self.assertAlmostEqual(l.min_raise_to(),13.5)

    def test_short_shove_call_does_not_count_as_3bet(self):
        l=HandLedger('Z',{'LJ':100,'HJ':3,'CO':100,'BTN':100,'SB':100,'BB':100})
        l.act('LJ',Move.RAISE,6)
        l.act('HJ',Move.SHOVE)  # call-allin curto de 3BB, não é reraise!
        self.assertFalse(l.events[-1].is_aggressive)
        self.assertEqual(l.pf_facing('CO'),'VS_OPEN')

    def test_bb_vs_limp_option_not_plain_walk(self):
        l=HandLedger('Z',{'SB':100,'BB':100})
        l.act('SB',Move.CALL)
        self.assertEqual(l.pf_facing('BB'),'BB_VS_LIMP_OPTION')
        self.assertIn(Move.RAISE,l.allowed('BB'))

    def test_squeeze_detection(self):
        l=HandLedger('S', SIX)
        l.act('LJ',Move.FOLD)
        l.act('HJ',Move.RAISE,2.5)
        l.act('CO',Move.CALL)
        e=l.act('BTN',Move.RAISE,11.0)
        self.assertTrue(e.is_squeeze)
        self.assertEqual(l.pf_facing('SB'),'VS_SQUEEZE')

    def test_postflop_bet_call_and_pot(self):
        l=HandLedger('T',HU)
        l.act('SB',Move.RAISE,2.5)
        l.act('BB',Move.CALL)
        l.next_street(Round.FLOP)
        e=l.act('BB',Move.BET,1.5)
        self.assertTrue(e.full_raise)
        self.assertAlmostEqual(l.pot_bb,6.5)
        self.assertAlmostEqual(l.to_call('SB'),1.5)
        l.act('SB',Move.CALL)
        self.assertAlmostEqual(l.pot_bb,8.0)
        l.next_street(Round.TURN)
        self.assertEqual(l.next_actor,'BB')

    def test_raise_below_min_disallowed(self):
        l=HandLedger('B',SIX)
        with self.assertRaises(LedgerError): l.act('LJ',Move.RAISE,1.5)
        self.assertEqual(l.next_actor,'LJ')

    def test_unknown_position_disallowed(self):
        with self.assertRaises(LedgerError): HandLedger('X',{'LJ':100,'SB':100,'BB':100})

    def test_out_of_turn(self):
        l=HandLedger('B',SIX)
        with self.assertRaises(LedgerError): l.act('BTN',Move.RAISE,2.5)

    def test_betsize_over_stack(self):
        l=HandLedger('B',SIX)
        with self.assertRaises(LedgerError): l.act('LJ',Move.RAISE,101.0)

    def test_no_fictive_transition(self):
        l=HandLedger('B',SIX)
        with self.assertRaises(LedgerError): l.next_street(Round.FLOP)

    def test_history_keys_distinguish_raise_size(self):
        a=HandLedger('A',SIX); b=HandLedger('B',SIX)
        a.act('LJ',Move.RAISE,2.5)
        b.act('LJ',Move.RAISE,3)
        self.assertNotEqual(a.current_spot_key(),b.current_spot_key())

    def test_bet_when_facing_bet_illegal(self):
        l=HandLedger('T',HU)
        l.act('SB',Move.CALL)
        l.act('BB',Move.CHECK)
        l.next_street(Round.FLOP)
        l.act('BB',Move.BET,3)
        with self.assertRaises(LedgerError): l.act('SB',Move.BET,6)

    def test_allin_partial_raise_does_not_reopen(self):
        l=HandLedger('P',{'SB':100,'BB':10})
        l.act('SB',Move.RAISE,6)
        # BB shove para 10BB: incremento +4 não é full raise (mínimo +5).
        e=l.act('BB',Move.SHOVE)
        self.assertFalse(e.full_raise)
        self.assertEqual(l.next_actor,'SB')
        self.assertNotIn(Move.RAISE,l.allowed('SB'))
        self.assertNotIn(Move.SHOVE,l.allowed('SB'))
        l.act('SB',Move.CALL)
        self.assertFalse(l.pending)

    def test_short_allin_call(self):
        l=HandLedger('C',{'SB':30,'BB':5})
        l.act('SB',Move.RAISE,10)
        self.assertEqual(l.next_actor,'BB')
        self.assertNotIn(Move.CALL,l.allowed('BB'))
        l.act('BB',Move.SHOVE)
        self.assertFalse(l.pending)
        self.assertAlmostEqual(l.pot_bb,15)

    def test_round_complete_after_fold(self):
        l=HandLedger('F',HU)
        l.act('SB', Move.RAISE,2.5)
        l.act('BB', Move.FOLD)
        self.assertTrue(l.finished)
        with self.assertRaises(LedgerError): l.next_street(Round.FLOP)

    def test_repeated_check_no_raise_unavailable(self):
        l=HandLedger('A',HU)
        l.act('SB',Move.CALL)
        self.assertIn(Move.CHECK,l.allowed('BB'))
        l.act('BB',Move.CHECK)
        l.next_street(Round.FLOP)
        l.act('BB',Move.CHECK)
        l.act('SB',Move.CHECK)
        l.next_street(Round.TURN)

    def test_illegal_street_to_on_check(self):
        l=HandLedger('A',HU)
        l.act('SB',Move.CALL)
        with self.assertRaises(LedgerError): l.act('BB',Move.CHECK,1)

    def test_same_observations_same_history_signature(self):
        a=HandLedger('A',HU); b=HandLedger('B',HU)
        for l in (a,b):
            l.act('SB',Move.RAISE,2.5)
            l.act('BB',Move.CALL)
        self.assertEqual(a.history_key(),b.history_key())

if __name__ == '__main__': unittest.main()
