"""PORT-2 test interpreter of the exact *.oppl lines; NOT an OpenHoldem engine.

All strategy choices come from OpenPPL handlists and ordered WHEN statements.
Python only maps documented observation symbols to test inputs. A no-match
returns None in this interpreter but is NOT a safety guarantee in OpenHoldem.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from portability.port1.port1_interpreter import ALL_HANDS, GUARD, Context as BaseContext, PortabilityError

SOURCE = Path(__file__).with_name('lj_rfi_mixed_port2.oppl')
RAISE = 'listPORT2LJRAISE'
FOLD = 'listPORT2LJFOLD'
MIX = 'listPORT2LJMIX'
ALL_LISTS = (RAISE, FOLD, MIX)
LIST_RE = re.compile(r'^##(listPORT2LJRAISE|listPORT2LJFOLD|listPORT2LJMIX)##$')
RULE_RE = re.compile(r'^WHEN \(([^()]+)\) (RaiseTo 2\.5|Fold) FORCE$')
RAND_RE = re.compile(r'^randomhand (<|>=) (0\.40)$')

@dataclass(frozen=True)
class Context(BaseContext):
    randomhand: float | None = None  # injected OpenHoldem symbol, NOT Python RNG

@dataclass(frozen=True)
class Rule:
    atoms: tuple[str,...]
    action: str

@dataclass(frozen=True)
class Parsed:
    lists: dict[str,frozenset[str]]
    rules: tuple[Rule,...]


def parse(source: str) -> Parsed:
    lists:dict[str,set[str]]={}
    rules:list[Rule]=[]
    section=None
    seen_preflop=False
    for line_no, original in enumerate(source.splitlines(),1):
        line=original.strip()
        if not line or line.startswith('//'):
            continue
        match=LIST_RE.fullmatch(line)
        if match:
            if seen_preflop or match[1] in lists:
                raise PortabilityError(f'line {line_no}: misplaced or repeated list')
            section=match[1]
            lists[section]=set()
            continue
        if line=='##f$preflop##':
            if seen_preflop or set(lists)!=set(ALL_LISTS):
                raise PortabilityError(f'line {line_no}: preflop section misplaced')
            seen_preflop=True
            section='preflop'
            continue
        if section in ALL_LISTS:
            tokens=line.split()
            if not tokens or any(hand not in ALL_HANDS for hand in tokens):
                raise PortabilityError(f'line {line_no}: not a recognized hand class')
            if len(set(tokens))!=len(tokens) or lists[section].intersection(tokens):
                raise PortabilityError(f'line {line_no}: duplicate class')
            lists[section].update(tokens)
            continue
        if section!='preflop':
            raise PortabilityError(f'line {line_no}: missing preflop section')
        rm=RULE_RE.fullmatch(line)
        if rm is None:
            raise PortabilityError(f'line {line_no}: not in audited OpenPPL subset')
        atoms=tuple(rm[1].split(' AND '))
        if atoms[:len(GUARD)]!=GUARD or len(atoms)!=len(GUARD)+(2 if len(rules)>=2 else 1):
            raise PortabilityError(f'line {line_no}: wrong guard or atom count')
        if len(set(atoms))!=len(atoms):
            raise PortabilityError(f'line {line_no}: duplicate atom')
        rules.append(Rule(atoms,rm[2]))

    if not seen_preflop or len(rules)!=4:
        raise PortabilityError('Exactly 4 ordered rules required')
    if set(lists)!=set(ALL_LISTS) or set.union(*lists.values())!=ALL_HANDS:
        raise PortabilityError('All 169 hand classes must be mapped')
    if any(lists[a].intersection(lists[b]) for a in ALL_LISTS for b in ALL_LISTS if a<b):
        raise PortabilityError('Overlapping handlists')
    if (len(lists[RAISE]),len(lists[FOLD]),lists[MIX]) != (43,125,{'KJo'}):
        raise PortabilityError('Unexpected base range or mix target')
    expected=((RAISE,None,'RaiseTo 2.5'),(FOLD,None,'Fold'),
              (MIX,'randomhand < 0.40','RaiseTo 2.5'),
              (MIX,'randomhand >= 0.40','Fold'))
    for rule,(target,rand,action) in zip(rules,expected):
        if rule.action!=action or rule.atoms[len(GUARD)]!=target:
            raise PortabilityError('Action/handlist order differs from reviewed design')
        if rand is not None and (len(rule.atoms)!=len(GUARD)+2 or rule.atoms[-1]!=rand
                                or not RAND_RE.fullmatch(rand)):
            raise PortabilityError('Not an audited hand-stable 40/60 split')
    return Parsed({k:frozenset(v) for k,v in lists.items()},tuple(rules))


def parse_file()->Parsed:
    return parse(SOURCE.read_text(encoding='utf-8'))


def evaluate(model:Parsed, s:Context) -> tuple[str,float|None]|None:
    if s.hand not in ALL_HANDS:
        raise PortabilityError(f'Invalid class: {s.hand}')
    # Interpreted observation symbols; do not reinterpret any hand strategy.
    observations={
        'IsPreflop':s.is_preflop,
        'nplayersdealt = 6':s.nplayersdealt==6,
        'InUTG':s.in_utg,
        'Raises = 0':s.raises==0,
        'Calls = 0':s.calls==0,
        'StillToAct = 5':s.still_to_act==5,
        'PotSize = 1.5':s.pot_bb==1.5,
        'AmountToCall = 1':s.amount_to_call_bb==1.,
        'NOT StackUnknown':not s.stack_unknown,
        'StackSize >= 95':s.hero_stack_bb>=95,
        'StackSize <= 105':s.hero_stack_bb<=105,
        'MinOpponentStackSize >= 95':s.min_opponent_stack_bb>=95,
        'MaxOpponentStackSize <= 105':s.max_opponent_stack_bb<=105,
    }
    # Reject impossible observation inputs. OpenHoldem's real missing/unknown
    # semantics still require a separate integration/replay validation.
    if (not all(isinstance(x,(int,float)) and math.isfinite(x) for x in
        (s.pot_bb,s.amount_to_call_bb,s.hero_stack_bb,
         s.min_opponent_stack_bb,s.max_opponent_stack_bb)) or
        s.min_opponent_stack_bb>s.max_opponent_stack_bb):
        return None
    for rule in model.rules:
        matched=True
        for atom in rule.atoms:
            if atom in observations:
                value=observations[atom]
            elif atom in model.lists:
                value=s.hand in model.lists[atom]
            else:
                rand=RAND_RE.fullmatch(atom)
                if not rand:
                    raise PortabilityError(f'Unsupported interpreted token: {atom}')
                valid=(isinstance(s.randomhand,(float,int)) and math.isfinite(s.randomhand)
                       and 0.0<=s.randomhand<1.0)
                value=valid and (s.randomhand < float(rand[2]) if rand[1]=='<' else
                                 s.randomhand >= float(rand[2]))
            if not value:
                matched=False
                break
        if matched:
            return ('RAISE',2.5) if rule.action=='RaiseTo 2.5' else ('FOLD',None)
    return None  # not proof of OpenHoldem fallback; gate remains blocked


if __name__=='__main__':
    m=parse_file()
    print('PORT-2 static mix: %s / %s / %s (stable randomhand supplied externally)'%
          (len(m.lists[RAISE]),len(m.lists[FOLD]),len(m.lists[MIX])))
