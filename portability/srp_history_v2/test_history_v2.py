"""OpenPPL-only source parity across 36 reachable history signatures.
These are synthetic logic checks, not OH runtime verification or poker EV proofs.
"""
from __future__ import annotations
import sys,unittest,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/'srp_history_v1'))
import history_v2_interpreter as v
import history_interpreter as old
import build_history_v2 as builder

FLOP={
 'B':dict(BotRaisedOnFlop=True,OpponentCalledOnFlop=True,NoVillainBetOrRaisedOnFlop=True),
 'C':dict(NoBettingOnFlop=True,NoVillainBetOrRaisedOnFlop=True),
 'X':dict(BotCalledOnFlop=True),
 'R':dict(BotRaisedOnFlop=True,OpponentCalledOnFlop=True),
 'H':dict(BotRaisedOnFlop=True,OpponentCalledOnFlop=True,BotCheckedOnFlop=True),
 'M':dict(BotRaisedOnFlop=True,BotCalledOnFlop=True,NumberOfRaisesOnFlop=1),
}
TURN={
 'B':dict(BotRaisedOnTurn=True,OpponentCalledOnTurn=True,NoVillainBetOrRaisedOnTurn=True),
 'C':dict(NoBettingOnTurn=True,NoVillainBetOrRaisedOnTurn=True),
 'X':dict(BotCalledOnTurn=True),
 'R':dict(BotRaisedOnTurn=True,OpponentCalledOnTurn=True),
 'H':dict(BotRaisedOnTurn=True,OpponentCalledOnTurn=True,BotCheckedOnTurn=True),
 'M':dict(BotRaisedOnTurn=True,BotCalledOnTurn=True,NumberOfRaisesOnTurn=1),
}

class CompleteTreeExpansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new=v.parse_file();cls.baseline=old.parse_file()

    def observed(self, a=None,b=None,**overrides):
        s={}
        if a is not None:s.update(FLOP[a])
        if b is not None:s.update(TURN[b])
        s.update(overrides)
        return v.observe(**s)

    def play(self,street,a=None,b=None,**kwargs):
        return v.evaluate(self.new,street,self.observed(a,b,**kwargs))

    def test_01_all_36_histories_have_unique_helper(self):
        self.assertEqual(len(builder.CATS),6)
        for a in builder.CATS:
            for b in builder.CATS:
                with self.subTest(a=a,b=b):
                    obs=self.observed(a,b)
                    matches=[i+j for i in builder.CATS for j in builder.CATS
                             if v.evaluate(self.new,'river',obs,helper='f$HLPath2'+i+j)]
                    self.assertEqual(matches,[a+b])
                    self.assertTrue(v.evaluate(self.new,'river',obs,helper='f$HLRiverDomainV2'))
                    self.assertIsNotNone(v.evaluate(self.new,'river',obs))

    def test_02_new_3_flop_categories_are_exclusive(self):
        cases={'R':('f$HLFlopRaiseCall',),'H':('f$HLFlopCheckRaiseCall',),
               'M':('f$HLFlopBetRaisedCall',)}
        for key,expected in cases.items():
            flags=self.observed(key)
            names=('f$HLFlopRaiseCall','f$HLFlopCheckRaiseCall','f$HLFlopBetRaisedCall')
            self.assertEqual(tuple(x for x in names if v.evaluate(self.new,'turn',flags,helper=x)),expected)

    def test_03_new_3_turn_categories_are_exclusive(self):
        for key,name in {'R':'f$HLTurnRaiseCall','H':'f$HLTurnCheckRaiseCall',
                         'M':'f$HLTurnBetRaisedCall'}.items():
            flags=self.observed('C',key)
            names=('f$HLTurnRaiseCall','f$HLTurnCheckRaiseCall','f$HLTurnBetRaisedCall')
            self.assertEqual([x for x in names if v.evaluate(self.new,'river',flags,helper=x)],[name])

    def test_04_prior_v1_paths_match_exact_9x_actions(self):
        for a in 'BCX':
            for b in 'BCX':
                for call in (0,1.0,3.0):
                    newinput=self.observed(a,b,AmountToCall=call,HaveTopPair=True,HaveBestKicker=True)
                    oldinput={k:val for k,val in newinput.items() if k not in ('BotCheckedOnFlop','BotCheckedOnTurn')}
                    expected=old.evaluate(self.baseline,'river',oldinput)
                    self.assertEqual(v.evaluate(self.new,'river',newinput),expected,
                                     f'Baseline parity path {a}{b}, call {call}')

    def test_05_new_turn_made_hand_actions_depend_on_previous_flop(self):
        hand={'HaveTopPair':True,'HaveBestKicker':True}
        for a in 'RHM':
            self.assertEqual(self.play('turn',a,**hand),'Check')
        self.assertEqual(self.play('turn','C',**hand),'BetHalfPot')

    def test_06_flop_check_raise_draw_mixing_uses_randomhand(self):
        self.assertEqual(self.play('turn','H',HaveNutFlushDraw=True,randomhand=.15),'BetHalfPot')
        self.assertEqual(self.play('turn','H',HaveNutFlushDraw=True,randomhand=.45),'Check')
        self.assertEqual(self.play('turn','R',HaveNutFlushDraw=True,randomhand=.15),'BetHalfPot')

    def test_07_river_new_path_action_overrides_are_specific(self):
        base={'HaveTopPair':True,'HaveBestKicker':True}
        self.assertEqual(self.play('river','H','B',**base),'Check')
        self.assertEqual(self.play('river','H','C',**base),'BetThirdPot')
        self.assertEqual(self.play('river','M','C',**base),'Check')
        self.assertEqual(self.play('river','R','X',AmountToCall=1,**base),'Fold')
        self.assertEqual(self.play('river','X','M',AmountToCall=1,**base),'Fold')
        self.assertEqual(self.play('river','H','B',HaveNuts=True),'BetTwoThirdPot')

    def test_08_conflicting_raise_and_call_flags_rejected(self):
        self.assertIsNone(self.play('turn','R',BotCalledOnFlop=True))
        self.assertIsNone(self.play('turn','H',NumberOfRaisesOnFlop=1))
        self.assertIsNone(self.play('turn','M',BotCheckedOnFlop=True))
        self.assertIsNone(self.play('river','R','M',BotCheckedOnTurn=True))
        self.assertIsNone(self.play('river','C','R',NumberOfRaisesOnTurn=2))

    def test_09_unknown_line_does_not_silently_fold(self):
        self.assertIsNone(self.play('turn',AmountToCall=5,HaveTopPair=True))
        self.assertIsNone(self.play('river',AmountToCall=5,HaveTopPair=True))

    def test_10_earlier_preflop_bytes_preserved(self):
        pre=builder.PREFLOP.read_bytes().rstrip()
        combined=builder.COMBINED.read_bytes()
        self.assertTrue(combined.startswith(pre+b'\n\n'))
        self.assertEqual(combined[len(pre)+2:],builder.SOURCE.read_bytes())

    def test_11_original_flop_source_unchanged(self):
        baseline=builder.V1.read_text().split('##f$flop##')[1].split('##f$turn##')[0]
        current=builder.SOURCE.read_text().split('##f$flop##')[1].split('##f$turn##')[0]
        self.assertEqual(baseline.strip(),current.strip())
        self.assertEqual(self.play('flop',HaveNuts=True),'BetTwoThirdPot')

    def test_12_guards_never_emit_actions_outside_g3_domain(self):
        for street in ('turn','river'):
            for key,value in [('nplayersdealt',5),('OpponentsLeft',2),
                              ('NumberOfOpponentsAllin',1),('StackUnknown',True)]:
                with self.subTest(street=street,key=key):
                    self.assertIsNone(self.play(street,'H','M',**{key:value}))

    def test_13_source_rules_are_always_guarded_by_v2_domain(self):
        for street,domain in [('turn','f$HLTurnDomainV2'),('river','f$HLRiverDomainV2')]:
            self.assertTrue(all(rule.atoms[0]==domain for rule in self.new.sections['f$'+street]))
        self.assertEqual([len(self.new.sections['f$'+s]) for s in v.STREETS],[14,22,39])
        self.assertEqual(len(v.HELPERS),70)

    def test_14_no_runtime_python_randomness_or_unknown_fallback(self):
        src=builder.SOURCE.read_text()
        self.assertNotIn('Random <',src)
        self.assertNotIn('WHEN Others Fold FORCE',src)
        for invalid in ('WHEN Others Fold FORCE','Random < 30','UNSUPPORTEDSYMBOL'):
            with self.subTest(invalid=invalid),self.assertRaises(v.SourceError):
                v.parse(src.replace('BotCheckedOnFlop', invalid,1))

    def test_15_exact_36_csv_rows(self):
        import csv
        with builder.MATRIX.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),36)
        self.assertEqual({r['PathHelper'] for r in rows},
                         {'f$HLPath2'+a+b for a in builder.CATS for b in builder.CATS})

    def test_16_deterministic_generation_and_base_unchanged(self):
        files=(builder.V1,builder.PREFLOP,builder.OVERLAY,builder.SOURCE,builder.COMBINED,builder.MATRIX)
        original=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
        builder.assemble()
        self.assertEqual(original,[hashlib.sha256(p.read_bytes()).hexdigest() for p in files])

    def test_17_nonfinite_or_incomplete_observations_rejected(self):
        s=self.observed('H','R')
        del s['NoVillainBetOrRaisedOnTurn']
        with self.assertRaises(v.SourceError):v.evaluate(self.new,'river',s)
        with self.assertRaises(v.SourceError):self.play('river','H','R',randomhand=1.0)

    def test_18_stable_evaluation_no_duplicate_policy(self):
        s=self.observed('H','C',HaveTopPair=True,HaveBestKicker=True,randomhand=.1234)
        self.assertEqual({v.evaluate(self.new,'river',s) for _ in range(100)},{'BetThirdPot'})
        self.assertEqual(sum('##f$preflop##' in line for line in builder.COMBINED.read_text().splitlines()),1)

if __name__=='__main__':unittest.main()
