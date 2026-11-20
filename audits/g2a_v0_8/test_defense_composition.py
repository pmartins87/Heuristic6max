"""Reproducible contract checks. Not GTO strategy acceptance tests."""
from __future__ import annotations
import sys
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import defense_composition as d

class AuditV08(unittest.TestCase):
    def test_partition_all_169_classes(self):
        rows=d.p.HERO[('LJ','HJ')]
        self.assertEqual(len(rows),169)
        self.assertEqual(len(set(d.hand_family(h) for h in rows)),9)
        self.assertEqual(d.hand_family('AA'),'PAIR_PREMIUM_QQ_PLUS')
        self.assertEqual(d.hand_family('98s'),'SUITED_OTHER')

    def test_mass_per_node_and_action_aggregation_vs_previous_version(self):
        for pair in d.p.PAIRS:
            with self.subTest(pair=pair):
                rows=list(d.class_rows(*pair))
                self.assertAlmostEqual(sum(r['HeroShareGivenRFIAnd3bet_pct'] for r in rows),100,places=9)
                v06,_,_=d.p.adjusted_action_percentages(*pair)
                for action,label in [('FOLD','Fold'),('CALL','Call'),('4BET','Fourbet')]:
                    self.assertAlmostEqual(sum(r[label+'Contribution_pp'] for r in rows),v06[action],places=8)

    def test_all_family_masses_and_actions(self):
        for pair in d.p.PAIRS:
            with self.subTest(pair=pair):
                groups=d.aggregate_family(*pair)
                self.assertAlmostEqual(sum(g['Mass'] for g in groups.values()),100,places=8)
                for g in groups.values():
                    self.assertAlmostEqual(g['Mass'],g['Fold']+g['Call']+g['Fourbet'],places=8)

    def test_defense_rfi_reachability(self):
        for pair in d.p.PAIRS:
            with self.subTest(pair=pair):
                for row in d.class_rows(*pair):
                    self.assertGreater(row['RFIProbability_pct'],0)
                    self.assertAlmostEqual(row['FoldProbability_pct']+row['CallProbability_pct']+
                                           row['FourbetProbability_pct'],100,places=8)

    def test_to_call_immediate_pot_odds(self):
        price,eq=d.price_of_call('LJ','HJ')
        self.assertAlmostEqual(price,5.5)
        self.assertAlmostEqual(eq,100*5.5/(4+8+5.5))
        self.assertGreater(d.price_of_call('BTN','SB')[1],0)

    def test_remaining_players_by_position(self):
        self.assertEqual(d.players_yet_to_act('HJ'),4)
        self.assertEqual(d.players_yet_to_act('CO'),3)
        self.assertEqual(d.players_yet_to_act('BTN'),2)
        self.assertEqual(d.players_yet_to_act('SB'),1)
        self.assertEqual(d.players_yet_to_act('BB'),0)

    def test_cold_action_q_monotonic_and_baseline(self):
        for pair in d.p.PAIRS:
            with self.subTest(pair=pair):
                a=d.cold_action_sensitivity(*pair)
                self.assertAlmostEqual(a['EV_if_NoColdAction_BB'],d.p.audit_spot(*pair).zero_equity_EV_bb,places=10)
                if a['PlayersBehind3bettor']>0:
                    self.assertGreaterEqual(a['EV_if_NoColdAction_BB'],a['EV_if_PNoColdAction95pct_BB'])
                    self.assertGreaterEqual(a['EV_if_PNoColdAction95pct_BB'],a['EV_if_PNoColdAction80pct_BB'])
                else:
                    self.assertIsNone(a['PerRemainingPlayerMaxColdAction_independent_pct'])
                    self.assertIsNone(a['EV_if_PNoColdAction95pct_BB'])

    def test_threshold_boundary(self):
        s=d.cold_action_sensitivity('HJ','CO')
        t=s['RequiredPNoColdAction_pct']/100
        spot=d.p.audit_spot('HJ','CO')
        p=t*spot.model_fold_pct/100
        self.assertAlmostEqual(p*spot.pot_before_bb-(1-p)*spot.invested_bb,0,places=9)

    def test_class_contributions_sorted(self):
        for pair in d.p.KEY_PAIRS:
            rows=list(d.class_rows(*pair))
            self.assertGreater(len(rows),0)
            top=sorted(rows,key=lambda r:-r['FoldContribution_pp'])[:12]
            self.assertTrue(all(a['FoldContribution_pp']>=b['FoldContribution_pp'] for a,b in zip(top,top[1:])))

    def test_reproducible_csv_format_and_no_policy_mutation(self):
        import hashlib, tempfile
        import csv
        policies=('RFI_100BB_169x5_DRAFT.csv','VS_OPEN_100BB_15x169_DRAFT.csv','VS_3BET_100BB_15x169_DRAFT.csv')
        before={n:hashlib.sha256((d.BASE/n).read_bytes()).hexdigest() for n in policies}
        with tempfile.TemporaryDirectory() as temp:
            paths=d.export(Path(temp))
            self.assertEqual(len(paths),4)
            with (Path(temp)/paths[0]).open(newline='',encoding='utf-8') as f:
                self.assertGreater(len(list(csv.DictReader(f))),0)
        self.assertEqual(before,{n:hashlib.sha256((d.BASE/n).read_bytes()).hexdigest() for n in policies})

if __name__=='__main__':unittest.main()
