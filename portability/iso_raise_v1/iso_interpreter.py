"""OpenPPL source-based offline interpreter for ISO-1 draft pots.

Uses all ancestor helper rules from source, not reimplemented strategies.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re,math,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'p3bet_multiway_v1'))
import mw3b_interpreter as prev
from build_iso import TOPOLOGY, POLICY
STREETS=prev.STREETS
BOOLS=prev.BOOLS|{'user_H6_ISOCO1','user_H6_ISOCO2','user_H6_ISOBTN1','user_H6_ISOBTN2','user_H6_ISOBTN3'}
NUMS=prev.NUMS
ACTIONS=prev.ACTIONS
RULE=prev.RULE
REL=prev.REL
class SourceError(ValueError):pass
@dataclass(frozen=True)
class Rule:
    atoms:tuple[str,...]
    action:str
    fallback:bool=False
@dataclass(frozen=True)
class Parsed:
    helpers:dict[str,tuple[Rule,...]]
    streets:dict[str,tuple[Rule,...]]

def parse(topology,policy):
    old=prev.parse_file()
    recognized=set(old.helpers)
    for s in (topology,policy):
        for name in re.findall(r'^##(f\$[^#]+)##$',s,re.M):
            if name in recognized:raise SourceError('duplicate helper')
            recognized.add(name)
    new={};streets={k:[] for k in STREETS};seen=set()
    for s in (topology,policy):
        current=None
        for line in s.splitlines():
            line=line.strip()
            if not line or line.startswith('//') and not line.startswith('//@STREET '):continue
            if line.startswith('//@STREET '):
                current=line.split(' ',1)[1]
                if current not in STREETS or current in seen:raise SourceError('duplicate street')
                seen.add(current);continue
            if line.startswith('##') and line.endswith('##'):
                current=line[2:-2]
                if current in new or current in old.helpers:raise SourceError('duplicate')
                new[current]=[];continue
            if current is None:raise SourceError('missing section')
            seq=streets[current] if current in STREETS else new[current]
            if line=='WHEN Others RETURN FALSE FORCE':
                if current in STREETS or (seq and seq[-1].fallback):raise SourceError('bad fallback')
                seq.append(Rule((),'RETURN FALSE',True));continue
            m=RULE.fullmatch(line)
            if m is None:raise SourceError('unreviewed source rule')
            atoms=tuple(m[1].split(' AND '));action=m[2]
            if len(atoms)!=len(set(atoms)):raise SourceError('duplicate atom')
            if current in STREETS:
                if action not in ACTIONS or not any(x in atoms for x in
                     ('f$H6ISOValid','f$H6ISOHU','f$H6ISOTwo',
                      'f$H6ISOCrowded')):raise SourceError('action lacks strict domain')
            elif action not in ('RETURN TRUE','RETURN FALSE'):raise SourceError('bad helper action')
            for atom in atoms:
                x=atom.removeprefix('NOT ')
                if x in BOOLS|recognized or x=='Position = Last':continue
                r=REL.fullmatch(x)
                if not r or r[1] not in NUMS or (r[4] and r[1]!='AmountToCall'):
                    raise SourceError('unknown symbol '+x)
                if r[1]=='randomhand':raise SourceError('new random split')
            if seq and seq[-1].fallback:raise SourceError('shadowed WHEN')
            seq.append(Rule(atoms,action))
    if len(new)!=7 or seen!=set(STREETS):raise SourceError('wrong helper or street count')
    if not all(v and v[-1].fallback for v in new.values()):raise SourceError('unsafe function')
    for s in STREETS:
        for price,act in [('AmountToCall > 0','Fold'),('AmountToCall = 0','Check')]:
            if not any(x.atoms==('f$H6ISOValid',price) and x.action==act for x in streets[s]):
                raise SourceError('missing guarded fallback')
    helpers={k:tuple(Rule(x.atoms,x.action,x.fallback) for x in v) for k,v in old.helpers.items()}
    helpers.update({k:tuple(v) for k,v in new.items()})
    return Parsed(helpers,{k:tuple(v) for k,v in streets.items()})

def parse_file():return parse(TOPOLOGY.read_text(),POLICY.read_text())

def observe(street='flop',**kwargs):
    data=prev.observe(street)
    data.update({x:False for x in BOOLS if x not in data})
    data.update({
        'user_H6_3betIntent':False,'user_H6_RFIIntent':False,
        'user_H6_VSOpenCallIntent':False,'BotRaisedBeforeFlop':True,
        'BotCalledBeforeFlop':False,'NumberOfRaisesBeforeFlop':0,
        'user_H6_ISOBTN1':True,'OpponentsOnFlop':2,
        'OpponentsOnTurn':2,'OpponentsOnRiver':2,'OpponentsLeft':2})
    if set(kwargs)-(BOOLS|NUMS|{'Position'}):raise SourceError('unknown input')
    data.update(kwargs)
    return data

def evaluate(model,street,data):
    if street not in STREETS or set(data)!=(BOOLS|NUMS|{'Position'}):raise SourceError('incomplete observed state')
    if any(type(data[x]) is not bool for x in BOOLS):raise SourceError('bad bool')
    if any(type(data[x]) not in (int,float) or not math.isfinite(data[x]) for x in NUMS):raise SourceError('bad number')
    if data['AmountToCall']<0 or data['PotSize']<=0 or not 0<=data['randomhand']<1:raise SourceError('bad price')
    if data['Position'] not in ('First','Middle','Last'):raise SourceError('bad position')
    if (data['IsFlop'],data['IsTurn'],data['IsRiver'])!=tuple(street==x for x in STREETS):raise SourceError('inconsistent street')
    active=set()
    def atom(a):
        if a.startswith('NOT '):return not atom(a[4:])
        if a in BOOLS:return data[a]
        if a in model.helpers:return fn(a)
        if a=='Position = Last':return data['Position']=='Last'
        m=REL.fullmatch(a)
        if m is None:raise SourceError('unknown token')
        lhs=float(data[m[1]]);rhs=float(m[3])
        if m[4]:rhs*=float(data['PotSize'])/100
        return {'=':lhs==rhs,'<':lhs<rhs,'>':lhs>rhs,'<=':lhs<=rhs,'>=':lhs>=rhs}[m[2]]
    def fn(name):
        if name in active:raise SourceError('recursive helper')
        active.add(name)
        try:
            for rule in model.helpers[name]:
                if rule.fallback or all(atom(x) for x in rule.atoms):
                    return rule.action=='RETURN TRUE'
            raise SourceError('helper missing fallback')
        finally:active.remove(name)
    for rule in model.streets[street]:
        if all(atom(x) for x in rule.atoms):return rule.action
    return None
