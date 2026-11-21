"""Limped BB source-only static regressions. No OpenHoldem runtime claim."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import limp_source_interpreter as p
import build_limp_bb as b

class LimpBB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m=p.parse_file()
    def action(self,street='flop',**kwargs):return p.evaluate(self.m,street,p.observe(**kwargs))

    def test_33_action_rules_4_helpers(self):
        self.assertEqual([len(self.m.rules[k]) for k in p.STREETS],[13,11,9])
        self.assertEqual(len(self.m.helpers),4)

    def test_sb_limp_ip_and_other_limp_oop(self):
        self.assertEqual(self.action(HaveTopPair=True,HaveBestKicker=True),'BetHalfPot')
        other={'user_H6_LimpSBIntent':False,'user_H6_LimpOtherIntent':True,
               'Position':'First'}
        self.assertEqual(self.action(**other),'Check')
        self.assertEqual(self.action(HaveTopPair=True,HaveBestKicker=True,**other),'Check')
        self.assertEqual(self.action(HaveTwoPair=True,**other),'BetHalfPot')

    def test_very_large_bet_nuts_never_folds(self):
        for street in p.STREETS:
            self.assertEqual(self.action(street,HaveNuts=True,AmountToCall=110),'Call')

    def test_priced_nuts_raise_and_value_bet(self):
        for street in p.STREETS:
            self.assertEqual(self.action(street,HaveNuts=True,AmountToCall=1),'RaiseHalfPot')
            self.assertEqual(self.action(street,HaveNuts=True),'BetTwoThirdPot')

    def test_top_pair_moderate_defense_vs_weak_blind_attack(self):
        d={'HaveTopPair':True,'HaveBestKicker':True}
        self.assertEqual(self.action(AmountToCall=2.25,**d),'Call')
        self.assertEqual(self.action(AmountToCall=2.26,**d),'Fold')
        self.assertEqual(self.action('turn',AmountToCall=1.75,**d),'Call')
        self.assertEqual(self.action('turn',AmountToCall=1.76,**d),'Fold')

    def test_flush_draw_price_boundaries(self):
        self.assertEqual(self.action(HaveNutFlushDraw=True,AmountToCall=1.75),'Call')
        self.assertEqual(self.action(HaveNutFlushDraw=True,AmountToCall=1.76),'Fold')

    def test_sb_limp_mix_stable_with_randomhand(self):
        d={'HaveNutFlushDraw':True,'Position':'Last'}
        for _ in range(6):
            self.assertEqual(self.action(randomhand=.349,**d),'BetThirdPot')
            self.assertEqual(self.action(randomhand=.35,**d),'Check')
        self.assertEqual(self.action(randomhand=.01,user_H6_LimpSBIntent=False,
                                     user_H6_LimpOtherIntent=True,**d),'Check')

    def test_no_unconditional_or_malicious_fallback(self):
        s=p.POLICY.read_text()
        for change in ('\nWHEN Others Fold FORCE','\nWHEN (AmountToCall > 0) Call FORCE'):
            with self.assertRaises(p.SourceError):p.parse(s+change)
        with self.assertRaises(p.SourceError):p.parse(s.replace('randomhand < 0.35','randomhand < 0.95'))

    def test_conflicting_or_unknown_intent_rejected(self):
        self.assertIsNone(self.action(user_H6_LimpOtherIntent=True))
        self.assertIsNone(self.action(user_H6_LimpSBIntent=False))
        self.assertIsNone(self.action(BotCheckedPreflop=False))
        self.assertIsNone(self.action(user_H6_RFIIntent=True))
        self.assertIsNone(self.action(user_H6_3betIntent=True))
        self.assertIsNone(self.action(user_H6_VSOpenCallIntent=True))

    def test_not_confused_with_srp_hu_3bet_or_multiway(self):
        self.assertIsNone(self.action(BotRaisedBeforeFlop=True))
        self.assertIsNone(self.action(BotCalledBeforeFlop=True))
        self.assertIsNone(self.action(NumberOfRaisesBeforeFlop=1))
        for left in (0,2,3,4,5):
            self.assertIsNone(self.action(OpponentsLeft=left))
        for initial in (2,3,4,5):
            self.assertIsNone(self.action(OpponentsOnFlop=initial))

    def test_lost_history_and_all_in_not_admitted(self):
        self.assertIsNone(self.action(StackUnknown=True))
        self.assertIsNone(self.action(NumberOfOpponentsAllin=1))
        self.assertIsNone(self.action(nplayersdealt=5))

    def test_dont_auto_bet_weak_river(self):
        self.assertEqual(self.action('river'),'Check')
        self.assertEqual(self.action('river',AmountToCall=2),'Fold')
        self.assertEqual(self.action('river',HaveTwoPair=True),'BetHalfPot')

    def test_preflop_option_is_check_not_call_or_raise(self):
        src=b.CHECK.read_text(encoding='utf-8')
        lines=[x for x in src.splitlines() if x.startswith('WHEN ')]
        self.assertEqual(len(lines),4)
        self.assertTrue(all('InBigBlind' in x and 'Calls = 1' in x and 'Raises = 0' in x for x in lines))
        self.assertTrue(all('StillToAct = 0' in x for x in lines))
        self.assertEqual(sum(' Check FORCE' in x for x in lines),2)
        self.assertEqual(sum(' Set user_H6_Limp' in x for x in lines),2)
        self.assertTrue(any('PotSize = 2)' in x for x in lines))
        self.assertTrue(any('PotSize = 2.5)' in x for x in lines))

    def test_parent_when_actions_preserved_in_integrated_file(self):
        old=b.PREV.read_text()
        new=b.COMBINED.read_text()
        # Existing branches stay ordered and text-identical; new BB-check branches add coverage.
        oldlines=[x for x in old.splitlines() if x.startswith('WHEN ')]
        newlines=[x for x in new.splitlines() if x.startswith('WHEN ')]
        i=0
        for line in oldlines:
            while i<len(newlines) and newlines[i]!=line:i+=1
            self.assertLess(i,len(newlines),line[:60])
            i+=1

    def test_integrated_has_single_street_and_original_3way_helpers(self):
        s=b.COMBINED.read_text()
        for street in ('preflop','flop','turn','river'):
            self.assertEqual(s.count(f'##f${street}##'),1)
        self.assertEqual(s.count('##f$H6ThreeWaySRP##'),1)
        self.assertEqual(s.count('##f$H6CrowdedSRP##'),1)
        self.assertEqual(s.count('##f$H6TransitionHU##'),1)
        self.assertEqual(s.count('##f$H6LimpBBHU##'),1)

    def test_inputs_malformed_rejected(self):
        for kwargs in ({'AmountToCall':float('nan')},{'PotSize':0},{'randomhand':1},
                       {'Position':'not_valid'},{'BotCheckedPreflop':1}):
            with self.assertRaises(p.SourceError):self.action(**kwargs)

    def test_output_deterministic_no_parent_modified(self):
        paths=(b.CHECK,b.COMBINED,b.PREV)
        before=[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths]
        self.assertEqual(b.build(),(2,33))
        self.assertEqual(before,[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths])

if __name__=='__main__':unittest.main()
