"""Gate de consistência de observação versus histórico reconstruído.

Não infere ações a partir do scrape. Se qualquer campo essencial faltar ou for
inconsistente, recusa decisões. Evidência = observação completa, não OCR isolado.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
import math
from action_ledger import HandLedger, Round, LedgerError


@dataclass(frozen=True)
class SeenSeat:
    stack_remaining_bb: float
    street_contribution_bb: float
    folded: bool
    allin: bool


@dataclass(frozen=True)
class Observation:
    hand_id: str
    street: Round
    hero_position: str
    hero_turn: bool
    pot_bb: float
    hero_to_call_bb: float
    seats: Mapping[str, SeenSeat]
    complete_history: bool = False
    stable_scrape: bool = False


def validate_observation(ledger: HandLedger, seen: Observation, *, tolerance_bb: float = 0.01) -> None:
    if not seen.complete_history or not seen.stable_scrape:
        raise LedgerError('histórico incompleto ou imagem não estável: bloquear decisão')
    if seen.hand_id != ledger.hand_id or seen.street != ledger.street:
        raise LedgerError('hand_id ou street divergente')
    if not seen.hero_turn or ledger.next_actor != seen.hero_position:
        raise LedgerError('hero_turn/posição diverge do histórico')
    if set(seen.seats) != set(ledger.seats):
        raise LedgerError('lista de jogadores incompleta ou divergente')
    if not math.isfinite(seen.pot_bb) or abs(seen.pot_bb - ledger.pot_bb) > tolerance_bb:
        raise LedgerError('pot incompatível')
    if not math.isfinite(seen.hero_to_call_bb) or abs(seen.hero_to_call_bb - ledger.to_call(seen.hero_position)) > tolerance_bb:
        raise LedgerError('to_call incompatível')
    for pos, snap in seen.seats.items():
        expected = ledger.seats[pos]
        for value, other, name in (
            (snap.stack_remaining_bb, expected.balance, 'balance'),
            (snap.street_contribution_bb, expected.contrib, 'currentbet'),
        ):
            if not math.isfinite(value) or abs(value-other) > tolerance_bb:
                raise LedgerError(f'{pos}: {name} diverge')
        if bool(snap.folded) != expected.folded or bool(snap.allin) != expected.allin:
            raise LedgerError(f'{pos}: fold/allin diverge')
