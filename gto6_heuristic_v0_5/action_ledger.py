"""Replay determinístico de ações públicas de NLHE 2-6 handed (GTO6 v0.2).

Não transforma screenshots em eventos: eventos são dados confirmados. Um adaptador
futuro deve detectar as transições e falhar quando a evidência não for suficiente.
Valores em BB, fichas efetivas de participantes, sem ante, sem rake no ledger.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping
import math

EPS = 1e-8
POSITION_ORDER = ('LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB')


class LedgerError(ValueError):
    pass


class Move(str, Enum):
    FOLD = 'FOLD'
    CHECK = 'CHECK'
    CALL = 'CALL'
    BET = 'BET'
    RAISE = 'RAISE'
    SHOVE = 'SHOVE'


class Round(str, Enum):
    PREFLOP = 'PREFLOP'
    FLOP = 'FLOP'
    TURN = 'TURN'
    RIVER = 'RIVER'


@dataclass
class Seat:
    pid: str
    position: str
    original_stack: float
    balance: float
    contrib: float = 0.0   # contribuição na street
    paid: float = 0.0      # contribuição em toda a mão
    folded: bool = False
    allin: bool = False


@dataclass(frozen=True)
class Event:
    street: Round
    pid: str
    position: str
    move: Move
    street_to_bb: float | None
    increment_bb: float
    pot_after_bb: float
    full_raise: bool
    is_aggressive: bool = False
    is_squeeze: bool = False


def _fmt(x: float) -> str:
    return f'{x:.3f}'.rstrip('0').rstrip('.')


class HandLedger:
    def __init__(self, hand_id: str, seats: Mapping[str, float], *, big_blind_bb: float = 1.0,
                 small_blind_bb: float = 0.5):
        if not hand_id or not hand_id.strip():
            raise LedgerError('hand_id requerido')
        if set(seats) not in (set(POSITION_ORDER[6-n:]) for n in range(2, 7)):
            raise LedgerError('posições inválidas ou não contíguas para número de jogadores')
        if any(not math.isfinite(s) or s <= 1 for s in seats.values()):
            raise LedgerError('stack inicial inválido')
        if abs(big_blind_bb - 1) > EPS or abs(small_blind_bb - 0.5) > EPS:
            raise LedgerError('v0.2 suporta blinds normalizados 0.5/1 somente')
        self.hand_id = hand_id
        self.seats = {pos: Seat(pos, pos, float(stack), float(stack)) for pos, stack in seats.items()}
        self.street = Round.PREFLOP
        self.events: list[Event] = []
        self.bet_level = 1.0
        self.last_full_raise_bb = 1.0
        self.acted_since_full_raise: set[str] = set()
        self.finished = False
        self._take_blind('SB', 0.5)
        self._take_blind('BB', 1.0)
        self.pending = [p for p in self._order() if not self.seats[p].allin]

    def _take_blind(self, pos: str, amount: float) -> None:
        s = self.seats[pos]
        if s.balance + EPS < amount:
            raise LedgerError('stack não cobre blind')
        s.balance -= amount
        s.contrib += amount
        s.paid += amount
        s.allin = s.balance < EPS

    def _order(self) -> list[str]:
        roles = [p for p in POSITION_ORDER if p in self.seats]
        if self.street == Round.PREFLOP:
            return roles
        if len(self.seats) == 2:
            return ['BB', 'SB']  # HU: BB joga primeiro pós-flop
        return [p for p in ('SB', 'BB', 'LJ', 'HJ', 'CO', 'BTN') if p in self.seats]

    def _order_after(self, pos: str) -> list[str]:
        order = self._order()
        idx = order.index(pos)
        return order[idx + 1:] + order[:idx]

    @property
    def pot_bb(self) -> float:
        return sum(s.paid for s in self.seats.values())

    @property
    def alive(self) -> tuple[str, ...]:
        return tuple(p for p in self._order() if not self.seats[p].folded)

    @property
    def next_actor(self) -> str | None:
        return None if not self.pending or self.finished else self.pending[0]

    def to_call(self, pid: str) -> float:
        return max(0.0, self.bet_level - self.seats[pid].contrib)

    def can_raise(self, pid: str) -> bool:
        s = self.seats[pid]
        return (not s.folded and not s.allin and pid not in self.acted_since_full_raise
                and s.balance > self.to_call(pid) + EPS)

    def min_raise_to(self) -> float:
        if self.bet_level < EPS:
            return 1.0
        return self.bet_level + self.last_full_raise_bb

    def allowed(self, pid: str) -> frozenset[Move]:
        if pid != self.next_actor:
            return frozenset()
        s = self.seats[pid]
        to_call = self.to_call(pid)
        can_raise = self.can_raise(pid)
        if to_call < EPS:
            out = {Move.CHECK}
            if can_raise:
                out.add(Move.BET if self.bet_level < EPS else Move.RAISE)
                out.add(Move.SHOVE)
            return frozenset(out)
        out = {Move.FOLD}
        if can_raise or s.balance <= to_call + EPS:
            out.add(Move.SHOVE)  # raise all-in ou call all-in curto
        if s.balance > to_call + EPS:
            out.add(Move.CALL)
        elif abs(s.balance - to_call) <= EPS:
            out.add(Move.CALL)
        if can_raise:
            out.add(Move.RAISE)
        return frozenset(out)

    def act(self, pid: str, move: Move, street_to_bb: float | None = None) -> Event:
        if self.finished or pid != self.next_actor:
            raise LedgerError(f'fora de turno: recebido={pid}, esperado={self.next_actor}')
        s = self.seats[pid]
        legal = self.allowed(pid)
        if move not in legal:
            raise LedgerError(f'ação ilegal {move}: legais={sorted(x.value for x in legal)}')
        if move not in (Move.BET, Move.RAISE) and street_to_bb is not None:
            raise LedgerError('street_to_bb permitido somente para BET/RAISE')
        if move in (Move.BET, Move.RAISE) and street_to_bb is None:
            raise LedgerError('BET/RAISE exige street_to_bb')
        to_call = self.to_call(pid)
        raising_was_allowed = self.can_raise(pid)
        target = s.contrib
        if move == Move.CHECK:
            if to_call > EPS:
                raise LedgerError('check enfrentando aposta')
        elif move == Move.FOLD:
            s.folded = True
        elif move == Move.CALL:
            target += to_call
        elif move == Move.SHOVE:
            target += s.balance
            # Crucial: rejeitar ANTES de debitar fichas, para manter atomicidade.
            # Um jogador cuja ação não foi reaberta pode dar call/all-in curto,
            # mas NÃO pode aumentar a maior aposta com um shove parcial.
            if target > self.bet_level + EPS and not raising_was_allowed:
                raise LedgerError('shove ilegal: aposta não reaberta')
        else:
            target = float(street_to_bb)
            if not math.isfinite(target) or target <= self.bet_level + EPS:
                raise LedgerError('raise_to não excede maior aposta')
            if target < self.min_raise_to() - EPS:
                raise LedgerError('raise menor que mínimo legal; só SHOVE pode ser parcial')
            if target > s.contrib + s.balance + EPS:
                raise LedgerError('raise excede stack')
            if move == Move.BET and self.bet_level > EPS:
                raise LedgerError('BET sobre aposta existente; usar RAISE')
            if move == Move.RAISE and self.bet_level < EPS:
                raise LedgerError('RAISE sem aposta existente; usar BET')
        before = self.bet_level
        if target > s.contrib + EPS:
            increment = target - s.contrib
            s.contrib = target
            s.balance -= increment
            s.paid += increment
        else:
            increment = 0.0
        if s.balance < EPS:
            s.balance = 0.0
            s.allin = True
        full_raise = False
        squeeze = False
        if target > before + EPS:
            delta = target - before
            full_raise = delta + EPS >= self.last_full_raise_bb
            if move != Move.SHOVE and not full_raise:
                raise LedgerError('raise parcial não all-in')
            if not raising_was_allowed:
                raise LedgerError('raise não reaberto')
            prev_events = [e for e in self.events if e.street == Round.PREFLOP]
            if self.street == Round.PREFLOP and any(e.is_aggressive for e in prev_events):
                last_raise_i = max((i for i, e in enumerate(prev_events) if e.is_aggressive), default=-1)
                squeeze = last_raise_i >= 0 and any(e.move == Move.CALL for e in prev_events[last_raise_i+1:])
            self.bet_level = target
            if full_raise:
                self.last_full_raise_bb = delta
                self.acted_since_full_raise = {pid}
            else:
                self.acted_since_full_raise.add(pid)
            self.pending = [p for p in self._order_after(pid) if not self.seats[p].folded and not self.seats[p].allin and self.to_call(p) > EPS]
        else:
            self.acted_since_full_raise.add(pid)
            self.pending.pop(0)
        if len(self.alive) <= 1:
            self.finished = True
            self.pending = []
        event = Event(self.street, pid, s.position, move,
                      target if move in (Move.BET, Move.RAISE, Move.SHOVE) else None,
                      increment, self.pot_bb, full_raise, target > before + EPS, squeeze)
        self.events.append(event)
        return event

    def next_street(self, street: Round) -> None:
        index = list(Round)
        if self.finished or self.pending or index.index(street) != index.index(self.street) + 1:
            raise LedgerError('transição de street prematura ou inválida')
        self.street = street
        self.bet_level = 0.0
        self.last_full_raise_bb = 1.0
        self.acted_since_full_raise.clear()
        for s in self.seats.values():
            s.contrib = 0.0
        self.pending = [p for p in self._order() if not self.seats[p].folded and not self.seats[p].allin]
        if len(self.pending) < 2:
            self.pending = []  # todos os adversários estão all-in: não há apostas laterais possíveis

    def history_key(self) -> str:
        """Chave de observações (não chave de política com equivalências)."""
        return '|'.join(f'{e.street.value}:{e.position}:{e.move.value}:'
                        f'{_fmt(e.street_to_bb) if e.street_to_bb is not None else "-"}'
                        for e in self.events)

    def pf_facing(self, pid: str) -> str:
        if self.street != Round.PREFLOP or pid != self.next_actor:
            raise LedgerError('classificação somente na vez do jogador preflop')
        pf = [e for e in self.events if e.street == Round.PREFLOP]
        agg = [e for e in pf if e.is_aggressive]
        if self.to_call(pid) < EPS:
            if pid == 'BB' and any(e.move == Move.CALL for e in pf):
                return 'BB_VS_LIMP_OPTION'
            return 'BB_OPTION' if pid == 'BB' else 'CHECK_OPTION'
        if agg:
            last = agg[-1]
            if last.move == Move.SHOVE:
                return 'VS_SHOVE'
            if last.is_squeeze:
                return 'VS_SQUEEZE'
            return {1: 'VS_OPEN', 2: 'VS_3BET', 3: 'VS_4BET', 4: 'VS_5BET'}.get(len(agg), 'VS_5BET_PLUS')
        if any(e.move == Move.CALL for e in pf):
            return 'VS_LIMP'
        return 'RFI'

    def current_spot_key(self) -> str:
        p = self.next_actor
        if p is None:
            raise LedgerError('sem ação pendente')
        # Chave completa: conserva quem agiu e quanto; pode ser agrupada depois.
        facing = self.pf_facing(p) if self.street == Round.PREFLOP else ('CHECKED_TO' if self.to_call(p) < EPS else 'VS_BET')
        return f'{self.street.value}|{p}|{facing}|TOCALL={_fmt(self.to_call(p))}|POT={_fmt(self.pot_bb)}|H={self.history_key()}'
