"""Focused functional regressions; OPPL is the single decision-rule source."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import csv
import hashlib
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'gto6_heuristic_v0_6_1'))
import rfi_source_interpreter as op  # noqa: E402
import generate_rfi_mvp as gen  # noqa: E402
from rfi_reference import RANGES  # noqa: E402
from scenario_contract import Position  # noqa: E402

class RfiMvpRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=op.parse_file()

    def test_845_hand_position_pairs_match_immutable_heuristic(self):
        # No hand strategy is duplicated in the interpreter: this is the offline oracle.
        n=0
        for pos in op.POSITIONS:
            for hand in op.ALL_HANDS:
                original=RANGES[Position(pos)][hand]
                for x in (0.,.39,.40,.49,.50,.74,.75,.999999):
                    result=op.evaluate(self.model,op.Observation(hand=hand,position=pos,randomhand=x))
                    expected=('RAISE',3. if pos=='SB' else 2.5) if x<original['RAISE'] else (
                             ('LIMP',None) if x<original['RAISE']+original['LIMP'] else ('FOLD',None))
                    self.assertEqual(result,expected,(pos,hand,x))
                    n+=1
        self.assertEqual(n,845*8)

    def test_mixes_are_exactly_five_known_cases(self):
        mixed=[]
        for pos in op.POSITIONS:
            for hand in op.ALL_HANDS:
                p=RANGES[Position(pos)][hand]
                if len([v for v in p.values() if v>0])>1:
                    mixed.append((pos,hand))
        self.assertEqual(set(mixed),{('LJ','KJo'),('HJ','QJo'),('BTN','53s'),('SB','K3s'),('SB','97o')})

    def test_small_blind_limp_and_half_blind_call(self):
        m=self.model
        self.assertEqual(op.evaluate(m,op.Observation('97o','SB',randomhand=.74)),('LIMP',None))
        self.assertEqual(op.evaluate(m,op.Observation('97o','SB',randomhand=.75)),('FOLD',None))
        self.assertEqual(op.evaluate(m,op.Observation('AA','SB',randomhand=.5)),('RAISE',3.))
        self.assertIsNone(op.evaluate(m,op.Observation('AA','SB',amount_to_call_bb=1.)))

    def test_mixed_boundaries_and_repeat_evaluation(self):
        for pos,hand,cut,low,high in (
            ('LJ','KJo',.40,'RAISE','FOLD'),('HJ','QJo',.50,'RAISE','FOLD'),
            ('BTN','53s',.50,'RAISE','FOLD'),('SB','K3s',.50,'RAISE','FOLD'),
            ('SB','97o',.75,'LIMP','FOLD')):
            self.assertEqual(op.evaluate(self.model,op.Observation(hand,pos,randomhand=cut-1e-9))[0],low)
            self.assertEqual(op.evaluate(self.model,op.Observation(hand,pos,randomhand=cut))[0],high)
            state=op.Observation(hand,pos,randomhand=cut-.01)
            self.assertEqual({op.evaluate(self.model,state) for _ in range(6)},
                {op.evaluate(self.model,state)})

    def test_missing_random_is_not_coerced_to_fold(self):
        self.assertIsNone(op.evaluate(self.model,op.Observation('KJo','LJ')))
        self.assertEqual(op.evaluate(self.model,op.Observation('AA','LJ')),('RAISE',2.5))
        for x in (-.01,1.,float('nan'),float('inf')):
            self.assertIsNone(op.evaluate(self.model,op.Observation('KJo','LJ',randomhand=x)))

    def test_positional_and_state_guards(self):
        from dataclasses import replace
        base=op.Observation('AA','HJ')
        for changed in (
            {'is_preflop':False},{'players_dealt':5},{'raises':1},{'calls':1},
            {'still_to_act':5},{'pot_bb':2.},{'amount_to_call_bb':0.},
            {'stack_unknown':True},{'hero_stack_bb':94.9},{'hero_stack_bb':105.1},
            {'min_opp_stack_bb':94.9},{'max_opp_stack_bb':105.1},
            {'max_opp_stack_bb':94.},
        ):
            with self.subTest(changed=changed):
                self.assertIsNone(op.evaluate(self.model,replace(base,**changed)))
        self.assertEqual(op.evaluate(self.model,replace(base,hero_stack_bb=95.,min_opp_stack_bb=95.)),('RAISE',2.5))
        self.assertEqual(op.evaluate(self.model,replace(base,hero_stack_bb=105.,max_opp_stack_bb=105.)),('RAISE',2.5))

    def test_illegal_position_and_hand_class_fail_explicitly(self):
        with self.assertRaises(op.UnsafeSource):op.evaluate(self.model,op.Observation('AA','BB'))
        with self.assertRaises(op.UnsafeSource):op.evaluate(self.model,op.Observation('AKx','LJ'))

    def test_no_fallback_or_python_only_random_actions(self):
        text=op.SOURCE.read_text(encoding='utf-8')
        self.assertNotIn('WHEN Others',text)
        self.assertNotIn('Random <',text)
        self.assertNotIn('randomround',text)
        self.assertEqual(text.count('##f$preflop##'),1)
        for extra in ('WHEN Others Fold FORCE','WHEN (Random < 40) Fold FORCE',
                      'WHEN (nplayersdealt = 6) Call FORCE'):
            with self.subTest(extra=extra),self.assertRaises(op.UnsafeSource):
                op.parse(text+'\n'+extra+'\n')

    def test_guard_or_sizing_tamper_is_rejected(self):
        text=op.SOURCE.read_text(encoding='utf-8')
        for before,after in (('StillToAct = 4','StillToAct = 3'),
                             ('RaiseTo 2.5','RaiseBy 2.5'),
                             ('randomhand < 0.40','randomhand < 0.39'),
                             ('InMiddlePosition3','InMiddlePosition1')):
            with self.subTest(tamper=after),self.assertRaises(op.UnsafeSource):
                op.parse(text.replace(before,after,1))

    def test_handlist_overlap_or_missing_class_is_rejected(self):
        text=op.SOURCE.read_text(encoding='utf-8')
        for altered in (text.replace('##listMVPLJFOLD##','##listMVPLJFOLD##\nAA',1),
                        text.replace('AA AJo','AJo',1)):
            with self.assertRaises(op.UnsafeSource):op.parse(altered)

    def test_mapping_845_rows_and_expected_distribution(self):
        with (HERE/'RFI_6MAX_845_MAPPING.csv').open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),845)
        self.assertEqual(len(set((r['Position'],r['Hand']) for r in rows)),845)
        for row in rows:
            ref=RANGES[Position(row['Position'])][row['Hand']]
            for a in ('RAISE','LIMP','FOLD'):
                self.assertAlmostEqual(float(row[a.capitalize()+'_pct'])/100,ref[a])

    def test_generator_is_deterministic_and_preserves_snapshots(self):
        outputs=[op.SOURCE,HERE/'RFI_6MAX_845_MAPPING.csv']
        base=[ROOT/'gto6_heuristic_v0_6_1'/file for file in
              ('rfi_reference.py','vs_open_reference.py','vs_3bet_reference.py')]
        digest=lambda ps:[hashlib.sha256(p.read_bytes()).hexdigest() for p in ps]
        old=digest(outputs);strategy=digest(base)
        self.assertEqual(gen.generate(),(845,21,5))
        self.assertEqual(old,digest(outputs))
        self.assertEqual(strategy,digest(base))

if __name__=='__main__':unittest.main()
