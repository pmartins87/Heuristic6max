"""Conecta replay confirmado + scrape estável + RFI 100 BB (apenas DRAFT)."""
from __future__ import annotations

from action_ledger import HandLedger, Round, LedgerError
from strict_observation import Observation, validate_observation
from rfi_reference import policy_for
from scenario_contract import (ScenarioState, Street, Position, PotType, Facing,
                               PositionalRelation, Policy, validate_hand_class)


def prepare_rfi(ledger: HandLedger, seen: Observation, hand_class: str) -> Policy | None:
    validate_observation(ledger, seen)
    validate_hand_class(hand_class)
    hero = ledger.next_actor
    if (ledger.street != Round.PREFLOP or hero is None
            or len(ledger.seats) != 6 or ledger.pf_facing(hero) != 'RFI'):
        return None
    effective = min(s.original_stack for s in ledger.seats.values()
                    if not s.folded)
    s=ScenarioState(hand_id=ledger.hand_id, street=Street.PREFLOP,
                    hero_position=Position(hero),hand_class=hand_class,
                    dealt_players=len(ledger.seats),active_players=len(ledger.alive),
                    effective_stack_bb=effective,pot_bb=ledger.pot_bb,
                    to_call_bb=ledger.to_call(hero),pot_type=PotType.UNOPENED,
                    facing=Facing.RFI,positional_relation=PositionalRelation.UNKNOWN)
    p=policy_for(s)
    if p is None:return None
    # Ações de política precisam ser executáveis neste nó (minraise/stack/turn).
    for a in p.actions:
        if a.action.value == 'RAISE' and (a.raise_to_bb is None
                or a.raise_to_bb < ledger.min_raise_to()-1e-8
                or a.raise_to_bb > ledger.seats[hero].contrib + ledger.seats[hero].balance + 1e-8):
            raise LedgerError('range RFI selecionou sizing de raise não executável')
    return p
