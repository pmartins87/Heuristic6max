"""Source-parity tests: OPPL handlists are the only live strategy source in PORT-1.

These do NOT prove OpenHoldem interpreter, chip-unit, scrape or fallback parity.
"""
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
import port1_interpreter as p  # noqa: E402
from rfi_reference import RANGES  # noqa: E402
from scenario_contract import Position  # noqa: E402

class PortOne(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=p.parse_file()
        cls.rows=RANGES[Position.LJ]

    def test_one_mix_class_is_explicitly_unsupported(self):
        self.assertEqual({h for h in p.ALL_HANDS if self.rows[h]['RAISE'] not in (0,1)},{'KJo'})
        self.assertEqual(self.rows['KJo']['RAISE'],.4)
        self.assertIsNone(p.evaluate(self.model,p.Context(hand='KJo')))

    def test_static_parity_for_every_pure_hand(self):
        self.assertEqual(len(p.ALL_HANDS),169)
        for h in sorted(p.ALL_HANDS):
            with self.subTest(hand=h):
                r=self.rows[h]['RAISE']
                expected=('RAISE',2.5) if r==1 else ('FOLD',None) if r==0 else None
                self.assertEqual(p.evaluate(self.model,p.Context(hand=h)),expected)

    def test_open_and_fold_partition(self):
        self.assertEqual(len(self.model.lists[p.LIST_RAISE]),43)
        self.assertEqual(len(self.model.lists[p.LIST_FOLD]),125)
        self.assertFalse(self.model.lists[p.LIST_RAISE]&self.model.lists[p.LIST_FOLD])
        self.assertEqual(set(p.ALL_HANDS)-set.union(*(set(s) for s in self.model.lists.values())),{'KJo'})

    def test_negative_guard_full_matrix(self):
        variants=(('is_preflop',False),('nplayersdealt',5),('nplayersdealt',7),
             ('in_utg',False),('raises',1),('calls',1),('still_to_act',4),
             ('pot_bb',1.),('amount_to_call_bb',0.),('stack_unknown',True),
             ('hero_stack_bb',94.9),('hero_stack_bb',105.1),
             ('min_opponent_stack_bb',94.9),('max_opponent_stack_bb',105.1),
             ('min_opponent_stack_bb',106.),('max_opponent_stack_bb',94.))
        n=0
        for hand in p.ALL_HANDS:
            for field,value in variants:
                with self.subTest(hand=hand,guard=field,value=value):
                    self.assertIsNone(p.evaluate(self.model,replace(p.Context(hand=hand),**{field:value})))
                    n+=1
        self.assertEqual(n,169*len(variants))

    def test_boundary_guards_95_105(self):
        for stack in (95,105):
            s=p.Context(hand='AA',hero_stack_bb=stack,min_opponent_stack_bb=stack,max_opponent_stack_bb=stack)
            self.assertEqual(p.evaluate(self.model,s),('RAISE',2.5))

    def test_raises_are_raise_to_not_raise_by(self):
        self.assertEqual(self.model.rules[0],(p.LIST_RAISE,'RaiseTo 2.5'))
        self.assertEqual(self.model.rules[1],(p.LIST_FOLD,'Fold'))

    def test_reject_python_only_randomness_and_implicit_fallback(self):
        text=p.SOURCE.read_text(encoding='utf-8')
        for suffix in ('\nWHEN Others Fold FORCE','\nWHEN Random < 40 Fold FORCE',
                       '\nif hand == "AA": action="raise"'):
            with self.subTest(suffix=suffix),self.assertRaises(p.PortabilityError):
                p.parse(text+suffix)

    def test_reject_missing_rfi_guard(self):
        text=p.SOURCE.read_text(encoding='utf-8')
        for atom in (' AND nplayersdealt = 6',' AND PotSize = 1.5',
                     ' AND Raises = 0',' AND NOT StackUnknown',' AND InUTG'):
            with self.subTest(atom=atom),self.assertRaises(p.PortabilityError):
                p.parse(text.replace(atom,'',1))

    def test_reject_unsafe_rounding_mixing(self):
        text=p.SOURCE.read_text(encoding='utf-8')
        with self.assertRaises(p.PortabilityError):
            p.parse(text.replace('RaiseTo 2.5 FORCE','RaiseTo 3 FORCE'))
        with self.assertRaises(p.PortabilityError):
            p.parse(text.replace('AND listPORT1LJRAISE','AND listPORT1LJFOLD'))

    def test_reject_overlapping_handlists(self):
        text=p.SOURCE.read_text(encoding='utf-8')
        target=f'##{p.LIST_FOLD}##'
        with self.assertRaises(p.PortabilityError):
            p.parse(text.replace(target,target+'\nAA',1))

    def test_reject_handlist_without_safe_hand_class(self):
        text=p.SOURCE.read_text(encoding='utf-8')
        target=f'##{p.LIST_FOLD}##'
        with self.assertRaises(p.PortabilityError):
            p.parse(text.replace(target,target+'\nhand$QJo',1))

    def test_mapping_csv_169_exhaustive(self):
        path=HERE/'PORT1_LJ_169_MAPPING.csv'
        with path.open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),169)
        self.assertEqual({r['Hand'] for r in rows},p.ALL_HANDS)
        by={r['Hand']:r for r in rows}
        self.assertEqual(by['KJo']['Portability'],'BLOCKED_MIX')
        for h in p.ALL_HANDS:
            self.assertAlmostEqual(float(by[h]['RFI_raise_pct'])/100,self.rows[h]['RAISE'])

    def test_generator_byte_identical(self):
        import generate_port1 as g
        paths=(p.SOURCE,HERE/'PORT1_LJ_169_MAPPING.csv')
        hashes=[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths]
        self.assertEqual(g.generate(),(43,125))
        self.assertEqual(hashes,[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths])

    def test_strategy_modules_remain_unchanged(self):
        files=[ROOT/'gto6_heuristic_v0_6_1'/n for n in
               ('rfi_reference.py','vs_open_reference.py','vs_3bet_reference.py')]
        hashes=[hashlib.sha256(x.read_bytes()).hexdigest() for x in files]
        p.evaluate(self.model,p.Context(hand='AA'))
        self.assertEqual(hashes,[hashlib.sha256(x.read_bytes()).hexdigest() for x in files])

    def test_nonexistent_hand_rejected(self):
        with self.assertRaises(p.PortabilityError):p.evaluate(self.model,p.Context(hand='A6x'))

if __name__=='__main__':unittest.main()
