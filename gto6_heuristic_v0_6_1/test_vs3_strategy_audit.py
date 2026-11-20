import csv
import tempfile
import unittest
from pathlib import Path
from vs_3bet_reference import SPECS, RANGES
from vs3_strategy_audit import audit_node, top_contributions, export_audit

class AuditCompositionTests(unittest.TestCase):
    def test_complete_nodes(self):
        self.assertEqual(len(SPECS),15)
        for s in SPECS:
            a=audit_node(s.opener,s.threebettor)
            self.assertEqual(a.reached_classes, sum(r.open_probability>0 for r in RANGES[(s.opener,s.threebettor)].values()))
            self.assertAlmostEqual(a.fourbet_pct+a.call_pct+a.fold_pct,100,places=7)
            self.assertAlmostEqual(a.value_mass+a.bluff_mass,a.fourbet_mass,places=7)
            self.assertGreaterEqual(a.bluff_share_pct,0)
            self.assertLessEqual(a.bluff_share_pct,100)
    def test_contributions_reconstruct_fourbet(self):
        for s in SPECS:
            a=audit_node(s.opener,s.threebettor)
            co=top_contributions(s.opener,s.threebettor,'4BET')
            self.assertAlmostEqual(sum(x[2] for x in co),a.fourbet_pct,places=4)
    def test_no_value_in_bluff_bucket(self):
        for s in SPECS:
            rows=RANGES[(s.opener,s.threebettor)]
            for h in ('AA','KK'):
                self.assertEqual(rows[h].bucket,'4BET_VALUE_PURE')
    def test_invalid_action(self):
        with self.assertRaises(ValueError):top_contributions('LJ','HJ','SHOVE')
    def test_export_full_and_draft_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_audit(Path(tmp))
            with (Path(tmp)/'G2_VS3_Hand_Contributions_v0_5.csv').open() as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),15*169)
            self.assertEqual({r['Status'] for r in rows},{'HOLD_UNCALIBRATED'})

if __name__=='__main__':unittest.main()
