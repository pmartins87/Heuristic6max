"""OH-G1G6-1 integrity/negative-control tests; no OpenHoldem runtime used."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import evidence_gate as g


class OHGateContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.cfg,self.entries=g.catalog()
        self.sha=g.source_digest(self.cfg)
        self.actions=('f$call','f$call')

    def tearDown(self):
        self.tmp.cleanup()

    def bundle(self,mode='SYNTHETIC',case_id='RFI_BTN_PURE'):
        case=self.entries[case_id]
        claims={x:'1' for x in case['required_symbols']}
        claims.update({'randomhand':'0.2','Raises':'0','Calls':'0',
                       'InButton':'1','InBigBlind':'0','StackUnknown':'0',
                       'nplayersdealt':'6','StillToAct':'2',
                       'StackSize':'100','PotSize':'1.5','AmountToCall':'0'})
        return {
            'protocol':g.PROTOCOL,'capture_mode':mode,
            'offline_attested':True,'connected_live':False,
            'openholdem_version':'unverified-test-only',
            'openholdem_exe_sha256':'a'*64,
            'tablemap_sha256':'b'*64,
            'loaded_oppl_sha256':self.sha,
            'cases':[{
                'case_id':case_id,'session_id':'S1','hand_id':'H1',
                'eval_index':0,'street':case['street'],
                'symbols':claims,'reported_best_action':'f$call',
                'reported_action_taken':'f$call',
                'artifacts':{k:{'path':'','sha256':''} for k in g.ARTIFACT_EXT}
            }]
        }

    def fill_evidence(self,bundle,action='f$call',taken=None):
        case=bundle['cases'][0]
        log=(f'2026-11-21 00:01:02 - Best action: {action}\n'
             f'2026-11-21 00:01:02 - Action taken: {taken or action}\n')
        debug=''.join(f'{s} = {case["symbols"][s]}\n'
                      for s in self.entries[case['case_id']]['required_symbols'])
        payload={
            'pre_html':b'<html><body>FAKE PRIVATE TEST ONLY</body></html>',
            'pre_bmp':b'BM\x00\x00\x00\x00TEST',
            'post_html':b'<html><body>FAKE POST ACTION TEST ONLY</body></html>',
            'post_bmp':b'BM\x00\x00\x00\x00TEST2',
            'debug_txt':debug.encode('utf-8'),
            'debug_png':b'\x89PNG\r\n\x1a\nFAKE_TEST_ONLY',
            'decision_log':log.encode('utf-8')
        }
        names={'pre_html':'before.html','pre_bmp':'before.bmp',
               'post_html':'after.html','post_bmp':'after.bmp',
               'debug_txt':'symbols.txt','debug_png':'symbols.png',
               'decision_log':'excerpt.log'}
        for k,v in payload.items():
            (self.root/names[k]).write_bytes(v)
            case['artifacts'][k]={'path':names[k],
                                  'sha256':hashlib.sha256(v).hexdigest()}
        case['reported_best_action']=action
        case['reported_action_taken']=taken or action
        return bundle

    def verdict(self,bundle):
        return g.audit(bundle,self.root)['results'][0]['verdict']

    def test_01_catalog_is_pinned_to_real_integrated_source(self):
        self.assertEqual(self.cfg['source'],'portability/iso_defense_v1/iso_defense_integrated_draft.oppl')
        self.assertEqual(len(self.entries),10)
        self.assertEqual(len(self.sha),64)
        self.assertIn('NO_MATCH_FALLBACK',self.entries)
        self.assertIn('MEMORY_NEW_HAND',self.entries)

    def test_02_synthetic_never_proves_runtime(self):
        report=g.audit(self.bundle(),self.root)
        self.assertEqual(report['results'][0]['verdict'],'STATIC_ONLY')
        self.assertFalse(report['runtime_approved'])
        self.assertEqual((report['G1'],report['G6']),('OPEN','PENDING'))
        self.assertEqual(report['R10d_release'],'BLOCKED')
        self.assertEqual(len(report['catalog_cases_missing']),9)

    def test_03_missing_key_is_hard_schema_error(self):
        b=self.bundle()
        del b['cases'][0]['artifacts']
        with self.assertRaises(g.EvidenceError):g.audit(b,self.root)

    def test_04_unknown_and_wrong_street_case_rejected(self):
        for k,v in [('case_id','NOT_A_CASE'),('street','river')]:
            b=self.bundle()
            b['cases'][0][k]=v
            with self.assertRaises(g.EvidenceError):g.audit(b,self.root)

    def test_05_live_context_immediately_blocks(self):
        for kw in ({'connected_live':True},{'offline_attested':False}):
            b=self.bundle('OH_REPLAY')
            b.update(kw)
            self.assertEqual(self.verdict(b),'BLOCKED_LIVE_CONTEXT')

    def test_06_mismatched_loaded_profile_blocks_even_synthetic(self):
        b=self.bundle()
        b['loaded_oppl_sha256']='0'*64
        self.assertEqual(self.verdict(b),'SOURCE_MISMATCH')

    def test_07_manual_mode_is_not_autoplayer_parity(self):
        self.assertEqual(self.verdict(self.bundle('OH_MANUALMODE')),'OBSERVATION_ONLY')

    def test_08_no_version_or_tablemap_prevents_real_review(self):
        for f in ('openholdem_version','openholdem_exe_sha256','tablemap_sha256'):
            b=self.fill_evidence(self.bundle('OH_REPLAY'))
            b[f]=''
            self.assertEqual(self.verdict(b),'INCOMPLETE')

    def test_09_missing_raw_evidence_blocks_review(self):
        self.assertEqual(self.verdict(self.bundle('OH_REPLAY')),'INCOMPLETE')

    def test_10_fake_raw_fixture_ready_is_still_never_approved(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        report=g.audit(b,self.root)
        self.assertEqual(report['results'][0]['verdict'],'READY_FOR_HUMAN_REVIEW')
        self.assertFalse(report['runtime_approved'])
        self.assertEqual(report['R10d_release'],'BLOCKED')

    def test_11_digest_mismatch_detected(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        b['cases'][0]['artifacts']['pre_bmp']['sha256']='0'*64
        self.assertEqual(self.verdict(b),'EVIDENCE_CONFLICT')

    def test_12_path_traversal_detected(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        b['cases'][0]['artifacts']['pre_html']['path']='../before.html'
        self.assertEqual(self.verdict(b),'EVIDENCE_CONFLICT')

    def test_13_html_bmp_pair_and_prepost_frame_order(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        a=b['cases'][0]['artifacts']
        a['post_bmp']=deepcopy(a['pre_bmp'])
        self.assertEqual(self.verdict(b),'EVIDENCE_CONFLICT')
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        a=b['cases'][0]['artifacts']
        a['post_bmp']=deepcopy(a['pre_bmp'])
        a['post_html']=deepcopy(a['pre_html'])
        self.assertEqual(self.verdict(b),'INCOMPLETE')

    def test_14_debug_value_conflict_blocks(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        b['cases'][0]['symbols']['Raises']='99'
        self.assertEqual(self.verdict(b),'SYMBOL_CONFLICT')

    def test_15_missing_debug_symbol_blocks(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        del b['cases'][0]['symbols']['Calls']
        self.assertEqual(self.verdict(b),'INCOMPLETE')

    def test_16_best_action_different_from_taken_detects_backup(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'),action='f$call',taken='f$check')
        report=g.audit(b,self.root)
        self.assertEqual(report['results'][0]['verdict'],'FALLBACK_OBSERVED')
        self.assertFalse(report['runtime_approved'])

    def test_17_transcription_mismatch_detected(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        b['cases'][0]['reported_action_taken']='f$fold'
        self.assertEqual(self.verdict(b),'EVIDENCE_CONFLICT')

    def test_18_ambiguous_multi_action_log_blocks(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        p=self.root/'excerpt.log'
        s=p.read_text()+'2026-11-21 00:02:00 - Action taken: f$check\n'
        p.write_text(s)
        b['cases'][0]['artifacts']['decision_log']['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(self.verdict(b),'INCOMPLETE')

    def test_19_different_timestamps_block_pairing(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        p=self.root/'excerpt.log'
        s=p.read_text().replace('00:01:02 - Action taken','00:01:03 - Action taken')
        p.write_text(s)
        b['cases'][0]['artifacts']['decision_log']['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(self.verdict(b),'INCOMPLETE')

    def test_20_randomhand_same_hand_stability_required(self):
        b=self.bundle()
        c=deepcopy(b['cases'][0]);c['eval_index']=1
        c['symbols']['randomhand']='0.8'
        b['cases'].append(c)
        report=g.audit(b,self.root)
        self.assertEqual([x['verdict'] for x in report['results']],
                         ['STATIC_ONLY','MISMATCH_RANDOM'])

    def test_21_duplicate_evaluation_rejected(self):
        b=self.bundle()
        b['cases'].append(deepcopy(b['cases'][0]))
        with self.assertRaises(g.EvidenceError):g.audit(b,self.root)

    def test_22_catalog_tags_cover_new_and_existing_origin(self):
        self.assertEqual({e['gate'] for e in self.entries.values()},{'G1','G6'})
        self.assertEqual({e['street'] for e in self.entries.values()},{'preflop','turn','river'})
        for e in self.entries.values():
            self.assertTrue(e['required_symbols'])
            self.assertTrue(e['source_markers'])

    def test_23_log_parser_rejects_no_action_taken(self):
        actions,reason=g.raw_log_actions('2026-11-21 01:02:03 - Best action: f$call\n')
        self.assertIsNone(actions)
        self.assertIn('exactly one',reason)

    def test_24_unobserved_boolean_or_invalid_random_denied(self):
        b=self.bundle()
        b['cases'][0]['symbols']['randomhand']='1.0'
        with self.assertRaises(g.EvidenceError):g.audit(b,self.root)
        b=self.bundle()
        b['cases'][0]['symbols']['randomhand']='NaN'
        with self.assertRaises(g.EvidenceError):g.audit(b,self.root)

    def test_25_cli_synthetic_output_is_nonpromoting(self):
        b=self.bundle()
        f=self.root/'bundle.json'
        f.write_text(json.dumps(b),encoding='utf-8')
        report=self.root/'report.json'
        rc=g.main(['--bundle',str(f),'--evidence-root',str(self.root),
                   '--out',str(report)])
        self.assertEqual(rc,0)
        self.assertFalse(json.loads(report.read_text())['runtime_approved'])
        # Never allow the CLI --out flag to overwrite project release gates.
        outside=self.root.parent/'OHG1G6_OUTSIDE_PRIVATE_ROOT.json'
        self.assertEqual(g.main(['--bundle',str(f),'--evidence-root',str(self.root),
                                 '--out',str(outside)]),2)
        self.assertFalse(outside.exists())

    def test_26_magic_file_integrity_not_just_sha(self):
        b=self.fill_evidence(self.bundle('OH_REPLAY'))
        p=self.root/'symbols.png'
        p.write_bytes(b'NOT_PNG')
        b['cases'][0]['artifacts']['debug_png']['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertNotEqual(self.verdict(b),'READY_FOR_HUMAN_REVIEW')


if __name__=='__main__':
    unittest.main()
