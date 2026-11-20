"""Strict parser/evaluator of the exact OpenPPL VS_OPEN source for OFFLINE tests.

The OpenPPL file, not this Python module, contains all poker hand decisions.
This is not an OpenHoldem compiler nor proof of real scraping/action parity.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
import re

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'vs_open_6max_mvp.oppl'
RANKS='AKQJT98765432'
ALL_HANDS=frozenset([x+x for x in RANKS]+[x+y+s for i,x in enumerate(RANKS) for y in RANKS[i+1:] for s in ('s','o')])
SEATS={'LJ':('InUTG',5,0.),'HJ':('InMiddlePosition3',4,0.),'CO':('InCutOff',3,0.),
       'BTN':('InButton',2,0.),'SB':('InSmallBlind',1,.5),'BB':('InBigBlind',0,1.)}
PAIRS=((op,hero) for op in ('LJ','HJ','CO','BTN','SB') for hero in list(SEATS)[list(SEATS).index(op)+1:])
PAIRS=frozenset(PAIRS)
LIST_RE=re.compile(r'^##(listVO(LJ|HJ|CO|BTN|SB)(LJ|HJ|CO|BTN|SB|BB)(3BET|CALL|FOLD|M3C|M3F|MCF)(\d{2})?)##$')
RULE_RE=re.compile(r'^WHEN \(([^()]+)\) (RaiseTo (?:8|10\.25|9\.6)|Call|Fold) FORCE$')
RAND_RE=re.compile(r'^randomhand (<|>=) (0\.\d{2})$')

class UnsafeOpenPPL(ValueError):pass

@dataclass(frozen=True)
class Rule:
    pair: tuple[str,str]
    listname: str
    action: str
    rand_op: str|None
    threshold: float|None

@dataclass(frozen=True)
class Model:
    lists: dict[str,frozenset[str]]
    rules: tuple[Rule,...]

@dataclass(frozen=True)
class Observation:
    hand: str
    opener: str
    hero: str
    randomhand: float|None = None
    is_preflop: bool=True
    players_dealt: int=6
    raises: int=1
    calls: int=0
    first_raiser_position: int|None=None
    last_raiser_position: int|None=None
    pot_bb: float=4.
    amount_to_call_bb: float|None=None
    stack_unknown: bool=False
    hero_stack_bb: float=100.
    min_opp_stack_bb: float=100.
    max_opp_stack_bb: float=100.


def guard(op:str,hero:str)->tuple[str,...]:
    if (op,hero) not in PAIRS:raise UnsafeOpenPPL('unsupported pair')
    hero_symbol=SEATS[hero][0]
    raiser_id=SEATS[op][1]
    open_to=3. if op=='SB' else 2.5
    pot=4.
    to_call=open_to-SEATS[hero][2]
    return ('IsPreflop','nplayersdealt = 6',hero_symbol,'Raises = 1','Calls = 0',
            f'FirstRaiserPosition = {raiser_id}',f'LastRaiserPosition = {raiser_id}',
            f'PotSize = {pot:g}',f'AmountToCall = {to_call:g}',
            'NOT StackUnknown','StackSize >= 95','StackSize <= 105',
            'MinOpponentStackSize >= 95','MaxOpponentStackSize <= 105')


def parse(source:str)->Model:
    lists={};rules=[];section=None;in_rules=False
    for no,raw in enumerate(source.splitlines(),1):
        line=raw.strip()
        if not line or line.startswith('//'):continue
        lm=LIST_RE.fullmatch(line)
        if lm:
            if in_rules or lm[1] in lists:raise UnsafeOpenPPL(f'handlist out of order at {no}')
            op,hero,tag,pct=lm[2],lm[3],lm[4],lm[5]
            if (op,hero) not in PAIRS or (tag.startswith('M')!=(pct is not None)):
                raise UnsafeOpenPPL(f'handlist name not canonical at {no}')
            if pct is not None and (int(pct)<=0 or int(pct)>=100):
                raise UnsafeOpenPPL('invalid mix weight')
            section=lm[1];lists[section]=set();continue
        if line=='##f$preflop##':
            if in_rules or not lists:raise UnsafeOpenPPL('bad preflop header')
            in_rules=True;section='preflop';continue
        if not in_rules:
            if section not in lists:raise UnsafeOpenPPL(f'bad list at {no}')
            hand_tokens=line.split()
            if not hand_tokens or len(set(hand_tokens))!=len(hand_tokens) or not set(hand_tokens)<=ALL_HANDS or lists[section].intersection(hand_tokens):
                raise UnsafeOpenPPL(f'bad/duplicate hand at {no}')
            lists[section].update(hand_tokens);continue
        rm=RULE_RE.fullmatch(line)
        if rm is None:raise UnsafeOpenPPL(f'noncanonical rule at {no}')
        atoms=tuple(rm[1].split(' AND '))
        matches=[]
        for (op,hero) in PAIRS:
            g=guard(op,hero)
            if atoms[:len(g)]!=g:continue
            trail=atoms[len(g):]
            if len(trail) not in (1,2) or trail[0] not in lists:continue
            lm2=LIST_RE.fullmatch('##'+trail[0]+'##')
            if lm2 is None or (lm2[2],lm2[3])!=(op,hero):continue
            tag,pct=lm2[4],lm2[5]
            if tag.startswith('M'):
                if len(trail)!=2:continue
                rand=RAND_RE.fullmatch(trail[1])
                if rand is None or float(rand[2])!=int(pct)/100:continue
                op_rand,thr=rand[1],float(rand[2])
                # Semantic action type verified; sizing parity checked vs baseline in tests.
                expected=('RaiseTo ' if tag in ('M3C','M3F') and op_rand=='<' else
                    'Call' if (tag=='MCF' and op_rand=='<') or (tag=='M3C' and op_rand=='>=') else 'Fold')
                if (rm[2].startswith('RaiseTo ') if expected=='RaiseTo ' else rm[2]==expected) is False:continue
            else:
                if len(trail)!=1:continue
                op_rand=thr=None
                expected='RaiseTo ' if tag=='3BET' else 'Call' if tag=='CALL' else 'Fold'
                if not (rm[2].startswith('RaiseTo ') if expected=='RaiseTo ' else rm[2]==expected):continue
            matches.append(Rule((op,hero),trail[0],rm[2],op_rand,thr))
        if len(matches)!=1:raise UnsafeOpenPPL(f'no unique matching pair/handlist at {no}')
        rules.append(matches[0])
    if not in_rules:raise UnsafeOpenPPL('no preflop section')
    if len(lists)!=81 or len(rules)!=121:raise UnsafeOpenPPL('unexpected static source shape')
    for op,hero in PAIRS:
        named=[ln for ln in lists if (m:=LIST_RE.fullmatch('##'+ln+'##')) and (m[2],m[3])==(op,hero)]
        if len(named)!=len(set(named)) or set.union(*(lists[ln] for ln in named))!=ALL_HANDS or sum(len(lists[ln]) for ln in named)!=169:
            raise UnsafeOpenPPL('missing or overlapping 169 hands: '+str((op,hero)))
    if set(r.listname for r in rules)!=set(lists):raise UnsafeOpenPPL('unused handlist')
    from collections import Counter
    c=Counter((r.listname,r.rand_op) for r in rules)
    if any(n!=1 for n in c.values()):raise UnsafeOpenPPL('duplicated/shadowed action rules')
    for ln in lists:
        m=LIST_RE.fullmatch('##'+ln+'##')
        hasmix=m[4].startswith('M')
        rules_here=[r for r in rules if r.listname==ln]
        if len(rules_here)!=(2 if hasmix else 1):raise UnsafeOpenPPL('missing mixed action alternative')
        if hasmix and [r.rand_op for r in rules_here]!=['<','>=']:
            raise UnsafeOpenPPL('mixed branch ordering/complement invalid')
        if not lists[ln]:raise UnsafeOpenPPL('empty handlist')
    return Model({x:frozenset(y) for x,y in lists.items()},tuple(rules))


def parse_file()->Model:
    return parse(SOURCE.read_text(encoding='utf-8'))


def evaluate(model:Model,s:Observation)->tuple[str,float|None]|None:
    if s.hand not in ALL_HANDS:raise UnsafeOpenPPL('unknown hand')
    if (s.opener,s.hero) not in PAIRS:raise UnsafeOpenPPL('unknown pair')
    target=SEATS[s.opener][1]
    first=target if s.first_raiser_position is None else s.first_raiser_position
    last=target if s.last_raiser_position is None else s.last_raiser_position
    call=(3. if s.opener=='SB' else 2.5)-SEATS[s.hero][2]
    amount=call if s.amount_to_call_bb is None else s.amount_to_call_bb
    numbers=(s.pot_bb,s.hero_stack_bb,s.min_opp_stack_bb,s.max_opp_stack_bb,amount)
    if (not all(isinstance(x,(float,int)) and math.isfinite(x) for x in numbers) or
        s.min_opp_stack_bb>s.max_opp_stack_bb):return None
    if (not s.is_preflop or s.players_dealt!=6 or s.raises!=1 or s.calls!=0 or
        first!=target or last!=target or s.pot_bb!=4. or amount!=call or
        s.stack_unknown or not (95<=s.hero_stack_bb<=105) or
        s.min_opp_stack_bb<95 or s.max_opp_stack_bb>105):return None
    for r in model.rules:
        if r.pair!=(s.opener,s.hero) or s.hand not in model.lists[r.listname]:continue
        if r.rand_op:
            x=s.randomhand
            if not isinstance(x,(float,int)) or not math.isfinite(x) or not 0<=x<1:continue
            if not (x<r.threshold if r.rand_op=='<' else x>=r.threshold):continue
        if r.action.startswith('RaiseTo '):return ('3BET',float(r.action.split()[1]))
        return ('CALL' if r.action=='Call' else 'FOLD',None)
    return None  # No-match is not a safe OH runtime fallback.

if __name__=='__main__':
    m=parse_file()
    print('VS_OPEN: %d pairs, %d distinct class-lists, %d OpenPPL rules'% (len(PAIRS),len(m.lists),len(m.rules)))
