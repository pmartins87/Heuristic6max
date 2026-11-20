from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import hashlib
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import srp_source_interpreter as s


class SRPHeadUpHeuristic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=s.parse_file()

    def play(self, street, **kw):
        return s.evaluate(self.model,street,s.observe(**kw))

    def test_01_parses_all_33_actions_with_5_helpers(self):
        self.assertEqual(len(self.model.sections),8)
        self.assertEqual([len(self.model.sections['f$'+i]) for i in s.STREETS],[14,10,9])

    def test_02_preflop_unmodified_in_combined_file(self):
        old=s.PREVIOUS.read_bytes()
        combined=s.COMBINED.read_bytes()
        self.assertTrue(combined.startswith(old.rstrip()+b'\n\n'))
        self.assertEqual(combined[len(old.rstrip()+b'\n\n'):],s.SOURCE.read_bytes())
        self.assertEqual(combined.count(b'##f$preflop##'),1)
        for name in s.ALL_SECTIONS:self.assertEqual(combined.count(f'##{name}##'.encode()),1)

    def test_03_guarded_out_of_scope(self):
        variants={'nplayersdealt':5,'OpponentsOnFlop':2,'OpponentsLeft':2,
                  'StackUnknown':True,'NumberOfOpponentsAllin':1,
                  'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,
                  'NumberOfRaisesBeforeFlop':1}
        for key,bad in variants.items():
            # Some variants change mode to a valid preflop caller; check only invalid as a pair.
            v={key:bad}
            if key=='BotRaisedBeforeFlop':v['BotCalledBeforeFlop']=False
            for street in s.STREETS:
                with self.subTest(key=key,street=street):
                    self.assertIsNone(self.play(street, **v))

    def test_04_caller_mode_is_explicit_and_rejects_3bet_defense(self):
        callmode={'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,'NumberOfRaisesBeforeFlop':1}
        self.assertEqual(self.play('flop',**callmode),'Check')
        self.assertEqual(self.play('turn',**callmode),'Check')
        self.assertEqual(self.play('river',**callmode),'Check')
        self.assertIsNone(self.play('flop',BotRaisedBeforeFlop=True,BotCalledBeforeFlop=True,
                                    NumberOfRaisesBeforeFlop=1))

    def test_05_free_flop_value_and_top_pair(self):
        for hand in ('HaveNuts','HaveSet','HaveFullHouse','HaveTwoPair','HaveTrips'):
            with self.subTest(hand=hand):
                self.assertEqual(self.play('flop',**{hand:True}),'BetTwoThirdPot')
        self.assertEqual(self.play('flop',HaveOverPair=True),'BetHalfPot')
        self.assertEqual(self.play('flop',HaveTopPair=True,HaveBestKicker=True),'BetHalfPot')
        self.assertEqual(self.play('flop',HaveTopPair=True),'Check')

    def test_06_bet_faced_flop_raise_call_fold(self):
        self.assertEqual(self.play('flop',AmountToCall=2,HaveNuts=True),'RaiseHalfPot')
        self.assertEqual(self.play('flop',AmountToCall=4,HaveNuts=True),'Call')
        self.assertEqual(self.play('flop',AmountToCall=6,HaveSet=True),'Call')
        self.assertEqual(self.play('flop',AmountToCall=2,HaveTopPair=True),'Fold')
        self.assertEqual(self.play('flop',AmountToCall=1.9,HaveTopPair=True),'Call')
        self.assertEqual(self.play('flop',AmountToCall=1,HaveFlushDraw=True),'Call')
        self.assertEqual(self.play('flop',AmountToCall=3,HaveFlushDraw=True),'Fold')

    def test_07_caller_in_position_stab_vs_oop_check(self):
        base={'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,'NumberOfRaisesBeforeFlop':1,
              'HaveTopPair':True,'HaveBestKicker':True}
        self.assertEqual(self.play('flop',**{**base,'Position':'Last'}),'BetHalfPot')
        self.assertEqual(self.play('flop',**{**base,'Position':'First'}),'Check')

    def test_08_stable_randomhand_25pct_cbet_on_dry_flops(self):
        base={'BotIsLastRaiser':True}
        for u in (0,0.001,.249999):
            self.assertEqual(self.play('flop',**base,randomhand=u),'BetThirdPot')
        for u in (.25,.4,.999999):
            self.assertEqual(self.play('flop',**base,randomhand=u),'Check')
        for key in ('FlushPossibleOnFlop','StraightPossibleOnFlop','PairOnBoard'):
            self.assertEqual(self.play('flop',**base,randomhand=.1,**{key:True}),'Check')
        self.assertEqual(self.play('flop',BotIsLastRaiser=False,randomhand=.10),'Check')

    def test_09_draws_flop_and_turn(self):
        self.assertEqual(self.play('flop',HaveNutFlushDraw=True),'BetHalfPot')
        self.assertEqual(self.play('turn',HaveNutFlushDraw=True,BotIsLastRaiser=True,randomhand=.29),'BetHalfPot')
        self.assertEqual(self.play('turn',HaveNutFlushDraw=True,BotIsLastRaiser=True,randomhand=.30),'Check')
        self.assertEqual(self.play('turn',AmountToCall=1.69,HaveNutFlushDraw=True),'Call')
        self.assertEqual(self.play('turn',AmountToCall=2,HaveNutFlushDraw=True),'Fold')

    def test_10_turn_value_and_price(self):
        self.assertEqual(self.play('turn',HaveFullHouse=True),'BetTwoThirdPot')
        self.assertEqual(self.play('turn',HaveTopPair=True,HaveBestKicker=True,BotIsLastRaiser=True),'BetHalfPot')
        self.assertEqual(self.play('turn',AmountToCall=2.73,HaveTopPair=True,HaveBestKicker=True),'Call')
        self.assertEqual(self.play('turn',AmountToCall=2.74,HaveTopPair=True,HaveBestKicker=True),'Fold')
        self.assertEqual(self.play('turn',AmountToCall=4,HaveSet=True),'Call')

    def test_11_river_value_and_price(self):
        self.assertEqual(self.play('river',HaveNuts=True),'BetTwoThirdPot')
        self.assertEqual(self.play('river',HaveSet=True),'BetHalfPot')
        self.assertEqual(self.play('river',HaveTopPair=True,HaveBestKicker=True),'BetThirdPot')
        self.assertEqual(self.play('river',AmountToCall=2,HaveNuts=True),'RaiseHalfPot')
        self.assertEqual(self.play('river',AmountToCall=6,HaveNuts=True),'Call')
        self.assertEqual(self.play('river',AmountToCall=2,HaveTwoPair=True),'Call')
        self.assertEqual(self.play('river',AmountToCall=5,HaveTwoPair=True),'Fold')
        self.assertEqual(self.play('river',AmountToCall=3,HaveTopPair=True,HaveBestKicker=True),'Fold')

    def test_12_completeness_of_covered_state_actions(self):
        for street in s.STREETS:
            for facing in (0,.1,1,3,6,9):
                for position in ('First','Last'):
                    for mode in (0,1):
                        o=s.observe(AmountToCall=facing,Position=position,
                            BotRaisedBeforeFlop=mode==0,BotCalledBeforeFlop=mode==1,
                            NumberOfRaisesBeforeFlop=mode)
                        self.assertIsNotNone(s.evaluate(self.model,street,o))

    def test_13_unavailable_symbol_is_not_silently_false(self):
        o=s.observe()
        del o['OpponentsOnFlop']
        with self.assertRaises(s.SourceError):s.evaluate(self.model,'flop',o)
        with self.assertRaises(s.SourceError):s.observe(NotARealSymbol=True)

    def test_14_reject_invalid_numbers_and_random(self):
        for k,bad in [('PotSize',0),('AmountToCall',-1),('randomhand',1),
                      ('randomhand',float('nan')),('OpponentsLeft','1')]:
            with self.subTest(key=k,value=bad),self.assertRaises(s.SourceError):
                self.play('flop',**{k:bad})

    def test_15_block_unsupported_oppl_syntax(self):
        src=s.SOURCE.read_text(encoding='utf-8')
        for old,new in [('BetThirdPot FORCE','RaiseTo 3 FORCE'),
                        ('WHEN Others RETURN FALSE FORCE','WHEN Others Fold FORCE'),
                        ('randomhand < 0.25','Random < 25'),
                        ('HaveTopPair AND','HaveSomething AND'),
                        ('f$SRPHU AND AmountToCall > 0','f$SRPHU OR AmountToCall > 0')]:
            self.assertIn(old,src)
            with self.subTest(new=new),self.assertRaises(s.SourceError):s.parse(src.replace(old,new,1))

    def test_16_no_unscoped_when_others_in_streets(self):
        for street in s.STREETS:
            rs=self.model.sections['f$'+street]
            self.assertFalse(any(rule.is_fallback for rule in rs))
            self.assertTrue(all('f$SRPHU' in rule.atoms or 'f$SRPHUOpen' in rule.atoms or
                                'f$SRPHUCaller' in rule.atoms for rule in rs))

    def test_17_same_hand_random_is_stable(self):
        context=s.observe(BotIsLastRaiser=True,randomhand=.179)
        self.assertEqual({s.evaluate(self.model,'flop',context) for _ in range(100)}, {'BetThirdPot'})

    def test_18_binary_identity_of_source_when_read(self):
        before={x:hashlib.sha256(x.read_bytes()).hexdigest() for x in (s.SOURCE,s.COMBINED)}
        for _ in range(3):s.parse_file()
        self.assertEqual(before,{x:hashlib.sha256(x.read_bytes()).hexdigest() for x in before})


if __name__=='__main__':unittest.main()
