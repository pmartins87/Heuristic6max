"""Restricted offline evaluator of the actual partial-multiway OpenPPL text.

Imports only upstream source-defined helper AST. NOT an independent strategy.
No OpenHoldem runtime connection; no fallback assertion.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re, math, sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'multiway_v2'))
import multiway_interpreter as prev
from build_transitions_v3 import HELPERS as GATE, POLICY
STREETS=('flop','turn','river')
NUMS=prev.NUMERICS|{'OpponentsOnTurn','OpponentsOnRiver'}
BOOLS=prev.BOOLS|{'IsFlop','IsTurn','IsRiver'}
RULE=re.compile(r'^WHEN \(([^()]+)\) (RETURN (?:TRUE|FALSE)|\w+) FORCE$')
REL=prev.REL
ACTIONS=prev.ACTIONS

class SourceError(ValueError):pass
@dataclass(frozen=True)
class Rule:
    atoms:tuple[str,...]
    action:str
    fallback:bool=False
@dataclass(frozen=True)
class Model:
    helpers:dict[str,tuple[Rule,...]]
    rules:dict[str,tuple[Rule,...]]


def parse(gates:str,policy:str)->Model:
    upstream=prev.parse_file()
    helper_names={*upstream.helpers}
    for text in (gates,policy):
        for header in re.findall(r'^##(f\$[^#]+)##$',text,re.M):
            if header in helper_names:raise SourceError('duplicate helper')
            helper_names.add(header)
    helpers={}
    streets={k:[] for k in STREETS}
    seen_streets=set()
    for text in (gates,policy):
        current=None
        for ln,raw in enumerate(text.splitlines(),1):
            line=raw.strip()
            if not line or line.startswith('//') and not line.startswith('//@STREET '):continue
            if line.startswith('//@STREET '):
                current=line.split(' ',1)[1]
                if current not in STREETS or current in seen_streets:raise SourceError('bad street marker')
                seen_streets.add(current);continue
            if line.startswith('##') and line.endswith('##'):
                current=line[2:-2]
                if current in helpers or current in upstream.helpers:raise SourceError('duplicated helper')
                helpers[current]=[];continue
            if current is None:raise SourceError(f'line {ln}: missing section')
            seq=streets[current] if current in STREETS else helpers[current]
            if line=='WHEN Others RETURN FALSE FORCE':
                if current in STREETS or any(x.fallback for x in seq):raise SourceError('unsafe fallback')
                seq.append(Rule((),'RETURN FALSE',True));continue
            m=RULE.fullmatch(line)
            if not m:raise SourceError(f'line {ln}: bad rule {line[:50]}')
            atoms=tuple(m[1].split(' AND '));action=m[2]
            if len(set(atoms))!=len(atoms):raise SourceError('repeated condition')
            if current in STREETS:
                if action not in ACTIONS or not any(x in atoms for x in
                    ('f$H6PartialF','f$H6PartialT','f$H6PartialR',
                     *[f'f$H6Partial{s}{n}' for s in 'FTR' for n in (2,3,4)])):
                    raise SourceError('unguarded action')
            elif action not in ('RETURN TRUE','RETURN FALSE'):raise SourceError('helper action')
            for atom in atoms:
                t=atom.removeprefix('NOT ')
                if t in BOOLS or t in helper_names or t=='Position = Last':continue
                mr=REL.fullmatch(t)
                if not mr or mr[1] not in NUMS or (mr[4] and mr[1]!='AmountToCall'):
                    raise SourceError('unsupported expression '+atom)
                if mr[1]=='randomhand' and (mr[2],mr[3])!=('<','0.20'):
                    raise SourceError('unknown mixed action frequency')
            if seq and seq[-1].fallback:raise SourceError('dead rule')
            seq.append(Rule(atoms,action))
    if seen_streets!=set(STREETS):raise SourceError('missing street')
    if len(helpers)!=13 or any(not v or not v[-1].fallback for v in helpers.values()):
        raise SourceError('not all topology helpers defined/fail-safe')
    for street,short in (('flop','F'),('turn','T'),('river','R')):
        domain='f$H6Partial'+short
        if not any(r.atoms==(domain,'AmountToCall = 0') and r.action=='Check' for r in streets[street]):
            raise SourceError('missing check')
        if not any(r.atoms==(domain,'AmountToCall > 0') and r.action=='Fold' for r in streets[street]):
            raise SourceError('missing priced fold')
    all_helpers={k:tuple(Rule(x.atoms,x.action,x.fallback) for x in v) for k,v in upstream.helpers.items()}
    all_helpers.update({k:tuple(v) for k,v in helpers.items()})
    return Model(all_helpers,{k:tuple(v) for k,v in streets.items()})


def parse_file():return parse(GATE.read_text(encoding='utf-8'),POLICY.read_text(encoding='utf-8'))


def observe(street='flop',**updates):
    if street not in STREETS:raise SourceError('unknown street')
    p=prev.observe()
    p.update({'OpponentsOnFlop':5,'OpponentsOnTurn':4,'OpponentsOnRiver':3,
              'OpponentsLeft':2,'IsFlop':street=='flop','IsTurn':street=='turn',
              'IsRiver':street=='river'})
    if set(updates)-(BOOLS|NUMS|{'Position'}):raise SourceError('unknown observed value')
    p.update(updates)
    return p


def evaluate(model:Model,street:str,o:dict):
    if street not in STREETS or set(o)!=(BOOLS|NUMS|{'Position'}):raise SourceError('unknown input')
    if any(type(o[k]) is not bool for k in BOOLS):raise SourceError('bad bool')
    if any(type(o[k]) not in (int,float) or not math.isfinite(o[k]) for k in NUMS):raise SourceError('bad number')
    if not (0<=o['randomhand']<1 and o['PotSize']>0 and o['AmountToCall']>=0):raise SourceError('bad price/random')
    if o['Position'] not in ('First','Middle','Last'):raise SourceError('bad position')
    if (o['IsFlop'],o['IsTurn'],o['IsRiver'])!=tuple(s==street for s in STREETS):
        raise SourceError('contradictory street flags')
    active=set()
    def atom(token):
        if token.startswith('NOT '):return not atom(token[4:])
        if token in BOOLS:return o[token]
        if token in model.helpers:return helper(token)
        if token=='Position = Last':return o['Position']=='Last'
        r=REL.fullmatch(token)
        if not r:raise SourceError('bad token')
        lhs=float(o[r[1]]);rhs=float(r[3])
        if r[4]:rhs=rhs*float(o['PotSize'])/100
        return {'=':lhs==rhs,'>':lhs>rhs,'<':lhs<rhs,'<=':lhs<=rhs,'>=':lhs>=rhs}[r[2]]
    def helper(name):
        if name in active:raise SourceError('cycle')
        active.add(name)
        try:
            for rule in model.helpers[name]:
                if rule.fallback or all(atom(a) for a in rule.atoms):
                    return rule.action=='RETURN TRUE'
            raise SourceError('missing false fallback')
        finally:active.remove(name)
    for rule in model.rules[street]:
        if all(atom(a) for a in rule.atoms):return rule.action
    return None # never assumes a safe OpenHoldem fallback
