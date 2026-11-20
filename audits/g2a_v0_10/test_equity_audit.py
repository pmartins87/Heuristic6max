"""Unit checks for source provenance, 7-card scoring, physical mass and MC sanity.

These tests do not validate GTO, realized equity, poker EV or site rake.
"""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import equity_audit as e


def cards(text):
    return tuple(e.CARDS[text[i:i+2]] for i in range(0,len(text),2))


class Audit(unittest.TestCase):
    def test_combinatorics_and_classes(self):
        self.assertEqual(len(e.COMBOS),1326)
        self.assertEqual(sum(len(x) for x in e.BY_CLASS.values()),1326)
        self.assertEqual(len(e.H),169)
        self.assertEqual(e.EXPECTED_ORDERED_PHYSICAL_MATCHUPS,1624350)

    def test_line_format_and_orientations(self):
        a,b,v=e.parse_equity_line(b'AcAd:AhAs=50.00\r\n')
        self.assertEqual(a,cards('AcAd'))
        self.assertEqual(b,cards('AhAs'))
        self.assertEqual(v,.5)
        a,b,v=e.parse_equity_line(b'AhKc:AcAd=6.53\n')
        self.assertEqual(v,.0653)
        self.assertEqual(e.hand_class(a),'AKo')
        self.assertEqual(e.hand_class(b),'AA')

    def test_invalid_matchups(self):
        for line in (b'AcAc:AhAs=50.00',b'AcAd:AhAx=50.00',
                     b'AcAd:AhAs=120.0',b'AcAd:AhAs=nan',
                     b'AcAd:AhAs=+30'):
            with self.subTest(line=line), self.assertRaises(ValueError):
                e.parse_equity_line(line)

    def test_rank_categories(self):
        hands={
            8:'AhKhQhJhTh2c3d', # royal flush
            7:'AcAdAhAsKc3d4h',
            6:'AcAdAhKcKd5d6h',
            5:'AcKcQc9c3c4h7d',
            4:'Ac2d3h4s5c7d8h',
            3:'AcAdAhKcQc5d6s',
            2:'AcAdKcKdQc3d4h',
            1:'AcAdKcQc8d3c4h',
            0:'AcKdQc9d7s3c4h',
        }
        for cat,hand in hands.items():
            with self.subTest(cat=cat):
                self.assertEqual(e.score7(cards(hand))[0],cat)

    def test_kickers_wheel_and_tie(self):
        self.assertEqual(e.straight_high((1<<12)|15),5)
        self.assertEqual(e.straight_high(sum(1<<i for i in range(8,13))),14)
        self.assertGreater(e.score7(cards('AcAdAhKcKd4s3d')),
                           e.score7(cards('QcQdQhJcJd4s3d')))
        self.assertEqual(e.score7(cards('AcKcQcJcTc3d2h')),
                         e.score7(cards('AcKcQcJcTc4d5h')))

    def test_hero_villain_weights(self):
        self.assertEqual(e.V3['AKs'].threebet,1)
        self.assertEqual(e.H['AQo'].fold,1)
        self.assertEqual(e.H['TT'].call,1)
        self.assertEqual(len(e.CANDIDATES),15)

    def test_reference_screen_complete(self):
        path=HERE/'HJ_CO_EQUITY_169_REFERENCE_v0_10.csv'
        with path.open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),169)
        self.assertEqual(len({r['Hand'] for r in rows}),169)
        self.assertEqual({r['Hand'] for r in rows},set(e.H))
        for r in rows:
            self.assertGreater(float(r['ModelCO3betWeightedMatchups']),0)
            self.assertTrue(0<=float(r['RawPreflopShowdownEquity_pct'])<=100)
        self.assertAlmostEqual(float(next(r['RawPreflopShowdownEquity_pct'] for r in rows if r['Hand']=='AQo')),41.310106,places=6)

    def test_independent_mc_vs_reference(self):
        with (HERE/'HJ_CO_EQUITY_169_REFERENCE_v0_10.csv').open(encoding='utf-8',newline='') as f:
            m={r['Hand']:float(r['RawPreflopShowdownEquity_pct'])/100 for r in csv.DictReader(f)}
        for hand in ('AQo','AJo','AA','22','KJo'):
            with self.subTest(hand=hand):
                estimate,se=e.mc_class(hand,4000)
                self.assertLess(abs(estimate-m[hand]),.055)
                self.assertLess(se,.009)

    def test_mc_seed_deterministic(self):
        self.assertEqual(e.mc_class('AQo',600),e.mc_class('AQo',600))

    def test_source_tables_remain_unmodified(self):
        files=('RFI_100BB_169x5_DRAFT.csv','VS_OPEN_100BB_15x169_DRAFT.csv',
               'VS_3BET_100BB_15x169_DRAFT.csv')
        before={f:hashlib.sha256((e.BASE/f).read_bytes()).hexdigest() for f in files}
        e.mc_class('AQo',500)
        self.assertEqual(before,{f:hashlib.sha256((e.BASE/f).read_bytes()).hexdigest() for f in files})


if __name__=='__main__':unittest.main()
