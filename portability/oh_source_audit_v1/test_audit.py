"""OH-SRC1 tests. Evidence is OpenPPL source and documented engine semantics.

These tests do not load OpenHoldem, approve G1/G6 or modify poker logic.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import audit as a


class OpenHoldemSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=a.produce()
        cls.source=a.active_source().read_text(encoding='utf-8')
        cls.pf=a.PRE.read_text(encoding='utf-8')

    def test_01_active_file_comes_from_r10d_source_of_truth(self):
        self.assertEqual(a.active_source().relative_to(a.ROOT).as_posix(),
                         'portability/iso_defense_v1/iso_defense_integrated_draft.oppl')

    def test_02_oppl_digest_is_cryptographic_source_identity_not_runtime_hash(self):
        source=a.active_source().read_bytes()
        self.assertEqual(self.report['source_sha256'],hashlib.sha256(source).hexdigest())
        self.assertEqual(self.report['source_sha256'],
                         '27be1f161535c9bc07f019fd6e0609c7a3018bf6b2cc640b80a6042c5b7df02b')

    def test_03_existing_openppl_source_has_four_action_callbacks(self):
        self.assertEqual(len(a.action_sections(self.source)),4)
        self.assertEqual(self.report['main_callback_count'],4)

    def test_04_missing_or_duplicate_callback_rejected(self):
        with self.assertRaises(a.SourceAuditError):
            a.action_sections(self.source.replace('##f$river##','##f$riverr##'))
        with self.assertRaises(a.SourceAuditError):
            a.action_sections(self.source+'\n##f$flop##')

    def test_05_2007_prior_rules_untouched(self):
        self.assertEqual(self.report['metrics']['total_when'],2007)
        self.assertEqual(self.report['source_bytes'],len(self.source.encode('utf-8')))

    def test_06_numeric_equality_hotspots_are_measured_not_silently_fixed(self):
        m=self.report['metrics']
        self.assertEqual(m['pot_exact_rules'],436)
        self.assertEqual(sum(m['pot_exact_values'].values()),436)
        self.assertEqual(m['pot_exact_values']['7'],10)
        self.assertEqual(m['pot_exact_values']['4'],202)

    def test_07_call_eq_zero_and_nonzero_are_distinguished(self):
        m=self.report['metrics']
        self.assertEqual(m['amount_to_call_exact_zero'],258)
        self.assertEqual(m['amount_to_call_exact_nonzero'],400)
        self.assertEqual(m['still_to_act_rules'],103)
        self.assertEqual(m['first_raiser_position_rules'],343)

    def test_08_float_counterexample_does_not_claim_actual_oh_bug(self):
        # Exact equality is *logically* brittle. The engine may or may not
        # actually produce such an observation in a particular scenario.
        self.assertFalse(7.0000000001==7.0)
        self.assertTrue(7.0000000001>6.999 and 7.0000000001<7.001)
        self.assertFalse(self.report['automatic_runtime_approval'])

    def test_09_two_isodef_nodes_have_identical_set_action_guard(self):
        z=a.validate_iso_defense_preflop(self.pf)
        self.assertEqual(set(z),{'BTN','BB'})
        self.assertTrue(all(n['set_then_raise_guard_identical'] and
                            n['set_then_call_guard_identical']
                            for n in z.values()))

    def test_10_3bet_and_call_guard_mutation_rejected(self):
        broken=self.pf.replace('RaiseTo 13.5 FORCE','RaiseTo 13.51 FORCE',1)
        # Altering an action amount is outside this guard-only contract;
        # this test should not pretend source audit validates EV/sizing.
        self.assertEqual(a.validate_iso_defense_preflop(broken)['BTN']['actions'],5)
        broken2=self.pf.replace('AND Calls = 1','AND Calls = 2',1)
        with self.assertRaises(a.SourceAuditError):
            a.validate_iso_defense_preflop(broken2)

    def test_11_mismatched_set_to_action_guard_rejected(self):
        bad=self.pf.replace('AND listH6DEF3BET) RaiseTo 13.5 FORCE',
                            'AND listH6DEFCALLBTN) RaiseTo 13.5 FORCE',1)
        with self.assertRaises(a.SourceAuditError):
            a.validate_iso_defense_preflop(bad)

    def test_12_fold_fallback_widening_is_rejected(self):
        bad=self.pf.replace('AND InButton AND NOT InBigBlind AND StillToAct = 2',
                            'AND InButton AND StillToAct = 2',1)
        with self.assertRaises(a.SourceAuditError):
            a.validate_iso_defense_preflop(bad)

    def test_13_the_risk_ledger_cannot_approve_runtime(self):
        self.assertEqual(self.report['contract'],a.RESEARCH_CONTRACT)
        self.assertFalse(self.report['automatic_runtime_approval'])
        self.assertFalse(self.report['strategy_changed'])
        self.assertIn('audit each distinct PotSize equality domain',
                      self.report['recommended_next_gate'])

    def test_14_knowledge_claims_are_explicit_not_unqualified(self):
        claims=self.report['source_facts']
        self.assertEqual(len(claims),7)
        self.assertIn('UpdateOnHandreset',claims['user_flags_reset'])
        self.assertIn('first action',claims['calls_not_raw_limper_count'].lower())
        self.assertIn('memory',claims['preflop_raises_stateful'].lower())
        self.assertIn('default',claims['fallback_not_failclosed'].lower())

    def test_15_dynamic_report_matches_committed_source_snapshot(self):
        self.assertEqual(a.rendered(),a.REPORT.read_text(encoding='utf-8'))

    def test_16_historical_preflop_ranges_remain_parent_consistent(self):
        parent=(a.ROOT/'portability/blind_iso_v2/blind_iso_integrated_draft.oppl').read_text(encoding='utf-8')
        old=[x for x in parent.splitlines() if x.startswith('WHEN ')]
        now=[x for x in self.source.splitlines() if x.startswith('WHEN ')]
        self.assertEqual(len(old),1920)
        idx=0
        for row in old:
            while idx<len(now) and now[idx]!=row:idx+=1
            self.assertLess(idx,len(now))
            idx+=1

    def test_17_catalogued_risks_do_not_contain_strategic_responses(self):
        self.assertEqual(len(self.report['finding_ids']),6)
        self.assertNotIn('bet_range',self.report)
        self.assertNotIn('promote_R10d',self.report)


if __name__=='__main__':
    unittest.main()
