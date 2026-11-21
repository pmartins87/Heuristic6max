"""Parser and test-only evaluator of actual OpenPPL limped BB postflop rules."""
from dataclasses import dataclass
from pathlib import Path
import math
import re
HERE=Path(__file__).resolve().parent
POLICY=HERE/'limped_bb_postflop.oppl'
CHECK=HERE/'limp_bb_preflop_capture.oppl'
HELPERS=frozenset({'f$H6LimpBBvsSB','f$H6LimpBBvsOther','f$H6LimpBBHU','f$H6LimpBBStrong'})
STREETS=('flop','turn','river')
BOOLS=frozenset({'StackUnknown','user_H6_RFIIntent','user_H6_3betIntent','user_H6_VSOpenCallIntent',
    'user_H6_LimpSBIntent','user_H6_LimpOtherIntent','BotCheckedPreflop','BotRaisedBeforeFlop',
    'BotCalledBeforeFlop','HaveNuts','HaveQuads','HaveFullHouse','HaveFlush','HaveStraight',
    'HaveSet','HaveTrips','HaveTwoPair','HaveOverPair','HaveTopPair','HaveBestKicker',
    'HaveNutFlushDraw','HaveOpenEndedStraightDraw','BotRaisedOnFlop'})
NUMS=frozenset({'nplayersdealt','OpponentsOnFlop','OpponentsLeft','NumberOfOpponentsAllin',
    'NumberOfRaisesBeforeFlop','AmountToCall','PotSize','randomhand'})
ACTIONS={'RaiseHalfPot','Call','Fold','BetTwoThirdPot','BetHalfPot','BetThirdPot','Check'}
RULE=re.compile(r'^WHEN \(([^()]+)\) (RETURN (?:TRUE|FALSE)|\w+) FORCE$')
REL=re.compile(r'^([A-Za-z][A-Za-z0-9]*) (<=|>=|=|<|>) (\d+(?:\.\d+)?)(% PotSize)?$')
class SourceError(ValueError):pass
@dataclass(frozen=True)
class Rule:
    atoms:tuple[str,...]
    action:str
    fallback:bool=False
@dataclass(frozen=True)
class Source:
    helpers:dict[str,tuple[Rule,...]]
    rules:dict[str,tuple[Rule,...]]

def parse(s):
    helpers={};streets={k:[] for k in STREETS};street_seen=set();current=None
    for lineno,original in enumerate(s.splitlines(),1):
        line=original.strip()
        if not line:continue
        if line.startswith('//@STREET '):
            current=line.split(' ',1)[1]
            if current not in STREETS or current in street_seen:raise SourceError('bad street')
            street_seen.add(current);continue
        if line.startswith('//'):continue
        if line.startswith('##') and line.endswith('##'):
            current=line[2:-2]
            if current not in HELPERS or current in helpers:raise SourceError('bad helper')
            helpers[current]=[];continue
        if current is None:raise SourceError('rule without section')
        seq=streets[current] if current in STREETS else helpers[current]
        if line=='WHEN Others RETURN FALSE FORCE':
            if current in STREETS or (seq and seq[-1].fallback):raise SourceError('bad fallback')
            seq.append(Rule((),'RETURN FALSE',True));continue
        m=RULE.fullmatch(line)
        if not m:raise SourceError(f'line {lineno} unsupported')
        atoms=tuple(m[1].split(' AND '));action=m[2]
        if len(atoms)!=len(set(atoms)):raise SourceError('duplicate atom')
        if current in STREETS:
            if action not in ACTIONS or not any(x in atoms for x in HELPERS if x in
                     ('f$H6LimpBBHU','f$H6LimpBBvsSB','f$H6LimpBBvsOther')):
                raise SourceError('street action unguarded')
        elif action not in ('RETURN TRUE','RETURN FALSE'):raise SourceError('helper action illegal')
        for a in atoms:
            x=a.removeprefix('NOT ')
            if x in BOOLS|HELPERS or x=='Position = Last':continue
            r=REL.fullmatch(x)
            if not r or r[1] not in NUMS or (r[4] and r[1]!='AmountToCall'):
                raise SourceError('unsupported atom '+a)
            if r[1]=='randomhand' and (r[2],r[3])!=('<','0.35'):
                raise SourceError('unreviewed random')
        if seq and seq[-1].fallback:raise SourceError('dead branch')
        seq.append(Rule(atoms,action))
    if set(helpers)!=HELPERS or street_seen!=set(STREETS):raise SourceError('missing section')
    if not all(helpers[x][-1].fallback for x in HELPERS):raise SourceError('helper false fallback missing')
    for street in STREETS:
        if not any(x.atoms==('f$H6LimpBBHU','AmountToCall > 0') and x.action=='Fold' for x in streets[street]):
            raise SourceError('missing priced fold')
        if not any(x.atoms==('f$H6LimpBBHU','AmountToCall = 0') and x.action=='Check' for x in streets[street]):
            raise SourceError('missing check')
    return Source({k:tuple(v) for k,v in helpers.items()},
                  {k:tuple(v) for k,v in streets.items()})

def parse_file():return parse(POLICY.read_text(encoding='utf-8'))

def observe(**change):
    o={k:False for k in BOOLS};o.update({k:0 for k in NUMS});o.update({
        'nplayersdealt':6,'OpponentsOnFlop':1,'OpponentsLeft':1,'PotSize':5,
        'NumberOfOpponentsAllin':0,'randomhand':.7,'Position':'Last',
        'user_H6_LimpSBIntent':True,'BotCheckedPreflop':True})
    if set(change)-(BOOLS|NUMS|{'Position'}):raise SourceError('unknown observed')
    o.update(change);return o

def evaluate(model,street,o):
    if street not in STREETS or set(o)!=BOOLS|NUMS|{'Position'}:raise SourceError('bad input')
    if any(type(o[x]) is not bool for x in BOOLS):raise SourceError('bad bool')
    if any(type(o[x]) not in (int,float) or not math.isfinite(o[x]) for x in NUMS):raise SourceError('bad number')
    if not 0<=o['randomhand']<1 or o['PotSize']<=0 or o['AmountToCall']<0:raise SourceError('bad pot/random')
    if o['Position'] not in ('First','Middle','Last'):raise SourceError('bad position')
    active=set()
    def atom(a):
        if a.startswith('NOT '):return not atom(a[4:])
        if a in BOOLS:return o[a]
        if a in HELPERS:return fn(a)
        if a=='Position = Last':return o['Position']=='Last'
        m=REL.fullmatch(a)
        if not m:raise SourceError('bad expression')
        lhs=float(o[m[1]]);rhs=float(m[3])
        if m[4]:rhs*=float(o['PotSize'])/100
        return {'=':lhs==rhs,'<':lhs<rhs,'>':lhs>rhs,'<=':lhs<=rhs,'>=':lhs>=rhs}[m[2]]
    def fn(k):
        if k in active:raise SourceError('cycle')
        active.add(k)
        try:
            for r in model.helpers[k]:
                if r.fallback or all(atom(x) for x in r.atoms):return r.action=='RETURN TRUE'
            raise SourceError('helper no fallback')
        finally:active.remove(k)
    for r in model.rules[street]:
        if all(atom(x) for x in r.atoms):return r.action
    return None
