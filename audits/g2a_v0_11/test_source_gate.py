"""Test strict source admissibility; never test profitability or authorize live play."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import source_gate as g

class TestSourceGate(unittest.TestCase):
    def setUp(self):
        self.reg=g.load_registry()
        self.target=self.reg['target']

    def test_baseline_contract(self):
        self.assertEqual(g.baseline_contract(),{'open_to_bb':2.5,'threebet_to_bb':8.,'defense_classes':169})

    def test_providers_not_admitted(self):
        result=[g.evaluate(self.target,s) for s in self.reg['sources']]
        self.assertEqual(len(result),3)
        self.assertTrue(all(x.result=='REFERENCE_ONLY' and x.reference_only for x in result))

    def test_art_incompatible_open_node(self):
        x=g.evaluate(self.target,self.reg['sources'][0])
        self.assertIn('open_to_bb:MISMATCH',x.gaps)
        self.assertIn('node:MISMATCH',x.gaps)
        self.assertIn('rights:UNVERIFIED',x.gaps)

    def test_simple_not_direct_replacement(self):
        x=g.evaluate(self.target,self.reg['sources'][1])
        self.assertIn('threebet_to_bb:MISMATCH',x.gaps)
        self.assertIn('rake_id:UNKNOWN',x.gaps)
        self.assertIn('node_evidence:UNVERIFIED',x.gaps)

    def test_unknown_rake_does_not_become_no_rake(self):
        s=dict(self.reg['sources'][1]);s['rake_id']=None;s['rake_cap_bb']=None
        x=g.evaluate(self.target,s)
        self.assertIn('rake_id:UNKNOWN',x.gaps)
        self.assertIn('rake_cap_bb:UNKNOWN',x.gaps)

    def test_exact_fully_licensed_synthetic_passes_only_manual_review(self):
        t=dict(self.target);t['rake_id']='SIMULATED_RAKE';t['rake_cap_bb']=3
        s={**t,'id':'SYNTHETIC_LICENSED_SOURCE','origin':'INDEPENDENT_SOLVED_SOURCE',
           'specific_node_verified':True,'range_frequencies_accessible':True,
           'explicit_derivative_rights':True}
        x=g.evaluate(t,s)
        self.assertEqual(x.result,'ELIGIBLE_FOR_MANUAL_REVIEW')
        self.assertFalse(x.reference_only)

    def test_missing_rights_fails_closed(self):
        t=dict(self.target);t['rake_id']='TEST';t['rake_cap_bb']=3
        s={**t,'id':'s','origin':'INDEPENDENT_SOLVED_SOURCE',
           'specific_node_verified':True,'range_frequencies_accessible':True,
           'explicit_derivative_rights':False}
        self.assertEqual(g.evaluate(t,s).result,'REFERENCE_ONLY')

    def test_fake_solver_claim_not_accepted(self):
        t=dict(self.target);t['rake_id']='TEST';t['rake_cap_bb']=3
        s={**t,'id':'s','origin':'HEURISTIC',
           'specific_node_verified':True,'range_frequencies_accessible':True,
           'explicit_derivative_rights':True}
        self.assertIn('origin:NOT_SOLVER_EVIDENCE',g.evaluate(t,s).gaps)

    def test_missing_required_field_rejected(self):
        with self.assertRaises(ValueError):g.evaluate(self.target,{'id':'incomplete'})

    def test_duplicate_source_ids_rejected(self):
        reg={**self.reg,'sources':[self.reg['sources'][0]]*2}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'registry.json'
            path.write_text(json.dumps(reg),encoding='utf-8')
            with self.assertRaises(ValueError):g.load_registry(path)

    def test_export_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'first.csv';b=Path(tmp)/'second.csv'
            g.run(a);g.run(b)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(a.read_text().count('\n'),4)

if __name__=='__main__':unittest.main()
