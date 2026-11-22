"""Source-contract checks only. They do NOT simulate OpenHoldem parsing or actions."""
from pathlib import Path
import unittest

P = Path(__file__).with_name('f2_two_spots_draft.oppl')
S = P.read_text(encoding='utf-8')

class F2PilotStaticTests(unittest.TestCase):
    def test_only_two_flop_actions(self):
        f = S.split('##f$flop##', 1)[1].split('##f$turn##', 1)[0]
        active = [x.strip() for x in f.splitlines() if x.strip().startswith('WHEN') and 'Beep FORCE' not in x]
        self.assertEqual(len(active), 2)
        self.assertIn('board$QhQc6d AND hand$QsJs AND HaveTrips) BetThirdPot FORCE', active[0])
        self.assertIn('board$As7d3c AND hand$Ah5h AND HaveTopPair) Check FORCE', active[1])
    def test_source_is_not_legacy_or_fallback_to_fold(self):
        self.assertEqual(S.count('##f$flop##'), 1)
        self.assertNotIn('Fold FORCE', S)
        self.assertNotIn('Allin FORCE', S)
        self.assertNotIn('RaiseMax FORCE', S)
        for section in ['preflop', 'flop', 'turn', 'river']:
            body = S.split(f'##f${section}##', 1)[1].split('##f$', 1)[0]
            self.assertIn('WHEN Others Beep FORCE', body)
    def test_real_preflop_origin_and_srp_guard(self):
        ctx = S.split('##f$V2PilotBTNOpenRFIContext##', 1)[1].split('##f$preflop##', 1)[0]
        for token in ['InButton', 'Position = Last', 'OpponentsOnFlop = 1', 'OpponentsLeft = 1',
                      'headsupchair = bigblindchair', 'user_V2PilotBTNOpen', 'BotRaisedBeforeFlop',
                      'NumberOfRaisesBeforeFlop = 0', 'NoBettingOnFlop', 'AmountToCall = 0',
                      'StackSize >= 90', 'StackSize <= 105']:
            self.assertIn(token, ctx)
        pf = S.split('##f$preflop##', 1)[1].split('##f$flop##', 1)[0]
        self.assertIn('Calls = 0 AND Raises = 0', pf)
        self.assertIn('Set user_V2PilotBTNOpen', pf)
        self.assertIn('RaiseTo 2.5 FORCE', pf)
    def test_no_ambiguous_trailing_s_hand_class(self):
        self.assertNotIn('hand$QJs', S)
        self.assertIn('hand$QsJs', S)
        self.assertIn('hand$Ah5h', S)

if __name__ == '__main__':
    unittest.main()
