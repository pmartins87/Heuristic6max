"""Test-only interpreter of the exact threeway OpenPPL rules. Not a bot runtime."""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import math
import re
SOURCE=Path(__file__).with_name('threeway_srp_postflop.oppl')
HELPERS={'f$H6ThreeWayPFR','f$H6ThreeWayCaller','f$H6ThreeWaySRP','f$H6ThreeWayStrong'}
STREETS=('flop','turn','river')
BOOLS=frozenset(('StackUnknown','user_H6_RFIIntent','user_H6_3betIntent',
    'user_H6_VSOpenCallIntent','BotRaisedBeforeFlop','BotCalledBeforeFlop',
    'HaveNuts','HaveQuads','HaveFullHouse','HaveFlush','HaveStraight','HaveSet',
    'HaveTrips','HaveTwoPair','HaveOverPair','HaveTopPair','HaveBestKicker',
    'HaveNutFlushDraw','HaveOpenEndedStraightDraw','BotRaisedOnFlop','PairOnBoard'))
NUMERICS=frozenset(('nplayersdealt','OpponentsOnFlop','OpponentsLeft',
    'NumberOfOpponentsAllin','NumberOfRaisesBeforeFlop','AmountToCall','PotSize','randomhand'))
ACTIONS={'RaiseHalfPot','Call','Fold','BetTwoThirdPot','BetHalfPot','BetThirdPot','Check'}
RE_RULE=re.compile(r'^WHEN \(([^()]+)\) (RETURN (?:TRUE|FALSE)|\w+) FORCE$')
RE_REL=re.compile(r'^([A-Za-z][A-Za-z0-9]*) (<=|>=|=|<|>) (\d+(?:\.\d+)?)(% PotSize)?$')

class SourceError(ValueError):pass

@dataclass(frozen=True)
class Rule:
    atoms:tuple[str,...]
    action:str
    fallback:bool=False

@dataclass(frozen=True)
class Source:
    rules:dict[str,tuple[Rule,...]]


def parse(text:str)->Source:
    sections={};current=None
    for no,line in enumerate(text.splitlines(),1):
        line=line.strip()
        if not line:continue
        if line.startswith('//@STREET '):
            current=line.split(' ',1)[1]
            if current not in STREETS or current in sections:raise SourceError('bad street')
            sections[current]=[];continue
        if line.startswith('//'):continue
        if line.startswith('##'):
            current=line[2:-2]
            if current not in HELPERS or current in sections:raise SourceError('unknown/duplicate helper')
            sections[current]=[];continue
        if current is None:raise SourceError('unscoped rule')
        if line=='WHEN Others RETURN FALSE FORCE':
            if current in STREETS or any(r.fallback for r in sections[current]):raise SourceError('unsafe fallback')
            sections[current].append(Rule((),'RETURN FALSE',True));continue
        m=RE_RULE.fullmatch(line)
        if not m:raise SourceError(f'Unsupported syntax on {no}')
        atoms=tuple(m[1].split(' AND '));act=m[2]
        if len(atoms)!=len(set(atoms)):raise SourceError('duplicated atoms')
        if current in STREETS:
            if act not in ACTIONS or not any(a in atoms for a in ('f$H6ThreeWaySRP','f$H6ThreeWayPFR','f$H6ThreeWayCaller')):
                raise SourceError('unguarded/unsupported postflop action')
        elif act not in ('RETURN TRUE','RETURN FALSE'):raise SourceError('helper emitted action')
        for a in atoms:
            b=a[4:] if a.startswith('NOT ') else a
            if b in BOOLS|HELPERS or b=='Position = Last':continue
            r=RE_REL.fullmatch(b)
            if r and r[1] in NUMERICS and (not r[4] or r[1]=='AmountToCall'):
                if r[1]=='randomhand' and (r[2],r[3]) not in (('<','0.40'),('<','0.30')):
                    raise SourceError('Unreviewed randomized action')
                continue
            raise SourceError(f'Unknown predicate: {a}')
        if any(r.fallback for r in sections[current]):raise SourceError('shadowed rule')
        sections[current].append(Rule(atoms,act))
    if set(sections)!=HELPERS|set(STREETS):raise SourceError('Missing sections')
    for h in HELPERS:
        if not sections[h][-1].fallback:raise SourceError('Helper missing false fallback')
    for name,n in (('flop',14),('turn',11),('river',8)):
        rules=sections[name]
        if len(rules)!=n or any(r.fallback for r in rules):raise SourceError('Unreviewed tree')
        if rules[-1].atoms!=('f$H6ThreeWaySRP','AmountToCall = 0') or rules[-1].action!='Check':raise SourceError('Unsafe tail')
        if not any(r.atoms==('f$H6ThreeWaySRP','AmountToCall > 0') and r.action=='Fold' for r in rules):raise SourceError('Missing priced fold')
    return Source({k:tuple(v) for k,v in sections.items()})


def parse_file():return parse(SOURCE.read_text(encoding='utf-8'))


def obs(**kw):
    o={x:False for x in BOOLS};o.update({x:0 for x in NUMERICS})
    o.update({'nplayersdealt':6,'OpponentsOnFlop':2,'OpponentsLeft':2,
              'NumberOfOpponentsAllin':0,'NumberOfRaisesBeforeFlop':0,'AmountToCall':0,
              'PotSize':7,'randomhand':0.80,'Position':'Last',
              'user_H6_RFIIntent':True,'BotRaisedBeforeFlop':True})
    for k,v in kw.items():
        if k not in BOOLS|NUMERICS|{'Position'}:raise SourceError('invalid observation')
        o[k]=v
    return o


def eval_source(model:Source,street:str,o:dict)->str|None:
    if street not in STREETS:raise SourceError('unknown street')
    if set(o)!=BOOLS|NUMERICS|{'Position'}:raise SourceError('missing observation')
    if any(type(o[x]) is not bool for x in BOOLS):raise SourceError('invalid boolean')
    if any(type(o[x]) not in (int,float) or not math.isfinite(o[x]) for x in NUMERICS):raise SourceError('invalid number')
    if not 0<=o['randomhand']<1 or o['PotSize']<=0 or o['AmountToCall']<0:raise SourceError('invalid observable domain')
    if o['Position'] not in ('First','Middle','Last'):raise SourceError('position invalid')
    active=set()
    def atom(a):
        if a.startswith('NOT '):return not atom(a[4:])
        if a in BOOLS:return o[a]
        if a in HELPERS:return helper(a)
        if a=='Position = Last':return o['Position']=='Last'
        r=RE_REL.fullmatch(a)
        if not r:raise SourceError('unhandled condition')
        lhs=float(o[r[1]]);rhs=float(r[3]);operator=r[2]
        if r[4]:rhs=rhs/100*float(o['PotSize'])
        return {'=':lhs==rhs,'<':lhs<rhs,'>':lhs>rhs,'<=':lhs<=rhs,'>=':lhs>=rhs}[operator]
    def helper(h):
        if h in active:raise SourceError('cyclic helper')
        active.add(h)
        try:
            for r in model.rules[h]:
                if r.fallback or all(atom(a) for a in r.atoms):return r.action=='RETURN TRUE'
            raise SourceError('missing default')
        finally:active.remove(h)
    for r in model.rules[street]:
        if all(atom(a) for a in r.atoms):return r.action
    return None

if __name__=='__main__':print('3way static rules',sum(len(parse_file().rules[k]) for k in STREETS))
