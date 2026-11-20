"""VS_OPEN parity: source-native OpenPPL interpreted offline, v0.6.1 unchanged.

Tests cannot prove action legality, runtime symbol values, or OpenHoldem fallback.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import csv
import hashlib
import math
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'gto6_heuristic_v0_6_1'))
from portability.vs_open_mvp import vs_open_source_interpreter as p
from portability.vs_open_mvp import generate_vs_open_mvp as gen
from portability.rfi_mvp import rfi_source_interpreter as ri
from vs_open_reference import RANGES, SPECS, SHADOWS, aggregate, threebet_to_bb
from scenario_contract import all_hand_classes


def target(row,x,sizing):
    # x is a *controlled OpenHoldem randomhand observation* in [0,1)
    if x<row.threebet:return ('3BET',sizing)
    if x<row.threebet+row.call:return ('CALL',None)
    return ('FOLD',None)


class VSOpenMVP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=p.parse_file()

    def test_15_opener_hero_pairs_and_2535_classes(self):
        self.assertEqual(len(p.PAIRS),15)
        self.assertEqual(set(p.PAIRS),set(RANGES))
        self.assertEqual(len(p.ALL_HANDS),169)
        self.assertEqual(len(self.model.lists),81)
        self.assertEqual(len(self.model.rules),121)
        self.assertEqual(sum(len(hs) for hs in self.model.lists.values()),2535)

    def test_all_2535_nodes_at_4_random_points(self):
        seen=0
        for op,hero in sorted(p.PAIRS):
            size=threebet_to_bb(op,hero)
            for hand,base in RANGES[(op,hero)].items():
                ctx=p.Observation(hand,op,hero)
                for x in (.0,.219999999999,.54,.99999999999):
                    with self.subTest(op=op,hero=hero,hand=hand,randomhand=x):
                        self.assertEqual(p.evaluate(self.model,replace(ctx,randomhand=x)),
                                         target(base,x,size))
                    seen+=1
        self.assertEqual(seen,2535*4)

    def test_every_mixed_boundary_and_predecessor(self):
        n=0
        for op,hero in sorted(p.PAIRS):
            for h,r in RANGES[(op,hero)].items():
                probs=[r.threebet,r.call,r.fold]
                if probs.count(0)>=2:continue
                limit=r.threebet if r.threebet>0 else r.call
                eps=math.nextafter(limit,0.)
                c=p.Observation(h,op,hero)
                with self.subTest(pair=(op,hero),h=h,lim=limit):
                    self.assertEqual(p.evaluate(self.model,replace(c,randomhand=eps)),target(r,eps,threebet_to_bb(op,hero)))
                    self.assertEqual(p.evaluate(self.model,replace(c,randomhand=limit)),target(r,limit,threebet_to_bb(op,hero)))
                n+=1
        self.assertEqual(n,59+154+61)

    def test_weighted_action_masses_unchanged(self):
        for op,hero in p.PAIRS:
            with self.subTest(pair=(op,hero)):
                rows=RANGES[(op,hero)]
                for key in ('3BET','CALL','FOLD'):
                    self.assertAlmostEqual(aggregate(op,hero,key),
                       100*sum((6 if len(hand)==2 else 4 if hand.endswith('s') else 12)*getattr(r,{'3BET':'threebet','CALL':'call','FOLD':'fold'}[key]) for hand,r in rows.items())/1326)

    def test_sizes_preserved_all_pairs(self):
        for op,hero in p.PAIRS:
            got=p.evaluate(self.model,p.Observation('AA',op,hero))
            self.assertEqual(got,('3BET',threebet_to_bb(op,hero)))
            self.assertIn(threebet_to_bb(op,hero),(8.0,9.6,10.25))

    def test_bb_versus_sb_open_to_3(self):
        a=p.Observation('AA','SB','BB')
        self.assertEqual(p.evaluate(self.model,a),('3BET',9.6))
        self.assertIsNone(p.evaluate(self.model,replace(a,amount_to_call_bb=1.5)))
        self.assertIsNone(p.evaluate(self.model,replace(a,first_raiser_position=2)))
        self.assertIsNone(p.evaluate(self.model,replace(a,pot_bb=4.5)))

    def test_no_flat_call_in_sb(self):
        for op in ('LJ','HJ','CO','BTN'):
            for r in RANGES[(op,'SB')].values():self.assertEqual(r.call,0)
            for h in p.ALL_HANDS:
                self.assertNotEqual(p.evaluate(self.model,p.Observation(h,op,'SB',randomhand=.3))[0],'CALL')

    def test_shadows_resolved_at_precedent_3bet(self):
        self.assertTrue(any(SHADOWS.values()))
        for pair,hands in SHADOWS.items():
            for h in hands:
                row=RANGES[pair][h]
                self.assertGreater(row.threebet,0)
                self.assertEqual(p.evaluate(self.model,p.Observation(h,*pair,randomhand=0))[0],'3BET')

    def test_invalid_context_guards_no_match(self):
        c=p.Observation('AA','HJ','CO')
        mutations={'is_preflop':False,'players_dealt':5,'players_dealt':5,'raises':2,
                   'calls':1,'first_raiser_position':3,'last_raiser_position':5,
                   'pot_bb':4.5,'amount_to_call_bb':1.5,'stack_unknown':True,
                   'hero_stack_bb':94.9,'min_opp_stack_bb':94.9,'max_opp_stack_bb':105.1}
        for key,value in mutations.items():
            with self.subTest(field=key):
                self.assertIsNone(p.evaluate(self.model,replace(c,**{key:value})))
        self.assertIsNone(p.evaluate(self.model,replace(c,min_opp_stack_bb=106,max_opp_stack_bb=94)))

    def test_stack_boundaries_and_nonfinite_refused(self):
        c=p.Observation('AA','HJ','CO')
        for s in (95,105):
            self.assertEqual(p.evaluate(self.model,replace(c,hero_stack_bb=s,min_opp_stack_bb=s,max_opp_stack_bb=s)),('3BET',8))
        for field in ('hero_stack_bb','min_opp_stack_bb','max_opp_stack_bb','pot_bb','amount_to_call_bb'):
            for invalid in (float('nan'),float('inf'),float('-inf')):
                self.assertIsNone(p.evaluate(self.model,replace(c,**{field:invalid})))

    def test_randomhand_repeated_and_cross_hand_input(self):
        pair=('LJ','HJ');h='JJ'
        c=p.Observation(h,*pair,randomhand=.20)
        actions={p.evaluate(self.model,c) for _ in range(20)}
        self.assertEqual(actions,{('3BET',8.)})
        self.assertEqual(p.evaluate(self.model,replace(c,randomhand=.90)),('CALL',None))
        for bad in (None,math.nan,-.001,1.,math.inf):
            self.assertIsNone(p.evaluate(self.model,replace(c,randomhand=bad)))
        # Pure branch still works even if randomhand is unavailable.
        self.assertEqual(p.evaluate(self.model,p.Observation('AA',*pair)),('3BET',8))

    def test_no_match_is_not_a_safe_fold(self):
        c=p.Observation('AA','LJ','HJ',raises=0)
        self.assertIsNone(p.evaluate(self.model,c))
        self.assertNotEqual(p.evaluate(self.model,c),('FOLD',None))

    def test_reject_unapproved_random_and_unconditional_fallback(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        for mutation in ('\nWHEN Others Fold FORCE','\nWHEN Random < 60 Fold FORCE',
                         '\nWHEN hand$AA Call FORCE','\nif hand == "AA": return "RAISE"'):
            with self.subTest(mutation=mutation), self.assertRaises(p.UnsafeOpenPPL):
                p.parse(source+mutation)

    def test_reject_missing_raiser_identification(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        for atom in (' AND FirstRaiserPosition = 5',' AND LastRaiserPosition = 5',
                     ' AND Raises = 1',' AND Calls = 0',' AND AmountToCall = 2.5'):
            with self.subTest(atom=atom),self.assertRaises(p.UnsafeOpenPPL):
                p.parse(source.replace(atom,'',1))

    def test_reject_duplicate_and_overlapping_class(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        marker='##listVOLJHJ3BET##'
        with self.assertRaises(p.UnsafeOpenPPL):
            p.parse(source.replace(marker,marker+'\nAA',1))
        source=source.replace('##listVOLJHJFOLD##','##listVOLJHJFOLD##\nAA',1)
        with self.assertRaises(p.UnsafeOpenPPL):p.parse(source)

    def test_reject_mixed_threshold_action_mutation(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        self.assertIn('randomhand <',source)
        with self.assertRaises(p.UnsafeOpenPPL):p.parse(source.replace('randomhand < 0.65','randomhand < 0.64',1))
        with self.assertRaises(p.UnsafeOpenPPL):p.parse(source.replace('randomhand >= 0.65','randomhand <= 0.65',1))

    def test_combined_single_preflop_entry_and_source_identity(self):
        combined=(HERE/'preflop_rfi_vsopen_draft.oppl').read_text(encoding='utf-8')
        rfi=(ROOT/'portability/rfi_mvp/rfi_6max_mvp.oppl').read_text(encoding='utf-8')
        vo=p.SOURCE.read_text(encoding='utf-8')
        self.assertEqual(combined,gen.combine(rfi,vo))
        self.assertEqual(combined.count('##f$preflop##'),1)
        self.assertIn('Raises = 0',combined)
        self.assertIn('Raises = 1',combined)
        self.assertEqual(len(ri.parse(rfi).rules),21)
        self.assertEqual(len(self.model.rules),121)
        self.assertEqual(len([x for x in combined.splitlines() if x.startswith('WHEN ')]),142)
        # Source handlists have distinct namespaces.
        self.assertFalse(set(ri.parse(rfi).lists)&set(self.model.lists))

    def test_mapping_2535_rows_and_one_class_per_pair(self):
        with (HERE/'VS_OPEN_2535_MAPPING.csv').open('r',newline='',encoding='utf-8') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),2535)
        self.assertEqual(len({(r['Opener'],r['Hero'],r['Hand']) for r in rows}),2535)
        for r in rows:
            base=RANGES[(r['Opener'],r['Hero'])][r['Hand']]
            for col,attr in (('Threebet_pct','threebet'),('Call_pct','call'),('Fold_pct','fold')):
                self.assertAlmostEqual(float(r[col]),100*getattr(base,attr))
            self.assertEqual(r['Bucket'],base.bucket)

    def test_generator_idempotent_and_baseline_unchanged(self):
        strategic=[ROOT/'gto6_heuristic_v0_6_1'/f for f in
                   ('rfi_reference.py','vs_open_reference.py','vs_3bet_reference.py')]
        generated=[p.SOURCE,HERE/'preflop_rfi_vsopen_draft.oppl',HERE/'VS_OPEN_2535_MAPPING.csv']
        hashes=[hashlib.sha256(x.read_bytes()).hexdigest() for x in strategic+generated]
        self.assertEqual(gen.generate(),(2535,81,121))
        self.assertEqual(hashes,[hashlib.sha256(x.read_bytes()).hexdigest() for x in strategic+generated])

if __name__=='__main__':unittest.main()
