"""Whitelist interpreter of the actual v1 OpenPPL 3bet HU source.

Static/unit-test only. No separate poker strategy in Python.
The emitted action and mix threshold are read from the .oppl file.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import math
import re

SOURCE=Path(__file__).with_name('threebet_hu_postflop.oppl')
HEADERS={'f$H6ThreeBetAggressorHU','f$H6ThreeBetCallerHU','f$H6ThreeBetHU','f$H6ThreeBetStrong'}
STREETS=('flop','turn','river')
BOOLS=frozenset(('StackUnknown','user_H6_3betIntent','user_H6_RFIIntent',
    'BotRaisedBeforeFlop','BotCalledBeforeFlop','HaveNuts','HaveQuads',
    'HaveFullHouse','HaveFlush','HaveStraight','HaveSet','HaveTrips','HaveTwoPair',
    'HaveOverPair','HaveTopPair','HaveBestKicker','HaveNutFlushDraw',
    'HaveOpenEndedStraightDraw','BotIsLastRaiser','FlushPossibleOnFlop',
    'StraightPossibleOnFlop','PairOnBoard','BotRaisedOnFlop','NoBettingOnFlop'))
NUMERICS=frozenset(('nplayersdealt','OpponentsOnFlop','OpponentsLeft',
    'NumberOfOpponentsAllin','NumberOfRaisesBeforeFlop','AmountToCall','PotSize','randomhand'))
ACTIONS={'RaiseHalfPot','Call','Fold','BetTwoThirdPot','BetHalfPot','BetThirdPot','Check'}
RULE=re.compile(r'^WHEN \(([^()]+)\) (RETURN (?:TRUE|FALSE)|\w+) FORCE$')
REL=re.compile(r'^([A-Za-z][A-Za-z0-9]*) (<=|>=|=|<|>) (\d+(?:\.\d+)?)(% PotSize)?$')

class PolicyError(ValueError): pass

@dataclass(frozen=True)
class Rule:
    atoms:tuple[str,...]
    action:str
    fallback:bool=False

@dataclass(frozen=True)
class Policy:
    sections:dict[str,tuple[Rule,...]]


def parse(text:str)->Policy:
    sections={};now=None
    for lineno,original in enumerate(text.splitlines(),1):
        line=original.strip()
        if not line:continue
        if line.startswith('//@STREET '):
            now=line.split(' ',1)[1]
            if now not in STREETS or now in sections:raise PolicyError('duplicate/unknown street')
            sections[now]=[];continue
        if line.startswith('//'):continue
        if line.startswith('##'):
            if not line.startswith('##f$') or not line.endswith('##'):raise PolicyError('bad header')
            now=line[2:-2]
            if now not in HEADERS or now in sections:raise PolicyError('duplicate/unknown helper')
            sections[now]=[];continue
        if now is None:raise PolicyError('rule before section')
        if line=='WHEN Others RETURN FALSE FORCE':
            if now in STREETS or any(r.fallback for r in sections[now]):raise PolicyError('unsafe fallback')
            sections[now].append(Rule((),'RETURN FALSE',True));continue
        m=RULE.fullmatch(line)
        if not m:raise PolicyError(f'Unsupported rule at {lineno}: {line}')
        atoms=tuple(m[1].split(' AND '));action=m[2]
        if now in STREETS and action not in ACTIONS:raise PolicyError('street emitted nonaction')
        if now not in STREETS and action not in ('RETURN TRUE','RETURN FALSE'):raise PolicyError('helper emitted action')
        if len(set(atoms))!=len(atoms):raise PolicyError('repeated condition')
        if now in STREETS and not any(x in atoms for x in ('f$H6ThreeBetHU','f$H6ThreeBetAggressorHU','f$H6ThreeBetCallerHU')):
            raise PolicyError('unguarded postflop action')
        for atom in atoms:
            stripped=atom[4:] if atom.startswith('NOT ') else atom
            if stripped in BOOLS | HEADERS or stripped=='Position = Last':continue
            rm=REL.fullmatch(stripped)
            if rm and rm[1] in NUMERICS and (not rm[4] or rm[1]=='AmountToCall'):
                if rm[1]=='randomhand' and (rm[2],rm[3]) not in (('<','0.50'),('<','0.30'),('<','0.35')):raise PolicyError('unreviewed mix')
                continue
            raise PolicyError(f'Unknown OpenPPL atom {atom}')
        if any(x.fallback for x in sections[now]):raise PolicyError('branch after helper fallback')
        sections[now].append(Rule(atoms,action))
    if set(sections)!=HEADERS|set(STREETS):raise PolicyError('Incomplete source')
    for h in HEADERS:
        if not sections[h] or not sections[h][-1].fallback:raise PolicyError('Missing helper false fallback')
    for street,expected in (('flop',16),('turn',14),('river',11)):
        if len(sections[street])!=expected:raise PolicyError('Unreviewed action tree')
        if any(r.fallback for r in sections[street]):raise PolicyError('Implicit action fallback prohibited')
        if sections[street][-1].atoms!=('f$H6ThreeBetHU','AmountToCall = 0') or sections[street][-1].action!='Check':
            raise PolicyError('Missing domain-protected check')
        if not any(r.atoms==('f$H6ThreeBetHU','AmountToCall > 0') and r.action=='Fold' for r in sections[street]):
            raise PolicyError('Missing domain-protected fold')
    return Policy({k:tuple(v) for k,v in sections.items()})


def parse_file():return parse(SOURCE.read_text(encoding='utf-8'))


def observations(**changes):
    result={x:False for x in BOOLS}
    result.update({x:0 for x in NUMERICS})
    result.update({'nplayersdealt':6,'OpponentsOnFlop':1,'OpponentsLeft':1,
                   'NumberOfOpponentsAllin':0,'NumberOfRaisesBeforeFlop':1,
                   'AmountToCall':0.0,'PotSize':20.0,'randomhand':0.80,
                   'Position':'Last', 'BotRaisedBeforeFlop':True,
                   'user_H6_3betIntent':True})
    for k,v in changes.items():
        if k not in BOOLS|NUMERICS|{'Position'}:raise PolicyError(f'unknown input {k}')
        result[k]=v
    return result


def evaluate(model:Policy,street:str,observed:dict)->str|None:
    if street not in STREETS:raise PolicyError('Unknown street')
    if set(observed)!=BOOLS|NUMERICS|{'Position'}:raise PolicyError('Missing/extra observed symbol')
    for k in NUMERICS:
        if isinstance(observed[k],bool) or not isinstance(observed[k],(int,float)) or not math.isfinite(observed[k]):
            raise PolicyError(f'Bad numeric input {k}')
    for k in BOOLS:
        if not isinstance(observed[k],bool):raise PolicyError(f'Bad boolean {k}')
    if not 0<=observed['randomhand']<1 or observed['PotSize']<=0 or observed['AmountToCall']<0:
        raise PolicyError('Invalid table values')
    if observed['Position'] not in ('First','Middle','Last'):raise PolicyError('Unknown relative position')
    active=set()
    def atom(a):
        if a.startswith('NOT '):return not atom(a[4:])
        if a in BOOLS:return observed[a]
        if a in HEADERS:return helper(a)
        if a=='Position = Last':return observed['Position']=='Last'
        rm=REL.fullmatch(a)
        if not rm:raise PolicyError(f'Bad parsed condition {a}')
        lhs=float(observed[rm[1]]);rhs=float(rm[3]);op=rm[2]
        if rm[4]:rhs*=float(observed['PotSize'])/100
        return {'=':lhs==rhs,'<':lhs<rhs,'>':lhs>rhs,'<=':lhs<=rhs,'>=':lhs>=rhs}[op]
    def helper(name):
        if name in active:raise PolicyError('Cyclic helper')
        active.add(name)
        try:
            for r in model.sections[name]:
                if r.fallback or all(atom(a) for a in r.atoms):return r.action=='RETURN TRUE'
            raise PolicyError('Unclosed helper')
        finally:active.remove(name)
    for r in model.sections[street]:
        if all(atom(a) for a in r.atoms):return r.action
    return None  # no-match is not fail-closed in real OpenHoldem

if __name__=='__main__':
    model=parse_file()
    print('static 3bet HU', sum(len(model.sections[x]) for x in STREETS),'actions')
