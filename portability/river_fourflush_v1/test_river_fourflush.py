"""Seven focused source-first checks for one new SRP river subfamily.

The whitelist interpreter reads four native WHEN actions directly. It is NOT
a parallel Python poker strategy and does NOT claim OpenHoldem runtime parity.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import re
import unittest

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'iso_defense_v1'/'iso_defense_integrated_draft.oppl'
POLICY=HERE/'river_policy.oppl'
INTEGRATED=HERE/'river_fourflush_integrated_draft.oppl'


def read_rules():
    text=POLICY.read_text(encoding='utf-8')
    a,b=text.split('//@STREET river')
    functions={}
    parts=re.split(r'(?m)^(##f\$[A-Za-z0-9_]+##)\s*$',a)
    for i in range(1,len(parts),2):
        functions[parts[i][2:-2]]=parts[i+1]
    return functions,[l for l in b.splitlines() if l.startswith('WHEN ')]


def evaluate(**obs):
    functions,river=read_rules()
    def field(name):
        if name in functions:
            for row in functions[name].splitlines():
                if row.startswith('WHEN Others '):
                    return 'RETURN TRUE' in row
                if row.startswith('WHEN '):
                    hit=re.fullmatch(r'WHEN \((.*?)\) RETURN (TRUE|FALSE) FORCE',row)
                    if not hit:raise ValueError('unsupported helper '+row)
                    if matches(hit[1]):return hit[2]=='TRUE'
            raise ValueError('missing helper fallback')
        if name not in obs:raise ValueError('unavailable native symbol '+name)
        return bool(obs[name])
    def matches(expr):
        for atom in expr.split(' AND '):
            if atom.startswith('NOT '):
                if field(atom[4:]):return False
            elif atom.startswith('AmountToCall '):
                hit=re.fullmatch(r'AmountToCall (<=|>|=) ([0-9]+)(?:% PotSize)?',atom)
                if not hit:raise ValueError('unsupported amount '+atom)
                limit=float(hit[2])
                if '% PotSize' in atom:limit=limit*float(obs['PotSize'])/100
                x=float(obs['AmountToCall'])
                if not {'<=':x<=limit,'>':x>limit,'=':x==limit}[hit[1]]:return False
            elif not field(atom):return False
        return True
    for row in river:
        hit=re.fullmatch(r'WHEN \((.*?)\) (Call|Fold|Check) FORCE',row)
        if not hit:raise ValueError('unsupported action '+row)
        if matches(hit[1]):return hit[2]
    return None


def state(**changes):
    data={'f$SRPHUOpen':True,'f$SRPHUCaller':False,
          'user_H6_RFIIntent':True,'user_H6_VSOpenCallIntent':False,'user_H6_3betIntent':False,
          'OneCardFlushPossible':True,'FlushOnBoard':False,'HaveFlush':False,'HaveNuts':False,
          'f$SRPStrongMade':False,'f$SRPTopGood':False,'AmountToCall':0,'PotSize':10}
    data.update(changes)
    return data


class FourFlushRiverSource(unittest.TestCase):
    def test_01_source_has_four_scoped_decisions_and_two_helpers(self):
        funcs,rules=read_rules()
        self.assertEqual(len(funcs),2)
        self.assertEqual(len(rules),4)
        self.assertEqual([s.split(') ')[-1] for s in rules],
                         ['Call FORCE','Call FORCE','Fold FORCE','Check FORCE'])
        self.assertFalse(any('WHEN Others' in s for s in rules))

    def test_02_made_hand_calls_under_20_pct_else_folds(self):
        s=state(**{'f$SRPStrongMade':True})
        self.assertEqual(evaluate(**{**s,'AmountToCall':1.99}),'Call')
        self.assertEqual(evaluate(**{**s,'AmountToCall':2.01}),'Fold')

    def test_03_top_pair_calls_under_10_pct_else_folds(self):
        s=state(**{'f$SRPTopGood':True})
        self.assertEqual(evaluate(**{**s,'AmountToCall':0.99}),'Call')
        self.assertEqual(evaluate(**{**s,'AmountToCall':1.01}),'Fold')

    def test_04_check_instead_of_thin_value_bet(self):
        s=state(**{'f$SRPTopGood':True,'f$SRPStrongMade':True})
        self.assertEqual(evaluate(**s),'Check')

    def test_05_nuts_own_flush_and_five_flush_board_still_use_old_policy(self):
        s=state(**{'f$SRPStrongMade':True,'AmountToCall':1})
        for marker in ('HaveNuts','HaveFlush','FlushOnBoard'):
            with self.subTest(marker=marker):
                self.assertIsNone(evaluate(**{**s,marker:True}))

    def test_06_origin_excludes_iso_multiway_3bet_and_unknown_texture(self):
        s=state(**{'f$SRPStrongMade':True,'AmountToCall':1})
        for changed in ({'user_H6_RFIIntent':False},{'f$SRPHUOpen':False},
                        {'user_H6_VSOpenCallIntent':True},{'user_H6_3betIntent':True},
                        {'OneCardFlushPossible':False}):
            with self.subTest(changed=changed):
                self.assertIsNone(evaluate(**{**s,**changed}))
        caller={**s,'f$SRPHUOpen':False,'f$SRPHUCaller':True,
                'user_H6_RFIIntent':False,'user_H6_VSOpenCallIntent':True}
        self.assertEqual(evaluate(**caller),'Call')

    def test_07_merger_retains_2007_ancestor_when_lines_and_exact_source(self):
        from build_river import render
        old=PARENT.read_text(encoding='utf-8')
        new=INTEGRATED.read_text(encoding='utf-8')
        self.assertEqual(new,render())
        pre=[x for x in old.splitlines() if x.startswith('WHEN ')]
        post=[x for x in new.splitlines() if x.startswith('WHEN ')]
        self.assertEqual((len(pre),len(post)),(2007,2016))
        pos=0
        for line in pre:
            while pos<len(post) and post[pos]!=line:pos+=1
            self.assertLess(pos,len(post))
            pos+=1
        self.assertEqual(sha256(PARENT.read_bytes()).hexdigest(),
                         '27be1f161535c9bc07f019fd6e0609c7a3018bf6b2cc640b80a6042c5b7df02b')


if __name__=='__main__':unittest.main()
