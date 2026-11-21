"""Static parity and non-interference checks for 3-way SRP OpenPPL draft."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import threeway_interpreter as p
import build_threeway as b

class ThreeWay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source=p.parse_file()
    def out(self,street='flop',**kw):return p.eval_source(self.source,street,p.obs(**kw))
    def test_31_rule_streets(self):
        self.assertEqual([len(self.source.rules[s]) for s in p.STREETS],[14,11,8])
    def test_threeway_rfi_pfr_and_vsopen_caller(self):
        self.assertEqual(self.out(),'Check')
        caller={'user_H6_RFIIntent':False,'user_H6_VSOpenCallIntent':True,
                'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,
                'NumberOfRaisesBeforeFlop':1}
        self.assertEqual(self.out(**caller),'Check')
        self.assertEqual(self.out('turn',**caller),'Check')
        self.assertEqual(self.out('river',**caller),'Check')
    def test_no_hero_origin_no_policy(self):
        self.assertIsNone(self.out(user_H6_RFIIntent=False))
        self.assertIsNone(self.out(user_H6_VSOpenCallIntent=True))
    def test_conflicting_origin_safely_excluded(self):
        self.assertIsNone(self.out(user_H6_VSOpenCallIntent=True))
        self.assertIsNone(self.out(user_H6_3betIntent=True))
    def test_no_heads_up_or_4plus_players(self):
        for n in (0,1,3,4,5):
            with self.subTest(n=n):self.assertIsNone(self.out(OpponentsOnFlop=n,OpponentsLeft=n))
        self.assertIsNone(self.out(OpponentsOnFlop=2,OpponentsLeft=1))
    def test_no_threebet_fourbet_fivebet(self):
        for n in (1,2,3,4):
            with self.subTest(n=n):self.assertIsNone(self.out(NumberOfRaisesBeforeFlop=n))
    def test_no_allin_or_scrape_unknown(self):
        self.assertIsNone(self.out(NumberOfOpponentsAllin=1))
        self.assertIsNone(self.out(StackUnknown=True))
        self.assertIsNone(self.out(nplayersdealt=5))
    def test_nuts_and_strong_value(self):
        self.assertEqual(self.out(HaveNuts=True),'BetTwoThirdPot')
        self.assertEqual(self.out(HaveTwoPair=True),'BetHalfPot')
        self.assertEqual(self.out(HaveNuts=True,AmountToCall=2),'RaiseHalfPot')
        self.assertEqual(self.out(HaveNuts=True,AmountToCall=5.9),'Call')
        self.assertEqual(self.out(HaveNuts=True,AmountToCall=22),'Call')
        self.assertEqual(self.out('turn',HaveNuts=True,AmountToCall=22),'Call')
    def test_top_pair_call_price_boundaries(self):
        self.assertEqual(self.out(HaveTopPair=True,HaveBestKicker=True,AmountToCall=2.24),'Call')
        self.assertEqual(self.out(HaveTopPair=True,HaveBestKicker=True,AmountToCall=2.25),'Fold')
    def test_draw_price_and_positional_guard(self):
        self.assertEqual(self.out(HaveNutFlushDraw=True,AmountToCall=1.96),'Call')
        self.assertEqual(self.out(HaveNutFlushDraw=True,AmountToCall=2.0),'Fold')
        self.assertEqual(self.out(HaveOpenEndedStraightDraw=True,AmountToCall=1.4,Position='Last'),'Call')
        self.assertEqual(self.out(HaveOpenEndedStraightDraw=True,AmountToCall=1.4,Position='First'),'Fold')
    def test_street_specific_conservatism(self):
        for s in p.STREETS:
            self.assertEqual(self.out(s),'Check')
            self.assertEqual(self.out(s,AmountToCall=7),'Fold')
        self.assertEqual(self.out('river',HaveNuts=True),'BetTwoThirdPot')
    def test_mix_from_openppl_only(self):
        data=dict(HaveTopPair=True,HaveBestKicker=True,Position='Last')
        self.assertEqual(self.out(randomhand=.39,**data),'BetThirdPot')
        self.assertEqual(self.out(randomhand=.40,**data),'Check')
    def test_preflop_call_intentions_derived_from_existing_rules(self):
        c=b.capture_calls(b.PREV.read_text())
        self.assertEqual(len(c),33)
        self.assertTrue(all('Raises = 1 AND Calls = 0' in x for x in c))
        self.assertTrue(all(' Set user_H6_VSOpenCallIntent' in x for x in c))
        self.assertFalse(any('BotRaisedBeforeFlop' in x for x in c))
    def test_preflop_action_decisions_unchanged(self):
        old=[x for x in b.PREV.read_text().splitlines() if x.startswith('WHEN ') and x.endswith(' FORCE')]
        new=[x for x in b.COMBINED.read_text().splitlines() if x.startswith('WHEN ') and x.endswith(' FORCE')]
        self.assertTrue(all(x in new for x in old))
        self.assertEqual(old[:20],new[:20])
    def test_generator_deterministic_and_upstream_immutable(self):
        hashes=[hashlib.sha256(x.read_bytes()).hexdigest() for x in (b.INTENT,b.COMBINED,b.PREV)]
        self.assertEqual(b.generate(),(33,33))
        self.assertEqual(hashes,[hashlib.sha256(x.read_bytes()).hexdigest() for x in (b.INTENT,b.COMBINED,b.PREV)])
    def test_bad_ppl_or_bad_inputs_are_rejected(self):
        s=p.SOURCE.read_text()
        for add in ('\nWHEN Others Fold FORCE','\nWHEN (AmountToCall > 0) Call FORCE',
                    '\nWHEN (f$H6ThreeWaySRP AND randomhand < 0.77) Call FORCE'):
            with self.subTest(add=add),self.assertRaises(p.SourceError):p.parse(s+add)
        for bad in ({'randomhand':1},{'PotSize':0},{'AmountToCall':float('nan')}):
            with self.assertRaises(p.SourceError):self.out(**bad)

if __name__=='__main__':unittest.main()
