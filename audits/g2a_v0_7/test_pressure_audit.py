"""Unit and forensic tests for isolated 3bet pressure audit (not GTO)."""
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import pressure_audit as p


class AuditTests(unittest.TestCase):
    def test_exact_eight_review_nodes(self):
        self.assertEqual(len(p.KEY_PAIRS),8)
        self.assertTrue(set(p.KEY_PAIRS).issubset(set(p.PAIRS)))

    def test_all_fifteen_mass_consistency_with_v06(self):
        self.assertEqual(len(p.PAIRS),15)
        for opener, threebettor in p.PAIRS:
            with self.subTest(pair=(opener, threebettor)):
                audit=p.audit_spot(opener,threebettor)
                reference, _, _=p.adjusted_action_percentages(opener,threebettor)
                self.assertAlmostEqual(audit.model_fold_pct,reference['FOLD'],places=8)
                self.assertGreater(audit.distinct_threebet_combos,0)
                self.assertGreaterEqual(audit.villain_combo_weight_pct_above_threshold,0)
                self.assertLessEqual(audit.villain_combo_weight_pct_above_threshold,100)

    def test_break_even_formula_blind_positions(self):
        self.assertAlmostEqual(p.breakeven_metrics('LJ','HJ')[3],100*8/12,places=10)
        a=p.breakeven_metrics('BTN','SB')
        self.assertAlmostEqual(a[1],9.75,places=8)
        self.assertAlmostEqual(a[2],4,places=8)
        self.assertAlmostEqual(a[3],100*9.75/13.75,places=8)
        b=p.breakeven_metrics('SB','BB')
        self.assertAlmostEqual(b[1],8.6,places=8)
        self.assertAlmostEqual(b[2],4,places=8)

    def test_inclusion_exclusion_bruteforce_physical(self):
        rows=p.HERO[('LJ','HJ')]
        for a,b,w,den,observed_fold in list(p.villain_combo_weights('LJ','HJ'))[::80][:5]:
            with self.subTest(hand=(a,b)):
                combos=[(x,y) for x,y in p.COMBOS if a not in (x,y) and b not in (x,y)]
                direct_den=sum(rows[p.hand_class((x,y))].open_probability for x,y in combos)
                direct_fold=sum(rows[p.hand_class((x,y))].open_probability*
                                rows[p.hand_class((x,y))].fold for x,y in combos)
                self.assertAlmostEqual(den,direct_den,places=8)
                self.assertAlmostEqual(observed_fold,direct_fold/direct_den,places=8)

    def test_poker_policy_unchanged_by_audit(self):
        # Independent snapshot: no write to source CSV/policy modules.
        import hashlib
        src=p.BASE
        names=('RFI_100BB_169x5_DRAFT.csv','VS_OPEN_100BB_15x169_DRAFT.csv',
               'VS_3BET_100BB_15x169_DRAFT.csv','vs_3bet_reference.py')
        before={n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in names}
        p.audit_spot('SB','BB')
        self.assertEqual(before,{n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in names})

    def test_critical_spot_signs(self):
        # Mechanically grounded regression observations, not GTO targets.
        self.assertGreater(p.audit_spot('HJ','CO').zero_equity_EV_bb,0)
        self.assertLess(p.audit_spot('SB','BB').zero_equity_EV_bb,0)

    def test_hand_detail_shares_conserve(self):
        for pair in p.KEY_PAIRS:
            with self.subTest(pair=pair):
                hands=list(p.class_details(*pair))
                self.assertAlmostEqual(sum(h[2] for h in hands),100,places=8)
                self.assertTrue(all(0<=h[3]<=100 for h in hands))
                self.assertEqual(len({h[0] for h in hands}),len(hands))

if __name__=='__main__':unittest.main()
