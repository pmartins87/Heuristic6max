"""Tests for diagnostic economic frontier; no solver or operational claims."""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import hj_co_frontier as m

class TestHJCO(unittest.TestCase):
    def test_full_169_and_coverage(self):
        rows=m.class_screen()
        self.assertEqual(len(rows),169)
        self.assertEqual({r['HeroHand'] for r in rows},set(m.HERO))
        self.assertAlmostEqual(sum(r['HeroShareGivenRFIAnd3bet_pct'] for r in rows),100)

    def test_reconcile_baseline(self):
        actual=m.baseline()
        ref,_,_=m.d.p.adjusted_action_percentages(*m.PAIR)
        for action in ('FOLD','CALL','4BET'):
            self.assertAlmostEqual(actual[action],ref[action],places=8)
        self.assertAlmostEqual(sum(actual.values()),100,places=8)

    def test_model_3bet_exposure_by_bruteforce(self):
        # Direct 1225 two-card opponent combinations, conditioned on Hero cards.
        v=m.d.p.VILLAIN[m.PAIR]
        for hand in ('A9o','AA','QJs'):
            combo=m.BY_CLASS[hand][0]
            possibles=[a for a in m.d.p.COMBOS if not (set(combo)&set(a))]
            self.assertEqual(len(possibles),1225)
            brute=sum(v[m.d.p.hand_class(a)].threebet for a in possibles)/1225
            available,_=m.villain_mass_by_hero_combo(*m.PAIR)
            self.assertAlmostEqual(available[combo]/1225,brute,places=10)
            self.assertTrue(0<=m.exposure_by_class(hand)<=1)

    def test_original_policy_unmodified_by_identity_counterfactual(self):
        orig=m.baseline()
        for h in ('A9o','AQo','AA'):
            cf=m.change_one_class(h)
            self.assertAlmostEqual(cf['Fold_pct'],orig['FOLD'],places=8)
            self.assertAlmostEqual(cf['Call_pct'],orig['CALL'],places=8)
            self.assertAlmostEqual(cf['Fourbet_pct'],orig['4BET'],places=8)

    def test_rfi_cut_reweights_but_not_ev(self):
        for h in ('A9o','KJo','22','AQo'):
            old=m.HERO[h]
            self.assertGreater(old.open_probability,0)
            a=m.change_one_class(h,open_multiplier=0.5)
            b=m.change_one_class(h,open_multiplier=0)
            self.assertLess(a['Fold_pct'],m.baseline()['FOLD'])
            self.assertLess(b['Fold_pct'],a['Fold_pct'])
            self.assertLess(b['DeltaRFI_total_pp'],a['DeltaRFI_total_pp'])

    def test_continue_from_fold_does_not_adjust_open(self):
        cf=m.change_one_class('AQo',fold_to_call=.25)
        self.assertLess(cf['Fold_pct'],m.baseline()['FOLD'])
        self.assertGreater(cf['Call_pct'],m.baseline()['CALL'])
        self.assertAlmostEqual(cf['Fourbet_pct'],m.baseline()['4BET'])
        self.assertAlmostEqual(cf['DeltaRFI_total_pp'],0)

    def test_invalid_counterfactuals(self):
        with self.assertRaises(ValueError):m.change_one_class('BAD')
        with self.assertRaises(ValueError):m.change_one_class('AQo',open_multiplier=1.1)
        with self.assertRaises(ValueError):m.change_one_class('AA',fold_to_call=.25)
        with self.assertRaises(ValueError):m.change_one_class('AQo',fold_to_call=.8,fold_to_4bet=.3)

    def test_call_price_and_rake(self):
        a=m.call_break_even(8,0,0,1)
        self.assertAlmostEqual(a['CallAdditional_BB'],5.5)
        self.assertAlmostEqual(a['PotAfterCall_BB'],17.5)
        self.assertAlmostEqual(a['RequiredRawEquity_pct'],100*5.5/17.5)
        b=m.call_break_even(8,.05,3,.75)
        self.assertAlmostEqual(b['ToyRake_BB'],.875)
        self.assertGreater(b['RequiredRawEquity_pct'],a['RequiredRawEquity_pct'])
        self.assertGreater(m.call_break_even(8,.08,3,.75)['RequiredRawEquity_pct'],b['RequiredRawEquity_pct'])
        with self.assertRaises(ValueError):m.call_break_even(8,0,0,0)

    def test_sizing_monotonic_thresholds(self):
        thresholds=[m.call_break_even(s,0,0,1)['RequiredRawEquity_pct'] for s in m.THREEBET_TO_BB]
        self.assertEqual(sorted(thresholds),thresholds)
        self.assertAlmostEqual(m.fourbet_zero_equity_fold_threshold(8)['FourbetTo_BB'],21.2)
        self.assertGreater(m.fourbet_zero_equity_fold_threshold(8)['RequiredEveryoneFolds_pct'],60)

    def test_aggregate_mass_and_counterfactual_conservation(self):
        for x in m.candidate_counterfactuals():
            self.assertAlmostEqual(x['Fold_pct']+x['Call_pct']+x['Fourbet_pct'],100,places=8)
        self.assertEqual(len(m.price_frontier()),len(m.THREEBET_TO_BB)*len(m.RAKES)*len(m.REALIZATION))

    def test_csv_stability_and_policies_untouched(self):
        keys=('RFI_100BB_169x5_DRAFT.csv','VS_OPEN_100BB_15x169_DRAFT.csv',
              'VS_3BET_100BB_15x169_DRAFT.csv')
        before={x:hashlib.sha256((m.BASE/x).read_bytes()).hexdigest() for x in keys}
        with tempfile.TemporaryDirectory() as folder:
            names=m.export(Path(folder))
            self.assertEqual(len(names),3)
            for name in names:
                with (Path(folder)/name).open(encoding='utf-8') as f:
                    self.assertTrue(list(csv.DictReader(f)))
        self.assertEqual(before,{x:hashlib.sha256((m.BASE/x).read_bytes()).hexdigest() for x in keys})

if __name__=='__main__':unittest.main()
