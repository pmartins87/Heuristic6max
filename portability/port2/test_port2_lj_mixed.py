"""PORT-2 static-source tests. NO actual OpenHoldem executable is exercised."""
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
from portability.port2 import port2_interpreter as p
from rfi_reference import RANGES
from scenario_contract import Position

class PortTwo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules=p.parse_file()
        cls.rfi=RANGES[Position.LJ]

    def test_all_169_classes_mapped_once(self):
        self.assertEqual(len(p.ALL_HANDS),169)
        self.assertEqual(tuple(len(self.rules.lists[x]) for x in p.ALL_LISTS),(43,125,1))
        self.assertEqual(set.union(*(set(x) for x in self.rules.lists.values())),p.ALL_HANDS)
        self.assertEqual(self.rules.lists[p.MIX],{'KJo'})
        for a in p.ALL_LISTS:
            for b in p.ALL_LISTS:
                if a!=b:self.assertFalse(self.rules.lists[a]&self.rules.lists[b])

    def test_168_pure_decisions_with_all_randomhand_values(self):
        values=[None,0.0,.1,.399999999,.4,.500001,.999999999,-1,1,math.nan]
        for hand in sorted(p.ALL_HANDS-{'KJo'}):
            expected=('RAISE',2.5) if self.rfi[hand]['RAISE']==1 else ('FOLD',None)
            for u in values:
                with self.subTest(hand=hand,randomhand=u):
                    self.assertEqual(p.evaluate(self.rules,p.Context(hand=hand,randomhand=u)),expected)

    def test_kjo_complete_threshold_partition(self):
        for value,expected in [(0.,('RAISE',2.5)),(.001,('RAISE',2.5)),
                               (.399999999,('RAISE',2.5)),(.4,('FOLD',None)),
                               (.400000001,('FOLD',None)),(.999999999,('FOLD',None))]:
            with self.subTest(value=value):
                self.assertEqual(p.evaluate(self.rules,p.Context(hand='KJo',randomhand=value)),expected)

    def test_kjo_exact_40_60_on_enumerated_uniform_grid(self):
        actions=[p.evaluate(self.rules,p.Context(hand='KJo',randomhand=i/10000))[0]
                 for i in range(10000)]
        self.assertEqual(actions.count('RAISE'),4000)
        self.assertEqual(actions.count('FOLD'),6000)

    def test_no_per_evaluation_resampling(self):
        for u in (0.,.20,.399,.4,.75,.99):
            context=p.Context(hand='KJo',randomhand=u)
            results=[p.evaluate(self.rules,context) for _ in range(50)]
            self.assertEqual(len(set(results)),1)
        source=p.SOURCE.read_text(encoding='utf-8')
        self.assertNotIn('WHEN Random ',source)
        self.assertNotIn('randomround',source)

    def test_missing_randomhand_fails_unmapped_kjo_only(self):
        for u in (None,math.nan,math.inf,-.0000001,1.0,'0.2'):
            with self.subTest(u=u):
                self.assertIsNone(p.evaluate(self.rules,p.Context(hand='KJo',randomhand=u)))
        self.assertEqual(p.evaluate(self.rules,p.Context(hand='AA')),('RAISE',2.5))

    def test_every_class_matches_baseline_on_uniform_100_grid(self):
        for h in sorted(p.ALL_HANDS):
            actual=sum(p.evaluate(self.rules,p.Context(hand=h,randomhand=i/100))[0]=='RAISE'
                       for i in range(100))/100
            with self.subTest(hand=h):
                self.assertEqual(actual,self.rfi[h]['RAISE'])

    def test_all_guard_variants_block_branch_including_kjo(self):
        variants=(('is_preflop',False),('nplayersdealt',5),('nplayersdealt',7),
             ('in_utg',False),('raises',1),('calls',1),('still_to_act',4),
             ('pot_bb',1.),('amount_to_call_bb',0.),('stack_unknown',True),
             ('hero_stack_bb',94.9),('hero_stack_bb',105.1),
             ('min_opponent_stack_bb',94.9),('max_opponent_stack_bb',105.1),
             ('min_opponent_stack_bb',106.),('max_opponent_stack_bb',94.))
        for hand in ('AA','72o','KJo'):
            for u in (0.2,.6):
                for field,val in variants:
                    s=replace(p.Context(hand=hand,randomhand=u),**{field:val})
                    with self.subTest(hand=hand,u=u,field=field,value=val):
                        self.assertIsNone(p.evaluate(self.rules,s))

    def test_stack_guard_boundaries(self):
        for stack in (95,105):
            s=p.Context(hand='KJo',randomhand=.15,hero_stack_bb=stack,
                        min_opponent_stack_bb=stack,max_opponent_stack_bb=stack)
            self.assertEqual(p.evaluate(self.rules,s),('RAISE',2.5))

    def test_invalid_numeric_observation_no_match(self):
        for field,val in [('pot_bb',math.nan),('pot_bb',math.inf),
                          ('hero_stack_bb',math.nan),('min_opponent_stack_bb',math.nan),
                          ('max_opponent_stack_bb',math.inf)]:
            with self.subTest(field=field):
                self.assertIsNone(p.evaluate(self.rules,replace(p.Context(hand='KJo',randomhand=.2),**{field:val})))

    def test_reject_random_symbol_substitution(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        for old,new in [('randomhand < 0.40','Random < 40'),
                        ('randomhand < 0.40','randomround < 0.40'),
                        ('randomhand < 0.40','randomhand <= 0.40'),
                        ('randomhand < 0.40','randomhand < 0.39'),
                        ('randomhand >= 0.40','randomhand > 0.40'),
                        ('randomhand >= 0.40','randomhand >= 0.41')]:
            with self.subTest(new=new),self.assertRaises(p.PortabilityError):
                p.parse(source.replace(old,new,1))

    def test_reject_unsafe_fallback_and_python_code(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        for suffix in ('\nWHEN Others Fold FORCE','\nWHEN Others Check FORCE',
                       '\nif hand == "KJo": return "Raise"',
                       '\nWHEN listPORT2LJMIX Fold FORCE'):
            with self.subTest(suffix=suffix),self.assertRaises(p.PortabilityError):
                p.parse(source+suffix)

    def test_reject_reordered_rules(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        lines=source.splitlines()
        idx=[i for i,line in enumerate(lines) if line.startswith('WHEN (')]
        lines[idx[2]],lines[idx[3]]=lines[idx[3]],lines[idx[2]]
        with self.assertRaises(p.PortabilityError):p.parse('\n'.join(lines))

    def test_reject_overshadowed_or_missing_hand(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        with self.assertRaises(p.PortabilityError):
            p.parse(source.replace('##listPORT2LJMIX##\nKJo','##listPORT2LJMIX##\nKJs KJo'))
        with self.assertRaises(p.PortabilityError):
            p.parse(source.replace('##listPORT2LJMIX##\nKJo','##listPORT2LJMIX##\n'))

    def test_reject_missing_guard_atom(self):
        source=p.SOURCE.read_text(encoding='utf-8')
        for atom in (' AND nplayersdealt = 6',' AND InUTG',' AND Raises = 0',
                     ' AND StillToAct = 5',' AND NOT StackUnknown'):
            with self.subTest(atom=atom),self.assertRaises(p.PortabilityError):
                p.parse(source.replace(atom,'',1))

    def test_csv_169_records_matches_reference(self):
        with (HERE/'PORT2_LJ_169_MAPPING.csv').open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),169)
        self.assertEqual({r['Hand'] for r in rows},p.ALL_HANDS)
        for row in rows:
            self.assertEqual(float(row['RFI_raise_pct'])/100,self.rfi[row['Hand']]['RAISE'])
        mixed=[r for r in rows if r['Portability']=='STATIC_MIX_NEEDS_OH_RUNTIME']
        self.assertEqual([(r['Hand'],r['Port2_decision']) for r in mixed],[('KJo','MIX_RANDOMHAND_LT_0_40')])

    def test_deterministic_generator_does_not_rewrite_unexpected_source(self):
        from portability.port2 import generate_port2 as g
        paths=(p.SOURCE,HERE/'PORT2_LJ_169_MAPPING.csv')
        before=[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths]
        self.assertEqual(g.generate(),(43,125,1))
        self.assertEqual(before,[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths])

    def test_immutable_baseline_read_only(self):
        paths=[ROOT/'gto6_heuristic_v0_6_1'/f for f in ('rfi_reference.py',
                   'vs_open_reference.py','vs_3bet_reference.py')]
        before=[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths]
        for h in ('AA','KJo','72o'):
            p.evaluate(self.rules,p.Context(hand=h,randomhand=.3))
        self.assertEqual(before,[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths])

    def test_no_claim_of_real_openholdem_parity(self):
        text=(HERE/'README.md').read_text(encoding='utf-8')
        self.assertIn('NÃO OPERACIONAL',text)
        self.assertIn('replay',text.lower())

if __name__=='__main__':unittest.main()
