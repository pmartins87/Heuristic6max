"""Practical regression suite; OPPL text is the ONLY proposed decision source.

No test here runs OpenHoldem. The original Python v0.6.1 model is a fixed
reference for comparison, never a second implementation in the bot runtime.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import replace
from pathlib import Path
import csv, hashlib, sys, unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'gto6_heuristic_v0_6_1'))
from portability.vs_3bet_mvp import vs3_source_interpreter as p
import portability.vs_3bet_mvp.generate_vs3_mvp as compiler
from vs_3bet_reference import RANGES, SPECS, threebet_to_bb, fourbet_to_bb, expected_pot_bb
from rfi_reference import RANGES as RFI_RANGES
from scenario_contract import Position

class VS3MVP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=p.parse_file()

    @staticmethod
    def expected(op,bt,hand,randomhand):
        row=RANGES[op,bt][hand]
        if row.open_probability<=0:return None
        if randomhand<row.fourbet:return ('4BET',fourbet_to_bb(op,bt))
        if randomhand<row.fourbet+row.call:return ('CALL',None)
        return ('FOLD',None)

    def test_full_2535_by_16_thresholds(self):
        rs=(0,.10,.24999,.25,.29999,.30,.34999,.35,.5,.54999,.55,.59999,.60,.64999,.65,.999999)
        count=0
        for op,bt in p.PAIRS:
            for hand in sorted(p.HANDS):
                for rnd in rs:
                    got=p.evaluate(self.model,p.observed(op,bt,hand,rnd))
                    expected=self.expected(op,bt,hand,rnd)
                    self.assertEqual(got,expected,(op,bt,hand,rnd))
                    count+=1
        self.assertEqual(count,2535*16)

    def test_15_pairs_all_source_tree(self):
        self.assertEqual(len(p.PAIRS),15)
        self.assertEqual(len(self.model.lists),90)
        self.assertEqual(len(self.model.rules),135)
        self.assertEqual({r.pair for r in self.model.rules},set(RANGES))

    def test_reachability_cannot_silently_fold(self):
        counts=Counter()
        for pair in p.PAIRS:
            union=set()
            for name,hands in self.model.lists.items():
                m=p.LIST_RE.fullmatch('##'+name+'##')
                if (m[2],m[3])==pair:union.update(hands)
            truth={h for h,row in RANGES[pair].items() if row.open_probability>0}
            self.assertEqual(union,truth)
            counts['reachable']+=len(union)
            counts['not_reachable']+=len(p.HANDS)-len(union)
            for hand in p.HANDS-union:
                self.assertIsNone(p.evaluate(self.model,p.observed(*pair,hand,.5)))
        self.assertEqual(counts,Counter(reachable=888,not_reachable=1647))

    def test_sizing_both_raise_to_and_3bet_to_fixed(self):
        for pair in p.PAIRS:
            self.assertAlmostEqual(p.expected_3bet_to(*pair),threebet_to_bb(*pair))
            self.assertAlmostEqual(p.expected_4bet_to(*pair),fourbet_to_bb(*pair))
            self.assertAlmostEqual(p.expected_pot(*pair),expected_pot_bb(*pair))
            s=p.observed(*pair,'AA',.5)
            self.assertEqual(p.evaluate(self.model,s),('4BET',fourbet_to_bb(*pair)))
            self.assertEqual(s.amount_to_call_bb,threebet_to_bb(*pair)-(3. if pair[0]=='SB' else 2.5))

    def test_openppl_raises_counts_only_villains(self):
        src=p.SOURCE.read_text(encoding='utf-8')
        self.assertIn('Raises = 1',src)
        self.assertIn('RaisesSinceLastPlay = 1',src)
        self.assertIn('BotRaisedBeforeFlop',src)
        self.assertNotIn('Raises = 2',src)
        for pair in p.PAIRS:
            s=p.observed(*pair,'AA',.5)
            self.assertEqual(p.evaluate(self.model,replace(s,raises=2)),None)
            self.assertEqual(p.evaluate(self.model,replace(s,raises_since_last_play=0)),None)
            self.assertEqual(p.evaluate(self.model,replace(s,bot_raised_before_flop=False)),None)

    def test_negative_guards_on_all_15_pairs(self):
        fields=(('is_preflop',False),('nplayersdealt',5),('nplayersdealt',7),
            ('raises',0),('raises',2),('raises_since_last_play',0),('calls',1),
            ('bot_raised_before_flop',False),('first_raiser_position',-1),
            ('last_raiser_position',-1),('pot_bb',-1),('amount_to_call_bb',-1),
            ('stack_unknown',True),('stack_at_round_start_bb',94.99),
            ('stack_at_round_start_bb',105.01),('min_opponent_stack_bb',94.99),
            ('max_opponent_stack_bb',105.01),('min_opponent_stack_bb',120),
            ('max_opponent_stack_bb',80))
        for pair in p.PAIRS:
            s=p.observed(*pair,'AA',.5)
            for field,value in fields:
                self.assertIsNone(p.evaluate(self.model,replace(s,**{field:value})),(pair,field))

    def test_guard_numbers_different_3bet_sizings(self):
        for pair in p.PAIRS:
            s=p.observed(*pair,'AA',.2)
            for field,value in (('amount_to_call_bb',s.amount_to_call_bb+.5),
                                ('pot_bb',s.pot_bb+1.)):
                self.assertIsNone(p.evaluate(self.model,replace(s,**{field:value})))

    def test_stack_start_used_after_open(self):
        txt=p.SOURCE.read_text(encoding='utf-8')
        self.assertIn('StackSizeAtBeginningOfCurrentRound >= 95',txt)
        self.assertNotIn('AND StackSize >= 95',txt)
        s=p.observed('LJ','CO','AA',.7)
        self.assertEqual(p.evaluate(self.model,replace(s,stack_at_round_start_bb=95.)),('4BET',21.2))
        self.assertEqual(p.evaluate(self.model,replace(s,stack_at_round_start_bb=105.)),('4BET',21.2))

    def test_randomhand_integer_percent_exact(self):
        for pair in p.PAIRS:
            # Exhaustive 10,000 quantiles for 6 mixed categories per pair.
            for r in self.model.rules:
                if r.pair!=pair or r.op!='<':continue
                hand=next(iter(self.model.lists[r.handlist]))
                actual=Counter(p.evaluate(self.model,p.observed(*pair,hand,k/10000))[0] for k in range(10000))
                target=r.action.split()[0]
                action='4BET' if target=='RaiseTo' else 'CALL'
                self.assertEqual(actual[action],int(r.threshold*10000),(pair,hand,r.threshold))

    def test_repeated_evaluation_is_stable_given_same_randomhand(self):
        for pair in p.PAIRS:
            s=p.observed(*pair,'QQ',.314159)
            a=p.evaluate(self.model,s)
            self.assertEqual([p.evaluate(self.model,s) for _ in range(12)],[a]*12)

    def test_invalid_random_does_not_misselect_mixed(self):
        s=p.observed('LJ','CO','QQ')
        for v in (None,-.1,1.,float('nan'),float('inf')):
            self.assertIsNone(p.evaluate(self.model,replace(s,randomhand=v)))
        # Pure rules have no RNG dependency.
        self.assertEqual(p.evaluate(self.model,p.observed('LJ','CO','AA')),('4BET',21.2))

    def test_source_parser_rejects_fallback_or_unsupported_code(self):
        txt=p.SOURCE.read_text(encoding='utf-8')
        for extra in ('\nWHEN Others Fold FORCE',
                      '\nWHEN Random < 40 Call FORCE',
                      '\nif hero: do_4bet()'):
            with self.assertRaises(p.UnsafeV3):p.parse(txt+extra)

    def test_parser_rejects_missing_history_guard(self):
        txt=p.SOURCE.read_text(encoding='utf-8')
        modified=txt.replace(' AND RaisesSinceLastPlay = 1','',1)
        with self.assertRaises(p.UnsafeV3):p.parse(modified)

    def test_parser_rejects_misordered_random_branch(self):
        txt=p.SOURCE.read_text(encoding='utf-8')
        first=next(r for r in txt.splitlines() if r.startswith('WHEN (') and 'randomhand <' in r)
        modified=txt.replace(first,first.replace('randomhand <','randomhand >='),1)
        with self.assertRaises(p.UnsafeV3):p.parse(modified)

    def test_parser_rejects_wrong_4bet_sizing(self):
        txt=p.SOURCE.read_text(encoding='utf-8')
        with self.assertRaises(p.UnsafeV3):p.parse(txt.replace('RaiseTo 21.2 FORCE','RaiseTo 25 FORCE',1))

    def test_parser_rejects_overlapping_lists(self):
        txt=p.SOURCE.read_text(encoding='utf-8')
        first_list=txt.find('##listV3LJHJP4##')
        self.assertGreater(first_list,-1)
        # AA already in value; injecting AA in a different bucket should fail.
        target='##listV3LJHJM4C65##'
        self.assertIn(target,txt)
        with self.assertRaises(p.UnsafeV3):p.parse(txt.replace(target,target+'\nAA',1))

    def test_3bet_range_does_not_depend_on_second_python_strategy(self):
        import inspect
        test_code=inspect.getsource(p)
        self.assertNotIn('from vs_3bet_reference import RANGES',test_code)
        self.assertNotIn('from rfi_reference import RANGES',test_code)
        self.assertIn('SOURCE=HERE/',test_code)

    def test_rfi_mixed_hands_do_not_reintroduce_second_random_dependence(self):
        for pair in p.PAIRS:
            op=pair[0]
            for h in p.HANDS:
                if 0<RFI_RANGES[Position(op)][h]['RAISE']<1:
                    row=RANGES[pair][h]
                    self.assertEqual((row.fourbet,row.call,row.fold),(0,0,1))

    def test_mapping_csv_2535_and_unreachable_explicit(self):
        with (HERE/'VS3_2535_MAPPING.csv').open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),2535)
        self.assertEqual(len({(r['Opener'],r['Threebettor'],r['Hand']) for r in rows}),2535)
        self.assertEqual(sum(r['Reachable']=='YES' for r in rows),888)
        self.assertEqual(sum(r['Reachable']=='NO' for r in rows),1647)
        for r in rows:
            truth=RANGES[r['Opener'],r['Threebettor']][r['Hand']]
            self.assertAlmostEqual(float(r['RFI_open_pct'])/100,truth.open_probability)
            if r['Reachable']=='NO':
                self.assertEqual(r['ActionBucket'],'NOT_REACHABLE')
                self.assertEqual(r['Handlist'],'')
                self.assertEqual(r['FourbetTo_BB'],'')

    def test_integrated_preflop_only_one_entrypoint(self):
        old=(ROOT/'portability/vs_open_mvp/preflop_rfi_vsopen_draft.oppl').read_text()
        current=(HERE/'preflop_rfi_vsopen_vs3_draft.oppl').read_text()
        new=p.SOURCE.read_text()
        self.assertEqual(current.count('##f$preflop##'),1)
        for piece in (old.split('##f$preflop##')[1].strip(),new.split('##f$preflop##')[1].strip()):
            self.assertIn(piece,current)
        self.assertEqual(current.count('WHEN ('),142+135)
        names=[r.split('##')[1] for r in current.splitlines() if r.startswith('##list')]
        self.assertEqual(len(names),len(set(names)))
        self.assertNotIn('WHEN Others',current)

    def test_generator_reproducible_and_no_strategy_mutation(self):
        historical=tuple(ROOT/'gto6_heuristic_v0_6_1'/n for n in
            ('rfi_reference.py','vs_open_reference.py','vs_3bet_reference.py'))
        outputs=(HERE/'vs_3bet_6max_mvp.oppl',HERE/'VS3_2535_MAPPING.csv',
                 HERE/'preflop_rfi_vsopen_vs3_draft.oppl')
        before={x:hashlib.sha256(x.read_bytes()).hexdigest() for x in (*historical,*outputs)}
        self.assertEqual(compiler.generate(),(2535,888,90,135))
        after={x:hashlib.sha256(x.read_bytes()).hexdigest() for x in before}
        self.assertEqual(before,after)

    def test_negative_nonfinite_inputs(self):
        s=p.observed('SB','BB','AA',.4)
        for field in ('pot_bb','amount_to_call_bb','stack_at_round_start_bb',
                      'min_opponent_stack_bb','max_opponent_stack_bb'):
            for bad in (float('inf'),float('nan'),None):
                self.assertIsNone(p.evaluate(self.model,replace(s,**{field:bad})))

    def test_source_version_and_scope_not_misrepresented(self):
        src=p.SOURCE.read_text()
        self.assertIn('DRAFT',src)
        self.assertIn('Do NOT',src)
        self.assertEqual(len(SPECS),15)
        self.assertNotIn('##f$flop##',src)

if __name__=='__main__':unittest.main()
