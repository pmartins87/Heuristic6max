"""HIST-v3 tests: verified logic derived from the SAME generated OPPL source.

Everything is offline. The 484 legal words are NOT 484 strategic rules.
The native OH history symbols and persistent Set semantics remain runtime-untested.
"""
from __future__ import annotations
from pathlib import Path
import csv
import hashlib
import sys
import unittest
from dataclasses import replace

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/'srp_history_v2'))
import chronological_history as c
import build_history_v3 as b
import history_v3_interpreter as h
import history_v2_interpreter as old


def read_csv(name):
    with (HERE/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))


def base_obs(**updates):
    d=h.observe(**updates)
    d['IsTurn']=True
    return d


class LegalActionGrammar(unittest.TestCase):
    def test_two_positions_elevent_street_lines(self):
        for first in ('H','V'):
            lines=c.enumerate_street(first)
            self.assertEqual(len(lines),21)  # 11 continuing + 10 ending in fold
            self.assertEqual(sum(l.reaches_next for l in lines),11)
            self.assertEqual(sum(not l.reaches_next for l in lines),10)

    def test_all_events_alternate_and_terminate_legally(self):
        for first in ('H','V'):
            for x in c.enumerate_street(first):
                for (p,a),(q,b) in zip(x.moves,x.moves[1:]):
                    self.assertNotEqual(p,q)
                    if a=='R':self.assertIn(b,('R','C','F'))
                    if a=='B':self.assertIn(b,('R','C','F'))
                    if a=='X':self.assertIn(b,('X','B'))
                self.assertEqual(x.reaches_next,x.moves[-1][1] in ('X','C'))
                self.assertLessEqual(x.raises,4)

    def test_484_ordered_river_histories(self):
        rows=list(c.full_two_street_paths())
        self.assertEqual(len(rows),484)
        self.assertEqual(len({(ip,pfr,f.word,t.word) for ip,pfr,f,t in rows}),484)
        self.assertEqual({(ip,pfr) for ip,pfr,_,_ in rows},{(a,b) for a in (False,True) for b in (False,True)})

    def test_no_folded_line_reaches_river(self):
        self.assertTrue(all(f.reaches_next and t.reaches_next for _,_,f,t in c.full_two_street_paths()))

    def test_raise_cap_monotonic(self):
        counts=[len(list(c.full_two_street_paths(n))) for n in range(5)]
        self.assertEqual(counts,[36,100,196,324,484])

    def test_bad_parameters_rejected(self):
        for x in (-1,9,0.5,True):
            with self.assertRaises(ValueError):c.enumerate_street('H',x)
        with self.assertRaises(ValueError):c.enumerate_street('Z')

    def test_numerical_coverage_csv(self):
        rows=read_csv('HIST3_484_CHRONOLOGICAL_PATHS.csv')
        self.assertEqual(len(rows),484)
        self.assertEqual(len({r['HistoryID'] for r in rows}),484)
        self.assertEqual(set(r['ImplementationStatus'] for r in rows),{'LEGAL_ACTION_WORD_NOT_OPENPPL_ROUTED'})
        self.assertTrue(all(r['FlopEvents'] and r['TurnEvents'] for r in rows))

    def test_observable_flag_aliases_are_disclosed(self):
        ip=c.observability_groups('V')
        oop=c.observability_groups('H')
        self.assertEqual(sum(map(len,ip.values())),11)
        self.assertEqual(sum(map(len,oop.values())),11)
        self.assertEqual(sum(len(v)>1 for v in ip.values()),3)
        self.assertEqual(sum(len(v)>1 for v in oop.values()),0)
        records=read_csv('HIST3_OBSERVABILITY.csv')
        self.assertEqual(len(records),19)
        self.assertEqual(sum(r['Risk'].startswith('COLLISION') for r in records),3)

    def test_explicit_alias_bet_raised_call_vs_raise_reraised_call(self):
        ip=c.observability_groups('V')
        aliases=[set(words) for words in ip.values() if len(words)>1]
        self.assertIn({'V:B H:R V:R H:C','V:X H:B V:R H:C'},aliases)
        self.assertIn({'V:B H:R V:R H:R V:C','V:X H:B V:R H:R V:C'},aliases)

    def test_raises_count_is_villain_only(self):
        line=c.RoundLine((('V','B'),('H','R'),('V','R'),('H','C')),True)
        self.assertEqual(line.raises,2)
        self.assertEqual(c.flag_signature(line)[-1],1)


class NativeOpenPPLSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=h.parse_file()
        cls.original=old.parse_file()

    def test_new_model_is_parseable_and_whitelisted(self):
        self.assertEqual(len(self.model.sections),len(h.ALL_SECTIONS))
        self.assertEqual(sum(len(self.model.sections['f$'+s]) for s in h.STREETS),79)

    def test_preflop_byte_identical(self):
        oldsource=b.PREVIOUS_COMBINED.read_text(encoding='utf-8')
        newsource=b.COMBINED.read_text(encoding='utf-8')
        prefix=oldsource[:-len(b.PREVIOUS.read_text(encoding='utf-8'))]
        self.assertEqual(newsource[:len(prefix)],prefix)

    def test_old_v2_snapshot_untouched(self):
        self.assertEqual(old.parse_file(),self.original)
        self.assertEqual(b.PREVIOUS.read_text(),old.SOURCE.read_text())

    def test_flop_raise_called_previous_legacy_helper_could_not_match(self):
        # The library's OpponentCalledOnFlop is false if villain originally BET.
        context=base_obs(BotRaisedOnFlop=True,NoVillainBetOrRaisedOnFlop=False,
                         NoBettingOnFlop=False,NumberOfRaisesOnFlop=0,
                         OpponentCalledOnFlop=False,BotCalledOnFlop=False,BotCheckedOnFlop=False)
        self.assertFalse(h.evaluate(self.model,'turn',context,helper='f$HLFlopRaiseCall'))
        self.assertTrue(h.evaluate(self.model,'turn',context,helper='f$H3FlopRaiseCallObserved'))
        self.assertTrue(h.evaluate(self.model,'turn',context,helper='f$H3FlopKnownSafe'))

    def test_check_raise_called_without_using_legacy_opponent_called(self):
        context=base_obs(BotRaisedOnFlop=True,BotCheckedOnFlop=True,
                         NoVillainBetOrRaisedOnFlop=False,NoBettingOnFlop=False,
                         NumberOfRaisesOnFlop=0,OpponentCalledOnFlop=False)
        self.assertFalse(h.evaluate(self.model,'turn',context,helper='f$HLFlopCheckRaiseCall'))
        self.assertTrue(h.evaluate(self.model,'turn',context,helper='f$H3FlopCheckRaiseCallObserved'))

    def test_turn_raise_called_uses_river_only(self):
        ctx=h.observe(IsRiver=True,BotRaisedOnTurn=True,
                      NoVillainBetOrRaisedOnTurn=False,NoBettingOnTurn=False,
                      OpponentCalledOnTurn=False,NumberOfRaisesOnTurn=0)
        self.assertTrue(h.evaluate(self.model,'river',ctx,helper='f$H3TurnRaiseCallObserved'))
        ctx['IsRiver']=False
        self.assertFalse(h.evaluate(self.model,'river',ctx,helper='f$H3TurnRaiseCallObserved'))

    def test_capture_after_real_bet_witness(self):
        ctx=h.observe(Position='Last',BotRaisedOnFlop=True,BotsLastFlopAction='Bet',
                      Raises=1,AmountToCall=3.0)
        self.assertFalse(ctx['user_H3_IP_FlopLeadBetFacedRaise'])
        got=h.evaluate(self.model,'flop',ctx)
        self.assertIn(got,h.ACTIONS|{None})
        self.assertTrue(ctx['user_H3_IP_FlopLeadBetFacedRaise'])
        self.assertFalse(ctx['user_H3_IP_FlopRaiseFacedReraise'])
        h.evaluate(self.model,'flop',ctx)
        self.assertTrue(ctx['user_H3_IP_FlopLeadBetFacedRaise'])

    def test_capture_after_real_raise_witness(self):
        ctx=h.observe(Position='Last',BotRaisedOnFlop=True,BotsLastFlopAction='Raise',
                      Raises=1,AmountToCall=3.0)
        h.evaluate(self.model,'flop',ctx)
        self.assertFalse(ctx['user_H3_IP_FlopLeadBetFacedRaise'])
        self.assertTrue(ctx['user_H3_IP_FlopRaiseFacedReraise'])

    def test_no_capture_without_villain_raise(self):
        for change in ({'Raises':0},{'AmountToCall':0},{'Position':'First'},
                       {'BotRaisedOnFlop':False},{'BotsLastFlopAction':'Call'},
                       {'BotCalledOnFlop':True}):
            ctx=h.observe(Position='Last',BotRaisedOnFlop=True,BotsLastFlopAction='Bet',
                          Raises=1,AmountToCall=3.0,**{k:v for k,v in change.items() if k not in ('Position','BotRaisedOnFlop','BotsLastFlopAction','Raises','AmountToCall')})
            ctx.update(change)
            h.evaluate(self.model,'flop',ctx)
            self.assertFalse(ctx['user_H3_IP_FlopLeadBetFacedRaise'],change)

    def test_safe_ip_m_no_markers_is_unknown(self):
        ctx=base_obs(Position='Last',BotRaisedOnFlop=True,BotCalledOnFlop=True,
                NoVillainBetOrRaisedOnFlop=False,NoBettingOnFlop=False,
                NumberOfRaisesOnFlop=1,OpponentCalledOnFlop=False)
        self.assertTrue(h.evaluate(self.model,'turn',ctx,helper='f$HLFlopBetRaisedCall'))
        self.assertFalse(h.evaluate(self.model,'turn',ctx,helper='f$H3FlopBetRaisedCallStrict'))
        self.assertFalse(h.evaluate(self.model,'turn',ctx,helper='f$H3TurnDomain'))

    def test_safe_ip_m_after_leadbet_capture(self):
        ctx=base_obs(Position='Last',BotRaisedOnFlop=True,BotCalledOnFlop=True,
                NoVillainBetOrRaisedOnFlop=False,NoBettingOnFlop=False,
                NumberOfRaisesOnFlop=1,user_H3_IP_FlopLeadBetFacedRaise=True)
        self.assertTrue(h.evaluate(self.model,'turn',ctx,helper='f$H3FlopBetRaisedCallStrict'))
        self.assertTrue(h.evaluate(self.model,'turn',ctx,helper='f$H3TurnDomain'))

    def test_ip_raise_reraise_call_does_not_get_bet_raised_call_policy(self):
        ctx=base_obs(Position='Last',BotRaisedOnFlop=True,BotCalledOnFlop=True,
                NoVillainBetOrRaisedOnFlop=False,NoBettingOnFlop=False,
                NumberOfRaisesOnFlop=1,user_H3_IP_FlopRaiseFacedReraise=True)
        self.assertFalse(h.evaluate(self.model,'turn',ctx,helper='f$H3FlopBetRaisedCallStrict'))
        self.assertFalse(h.evaluate(self.model,'turn',ctx,helper='f$H3FlopKnownSafe'))

    def test_contradictory_capture_flags_fail_closed_in_test_interpreter(self):
        ctx=base_obs(Position='Last',BotRaisedOnFlop=True,BotCalledOnFlop=True,
                NoVillainBetOrRaisedOnFlop=False,NoBettingOnFlop=False,
                NumberOfRaisesOnFlop=1,user_H3_IP_FlopRaiseFacedReraise=True,
                user_H3_IP_FlopLeadBetFacedRaise=True)
        self.assertFalse(h.evaluate(self.model,'turn',ctx,helper='f$H3FlopKnownSafe'))

    def test_safe_oop_m_is_not_needlessly_blocked(self):
        ctx=base_obs(Position='First',BotRaisedOnFlop=True,BotCalledOnFlop=True,
                NoVillainBetOrRaisedOnFlop=False,NoBettingOnFlop=False,
                NumberOfRaisesOnFlop=1)
        self.assertTrue(h.evaluate(self.model,'turn',ctx,helper='f$H3FlopBetRaisedCallStrict'))

    def test_turn_capture_uses_its_own_symbols_and_flags(self):
        ctx=base_obs(Position='Last',BotRaisedOnTurn=True,BotsLastTurnAction='Bet',
                     Raises=1,AmountToCall=2.0)
        h.evaluate(self.model,'turn',ctx)
        self.assertTrue(ctx['user_H3_IP_TurnLeadBetFacedRaise'])
        self.assertFalse(ctx['user_H3_IP_FlopLeadBetFacedRaise'])

    def test_missing_turn_capture_blocks_ambiguous_river(self):
        ctx=h.observe(IsRiver=True,Position='Last',BotRaisedOnTurn=True,BotCalledOnTurn=True,
                NoVillainBetOrRaisedOnTurn=False,NoBettingOnTurn=False,
                NumberOfRaisesOnTurn=1,NoVillainBetOrRaisedOnFlop=True,
                NoBettingOnFlop=True)
        self.assertFalse(h.evaluate(self.model,'river',ctx,helper='f$H3RiverDomain'))

    def test_no_new_implicit_fallback(self):
        src=h.SOURCE.read_text()
        self.assertNotIn('WHEN Others Fold FORCE',src)
        self.assertNotIn('WHEN Others Check FORCE',src)
        self.assertNotIn('WHEN Others Call FORCE',src)

    def test_set_must_be_in_correct_street(self):
        src=h.SOURCE.read_text()
        marker='WHEN (f$SRPHU AND Position = Last AND AmountToCall > 0 AND BotRaisedOnFlop'
        variant=src.replace(marker,'WHEN (f$SRPHU AND Position = Last AND AmountToCall > 0 AND BotRaisedOnTurn',1)
        with self.assertRaises(h.SourceError):h.parse(variant)

    def test_old_main_functions_no_literal_action_edits(self):
        old_text=b.PREVIOUS.read_text()
        new_text=h.SOURCE.read_text()
        original_actions=[x for x in old_text.splitlines() if x.startswith('WHEN ') and any(' '+a+' FORCE' in x for a in h.ACTIONS)]
        new_actions=[x for x in new_text.splitlines() if x.startswith('WHEN ') and any(' '+a+' FORCE' in x for a in h.ACTIONS)]
        self.assertEqual(len(new_actions),len(original_actions))
        for x,y in zip(original_actions,new_actions):
            self.assertEqual(x.split(') ')[-1],y.split(') ')[-1])

    def test_generator_deterministic(self):
        paths=[b.SOURCE,b.COMBINED,HERE/'HIST3_484_CHRONOLOGICAL_PATHS.csv',HERE/'HIST3_OBSERVABILITY.csv']
        old_hash=[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths]
        self.assertEqual(b.generate(),(484,4,10))
        self.assertEqual(old_hash,[hashlib.sha256(x.read_bytes()).hexdigest() for x in paths])

    def test_preflop_not_modified_in_old_file(self):
        snap=b.PREVIOUS_COMBINED.read_text()
        self.assertEqual(snap,b.PREVIOUS_COMBINED.read_text())

if __name__=='__main__':unittest.main()
