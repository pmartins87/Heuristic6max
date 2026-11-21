"""OpenPPL source-based offline interpreter for ISODEF-1 strict two-spot isolation defense.

Uses all ancestor helper rules from source, not reimplemented strategies.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re,math,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'blind_iso_v2'))
import blind_iso_interpreter as prev
from build_defense import TOPOLOGY, POLICY, PREFLOP, HAND
STREETS=prev.STREETS
BOOLS=prev.BOOLS|{"user_H6_DEF_BTN3","user_H6_DEF_BTNC","user_H6_DEF_BB3","user_H6_DEF_BBC"}
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
                     ('f$H6DEFValid','f$H6DEFHU','f$H6DEFTwo',
                      'f$H6BISOCrowded')):raise SourceError('action lacks strict domain')
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
            if not any(x.atoms==('f$H6DEFValid',price) and x.action==act for x in streets[s]):
                raise SourceError('missing guarded fallback')
    helpers={k:tuple(Rule(x.atoms,x.action,x.fallback) for x in v) for k,v in old.helpers.items()}
    helpers.update({k:tuple(v) for k,v in new.items()})
    return Parsed(helpers,{k:tuple(v) for k,v in streets.items()})

def parse_file():return parse(TOPOLOGY.read_text(),POLICY.read_text())

def observe(street='flop',**kwargs):
    data=prev.observe(street)
    data.update({x:False for x in BOOLS if x not in data})
    data.update({x:False for x in BOOLS if x.startswith('user_H6_')})
    data.update({
        'BotRaisedBeforeFlop':False,'BotCalledBeforeFlop':True,
        'BotCheckedPreflop':False,'NumberOfRaisesBeforeFlop':1,
        'OpponentsOnFlop':2,'OpponentsOnTurn':2,
        'OpponentsOnRiver':2,'OpponentsLeft':2,
        'user_H6_DEF_BTNC':True})
    if set(kwargs)-(BOOLS|NUMS|{'Position'}):raise SourceError('unknown observation')
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

# First-match OpenPPL preflop evaluator: parse the ACTUAL authored handlists/WHENs.
# The interpreter never embeds or generates poker ranges.
from dataclasses import dataclass as _dataclass

@_dataclass(frozen=True)
class PFRule:
    atoms:tuple[str,...]
    action:str

@_dataclass(frozen=True)
class PFSource:
    lists:dict[str,frozenset[str]]
    rules:tuple[PFRule,...]

PFRULE=re.compile(r'^WHEN \(([^()]*)\) (Set user_H6_DEF_\w+|RaiseTo [0-9.]+ FORCE|Call FORCE|Fold FORCE)$')
PFREL=re.compile(r'^(\w+) (<=|>=|=|<|>) ([0-9.]+)$')
PFNUMS={'nplayersdealt','Raises','Calls','StackSize','MinOpponentStackSize',
        'MaxOpponentStackSize','StillToAct','FirstRaiserPosition',
        'LastRaiserPosition','PotSize','AmountToCall'}
PFBOOLS={'IsPreflop','StackUnknown','InButton','InBigBlind'}

def parse_preflop(hand_text:str,rule_text:str)->PFSource:
    names=list(re.finditer(r'^##(listH6DEF\w+)##\s*$',hand_text,re.M))
    if len(names)!=3:raise SourceError('three explicit handlists required')
    lists={}
    for idx,match in enumerate(names):
        end=names[idx+1].start() if idx+1<len(names) else len(hand_text)
        raw=hand_text[match.end():end].strip()
        classes=raw.split()
        if not classes or len(classes)!=len(set(classes)):
            raise SourceError('empty or duplicated class list')
        if any(not re.fullmatch(r'[AKQJT98765432]{2}[so]?',x) for x in classes):
            raise SourceError('invalid class token')
        lists[match[1]]=frozenset(classes)
    if set(lists)!={'listH6DEF3BET','listH6DEFCALLBTN','listH6DEFCALLBB'}:
        raise SourceError('wrong handlists')
    if lists['listH6DEF3BET'] & (lists['listH6DEFCALLBTN']|lists['listH6DEFCALLBB']):
        raise SourceError('3bet and call range overlap')
    rules=[]
    for line in rule_text.splitlines():
        if not line or line.lstrip().startswith('//'):continue
        m=PFRULE.fullmatch(line)
        if not m:raise SourceError('unknown preflop action syntax '+line)
        atoms=tuple(m[1].split(' AND '))
        if len(set(atoms))!=len(atoms):raise SourceError('duplicate preflop guard')
        for atom in atoms:
            atom=atom.removeprefix('NOT ')
            if atom in PFBOOLS or atom in lists:continue
            rel=PFREL.fullmatch(atom)
            if not rel or rel[1] not in PFNUMS:raise SourceError('unknown preflop symbol '+atom)
            if not (float('inf')>float(rel[3])>=0):raise SourceError('bad preflop numeric')
        rules.append(PFRule(atoms,m[2]))
    if len(rules)!=10:raise SourceError('2 contexts x 5 rules required')
    for k in range(0,10,5):
        set3,raise3,setc,call,fold=rules[k:k+5]
        if set3.atoms!=raise3.atoms or setc.atoms!=call.atoms:
            raise SourceError('intent missing matching action')
        if not (set3.action.startswith('Set user_H6_DEF_') and
                raise3.action.startswith('RaiseTo ') and
                setc.action.startswith('Set user_H6_DEF_') and
                call.action=='Call FORCE' and fold.action=='Fold FORCE'):
            raise SourceError('not 3bet -> call -> fold order')
        if set3.atoms[-1]!='listH6DEF3BET' or not setc.atoms[-1].startswith('listH6DEFCALL'):
            raise SourceError('wrong preflop range')
        if fold.atoms != set3.atoms[:-1] or fold.atoms != setc.atoms[:-1]:
            raise SourceError('broad fallback or guards inconsistent')
    return PFSource(lists,tuple(rules))

def preflop_file()->PFSource:
    return parse_preflop(HAND.read_text(),PREFLOP.read_text())

def preflop_state(hand='AKs',**kw):
    state={'IsPreflop':True,'StackUnknown':False,'nplayersdealt':6,'Raises':1,
           'Calls':1,'StackSize':100,'MinOpponentStackSize':99,
           'MaxOpponentStackSize':100,'StillToAct':2,
           'FirstRaiserPosition':3,'LastRaiserPosition':3,
           'PotSize':7,'AmountToCall':4.5,'InButton':True,'InBigBlind':False,
           'hand':hand}
    if set(kw)-set(state):raise SourceError('unknown preflop input')
    state.update(kw)
    return state

def preflop_evaluate(source:PFSource,state:dict)->tuple[str|None,tuple[str,...]]:
    if set(state)!=(PFNUMS|PFBOOLS|{'hand'}):raise SourceError('incomplete preflop state')
    if any(type(state[k]) is not bool for k in PFBOOLS):raise SourceError('bad preflop bool')
    if any(type(state[k]) not in (int,float) or not math.isfinite(state[k]) for k in PFNUMS):
        raise SourceError('bad preflop number')
    if not isinstance(state['hand'],str) or not state['hand']:
        raise SourceError('bad handclass')
    def atom(x):
        if x.startswith('NOT '):return not atom(x[4:])
        if x in PFBOOLS:return state[x]
        if x in source.lists:return state['hand'] in source.lists[x]
        m=PFREL.fullmatch(x)
        if not m:raise SourceError('unknown preflop atom')
        value=float(state[m[1]]);rhs=float(m[3])
        return {'=':value==rhs,'>':value>rhs,'<':value<rhs,
                '>=':value>=rhs,'<=':value<=rhs}[m[2]]
    tags=[]
    for rule in source.rules:
        if all(atom(x) for x in rule.atoms):
            if rule.action.startswith('Set '):
                tags.append(rule.action[4:])
                continue
            if len(tags)>1:raise SourceError('two intent tags matched')
            if rule.action.startswith('RaiseTo '):
                return rule.action,tuple(tags)
            return rule.action,tuple(tags)
    return None,tuple(tags)
