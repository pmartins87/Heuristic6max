"""Strict offline interpretation of ONE authored OpenPPL file.

This is a test oracle for the exact OPPL rules, not a second strategy.
It does not claim that OpenHoldem compiles/executes the source identically.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'rfi_6max_mvp.oppl'
RANKS = 'AKQJT98765432'
ALL_HANDS = frozenset([r+r for r in RANKS]
     + [a+b+s for i,a in enumerate(RANKS) for b in RANKS[i+1:] for s in ('s','o')])
POSITIONS = {
    'LJ': ('InUTG',5,1.,2.5),
    'HJ': ('InMiddlePosition3',4,1.,2.5),
    'CO': ('InCutOff',3,1.,2.5),
    'BTN': ('InButton',2,1.,2.5),
    'SB': ('InSmallBlind',1,.5,3.),
}
LIST_PATTERN = re.compile(r'^##(listMVP(LJ|HJ|CO|BTN|SB)(RAISE|LIMP|FOLD|MIXRAISE40|MIXRAISE50|MIXLIMP75))##$')
RULE_PATTERN = re.compile(r'^WHEN \((.+)\) (RaiseTo 2\.5|RaiseTo 3|Call|Fold) FORCE$')
RAND_PATTERN = re.compile(r'^randomhand (<|>=) (0\.40|0\.50|0\.75)$')

class UnsafeSource(ValueError):
    """Not inside the strictly reviewed OpenPPL subset."""

@dataclass(frozen=True)
class Rule:
    position: str
    handlist: str
    action: str
    rand_op: str|None = None
    rand_threshold: float|None = None

@dataclass(frozen=True)
class Model:
    lists: dict[str, frozenset[str]]
    rules: tuple[Rule,...]

@dataclass(frozen=True)
class Observation:
    hand: str
    position: str
    randomhand: float|None = None
    is_preflop: bool = True
    players_dealt: int = 6
    raises: int = 0
    calls: int = 0
    still_to_act: int|None = None
    pot_bb: float = 1.5
    amount_to_call_bb: float|None = None
    stack_unknown: bool = False
    hero_stack_bb: float = 100.
    min_opp_stack_bb: float = 100.
    max_opp_stack_bb: float = 100.


def guard_atoms(pos: str) -> tuple[str,...]:
    label, behind, call_bb, _ = POSITIONS[pos]
    return ('IsPreflop','nplayersdealt = 6',label,'Raises = 0','Calls = 0',
        f'StillToAct = {behind}','PotSize = 1.5',
        f'AmountToCall = {call_bb:g}','NOT StackUnknown','StackSize >= 95',
        'StackSize <= 105','MinOpponentStackSize >= 95','MaxOpponentStackSize <= 105')


def parse(text:str)->Model:
    lists: dict[str, set[str]] = {}
    rules=[]
    current=None
    seen=False
    for n,raw in enumerate(text.splitlines(),1):
        line=raw.strip()
        if not line or line.startswith('//'):continue
        lm=LIST_PATTERN.fullmatch(line)
        if lm:
            if seen or lm[1] in lists: raise UnsafeSource(f'list misplaced/duplicate at {n}')
            current=lm[1];lists[current]=set();continue
        if line=='##f$preflop##':
            if seen or not lists:raise UnsafeSource(f'header misplaced at {n}')
            seen=True;current=None;continue
        if not seen and current:
            hs=line.split()
            if len(set(hs))!=len(hs) or not set(hs)<=ALL_HANDS or lists[current].intersection(hs):
                raise UnsafeSource(f'handlist invalid/overlap within list at {n}')
            lists[current].update(hs);continue
        if not seen:raise UnsafeSource(f'missing OPPL section at {n}')
        rm=RULE_PATTERN.fullmatch(line)
        if not rm:raise UnsafeSource(f'unreviewed OpenPPL rule at {n}')
        atoms=tuple(rm[1].split(' AND '));action=rm[2]
        matches=[]
        for pos in POSITIONS:
            head=guard_atoms(pos)
            if atoms[:len(head)]!=head:continue
            trail=atoms[len(head):]
            if len(trail) not in (1,2) or trail[0] not in lists:
                continue
            lm2=LIST_PATTERN.fullmatch('##'+trail[0]+'##')
            if lm2 is None or lm2[2]!=pos:continue
            tag=lm2[3]
            allowed=('RAISE','LIMP','FOLD','MIXRAISE40','MIXRAISE50','MIXLIMP75')
            if tag not in allowed:continue
            if tag.startswith('MIX'):
                if len(trail)!=2:continue
                ra=RAND_PATTERN.fullmatch(trail[1])
                if not ra:continue
                threshold=float(ra[2]);expected=float(tag[-2:])/100
                if abs(threshold-expected)>1e-12:continue
                op=ra[1]
                expected_action=(f'RaiseTo {POSITIONS[pos][3]:g}' if op=='<' and tag.startswith('MIXRAISE')
                    else 'Call' if op=='<' and tag.startswith('MIXLIMP') else 'Fold')
                if action!=expected_action:continue
            else:
                if len(trail)!=1:continue
                op=threshold=None
                expected_action=(f'RaiseTo {POSITIONS[pos][3]:g}' if tag=='RAISE'
                                 else 'Call' if tag=='LIMP' else 'Fold')
                if action!=expected_action:continue
            matches.append(Rule(pos,trail[0],action,op,threshold))
        if len(matches)!=1:raise UnsafeSource(f'guard/action mismatch at {n}')
        rules.append(matches[0])
    if not seen or len(rules)!=21:raise UnsafeSource('Expected 21 ordered first-in decision rules')
    for pos in POSITIONS:
        names=[k for k in lists if k.startswith('listMVP'+pos)]
        if set.union(*(lists[k] for k in names))!=ALL_HANDS:
            raise UnsafeSource(f'{pos}: all 169 hands required')
        if sum(len(lists[k]) for k in names)!=169:
            raise UnsafeSource(f'{pos}: overlapping handlists')
    if set(rule.handlist for rule in rules)!=set(lists):
        raise UnsafeSource('orphan or undocumented handlist')
    if len({(r.position,r.handlist,r.action,r.rand_op) for r in rules})!=len(rules):
        raise UnsafeSource('duplicate actions')
    return Model({k:frozenset(v) for k,v in lists.items()},tuple(rules))


def parse_file()->Model:
    return parse(SOURCE.read_text(encoding='utf-8'))


def evaluate(model:Model, s:Observation)->tuple[str,float|None]|None:
    if s.position not in POSITIONS or s.hand not in ALL_HANDS:
        raise UnsafeSource('unknown position/hand class')
    _,n,call_bb,_=POSITIONS[s.position]
    values=(s.pot_bb,s.hero_stack_bb,s.min_opp_stack_bb,s.max_opp_stack_bb)
    if (not all(isinstance(v,(int,float)) and math.isfinite(v) for v in values)
        or s.min_opp_stack_bb>s.max_opp_stack_bb):return None
    still=n if s.still_to_act is None else s.still_to_act
    call=call_bb if s.amount_to_call_bb is None else s.amount_to_call_bb
    if (not s.is_preflop or s.players_dealt!=6 or s.raises!=0 or s.calls!=0
        or still!=n or s.pot_bb!=1.5 or call!=call_bb or s.stack_unknown
        or not 95<=s.hero_stack_bb<=105 or s.min_opp_stack_bb<95
        or s.max_opp_stack_bb>105):return None
    for rule in model.rules:
        if rule.position!=s.position or s.hand not in model.lists[rule.handlist]:continue
        if rule.rand_op:
            x=s.randomhand
            if not (isinstance(x,(float,int)) and math.isfinite(x) and 0<=x<1):
                continue
            if not ((x < rule.rand_threshold) if rule.rand_op=='<' else
                    (x>=rule.rand_threshold)):
                continue
        if rule.action.startswith('RaiseTo '):return ('RAISE',float(rule.action.split()[1]))
        if rule.action=='Call':return ('LIMP',None)
        return ('FOLD',None)
    return None # The OH default.bot may still act; no fail-closed guarantee.

if __name__=='__main__':
    source=parse_file()
    print('RFI-MVP: %s rules, %s seats, 845 class+position nodes' %
          (len(source.rules),len(POSITIONS)))
