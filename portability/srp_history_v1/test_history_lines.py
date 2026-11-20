"""Pragmatic OpenPPL source tests; all actions originate in authored OPPL.
No solver, no money, and NO OpenHoldem executable is exercised by this module.
"""
from __future__ import annotations
import hashlib
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import history_interpreter as h
import build_history as build

FLOP={
 'B':{'BotRaisedOnFlop':True,'OpponentCalledOnFlop':True,
      'NoVillainBetOrRaisedOnFlop':True,'NoBettingOnFlop':False},
 'C':{'NoBettingOnFlop':True,'NoVillainBetOrRaisedOnFlop':True},
 'X':{'BotCalledOnFlop':True,'NoVillainBetOrRaisedOnFlop':False,'NoBettingOnFlop':False},
}
TURN={
 'B':{'BotRaisedOnTurn':True,'OpponentCalledOnTurn':True,
      'NoVillainBetOrRaisedOnTurn':True,'NoBettingOnTurn':False},
 'C':{'NoBettingOnTurn':True,'NoVillainBetOrRaisedOnTurn':True},
 'X':{'BotCalledOnTurn':True,'NoVillainBetOrRaisedOnTurn':False,'NoBettingOnTurn':False},
}

class HistoricalTrees(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=h.parse_file()

    def play(self, street, flop=None, turn=None, **kwargs):
        props={}
        if flop is not None:props.update(FLOP[flop])
        if turn is not None:props.update(TURN[turn])
        props.update(kwargs)
        return h.evaluate(self.model,street,h.observe(**props))

    def test_01_composition_preserves_three_streets_preflop(self):
        p=build.PREFLOP.read_bytes().rstrip()
        combo=h.COMBINED.read_bytes()
        self.assertEqual(combo[:len(p)+2],p+b'\n\n')
        self.assertEqual(combo[len(p)+2:],h.SOURCE.read_bytes())
        self.assertEqual(combo.count(b'##f$preflop##'),1)
        for street in h.STREETS:
            self.assertEqual(combo.count(f'##f${street}##'.encode()),1)

    def test_02_all_9_two_street_paths(self):
        self.assertEqual(len(h.HELPERS),24)
        self.assertEqual([len(self.model.sections['f$'+x]) for x in h.STREETS], [14,16,28])
        expected={'BB':'Check','BC':'BetThirdPot','BX':'Check',
                  'CB':'Check','CC':'BetThirdPot','CX':'Check',
                  'XB':'Check','XC':'BetThirdPot','XX':'Check'}
        for key,action in expected.items():
            with self.subTest(path=key):
                self.assertEqual(self.play('river',key[0],key[1],
                            HaveTopPair=True,HaveBestKicker=True,randomhand=.90),action)

    def test_03_flop_source_actions_unchanged(self):
        base=build.BASE.read_text(encoding='utf-8').split('##f$flop##')[1].split('##f$turn##')[0].strip()
        current=h.SOURCE.read_text(encoding='utf-8').split('##f$flop##')[1].split('##f$turn##')[0].strip()
        self.assertEqual(base,current)
        self.assertEqual(self.play('flop',HaveNuts=True),'BetTwoThirdPot')
        self.assertEqual(self.play('flop',AmountToCall=2,HaveFlushDraw=True),'Fold')

    def test_04_new_turn_delayed_value_stabs(self):
        self.assertEqual(self.play('turn','C',HaveTopPair=True,HaveBestKicker=True),'BetHalfPot')
        self.assertEqual(self.play('turn','X',HaveTopPair=True,HaveBestKicker=True),'Check')
        self.assertEqual(self.play('turn','B',HaveTopPair=True,HaveBestKicker=True,randomhand=.5),'BetHalfPot')

    def test_05_nut_draw_stable_mixes(self):
        for x,want in ((.0,'BetHalfPot'),(.3999,'BetHalfPot'),(.40,'Check'),(.999,'Check')):
            with self.subTest(randomhand=x):
                self.assertEqual(self.play('turn','B',HaveNutFlushDraw=True,randomhand=x),want)
        o=h.observe(**FLOP['B'],HaveNutFlushDraw=True,randomhand=.123)
        self.assertEqual({h.evaluate(self.model,'turn',o) for _ in range(100)}, {'BetHalfPot'})

    def test_06_no_story_no_turn_or_river_action(self):
        self.assertIsNone(self.play('turn',HaveNuts=True))
        self.assertIsNone(self.play('river',flop='C',HaveNuts=True))
        self.assertIsNone(self.play('river',turn='C',HaveNuts=True))

    def test_07_cbet_versus_flop_raise_not_confused(self):
        # Bet-and-call contains no opponent flop bet or raise; if villain bet and
        # hero raised, the same BotRaisedOnFlop must NOT become our cbet path.
        raised={'BotRaisedOnFlop':True,'OpponentCalledOnFlop':True,
                'NoVillainBetOrRaisedOnFlop':False}
        self.assertIsNone(self.play('turn',**raised))
        self.assertIsNone(self.play('river',turn='C',**raised))

    def test_08_multiple_actions_are_not_misclassified(self):
        self.assertIsNone(self.play('turn',flop='B',BotCalledOnFlop=True))
        self.assertIsNone(self.play('river',flop='C',turn='B',BotCalledOnTurn=True))
        self.assertIsNone(self.play('turn',flop='C',NumberOfRaisesOnFlop=1))
        self.assertIsNone(self.play('turn',flop='C',OpponentCalledOnFlop=True))
        self.assertIsNone(self.play('river',flop='C',turn='C',OpponentCalledOnTurn=True))
        self.assertIsNone(self.play('river',flop='C',turn='C',NumberOfRaisesOnTurn=1))

    def test_09_new_line_pricing_is_not_global(self):
        self.assertEqual(self.play('river','B','C',AmountToCall=1,HaveTopPair=True,HaveBestKicker=True),'Call')
        self.assertEqual(self.play('river','B','C',AmountToCall=2,HaveTopPair=True,HaveBestKicker=True),'Fold')
        self.assertEqual(self.play('river','X','X',AmountToCall=.5,HaveTopPair=True,HaveBestKicker=True),'Fold')
        self.assertEqual(self.play('river','C','C',AmountToCall=0,HaveTopPair=True,HaveBestKicker=True),'BetThirdPot')

    def test_10_strong_hands_have_priority_over_top_pair_shortcuts(self):
        for f in FLOP:
            for t in TURN:
                with self.subTest(f=f,t=t):
                    self.assertNotEqual(self.play('river',f,t,HaveNuts=True,HaveTopPair=True,
                                   HaveBestKicker=True), 'Check')
                    self.assertNotEqual(self.play('river',f,t,HaveNuts=True,HaveTopPair=True,
                                   HaveBestKicker=True,AmountToCall=1), 'Fold')

    def test_11_all_postflop_actions_require_known_domain_except_flop(self):
        for st,flag in [('turn','f$HLTurnDomain'),('river','f$HLRiverDomain')]:
            self.assertTrue(all(r.atoms[0]==flag for r in self.model.sections['f$'+st]))
            self.assertIsNone(self.play(st,nplayersdealt=5,flop='B',turn='C'))
            self.assertIsNone(self.play(st,flop='B',turn='C',OpponentsLeft=2))

    def test_12_open_and_caller_preflop_modes_both_remain(self):
        c={'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,'NumberOfRaisesBeforeFlop':1}
        self.assertEqual(self.play('turn','C',**c),'Check')
        self.assertEqual(self.play('river','C','C',**c),'Check')
        self.assertIsNone(self.play('river','C','C',BotRaisedBeforeFlop=True,
                                    BotCalledBeforeFlop=True,NumberOfRaisesBeforeFlop=1))

    def test_13_reject_unexpected_source_syntax(self):
        src=h.SOURCE.read_text(encoding='utf-8')
        for old,new in [('NoVillainBetOrRaisedOnFlop','UnfoundedOpponentPosition'),
                        ('randomhand < 0.40','Random < 40'),
                        ('f$HLFlopBetCall AND','f$HLFlopBetCall OR'),
                        ('WHEN Others RETURN FALSE FORCE','WHEN Others Fold FORCE')]:
            with self.subTest(old=old),self.assertRaises(h.SourceError):h.parse(src.replace(old,new,1))

    def test_14_observations_must_be_explicit_and_finite(self):
        obs=h.observe(**FLOP['B'])
        del obs['BotRaisedOnFlop']
        with self.assertRaises(h.SourceError):h.evaluate(self.model,'turn',obs)
        with self.assertRaises(h.SourceError):self.play('turn','B',NumberOfRaisesOnFlop=float('nan'))

    def test_15_build_is_deterministic_without_editing_ancestor(self):
        sources=(build.BASE,build.PREFLOP,build.OVERLAY,build.OUT,build.COMBINED)
        first=[hashlib.sha256(p.read_bytes()).hexdigest() for p in sources]
        build.assemble()
        self.assertEqual(first,[hashlib.sha256(p.read_bytes()).hexdigest() for p in sources])

    def test_16_original_g3_baseline_hashes_unchanged(self):
        self.assertIn('WHEN (f$SRPHU AND AmountToCall > 0) Fold FORCE',build.BASE.read_text())
        self.assertIn('WHEN (f$HLRiverDomain AND f$SRPHU AND AmountToCall > 0) Fold FORCE',h.SOURCE.read_text())

    def test_17_invalid_history_cannot_default_to_synthetically_safe_fold(self):
        self.assertIsNone(self.play('river',AmountToCall=9))
        self.assertIsNone(self.play('turn',AmountToCall=9))
        # Python None remains unsafe in OH runtime: never claim fallback safety.

    def test_18_each_new_path_is_unique_in_the_oppl_text(self):
        src=h.SOURCE.read_text(encoding='utf-8')
        for a in 'BCX':
            for b in 'BCX':
                self.assertEqual(src.count('##f$HLPath'+a+b+'##'),1)
        self.assertFalse(any('WHEN Others Fold FORCE' in x for x in src.splitlines()))

if __name__=='__main__':unittest.main()
