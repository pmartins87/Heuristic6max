"""Offline restricted interpreter of the actual OpenPPL source.

Never called by OpenHoldem. No poker policy is specified in this Python file;
rule priority, sizings and mix thresholds all come from the .oppl text.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import math
import re

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'srp_hu_history_v2.oppl'
COMBINED = HERE / 'preflop_srp_history_v2.oppl'
PREVIOUS = HERE.parent / 'vs_3bet_mvp' / 'preflop_rfi_vsopen_vs3_draft.oppl'

HELPERS = ('f$SRPHUOpen', 'f$SRPHUCaller', 'f$SRPHU', 'f$SRPStrongMade', 'f$SRPTopGood',
    'f$HLFlopBetCall', 'f$HLFlopCheckedThrough', 'f$HLFlopCall', 'f$HLFlopKnown',
    'f$HLTurnBetCall', 'f$HLTurnCheckedThrough', 'f$HLTurnCall', 'f$HLTurnKnown',
    'f$HLTurnDomain', 'f$HLRiverDomain',
    'f$HLPathBB','f$HLPathBC','f$HLPathBX','f$HLPathCB','f$HLPathCC','f$HLPathCX',
    'f$HLPathXB','f$HLPathXC','f$HLPathXX') + (
    'f$HLFlopRaiseCall','f$HLFlopCheckRaiseCall','f$HLFlopBetRaisedCall',
    'f$HLTurnRaiseCall','f$HLTurnCheckRaiseCall','f$HLTurnBetRaisedCall',
    'f$HLFlopKnownV2','f$HLTurnKnownV2','f$HLTurnDomainV2','f$HLRiverDomainV2') + tuple(
        'f$HLPath2'+a+b for a in 'BCXRHM' for b in 'BCXRHM')
STREETS = ('flop', 'turn', 'river')
ALL_SECTIONS = HELPERS + tuple('f$' + x for x in STREETS)
BOOLS = frozenset(('StackUnknown', 'BotRaisedBeforeFlop', 'BotCalledBeforeFlop',
                   'HaveNuts', 'HaveQuads', 'HaveFullHouse', 'HaveFlush',
                   'HaveStraight', 'HaveSet', 'HaveTrips', 'HaveTwoPair',
                   'HaveOverPair', 'HaveTopPair', 'HaveBestKicker',
                   'HaveNutFlushDraw', 'HaveFlushDraw', 'HaveOpenEndedStraightDraw',
                   'BotIsLastRaiser', 'FlushPossibleOnFlop', 'StraightPossibleOnFlop',
                   'PairOnBoard',
                   'BotRaisedOnFlop','BotCalledOnFlop','OpponentCalledOnFlop',
                   'NoVillainBetOrRaisedOnFlop','NoBettingOnFlop',
                   'BotRaisedOnTurn','BotCalledOnTurn','OpponentCalledOnTurn',
                   'NoVillainBetOrRaisedOnTurn','NoBettingOnTurn','BotCheckedOnFlop','BotCheckedOnTurn'))
NUMERIC = frozenset(('nplayersdealt', 'OpponentsOnFlop', 'OpponentsLeft',
                     'NumberOfOpponentsAllin', 'NumberOfRaisesBeforeFlop',
                     'AmountToCall', 'PotSize', 'randomhand', 'NumberOfRaisesOnFlop', 'NumberOfRaisesOnTurn'))
ACTIONS = frozenset(('RaiseHalfPot', 'Call', 'Fold', 'BetTwoThirdPot',
                     'BetHalfPot', 'BetThirdPot', 'Check'))
HEADER = re.compile(r'^##(f\$[A-Za-z0-9]+)##$')
RULE = re.compile(r'^WHEN \(([^()]+)\) (RETURN (?:TRUE|FALSE)|(?:RaiseHalfPot|Call|Fold|BetTwoThirdPot|BetHalfPot|BetThirdPot|Check)) FORCE$')
OTHERS = re.compile(r'^WHEN Others RETURN FALSE FORCE$')
REL = re.compile(r'^([A-Za-z][A-Za-z0-9]*) (<=|>=|=|<|>) (\d+(?:\.\d+)?)(?:% PotSize)?$')
RAND = re.compile(r'^randomhand (<|>=) (0\.25|0\.30|0\.40|0\.65)$')

class SourceError(ValueError):
    pass

@dataclass(frozen=True)
class Rule:
    atoms: tuple[str, ...]
    action: str
    is_fallback: bool = False

@dataclass(frozen=True)
class Model:
    sections: dict[str, tuple[Rule, ...]]


def parse(source: str) -> Model:
    sections: dict[str, list[Rule]] = {}
    current: str | None = None
    for line_no, original in enumerate(source.splitlines(), 1):
        line = original.strip()
        if not line or line.startswith('//'):
            continue
        m = HEADER.fullmatch(line)
        if m:
            current = m[1]
            if current not in ALL_SECTIONS or current in sections:
                raise SourceError(f'line {line_no}: section not whitelisted / duplicate')
            sections[current] = []
            continue
        if current is None:
            raise SourceError(f'line {line_no}: rule before section')
        if OTHERS.fullmatch(line):
            if current not in HELPERS or any(x.is_fallback for x in sections[current]):
                raise SourceError(f'line {line_no}: invalid fallback')
            sections[current].append(Rule((), 'RETURN FALSE', True))
            continue
        rm = RULE.fullmatch(line)
        if rm is None:
            raise SourceError(f'line {line_no}: unsupported OpenPPL syntax')
        atoms = tuple(rm[1].split(' AND '))
        if not atoms or len(atoms) != len(set(atoms)):
            raise SourceError(f'line {line_no}: missing or duplicated condition')
        for a in atoms:
            atom = a.removeprefix('NOT ')
            if atom in BOOLS or atom in HELPERS or atom == 'Position = Last':
                continue
            mrel = REL.fullmatch(atom)
            if mrel and mrel[1] in NUMERIC:
                if mrel[1] == 'randomhand' and not RAND.fullmatch(atom):
                    raise SourceError('randomhand threshold is not reviewed')
                if atom.endswith('% PotSize') and (mrel[1] != 'AmountToCall' or mrel[2] != '<='):
                    raise SourceError('ratio only supported for AmountToCall <= % PotSize')
                continue
            raise SourceError(f'line {line_no}: unrecognized symbol/expression {a}')
        action = rm[2]
        if current in HELPERS and action not in ('RETURN TRUE', 'RETURN FALSE'):
            raise SourceError('helper must RETURN bool')
        if current not in HELPERS and action not in ACTIONS:
            raise SourceError('street rule must emit an action')
        if any(x.is_fallback for x in sections[current]):
            raise SourceError('rules after fallback are shadowed')
        sections[current].append(Rule(atoms, action))
    if set(sections) != set(ALL_SECTIONS):
        raise SourceError('missing expected sections')
    for h in HELPERS:
        if not sections[h] or not sections[h][-1].is_fallback:
            raise SourceError(f'helper {h} must end with explicit false fallback')
    for street in STREETS:
        rules = sections['f$'+street]
        if not rules or any(x.is_fallback for x in rules):
            raise SourceError('No implicit or unconditional fallback on actions')
        tail = rules[-1]
        if tail.atoms != ((('f$SRPHU','AmountToCall = 0') if street=='flop' else ('f$HLTurnDomainV2' if street=='turn' else 'f$HLRiverDomainV2','f$SRPHU','AmountToCall = 0'))) or tail.action != 'Check':
            raise SourceError(f'{street} must end in guarded check')
        if not any(x.atoms == ((('f$SRPHU','AmountToCall > 0') if street=='flop' else ('f$HLTurnDomainV2' if street=='turn' else 'f$HLRiverDomainV2','f$SRPHU','AmountToCall > 0'))) and x.action == 'Fold' for x in rules):
            raise SourceError(f'{street} must contain guarded fold')
    for street, domain in (('turn','f$HLTurnDomainV2'),('river','f$HLRiverDomainV2')):
        if any(not x.atoms or x.atoms[0]!=domain for x in sections['f$'+street]):
            raise SourceError('Every turn/river branch must use audited history domain')
    return Model({k:tuple(v) for k,v in sections.items()})


def parse_file() -> Model:
    return parse(SOURCE.read_text(encoding='utf-8'))


def observe(**overrides: bool | float | int | str) -> dict[str, bool | float | int | str]:
    """Synthetic witness only. Values are NOT inferred from a real poker table."""
    result: dict[str, bool | float | int | str] = {x:False for x in BOOLS}
    result.update({x:0 for x in NUMERIC})
    result.update({'nplayersdealt':6, 'OpponentsOnFlop':1, 'OpponentsLeft':1,
                   'NumberOfOpponentsAllin':0, 'NumberOfRaisesBeforeFlop':0,
                   'BotRaisedBeforeFlop':True, 'BotCalledBeforeFlop':False,
                   'PotSize':6.5, 'randomhand':0.70, 'Position':'First'})
    for k,v in overrides.items():
        if k not in BOOLS | NUMERIC | {'Position'}:
            raise SourceError(f'unknown symbol supplied: {k}')
        result[k] = v
    return result


def evaluate(model: Model, street: str, observations: dict[str,bool|float|int|str], *, helper: str | None = None) -> str | bool | None:
    if street not in STREETS:
        raise SourceError('Invalid street')
    missing = (BOOLS | NUMERIC | {'Position'}) - set(observations)
    if missing:
        raise SourceError(f'Missing observation symbols {sorted(missing)}')
    for k in NUMERIC:
        v = observations[k]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
            raise SourceError(f'Invalid numerical observation {k}')
    for k in BOOLS:
        if not isinstance(observations[k], bool):
            raise SourceError(f'Invalid boolean observation {k}')
    rand=observations['randomhand']
    if rand < 0 or rand >= 1:
        raise SourceError('randomhand must be OH-style [0,1)')
    if observations['Position'] not in ('First','Middle','Last'):
        raise SourceError('Position outside reviewed values')
    if observations['AmountToCall'] < 0 or observations['PotSize'] <= 0:
        raise SourceError('Invalid pot/price')
    active: set[str] = set()

    def fn(name: str) -> bool:
        if name in active:
            raise SourceError('cyclic function reference')
        active.add(name)
        try:
            for r in model.sections[name]:
                if r.is_fallback or all(atom(a) for a in r.atoms):
                    return r.action == 'RETURN TRUE'
            raise SourceError(f'helper missing fallback: {name}')
        finally:
            active.remove(name)

    def atom(a: str) -> bool:
        if a.startswith('NOT '):
            return not atom(a[4:])
        if a in BOOLS:
            return bool(observations[a])
        if a in HELPERS:
            return fn(a)
        if a == 'Position = Last':
            return observations['Position']=='Last'
        m=REL.fullmatch(a)
        if not m or m[1] not in NUMERIC:
            raise SourceError(f'Unsupported interpreted token {a}')
        lhs=float(observations[m[1]])
        rhs=float(m[3])
        if a.endswith('% PotSize'):
            rhs = rhs/100.0 * float(observations['PotSize'])
        op=m[2]
        return {'=':lambda:lhs==rhs,'>':lambda:lhs>rhs,'<':lambda:lhs<rhs,
                '<=':lambda:lhs<=rhs,'>=':lambda:lhs>=rhs}[op]()

    if helper is not None:
        if helper not in HELPERS: raise SourceError('Unknown requested helper')
        return fn(helper)
    for r in model.sections['f$'+street]:
        if all(atom(a) for a in r.atoms):
            return r.action
    return None  # The real OpenHoldem may still invoke fallback. Not fail-closed.

if __name__=='__main__':
    model=parse_file()
    print('SRP-HU source parsed:', sum(len(model.sections['f$'+s]) for s in STREETS), 'action rules')
