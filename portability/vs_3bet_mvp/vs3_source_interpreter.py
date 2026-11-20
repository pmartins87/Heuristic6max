"""Strict static test interpreter of VS_3BET OpenPPL; never OpenHoldem runtime.

The *only* hand decisions are parsed from vs_3bet_6max_mvp.oppl.
This interpreter rejects unknown syntax instead of guessing an action.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import math
import re

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'vs_3bet_6max_mvp.oppl'
POS={
 'LJ':('InUTG',5),'HJ':('InMiddlePosition3',4),
 'CO':('InCutOff',3),'BTN':('InButton',2),
 'SB':('InSmallBlind',1),'BB':('InBigBlind',0),
}
PAIRS=tuple((a,b) for a in ('LJ','HJ','CO','BTN','SB') for b in ('HJ','CO','BTN','SB','BB') if
               list(POS).index(b)>list(POS).index(a))
RANKS='AKQJT98765432'
HANDS=frozenset([r*2 for r in RANKS]+[a+b+k for i,a in enumerate(RANKS) for b in RANKS[i+1:] for k in 'so'])
TAGS=('P4','M4C','M4F','PC','MCF','PF')
LIST_RE=re.compile(r'^##(listV3(LJ|HJ|CO|BTN|SB)(HJ|CO|BTN|SB|BB)(P4|M4C|M4F|PC|MCF|PF)(\d{2})?)##$')
RULE_RE=re.compile(r'^WHEN \(([^()]+)\) (RaiseTo (\d+(?:\.\d+)?)|Call|Fold) FORCE$')
RAND_RE=re.compile(r'^randomhand (<|>=) (0\.\d{2})$')

class UnsafeV3(ValueError):pass


def expected_3bet_to(op:str,bt:str)->float:
    # OpenPPL audit assumes fixed VS_OPEN sizing v0.6.1: 3.2x IP, 4.1x OOP.
    # Source-of-truth for hand frequencies remains the OPPL rules themselves.
    open_to=3. if op=='SB' else 2.5
    threebettor_ip=(bt=='BTN' or (bt in ('HJ','CO') and POS[bt][1]<POS[op][1]) or (bt=='BB' and op=='SB'))
    return round(open_to*(3.2 if threebettor_ip else 4.1),2)


def expected_4bet_to(op:str,bt:str)->float:
    three=expected_3bet_to(op,bt)
    opener_ip=bt in ('SB','BB') and op!='SB'
    return round(three*(2.30 if opener_ip else 2.65)+1e-8,2)


def expected_pot(op:str,bt:str)->float:
    invested_blinds=(0. if 'SB' in (op,bt) else .5)+(0. if 'BB' in (op,bt) else 1.)
    return (3. if op=='SB' else 2.5)+expected_3bet_to(op,bt)+invested_blinds


def guard(op:str,bt:str)->tuple[str,...]:
    if (op,bt) not in PAIRS:raise UnsafeV3('invalid positional pair')
    return ('IsPreflop','nplayersdealt = 6',POS[op][0],
            'Raises = 1','RaisesSinceLastPlay = 1','Calls = 0',
            'BotRaisedBeforeFlop',
            f'FirstRaiserPosition = {POS[op][1]}',
            f'LastRaiserPosition = {POS[bt][1]}',
            f'PotSize = {expected_pot(op,bt):g}',
            f'AmountToCall = {expected_3bet_to(op,bt)-(3. if op=="SB" else 2.5):g}',
            'NOT StackUnknown','StackSizeAtBeginningOfCurrentRound >= 95',
            'StackSizeAtBeginningOfCurrentRound <= 105',
            'MinOpponentStackSize >= 95','MaxOpponentStackSize <= 105')


@dataclass(frozen=True)
class Rule:
    pair:tuple[str,str]
    handlist:str
    action:str
    op:str|None
    threshold:float|None

@dataclass(frozen=True)
class Model:
    lists:dict[str,frozenset[str]]
    rules:tuple[Rule,...]

@dataclass(frozen=True)
class Observation:
    hand:str
    opener:str
    threebettor:str
    randomhand:float|None=None
    is_preflop:bool=True
    nplayersdealt:int=6
    raises:int=1  # opponent raises only; Hero RFI does NOT count
    raises_since_last_play:int=1
    calls:int=0
    bot_raised_before_flop:bool=True
    first_raiser_position:int|None=None
    last_raiser_position:int|None=None
    pot_bb:float|None=None
    amount_to_call_bb:float|None=None
    stack_unknown:bool=False
    stack_at_round_start_bb:float=100.
    min_opponent_stack_bb:float=100.
    max_opponent_stack_bb:float=100.


def observed(op:str,bt:str,hand:str,randomhand:float|None=None)->Observation:
    return Observation(hand=hand,opener=op,threebettor=bt,randomhand=randomhand,
        first_raiser_position=POS[op][1],last_raiser_position=POS[bt][1],
        pot_bb=expected_pot(op,bt),
        amount_to_call_bb=expected_3bet_to(op,bt)-(3. if op=='SB' else 2.5))


def parse(text:str)->Model:
    lists:dict[str,set[str]]={}
    rules=[];section=None;in_rules=False
    for number,raw in enumerate(text.splitlines(),1):
        line=raw.strip()
        if not line or line.startswith('//'):continue
        lm=LIST_RE.fullmatch(line)
        if lm:
            if in_rules or lm[1] in lists or (lm[2],lm[3]) not in PAIRS:
                raise UnsafeV3(f'Bad list header: {number}')
            if (lm[4].startswith('M')!=(lm[5] is not None)):
                raise UnsafeV3('Mixed group must specify an integer percent')
            if lm[5] and not 1<=int(lm[5])<=99:raise UnsafeV3('bad mixed percentage')
            section=lm[1];lists[section]=set();continue
        if line=='##f$preflop##':
            if in_rules or not lists:raise UnsafeV3('bad preflop entrypoint')
            in_rules=True;section='preflop';continue
        if not in_rules:
            if section not in lists:raise UnsafeV3(f'handlist missing: {number}')
            words=line.split()
            if (not words or len(set(words))!=len(words) or
                not set(words)<=HANDS or set(words)&lists[section]):
                raise UnsafeV3(f'invalid or duplicated hand in list: {number}')
            lists[section].update(words);continue
        rm=RULE_RE.fullmatch(line)
        if rm is None:raise UnsafeV3(f'unknown OPPL rule/implicit fallback: {number}')
        atoms=tuple(rm[1].split(' AND '))
        candidates=[]
        for op,bt in PAIRS:
            g=guard(op,bt)
            if atoms[:len(g)]!=g:continue
            tail=atoms[len(g):]
            if len(tail) not in (1,2) or tail[0] not in lists:continue
            mt=LIST_RE.fullmatch(f'##{tail[0]}##')
            if mt is None or (mt[2],mt[3])!=(op,bt):continue
            tag,pct=mt[4],mt[5]
            randomop=threshold=None
            if pct:
                if len(tail)!=2:continue
                rnd=RAND_RE.fullmatch(tail[1])
                if not rnd or abs(float(rnd[2])-int(pct)/100)>1e-12:continue
                randomop,threshold=rnd[1],float(rnd[2])
            elif len(tail)!=1:continue
            action=rm[2]
            expected=(f'RaiseTo {expected_4bet_to(op,bt):g}' if
                      (tag=='P4' or tag in ('M4C','M4F') and randomop=='<')
                      else 'Call' if (tag=='PC' or tag=='M4C' and randomop=='>=' or
                                      tag=='MCF' and randomop=='<') else 'Fold')
            if action!=expected:continue
            candidates.append(Rule((op,bt),tail[0],action,randomop,threshold))
        if len(candidates)!=1:raise UnsafeV3(f'cannot determine exact rule/size at {number}')
        rules.append(candidates[0])
    if not in_rules:raise UnsafeV3('no preflop section')
    # ALL 15 trees must be represented with exactly six audited buckets.
    for pair in PAIRS:
        mine=[]; union=set()
        for name,hands in lists.items():
            m=LIST_RE.fullmatch(f'##{name}##')
            if (m[2],m[3])==pair:
                if union & hands:raise UnsafeV3('overlapping classes '+str(pair))
                union|=hands;mine.append((name,m[4],m[5]))
        if len(mine)!=6:raise UnsafeV3(f'exactly 6 categories required: {pair}, {mine}')
        if {tag for _,tag,_ in mine}!=set(TAGS):raise UnsafeV3('bad category set')
        for name,tag,pct in mine:
            matches=[r for r in rules if r.pair==pair and r.handlist==name]
            if len(matches)!=(2 if pct is not None else 1):raise UnsafeV3('missing/duplicate mixed branch')
            if pct is not None and [r.op for r in matches]!=['<','>=']:
                raise UnsafeV3('mixed branch order/threshold unsafe')
        # Not-reachable hands are intentionally absent: caller checks per hand.
    if len(rules)!=sum(2 if LIST_RE.fullmatch(f'##{n}##')[5] else 1 for n in lists):
        raise UnsafeV3('unassigned or shadowed rule')
    return Model({name:frozenset(h) for name,h in lists.items()},tuple(rules))


def parse_file()->Model:return parse(SOURCE.read_text(encoding='utf-8'))


def evaluate(model:Model,s:Observation)->tuple[str,float|None]|None:
    if (s.opener,s.threebettor) not in PAIRS or s.hand not in HANDS:
        raise UnsafeV3('unsupported pair or hand')
    op,bt=s.opener,s.threebettor
    if not all(isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v)
        for v in (s.pot_bb,s.amount_to_call_bb,s.stack_at_round_start_bb,
                  s.min_opponent_stack_bb,s.max_opponent_stack_bb)):
        return None
    if s.min_opponent_stack_bb>s.max_opponent_stack_bb:return None
    observed_guards={
        'IsPreflop':s.is_preflop,'nplayersdealt = 6':s.nplayersdealt==6,
        POS[op][0]:True,'Raises = 1':s.raises==1,
        'RaisesSinceLastPlay = 1':s.raises_since_last_play==1,
        'Calls = 0':s.calls==0,'BotRaisedBeforeFlop':s.bot_raised_before_flop,
        f'FirstRaiserPosition = {POS[op][1]}':s.first_raiser_position==POS[op][1],
        f'LastRaiserPosition = {POS[bt][1]}':s.last_raiser_position==POS[bt][1],
        f'PotSize = {expected_pot(op,bt):g}':s.pot_bb==expected_pot(op,bt),
        f'AmountToCall = {expected_3bet_to(op,bt)-(3. if op=="SB" else 2.5):g}':
            abs(s.amount_to_call_bb-(expected_3bet_to(op,bt)-(3. if op=='SB' else 2.5)))<1e-8,
        'NOT StackUnknown':not s.stack_unknown,
        'StackSizeAtBeginningOfCurrentRound >= 95':s.stack_at_round_start_bb>=95,
        'StackSizeAtBeginningOfCurrentRound <= 105':s.stack_at_round_start_bb<=105,
        'MinOpponentStackSize >= 95':s.min_opponent_stack_bb>=95,
        'MaxOpponentStackSize <= 105':s.max_opponent_stack_bb<=105,
    }
    for rule in model.rules:
        if rule.pair!=(op,bt):continue
        if any(not observed_guards[atom] for atom in guard(op,bt)):
            return None
        if s.hand not in model.lists[rule.handlist]:continue
        if rule.op is not None:
            v=s.randomhand
            if (v is None or not isinstance(v,(int,float)) or not math.isfinite(v) or
                not 0<=v<1):continue
            if (v<rule.threshold) != (rule.op=='<'):continue
        if rule.action.startswith('RaiseTo '):return ('4BET',float(rule.action.split()[1]))
        return ('CALL',None) if rule.action=='Call' else ('FOLD',None)
    return None  # DOES NOT guarantee safe behavior of OpenHoldem on no match.
