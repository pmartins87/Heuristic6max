"""Constrained, source-driven V2 OpenPPL static evaluator.

IMPORTANT: This is NOT OpenHoldem, an OpenPPL compiler, a poker solver, or
operational replay evidence. It parses only constructs used by the isolated
V2 two-spot fixture and deliberately rejects any other construct.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'f2_two_spots_draft.oppl'

SYMBOLS = frozenset({
    'IsFlop', 'IsPreflop', 'nplayersdealt', 'InButton', 'Position', 'Last',
    'OpponentsOnFlop', 'OpponentsLeft', 'headsupchair', 'bigblindchair',
    'user_V2PilotBTNOpen', 'BotRaisedBeforeFlop',
    'NumberOfRaisesBeforeFlop', 'NoBettingOnFlop', 'AmountToCall', 'StackSize',
    'Calls', 'Raises', 'HaveTrips', 'HaveTopPair', 'Others',
})
TOKEN = re.compile(r'hand\$[A-Za-z0-9]+|board\$[A-Za-z0-9]+|f\$[A-Za-z_0-9]+|[A-Za-z_][A-Za-z_0-9]*|(?:\d+\.\d+|\d+)|>=|<=|!=|=|<|>|\(|\)')
CARD = re.compile(r'[AKQJT98765432][cdhs]')
KEYWORD = {'AND': 'and', 'OR': 'or', 'NOT': 'not', 'TRUE': 'True', 'FALSE': 'False'}
HEAD = re.compile(r'^##f\$([A-Za-z_0-9]+)##$')

class UnsupportedSource(ValueError):
    pass

@dataclass(frozen=True)
class Snapshot:
    street: str
    hand: tuple[str, str]
    board: tuple[str, ...]
    nplayersdealt: int = 6
    in_button: bool = True
    position: str = 'Last'
    opponents_on_flop: int = 1
    opponents_left: int = 1
    headsupchair: int = 5
    bigblindchair: int = 5
    user_open: bool = False
    bot_raised_preflop: bool = False
    opponents_preflop_raises: int = 0
    no_betting_on_flop: bool = True
    amount_to_call: float = 0.0
    stack_size: float = 97.5
    calls: int = 0
    raises: int = 0
    have_trips: bool = False
    have_top_pair: bool = False

    def symbols(self) -> dict[str, object]:
        return {
            'IsFlop': self.street == 'flop',
            'IsPreflop': self.street == 'preflop',
            'nplayersdealt': self.nplayersdealt,
            'InButton': self.in_button,
            'Position': self.position,
            'Last': 'Last',
            'OpponentsOnFlop': self.opponents_on_flop,
            'OpponentsLeft': self.opponents_left,
            'headsupchair': self.headsupchair,
            'bigblindchair': self.bigblindchair,
            'user_V2PilotBTNOpen': self.user_open,
            'BotRaisedBeforeFlop': self.bot_raised_preflop,
            'NumberOfRaisesBeforeFlop': self.opponents_preflop_raises,
            'NoBettingOnFlop': self.no_betting_on_flop,
            'AmountToCall': self.amount_to_call,
            'StackSize': self.stack_size,
            'Calls': self.calls,
            'Raises': self.raises,
            'HaveTrips': self.have_trips,
            'HaveTopPair': self.have_top_pair,
            'Others': True,
        }


def _parse_physical_cards(text: str) -> tuple[str, ...]:
    cards = tuple(CARD.findall(text))
    if not cards or ''.join(cards) != text or len(cards) != len(set(cards)):
        raise UnsupportedSource(f'invalid physical-card expression {text!r}')
    return cards


def _expr_to_ast(expr: str) -> ast.Expression:
    tokens = TOKEN.findall(expr)
    if not tokens or re.sub(r'\s+', '', ''.join(tokens)) != re.sub(r'\s+', '', expr):
        raise UnsupportedSource(f'unknown lexical token: {expr!r}')
    rebuilt = []
    for t in tokens:
        if t in KEYWORD:
            rebuilt.append(KEYWORD[t])
        elif t == '=':
            rebuilt.append('==')
        elif t in ('>=', '<=', '!=', '<', '>', '(', ')') or re.fullmatch(r'\d+(?:\.\d+)?', t):
            rebuilt.append(t)
        elif t in SYMBOLS or t.startswith(('hand$', 'board$', 'f$')):
            rebuilt.append(f'S({t!r})')
        else:
            raise UnsupportedSource(f'unsupported symbol: {t}')
    try:
        return ast.parse(' '.join(rebuilt), mode='eval')
    except SyntaxError as e:
        raise UnsupportedSource(f'expression is not in supported subset: {expr}') from e


class StrictSource:
    def __init__(self, text: str):
        self.sections: dict[str, list[tuple[str, str]]] = {}
        current: str | None = None
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith('//'):
                continue
            m = HEAD.fullmatch(line)
            if m:
                current = m.group(1)
                if current in self.sections:
                    raise UnsupportedSource(f'duplicate section {current}')
                self.sections[current] = []
                continue
            if current is None or not line.startswith('WHEN '):
                raise UnsupportedSource(f'unexpected source line: {line}')
            if line.startswith('WHEN Others '):
                cond, action = 'Others', line[len('WHEN Others '):]
            elif line.startswith('WHEN ('):
                p = line.rfind(')')
                if p < 6:
                    raise UnsupportedSource(f'unclosed WHEN condition {line}')
                cond, action = line[len('WHEN ('):p], line[p + 1:].strip()
            else:
                raise UnsupportedSource(f'non-parenthesized WHEN unsupported: {line}')
            if not (action.endswith(' FORCE') or action.startswith('Set user_')):
                raise UnsupportedSource(f'unsupported action syntax: {action}')
            _expr_to_ast(cond)
            self.sections[current].append((cond, action))
        for section in ('preflop', 'flop', 'turn', 'river', 'V2PilotBTNOpenRFIContext'):
            if section not in self.sections:
                raise UnsupportedSource(f'missing required section {section}')

    def _evaluate(self, node: ast.AST, snap: Snapshot) -> object:
        if isinstance(node, ast.Expression):
            return self._evaluate(node.body, snap)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str, bool)):
            return node.value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'S' and len(node.args) == 1 and not node.keywords:
            name = self._evaluate(node.args[0], snap)
            if not isinstance(name, str):
                raise UnsupportedSource('S requires symbol string')
            if name.startswith('hand$'):
                return set(_parse_physical_cards(name[5:])).issubset(snap.hand)
            if name.startswith('board$'):
                return set(_parse_physical_cards(name[6:])).issubset(snap.board)
            if name.startswith('f$'):
                return self.execute_section(name[2:], snap)[0] == 'TRUE'
            values = snap.symbols()
            if name not in values:
                raise UnsupportedSource(f'unknown symbol at runtime: {name}')
            return values[name]
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(bool(self._evaluate(v, snap)) for v in node.values)
            if isinstance(node.op, ast.Or):
                return any(bool(self._evaluate(v, snap)) for v in node.values)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not bool(self._evaluate(node.operand, snap))
        if isinstance(node, ast.Compare):
            a = self._evaluate(node.left, snap)
            for op, comp in zip(node.ops, node.comparators):
                b = self._evaluate(comp, snap)
                if isinstance(op, ast.Eq): ok = a == b
                elif isinstance(op, ast.NotEq): ok = a != b
                elif isinstance(op, ast.Gt): ok = a > b
                elif isinstance(op, ast.GtE): ok = a >= b
                elif isinstance(op, ast.Lt): ok = a < b
                elif isinstance(op, ast.LtE): ok = a <= b
                else: raise UnsupportedSource('unsupported comparison')
                if not ok: return False
                a = b
            return True
        raise UnsupportedSource(f'unsupported AST node {type(node).__name__}')

    def execute_section(self, section: str, snap: Snapshot) -> tuple[str, Snapshot]:
        if section not in self.sections:
            raise UnsupportedSource(f'unknown section {section}')
        active = snap
        for cond, action in self.sections[section]:
            if not bool(self._evaluate(_expr_to_ast(cond), active)):
                continue
            if action.startswith('Set user_'):
                var = action[len('Set '):]
                if var != 'user_V2PilotBTNOpen':
                    raise UnsupportedSource(f'unknown side effect {var}')
                active = replace(active, user_open=True)
                continue
            if action == 'RETURN TRUE FORCE': return 'TRUE', active
            if action == 'RETURN FALSE FORCE': return 'FALSE', active
            if action == 'Beep FORCE': return 'BEEP_NO_ACTION', active
            if action == 'Check FORCE': return 'CHECK', active
            if action == 'BetThirdPot FORCE': return 'BET_THIRD_POT', active
            if action == 'RaiseTo 2.5 FORCE': return 'RAISE_TO_2_5_BB', active
            raise UnsupportedSource(f'unsupported action {action}')
        raise UnsupportedSource(f'no return/action at end of section {section}')


def source() -> StrictSource:
    return StrictSource(SOURCE.read_text(encoding='utf-8'))
