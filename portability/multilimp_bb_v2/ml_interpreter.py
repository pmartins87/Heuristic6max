"""Restricted offline source evaluator for BB-versus-multiple-limp OpenPPL.

Consumes PREVIOUS generated OpenPPL helper AST, not a parallel poker policy.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import sys, re, math
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'multiway_transitions_v3'))
import source_interpreter as prev
from build_multilimp import HELPERS as TOPOLOGY, STRATEGY, INTENTS
STREETS=prev.STREETS
BOOLS=prev.BOOLS|{'BotCheckedPreflop'}|{tag for _,_,tag in INTENTS}|{'user_H6_LimpSBIntent','user_H6_LimpOtherIntent'}
NUMS=prev.NUMS
ACTIONS=prev.ACTIONS
REL=prev.REL
RULE=prev.RULE

class SourceError(ValueError):pass
@dataclass(frozen=True)
class Branch:
    atoms:tuple[str,...]
    action:str
    fallback:bool=False
@dataclass(frozen=True)
class Model:
    helpers:dict[str,tuple[Branch,...]]
    rules:dict[str,tuple[Branch,...]]


def parse(topology,policy):
    upstream=prev.parse_file()
    helper_names=set(upstream.helpers)
    for data in (topology,policy):
        for h in re.findall(r'^##(f\$[^#]+)##$',data,re.M):
            if h in helper_names:raise SourceError('duplicate helper')
            helper_names.add(h)
    helpers={};rules={s:[] for s in STREETS};seen=set()
    for data in (topology,policy):
        at=None
        for number,raw in enumerate(data.splitlines(),1):
            line=raw.strip()
            if not line or (line.startswith('//') and not line.startswith('//@STREET ')):continue
            if line.startswith('//@STREET '):
                at=line.split(' ',1)[1]
                if at not in STREETS or at in seen:raise SourceError('bad street')
                seen.add(at);continue
            if line.startswith('##') and line.endswith('##'):
                at=line[2:-2]
                if at in helpers or at in upstream.helpers:raise SourceError('duplicate helper body')
                helpers[at]=[];continue
            if at is None:raise SourceError('missing section')
            seq=rules[at] if at in STREETS else helpers[at]
            if line=='WHEN Others RETURN FALSE FORCE':
                if at in STREETS or (seq and seq[-1].fallback):raise SourceError('unsafe fallback')
                seq.append(Branch((),'RETURN FALSE',True));continue
            rm=RULE.fullmatch(line)
            if rm is None:raise SourceError(f'unrecognized syntax {line[:80]}')
            atoms=tuple(rm[1].split(' AND '));action=rm[2]
            if len(atoms)!=len(set(atoms)):raise SourceError('duplicate atom')
            if at in STREETS:
                if action not in ACTIONS or not any(x in atoms for x in
                    ('f$H6MLValid','f$H6MLHU','f$H6MLTwo','f$H6MLCrowded')):
                    raise SourceError('unguarded action')
            elif action not in ('RETURN TRUE','RETURN FALSE'):raise SourceError('unknown helper action')
            for raw_atom in atoms:
                a=raw_atom.removeprefix('NOT ')
                if a in BOOLS|helper_names or a=='Position = Last':continue
                match=REL.fullmatch(a)
                if (not match or match[1] not in NUMS or
                    (match[4] and match[1]!='AmountToCall')):
                    raise SourceError('unsupported atom '+raw_atom)
                if match[1]=='randomhand':raise SourceError('new mix unsupported')
            if seq and seq[-1].fallback:raise SourceError('dead code after fallback')
            seq.append(Branch(atoms,action))
    if seen!=set(STREETS) or len(helpers)!=9:raise SourceError('wrong helper count')
    if not all(v[-1].fallback for v in helpers.values()):raise SourceError('unsafe boolean fallback')
    for s in STREETS:
        for check in ('AmountToCall > 0','AmountToCall = 0'):
            action='Fold' if '>' in check else 'Check'
            if not any(x.atoms==('f$H6MLValid',check) and x.action==action for x in rules[s]):
                raise SourceError('missing scoped priced fallback')
    result={k:tuple(Branch(vv.atoms,vv.action,vv.fallback) for vv in v) for k,v in upstream.helpers.items()}
    result.update({k:tuple(v) for k,v in helpers.items()})
    return Model(result,{s:tuple(v) for s,v in rules.items()})


def parse_file():return parse(TOPOLOGY.read_text(),STRATEGY.read_text())


def observe(street='flop',**kwargs):
    if street not in STREETS:raise SourceError('invalid street')
    obs=prev.observe(street)
    obs.update({k:False for k in BOOLS if k not in obs})
    obs.update({'user_H6_RFIIntent':False,'BotRaisedBeforeFlop':False,
                'BotCheckedPreflop':True,'user_H6_ML2SB':True,
                'OpponentsOnFlop':2,'OpponentsOnTurn':2,'OpponentsOnRiver':2,
                'OpponentsLeft':2})
    if set(kwargs)-(BOOLS|NUMS|{'Position'}):raise SourceError('unknown observation')
    obs.update(kwargs)
    return obs


def evaluate(model,street,o):
    if street not in STREETS or set(o)!=(BOOLS|NUMS|{'Position'}):raise SourceError('missing inputs')
    if any(type(o[k]) is not bool for k in BOOLS):raise SourceError('not bool')
    if any(type(o[k]) not in (int,float) or not math.isfinite(o[k]) for k in NUMS):raise SourceError('bad numeric')
    if not 0<=o['randomhand']<1 or o['AmountToCall']<0 or o['PotSize']<=0:raise SourceError('bad price')
    if o['Position'] not in ('First','Middle','Last'):raise SourceError('bad position')
    if (o['IsFlop'],o['IsTurn'],o['IsRiver'])!=tuple(s==street for s in STREETS):
        raise SourceError('bad street flags')
    active=set()
    def atom(a):
        if a.startswith('NOT '):return not atom(a[4:])
        if a in BOOLS:return o[a]
        if a in model.helpers:return helper(a)
        if a=='Position = Last':return o['Position']=='Last'
        m=REL.fullmatch(a)
        if not m:raise SourceError('unknown symbol')
        lhs=float(o[m[1]]);rhs=float(m[3])
        if m[4]:rhs*=float(o['PotSize'])/100
        return {'=':lhs==rhs,'>':lhs>rhs,'<':lhs<rhs,'<=':lhs<=rhs,'>=':lhs>=rhs}[m[2]]
    def helper(name):
        if name in active:raise SourceError('cycle')
        active.add(name)
        try:
            for rule in model.helpers[name]:
                if rule.fallback or all(atom(x) for x in rule.atoms):return rule.action=='RETURN TRUE'
            raise SourceError('missing fallback')
        finally:active.remove(name)
    for rule in model.rules[street]:
        if all(atom(a) for a in rule.atoms):return rule.action
    return None
