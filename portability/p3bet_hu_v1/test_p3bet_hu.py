"""Functional static tests. Real OpenHoldem action & scrape remain untested."""
from pathlib import Path
import hashlib
import unittest
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import p3bet_interpreter as it
import build_p3bet_hu as build

class ThreeBetHU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model=it.parse_file()
    def play(self,street='flop',**kw):return it.evaluate(self.model,street,it.observations(**kw))

    def test_p3bet_aggressor_and_caller_domains_are_exclusive(self):
        self.assertTrue(self.play()=='Check')
        caller={'user_H6_3betIntent':False,'user_H6_RFIIntent':True,'BotCalledBeforeFlop':True}
        self.assertEqual(self.play(**caller),'Check')
        self.assertIsNone(self.play(**{'user_H6_RFIIntent':False,'user_H6_3betIntent':False}))
        self.assertIsNone(self.play(**{'user_H6_RFIIntent':True,'user_H6_3betIntent':True,'BotCalledBeforeFlop':True}))

    def test_srp_cannot_enter_threebet_module(self):
        self.assertIsNone(self.play(NumberOfRaisesBeforeFlop=0))
        self.assertIsNone(self.play(user_H6_3betIntent=False,NumberOfRaisesBeforeFlop=0))

    def test_4bet_and_5bet_pots_never_enter(self):
        for n in (2,3,4,5):
            self.assertIsNone(self.play(NumberOfRaisesBeforeFlop=n))

    def test_no_multiway_heads_up_regression(self):
        for key,val in (('OpponentsOnFlop',2),('OpponentsLeft',2),('nplayersdealt',5),
                        ('NumberOfOpponentsAllin',1),('StackUnknown',True)):
            with self.subTest(field=key):self.assertIsNone(self.play(**{key:val}))

    def test_all_three_streets_have_actions(self):
        self.assertEqual([len(self.model.sections[s]) for s in it.STREETS],[15,13,11])
        for s in it.STREETS:
            self.assertEqual(self.play(s),'Check')
            self.assertEqual(self.play(s,AmountToCall=11),'Fold')

    def test_nuts_price_and_bet_logic(self):
        self.assertEqual(self.play(HaveNuts=True,AmountToCall=4),'RaiseHalfPot')
        self.assertEqual(self.play(HaveNuts=True,AmountToCall=15),'Call')
        self.assertEqual(self.play(HaveNuts=True),'BetTwoThirdPot')
        self.assertEqual(self.play('river',HaveNuts=True,AmountToCall=12),'Call')

    def test_flop_overpair_aggressor_and_caller_difference(self):
        self.assertEqual(self.play(HaveOverPair=True,AmountToCall=12),'Call')
        caller={'user_H6_3betIntent':False,'user_H6_RFIIntent':True,'BotCalledBeforeFlop':True}
        self.assertEqual(self.play(HaveOverPair=True,AmountToCall=12,**caller),'Fold')

    def test_calling_range_relative_price_limits(self):
        self.assertEqual(self.play(HaveNutFlushDraw=True,AmountToCall=9),'Call')
        self.assertEqual(self.play(HaveNutFlushDraw=True,AmountToCall=9.1),'Fold')
        self.assertEqual(self.play(HaveOpenEndedStraightDraw=True,AmountToCall=6.4),'Call')
        self.assertEqual(self.play(HaveOpenEndedStraightDraw=True,AmountToCall=6.5),'Fold')

    def test_mix_threshold_from_oppl_source(self):
        for rand,result in ((0.0,'BetHalfPot'),(.49999,'BetHalfPot'),(.50,'Check'),(.95,'Check')):
            with self.subTest(rand=rand):
                self.assertEqual(self.play(HaveNutFlushDraw=True,randomhand=rand),result)

    def test_street_specific_historical_turn_barrel(self):
        self.assertEqual(self.play('turn',HaveOverPair=True,BotRaisedOnFlop=True),'BetHalfPot')
        self.assertEqual(self.play('turn',HaveOverPair=True,BotRaisedOnFlop=False),'Check')

    def test_reject_unknown_unsafe_openppl_extensions(self):
        s=it.SOURCE.read_text()
        for new in ('\nWHEN Others Fold FORCE','\nWHEN (f$H6ThreeBetHU AND randomhand < 0.99) Call FORCE',
                    '\nWHEN (AmountToCall > 0) Call FORCE'):
            with self.subTest(rule=new),self.assertRaises(it.PolicyError):it.parse(s+new)

    def test_inputs_invalid_do_not_choose(self):
        for changed in ({'randomhand':float('nan')},{'randomhand':1.0},
                        {'AmountToCall':-1},{'PotSize':0}):
            with self.assertRaises(it.PolicyError):self.play(**changed)

    def test_generated_preflop_action_text_byte_identical(self):
        old=build.PREVIOUS.read_text();new=build.OUT.read_text()
        captures=[x for x in build.ORIGIN.read_text().splitlines() if x]
        pre='\n'.join(captures)
        # Restoring original preflop section by deleting generated Set rules.
        for line in captures:
            if line.startswith('WHEN '):new=new.replace(line+'\n','',1)
        self.assertEqual([x for x in new.splitlines() if x.startswith('WHEN ') and
                          x.endswith(' FORCE') and 'RaiseTo ' in x],
                         [x for x in old.splitlines() if x.startswith('WHEN ') and
                          x.endswith(' FORCE') and 'RaiseTo ' in x])
        self.assertIn('##f$preflop##',new)

    def test_preflop_intent_instrumentation_precise(self):
        rfi,three=build.capture_rules(build.PREVIOUS.read_text())
        self.assertEqual(len(rfi),9)
        self.assertEqual(len(three),44)
        self.assertTrue(all('Raises = 0 AND Calls = 0' in line for line in rfi))
        self.assertTrue(all('Raises = 1 AND Calls = 0' in line for line in three))
        self.assertTrue(all('Set user_H6_3betIntent' in line for line in three))
        self.assertFalse(any('RaisesSinceLastPlay' in line for line in three))

    def test_regeneration_repeatable_and_frozen_sources(self):
        out=(build.OUT,build.ORIGIN)
        orig=[hashlib.sha256(p.read_bytes()).hexdigest() for p in out]
        frozen=hashlib.sha256(build.PREVIOUS.read_bytes()).hexdigest()
        self.assertEqual(build.generate(),(9,44,39))
        self.assertEqual(orig,[hashlib.sha256(p.read_bytes()).hexdigest() for p in out])
        self.assertEqual(frozen,hashlib.sha256(build.PREVIOUS.read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
