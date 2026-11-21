"""Benchmark honesty and reproducibility, not a bot performance benchmark."""
from __future__ import annotations
from pathlib import Path
from unittest.mock import patch
import json
import csv
import unittest
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import comparison as c

class R10dFloor(unittest.TestCase):
    def test_r10d_measured_real_blob_not_another_version(self):
        ref=json.loads(c.R10D.read_text())
        self.assertEqual(ref['source_path'],'artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt')
        self.assertEqual(ref['github_blob_sha'],'9f9cba79cdb9dc4438895770cf61a450fb55d17c')
        self.assertEqual(ref['sha256_documented'],'1b198b7086870b427d085506c3c538d3b67d2bc6ac9e35c67b9bf30babb5f46f')

    def test_pinned_reference_counts(self):
        r=json.loads(c.R10D.read_text())
        self.assertEqual((r['function_headers'],r['list_headers'],r['when_rules'],r['distinct_user_symbols']),(725,545,6021,561))
        self.assertEqual(r['function_headers']+r['list_headers'],1270)

    def test_fourteen_capability_families(self):
        with c.MATRIX.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual([r['CapabilityID'] for r in rows],['M%02d'%i for i in range(1,15)])
        self.assertIn('MISSING',{r['CurrentStatus'] for r in rows})

    def test_current_source_is_present_and_native_oppl(self):
        text=c.SOURCE.read_text()
        self.assertIn('##f$preflop##',text)
        self.assertIn('##f$flop##',text)
        self.assertIn('##f$turn##',text)
        self.assertIn('##f$river##',text)
        self.assertIn('user_H6_3betIntent',text)

    def test_count_current_source_even_if_different_from_r10d(self):
        m=c.inventory(c.SOURCE.read_text())
        self.assertGreater(m['when_rules'],541)
        self.assertEqual(m['distinct_user_symbols'],7)
        self.assertEqual(m['set_user_lines'],90)

    def test_false_superiority_is_blocked(self):
        r=c.measure()
        self.assertFalse(r['surpasses_R10d'])
        self.assertEqual(len(r['unmet_capabilities']),14)
        self.assertTrue(r['release_gate'].startswith('BLOCKED'))

    def test_report_matches_generated_source(self):
        self.assertEqual(json.loads(c.REPORT.read_text()),c.measure())

    def test_not_mistaking_484_legal_histories_for_policies(self):
        # A model of chronological words isn't a set of operational poker actions.
        self.assertNotIn('historical_paths',c.measure()['metrics'])

    def test_json_schema_requires_authentic_boolean_flags(self):
        original=c.PROMOTION.read_text()
        try:
            c.PROMOTION.write_text('{"runtime_replay_verified": "yes"}')
            with self.assertRaises(ValueError):c.measure()
        finally:c.PROMOTION.write_text(original)

    def test_all_labels_verified_without_runtime_not_enough(self):
        original=c.MATRIX.read_text()
        try:
            c.MATRIX.write_text(original.replace(',PARTIAL,',',VERIFIED,').replace(',MISSING,',',VERIFIED,'))
            self.assertFalse(c.measure()['surpasses_R10d'])
        finally:c.MATRIX.write_text(original)

    def test_forged_external_blob_is_rejected(self):
        with self.assertRaises(ValueError):c.measure(c.R10D)

    def test_no_auto_promotion_on_version_or_header_counts(self):
        info=c.measure()
        self.assertLess(info['metrics']['when_rules']['Heuristic'],info['metrics']['when_rules']['R10d'])
        self.assertLess(info['metrics']['distinct_user_symbols']['Heuristic'],info['metrics']['distinct_user_symbols']['R10d'])

if __name__=='__main__':unittest.main()
