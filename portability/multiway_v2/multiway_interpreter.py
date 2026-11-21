"""Restricted static interpreter of the *same* new OpenPPL source.

Never runs in OpenHoldem, never models opponents, never chooses strategy
separately from .oppl. In particular None != safe OpenHoldem fallback.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import math
import re

HERE=Path(__file__).resolve().parent
CROWDED=HERE/'crowded_srp_postflop.oppl'
TRANSITION=HERE/'transition_to_hu_postflop.oppl'
STREETS=('flop','turn','river')
HELPERS=frozenset({'f$H6CrowdedPFR','f$H6CrowdedCaller','f$H6Crowded4',
    'f$H6Crowded5','f$H6Crowded6','f$H6CrowdedSRP','f$H6CrowdedStrong',
    'f$H6Transition3','f$H6Transition4Plus','f$H6TransitionHU'})
BOOLS=frozenset({'StackUnknown','user_H6_RFIIntent','user_H6_3betIntent',
    'user_H6_VSOpenCallIntent','BotRaisedBeforeFlop','BotCalledBeforeFlop',
    'HaveNuts','HaveQuads','HaveFullHouse','HaveFlush','HaveStraight',
    'HaveSet','HaveTrips','HaveTwoPair','HaveOverPair','HaveTopPair',
    'HaveBestKicker','HaveNutFlushDraw','BotRaisedOnFlop','PairOnBoard'})
NUMERICS=frozenset({'nplayersdealt','OpponentsOnFlop','OpponentsLeft',
    'NumberOfOpponentsAllin','NumberOfRaisesBeforeFlop','AmountToCall',
    'PotSize','randomhand'})
ACTIONS=frozenset({'RaiseHalfPot','Call','Fold','BetTwoThirdPot',
    'BetHalfPot','BetThirdPot','Check'})
RULE=re.compile(r'^WHEN \(([^()]+)\) (RETURN (?:TRUE|FALSE)|\w+) FORCE$')
REL=re.compile(r'^([A-Za-z][A-Za-z0-9]*) (<=|>=|=|<|>) (\d+(?:\.\d+)?)(% PotSize)?$')

class SourceError(ValueError):pass
@dataclass(frozen=True)
class Branch:
    atoms:tuple[str,...]
    action:str
    fallback:bool=False
@dataclass(frozen=True)
class Parsed:
    helpers:dict[str,tuple[Branch,...]]
    rules:dict[str,tuple[Branch,...]]


def parse(*sources:str)->Parsed:
    helpers={};streets={s:[] for s in STREETS}
    allstreet=set()
    for source in sources:
        current=None
        source_streets=set()
        for lineno,raw in enumerate(source.splitlines(),1):
            line=raw.strip()
            if not line:continue
            if line.startswith('//@STREET '):
                current=line.split(' ',1)[1]
                if current not in STREETS or current in source_streets:raise SourceError('duplicate/bad street marker')
                source_streets.add(current);allstreet.add(current);continue
            if line.startswith('//'):continue
            if line.startswith('##') and line.endswith('##'):
                current=line[2:-2]
                if current not in HELPERS or current in helpers:raise SourceError('unreviewed helper')
                helpers[current]=[];continue
            if current is None:raise SourceError(f'line {lineno} has no section')
            if line=='WHEN Others RETURN FALSE FORCE':
                if current in STREETS or any(b.fallback for b in helpers[current]):
                    raise SourceError('unsafe helper fallback')
                helpers[current].append(Branch((),'RETURN FALSE',True));continue
            m=RULE.fullmatch(line)
            if not m:raise SourceError(f'line {lineno} unreviewed OpenPPL syntax')
            atoms=tuple(m[1].split(' AND '));act=m[2]
            if len(atoms)!=len(set(atoms)):raise SourceError('duplicate atom')
            if current in STREETS:
                if act not in ACTIONS or not any(x in atoms for x in
                    ('f$H6CrowdedSRP','f$H6Crowded4','f$H6Crowded5',
                     'f$H6Crowded6','f$H6TransitionHU','f$H6Transition3',
                     'f$H6Transition4Plus')):raise SourceError('unguarded street action')
            elif act not in ('RETURN TRUE','RETURN FALSE'):raise SourceError('helper action illegal')
            for atom in atoms:
                x=atom.removeprefix('NOT ')
                if x in BOOLS or x in HELPERS or x=='Position = Last':continue
                r=REL.fullmatch(x)
                if not r or r[1] not in NUMERICS or (r[4] and r[1]!='AmountToCall'):
                    raise SourceError(f'unknown expression {atom}')
                if r[1]=='randomhand' and (r[2],r[3])!=('<','0.20'):
                    raise SourceError('unreviewed randomhand split')
            seq=streets[current] if current in STREETS else helpers[current]
            if seq and seq[-1].fallback:raise SourceError('dead code after fallback')
            seq.append(Branch(atoms,act))
    if set(helpers)!=HELPERS or allstreet!=set(STREETS):raise SourceError('missing helper/street')
    for key,values in helpers.items():
        if not values or not values[-1].fallback:raise SourceError(f'no boolean false fallback {key}')
    for street in STREETS:
        branches=streets[street]
        if not branches or any(x.fallback for x in branches):raise SourceError('invalid street')
        # Both modules must have an explicit check and fold in their own domain.
        for domain in ('f$H6CrowdedSRP','f$H6TransitionHU'):
            if not any(x.atoms==(domain,'AmountToCall = 0') and x.action=='Check' for x in branches):
                raise SourceError('missing guarded check')
            if not any(x.atoms==(domain,'AmountToCall > 0') and x.action=='Fold' for x in branches):
                raise SourceError('missing guarded fold')
    return Parsed({k:tuple(v) for k,v in helpers.items()},
                  {k:tuple(v) for k,v in streets.items()})


def parse_file()->Parsed:
    return parse(CROWDED.read_text(encoding='utf-8'),TRANSITION.read_text(encoding='utf-8'))


def observe(**overrides):
    d={k:False for k in BOOLS};d.update({k:0 for k in NUMERICS});d.update({
        'nplayersdealt':6,'OpponentsOnFlop':3,'OpponentsLeft':3,
        'NumberOfOpponentsAllin':0,'NumberOfRaisesBeforeFlop':0,
        'PotSize':10.,'AmountToCall':0.,'randomhand':0.70,'Position':'Last',
        'user_H6_RFIIntent':True,'BotRaisedBeforeFlop':True})
    if set(overrides)-(BOOLS|NUMERICS|{'Position'}):raise SourceError('invalid observed symbol')
    d.update(overrides);return d


def evaluate(model:Parsed,street:str,data:dict)->str|None:
    if street not in STREETS:raise SourceError('bad street')
    if set(data)!=BOOLS|NUMERICS|{'Position'}:raise SourceError('missing observation')
    if any(type(data[x]) is not bool for x in BOOLS):raise SourceError('not boolean')
    if any(type(data[x]) not in (int,float) or not math.isfinite(data[x]) for x in NUMERICS):
        raise SourceError('not finite number')
    if not 0<=data['randomhand']<1 or data['PotSize']<=0 or data['AmountToCall']<0:
        raise SourceError('invalid price or randomhand')
    if data['Position'] not in ('First','Middle','Last'):raise SourceError('invalid position')
    evaluating=set()
    def atom(a):
        if a.startswith('NOT '):return not atom(a[4:])
        if a in BOOLS:return data[a]
        if a in HELPERS:return helper(a)
        if a=='Position = Last':return data['Position']=='Last'
        r=REL.fullmatch(a)
        if not r:raise SourceError('unparsed rule')
        lhs=float(data[r[1]]);rhs=float(r[3]);cmp=r[2]
        if r[4]:rhs*=float(data['PotSize'])/100.0
        return {'=':lhs==rhs,'>':lhs>rhs,'<':lhs<rhs,'>=':lhs>=rhs,'<=':lhs<=rhs}[cmp]
    def helper(name):
        if name in evaluating:raise SourceError('circular helpers')
        evaluating.add(name)
        try:
            for rule in model.helpers[name]:
                if rule.fallback or all(atom(a) for a in rule.atoms):
                    return rule.action=='RETURN TRUE'
            raise SourceError('undefined helper')
        finally:evaluating.remove(name)
    for branch in model.rules[street]:
        if all(atom(a) for a in branch.atoms):return branch.action
    return None  # not equivalent to OH default.bot!
