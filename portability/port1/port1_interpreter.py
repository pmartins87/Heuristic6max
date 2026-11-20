"""Strict PORT-1 *test* interpreter: reads the OPPL source; NEVER a runtime bot.

No poker ranges or decisions are authored here. The two imported handlists
and corresponding WHEN lines are the complete source for the statically
supported domain. Unmatched means test-only None, not a safe OpenHoldem action.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('lj_rfi_pure_port1.oppl')
RANKS='AKQJT98765432'
ALL_HANDS=frozenset([r+r for r in RANKS]+[a+b+t for i,a in enumerate(RANKS) for b in RANKS[i+1:] for t in 'so'])
LIST_RAISE='listPORT1LJRAISE'
LIST_FOLD='listPORT1LJFOLD'
GUARD=('IsPreflop','nplayersdealt = 6','InUTG','Raises = 0','Calls = 0',
       'StillToAct = 5','PotSize = 1.5','AmountToCall = 1',
       'NOT StackUnknown','StackSize >= 95','StackSize <= 105',
       'MinOpponentStackSize >= 95','MaxOpponentStackSize <= 105')
LIST_RE = re.compile(r'^##(listPORT1LJRAISE|listPORT1LJFOLD)##$')
RULE_RE = re.compile(r'^WHEN \(([^()]+)\) (RaiseTo 2\.5|Fold) FORCE$')

class PortabilityError(ValueError):
    pass

@dataclass(frozen=True)
class Parsed:
    lists: dict[str, frozenset[str]]
    rules: tuple[tuple[str,str], ...]

@dataclass(frozen=True)
class Context:
    hand: str
    is_preflop: bool = True
    nplayersdealt: int = 6
    in_utg: bool = True
    raises: int = 0
    calls: int = 0
    still_to_act: int = 5
    pot_bb: float = 1.5
    amount_to_call_bb: float = 1.0
    stack_unknown: bool = False
    hero_stack_bb: float = 100.0
    min_opponent_stack_bb: float = 100.0
    max_opponent_stack_bb: float = 100.0


def parse(source: str) -> Parsed:
    lines = source.splitlines()
    lists: dict[str,set[str]] = {}
    rules=[]
    section=None
    seen_preflop=False
    for no, original in enumerate(lines,1):
        line=original.strip()
        if not line or line.startswith('//'):
            continue
        ml=LIST_RE.fullmatch(line)
        if ml:
            if seen_preflop or ml[1] in lists: raise PortabilityError(f'line {no}: invalid handlist section')
            section=ml[1];lists[section]=set()
            continue
        if line=='##f$preflop##':
            if seen_preflop or set(lists)!={LIST_RAISE,LIST_FOLD}:
                raise PortabilityError(f'line {no}: preflop header misplaced')
            seen_preflop=True;section='preflop'
            continue
        if section in (LIST_RAISE,LIST_FOLD):
            tokens=line.split()
            if not tokens or any(x not in ALL_HANDS for x in tokens):
                raise PortabilityError(f'line {no}: invalid/unsupported list token')
            for hand in tokens:
                if hand in lists[section]:raise PortabilityError(f'line {no}: duplicate hand')
                lists[section].add(hand)
            continue
        if section!='preflop':raise PortabilityError(f'line {no}: no valid section')
        mr=RULE_RE.fullmatch(line)
        if not mr:raise PortabilityError(f'line {no}: outside audited OPPL subset')
        atoms=mr[1].split(' AND ')
        if len(atoms)!=len(GUARD)+1 or len(set(atoms))!=len(atoms):
            raise PortabilityError(f'line {no}: guard atom count/duplicates')
        if tuple(atoms[:len(GUARD)])!=GUARD:
            raise PortabilityError(f'line {no}: noncanonical guard')
        listname=atoms[-1]
        action=mr[2]
        if (listname,action) not in ((LIST_RAISE,'RaiseTo 2.5'),(LIST_FOLD,'Fold')):
            raise PortabilityError(f'line {no}: unsupported action/list')
        rules.append((listname,action))
    if not seen_preflop or rules!=[(LIST_RAISE,'RaiseTo 2.5'),(LIST_FOLD,'Fold')]:
        raise PortabilityError('Expected exactly ordered RaiseTo and Fold rules')
    if lists[LIST_RAISE] & lists[LIST_FOLD]: raise PortabilityError('Overlapping handlists')
    if len(lists[LIST_RAISE]|lists[LIST_FOLD])!=168:
        raise PortabilityError('Exactly one class must remain unsupported (mixed KJo)')
    if ALL_HANDS-(lists[LIST_RAISE]|lists[LIST_FOLD])!={'KJo'}:
        raise PortabilityError('Unexpected unmapped class (only KJo may be mixed)')
    return Parsed({k:frozenset(v) for k,v in lists.items()},tuple(rules))


def parse_file()->Parsed:
    return parse(SOURCE.read_text(encoding='utf-8'))


def evaluate(model: Parsed, s: Context) -> tuple[str,float|None]|None:
    if s.hand not in ALL_HANDS:raise PortabilityError(f'Unknown hand {s.hand}')
    if not (s.is_preflop and s.nplayersdealt==6 and s.in_utg and s.raises==0
        and s.calls==0 and s.still_to_act==5 and s.pot_bb==1.5
        and s.amount_to_call_bb==1. and not s.stack_unknown
        and 95 <= s.hero_stack_bb <= 105
        and s.min_opponent_stack_bb>=95 and s.max_opponent_stack_bb<=105
        and s.min_opponent_stack_bb<=s.max_opponent_stack_bb):
        return None
    for handlist,action in model.rules:
        if s.hand in model.lists[handlist]:
            return ('RAISE',2.5) if action=='RaiseTo 2.5' else ('FOLD',None)
    return None  # TEST INTERPRETER ONLY; OpenHoldem no-match is NOT fail-closed.


if __name__=='__main__':
    m=parse_file()
    print('PORT-1 static-only: %d pure opens, %d pure folds, KJo mixed blocked' %
          (len(m.lists[LIST_RAISE]),len(m.lists[LIST_FOLD])))
