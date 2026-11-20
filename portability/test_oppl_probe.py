"""Static one-to-one proof on an intentionally tiny pure-decision subset."""
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import oppl_probe as p


class PortabilityContractTests(unittest.TestCase):
    def test_two_authored_oppl_rules(self):
        rules = p.parse_file()
        self.assertEqual(len(rules), 2)
        self.assertEqual([r.line for r in rules], [5, 6])

    def test_pure_rfi_aa_and_kk(self):
        rules = p.parse_file()
        for hand in ('AA', 'KK'):
            self.assertEqual(p.evaluate(rules, hand=hand, in_button=True,
                                        raises=0, calls=0), ('RaiseTo', 2.5))

    def test_no_fallback_in_test_interpreter(self):
        rules = p.parse_file()
        for hand,button,raises,calls in [('AQs',True,0,0),('AA',False,0,0),
                                          ('KK',True,1,0),('AA',True,0,1)]:
            self.assertIsNone(p.evaluate(rules, hand=hand, in_button=button,
                                         raises=raises, calls=calls))

    def test_3042_state_enumeration(self):
        from itertools import product
        ranks='AKQJT98765432'
        hands=[r+r for r in ranks]+[a+b+s for i,a in enumerate(ranks)
                                          for b in ranks[i+1:] for s in 'so']
        self.assertEqual(len(hands),169)
        rules=p.parse_file()
        n=0
        for hand,button,raises,calls in product(hands,(False,True),range(3),range(3)):
            expected=('RaiseTo',2.5) if hand in ('AA','KK') and button and raises==0 and calls==0 else None
            self.assertEqual(p.evaluate(rules,hand=hand,in_button=button,raises=raises,calls=calls),expected)
            n+=1
        self.assertEqual(n,169*2*3*3)

    def test_reject_python_only_mixing(self):
        for bad in ('WHEN (InButton AND Raises = 0 AND Calls = 0 AND hand$AA AND Random < 50) RaiseTo 2.5 FORCE',
                    'WHEN (InButton AND Raises = 0 AND Calls = 0 AND hand$AA) RaiseTo 3 FORCE',
                    'WHEN Others Fold FORCE',
                    'if hand == "AA": return 2.5',
                    'WHEN (InButton AND Raises = 0 AND Calls = 0 AND hand$AQSuited) RaiseTo 2.5 FORCE'):
            with self.subTest(bad=bad),self.assertRaises(p.PortabilityError):
                p.parse_lines('##f$preflop##\n'+bad+'\n')

    def test_reject_shadow_and_unrecognized_condition(self):
        lines = p.SOURCE.read_text(encoding='utf-8')
        with self.assertRaises(p.PortabilityError):
            p.parse_lines(lines+'\n'+lines.splitlines()[4])
        with self.assertRaises(p.PortabilityError):
            p.parse_lines(lines.replace('InButton','InPosition'))

    def test_source_policy_is_not_changed(self):
        import hashlib
        root=HERE.parents[0]
        # This audit reads only its own example, never strategic policy modules.
        names=('gto6_heuristic_v0_6_1/rfi_reference.py',
               'gto6_heuristic_v0_6_1/vs_open_reference.py',
               'gto6_heuristic_v0_6_1/vs_3bet_reference.py')
        if all((root/name).is_file() for name in names):
            before={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}
            p.parse_file()
            self.assertEqual(before,{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names})


if __name__=='__main__':
    unittest.main()
