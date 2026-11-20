"""PORT-3 source+evidence gate tests, with zero OpenHoldem process usage."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from portability.port3 import replay_audit as p


class ReplayAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=p.read_csv(HERE/'SYNTHETIC_REPLAY_INPUT.csv')
        cls.digest=hashlib.sha256(p.port2.SOURCE.read_bytes()).hexdigest()

    def sample(self,hand='KJo',random='0.39',source='SYNTHETIC',**changes):
        row=deepcopy(self.rows[0]);row.update(case_id='MUTATED',session_id='S',hand_id='H',eval_index='0',hand_class=hand,randomhand=random,capture_source=source)
        row.update({k:str(v) for k,v in changes.items()})
        return row

    def verdict(self,row,root=None):
        with tempfile.TemporaryDirectory() as temp:
            return p.audit_rows([row],Path(root or temp))[0]

    def test_synthetic_dataset_contains_no_claim_of_oh_measurement(self):
        report=p.audit_rows(self.rows,HERE/'private_evidence_not_tracked')
        self.assertEqual(len(report),6)
        self.assertEqual([x['verdict'] for x in report],['STATIC_ONLY']*5+['BLOCKED_NO_MATCH'])
        self.assertNotIn('APPROVED',' '.join(x['verdict'] for x in report))

    def test_case_schema_pinned_to_real_symbols(self):
        self.assertEqual(len(p.SCHEMA),27)
        self.assertIn('observed_final_action',p.SCHEMA)
        self.assertIn('randomhand',p.SCHEMA)
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'bad.csv'
            output.write_text('case_id,randomhand\nA,0.39\n',encoding='utf-8')
            with self.assertRaises(p.EvidenceError):p.read_csv(output)

    def test_matches_port2_openppl_and_169_classes(self):
        model=p.port2.parse_file()
        for hand in sorted(p.port2.ALL_HANDS):
            value='0.2'
            row=self.sample(hand=hand,random=value)
            expected=p.port2.evaluate(model,p.parse_case(row)[0])
            self.assertIsNotNone(expected)
            self.assertEqual(self.verdict(row)['expected_action'],expected[0])

    def test_kjo_boundary_and_repeated_evaluations(self):
        for u,expected in [('0','RAISE'),('0.399999999','RAISE'),('0.4','FOLD'),('0.99999999','FOLD')]:
            row=self.sample(random=u)
            self.assertEqual(self.verdict(row)['expected_action'],expected)
        rows=[self.sample(random='0.399999999',eval_index=i,case_id=f'A{i}') for i in range(4)]
        self.assertEqual({x['verdict'] for x in p.audit_rows(rows,HERE)}, {'STATIC_ONLY'})

    def test_unstable_randomhand_same_hand_blocks(self):
        rows=[self.sample(random='0.2',eval_index=0,case_id='A'),self.sample(random='0.8',eval_index=1,case_id='B')]
        self.assertEqual([x['verdict'] for x in p.audit_rows(rows,HERE)],['STATIC_ONLY','MISMATCH_RANDOM'])

    def test_same_randomhand_different_hands_permitted(self):
        rows=[self.sample(random='0.2',hand_id='A'),self.sample(random='0.2',hand_id='B')]
        self.assertEqual([x['verdict'] for x in p.audit_rows(rows,HERE)],['STATIC_ONLY']*2)

    def test_same_hand_label_different_sessions_permitted(self):
        rows=[self.sample(random='0.2',session_id='A'),self.sample(random='0.8',session_id='B')]
        self.assertEqual([x['verdict'] for x in p.audit_rows(rows,HERE)],['STATIC_ONLY']*2)

    def test_no_match_does_not_become_safe_fold_or_check(self):
        for kw in ({'in_utg':'0'},{'nplayersdealt':'5'},{'stack_unknown':'1'},
                   {'raises':'1'},{'pot_bb':'3.5'}):
            row=self.sample(hand='AA',observed_final_action='FOLD',**kw)
            self.assertEqual(self.verdict(row)['verdict'],'BLOCKED_NO_MATCH')

    def test_mismatched_source_sha_prevents_ready(self):
        row=self.sample(oppl_sha256='0'*64)
        self.assertEqual(self.verdict(row)['verdict'],'MISMATCH_SOURCE')

    def test_oh_version_required_even_if_observed_actions_match(self):
        row=self.sample(source='OH_REPLAY',observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='RAISE',observed_final_raise_to_bb='2.5')
        self.assertEqual(self.verdict(row)['verdict'],'EVIDENCE_INCOMPLETE')

    def test_missing_randomhand_for_mixed_hand_blocks_no_match(self):
        row=self.sample(source='OH_MANUALMODE',random='',openholdem_version='manual-target',observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='RAISE',observed_final_raise_to_bb='2.5')
        self.assertEqual(self.verdict(row)['verdict'],'BLOCKED_NO_MATCH')

    def test_formula_wrong_action_flagged(self):
        row=self.sample(source='OH_REPLAY',observed_formula_action='FOLD',observed_final_action='FOLD')
        self.assertEqual(self.verdict(row)['verdict'],'MISMATCH_FORMULA')

    def test_wrong_raise_to_sizing_flagged_even_if_action_same(self):
        for size in ('2.49','3.0','0','NaN'):
            row=self.sample(observed_formula_action='RAISE',observed_formula_raise_to_bb=size)
            with self.subTest(size=size):
                self.assertEqual(self.verdict(row)['verdict'],'MISMATCH_FORMULA')

    def test_final_action_fallback_detected_separately(self):
        row=self.sample(observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='CHECK')
        self.assertEqual(self.verdict(row)['verdict'],'MISMATCH_FINAL')

    def test_final_wrong_sizing_flagged(self):
        row=self.sample(observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='RAISE',observed_final_raise_to_bb='3')
        self.assertEqual(self.verdict(row)['verdict'],'MISMATCH_FINAL')

    def test_pure_fold_must_not_have_raise_sizing(self):
        row=self.sample(hand='72o',observed_formula_action='FOLD',observed_final_action='FOLD',observed_formula_raise_to_bb='2.5')
        self.assertEqual(self.verdict(row)['verdict'],'MISMATCH_FORMULA')

    def test_invalid_observed_action_rejected(self):
        with self.assertRaises(p.EvidenceError):
            self.verdict(self.sample(observed_formula_action='RAISEBY'))

    def test_missing_trace_sha_blocks_real_evidence(self):
        row=self.sample(source='OH_REPLAY',openholdem_version='9.x',observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='RAISE',observed_final_raise_to_bb='2.5')
        self.assertEqual(self.verdict(row)['verdict'],'EVIDENCE_INCOMPLETE')

    def test_ready_for_review_only_when_trace_hashed_not_auto_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'frame_1_oh_trace.log'
            path.write_text('Synthetic test fixture only, not a real OH log\n',encoding='utf-8')
            row=self.sample(source='OH_REPLAY',openholdem_version='TEST_VALUE_NOT_REAL',observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='RAISE',observed_final_raise_to_bb='2.5',evidence_file=path.name,evidence_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            verdict=self.verdict(row,tmp)
            self.assertEqual(verdict['verdict'],'READY_FOR_MANUAL_REVIEW')
            self.assertIn('not runtime approval',verdict['reason'])

    def test_modified_trace_sha_blocks_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'trace.txt';path.write_text('trace',encoding='utf-8')
            row=self.sample(source='OH_MANUALMODE',openholdem_version='OH-test',observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='RAISE',observed_final_raise_to_bb='2.5',evidence_file='trace.txt',evidence_sha256='a'*64)
            self.assertEqual(self.verdict(row,tmp)['verdict'],'EVIDENCE_INCOMPLETE')

    def test_trace_path_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            for f in ('../outside.log','/tmp/anything','c:\\windows\\bad.log'):
                row=self.sample(source='OH_REPLAY',openholdem_version='x',observed_formula_action='RAISE',observed_formula_raise_to_bb='2.5',observed_final_action='RAISE',observed_final_raise_to_bb='2.5',evidence_file=f,evidence_sha256='a'*64)
                self.assertEqual(self.verdict(row,tmp)['verdict'],'EVIDENCE_INCOMPLETE')

    def test_invalid_randomhand_outside_interval_rejected(self):
        for rand in ('-0.1','1.0','nan','Infinity','bad'):
            with self.subTest(rand=rand),self.assertRaises(p.EvidenceError):
                self.verdict(self.sample(random=rand))

    def test_malformed_boolean_rejected(self):
        for item in ('true','yes','2',''):
            with self.assertRaises(p.EvidenceError):
                self.verdict(self.sample(in_utg=item))

    def test_duplicate_eval_index_rejected(self):
        with self.assertRaises(p.EvidenceError):p.audit_rows([self.sample(),self.sample(case_id='B')],HERE)

    def test_missing_column_rejected(self):
        row=self.sample();row.pop('oppl_sha256')
        with self.assertRaises(p.EvidenceError):p.audit_rows([row],HERE)

    def test_static_fixture_report_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/'x.csv',Path(tmp)/'y.csv']
            for path in paths:p.export_report(p.audit_rows(self.rows,HERE),path)
            self.assertEqual(paths[0].read_bytes(),paths[1].read_bytes())
            self.assertEqual(paths[0].read_bytes(),(HERE/'SYNTHETIC_REPLAY_REPORT.csv').read_bytes())

    def test_source_strategy_unchanged(self):
        base=ROOT/'gto6_heuristic_v0_6_1'
        paths=[base/name for name in ('rfi_reference.py','vs_open_reference.py','vs_3bet_reference.py')]
        hashes=[hashlib.sha256(f.read_bytes()).hexdigest() for f in paths]
        p.audit_rows(self.rows,HERE)
        self.assertEqual(hashes,[hashlib.sha256(f.read_bytes()).hexdigest() for f in paths])


if __name__=='__main__': unittest.main()
