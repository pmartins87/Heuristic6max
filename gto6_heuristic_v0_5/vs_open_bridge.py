"""Gate RFI -> VS_OPEN: exige replay + snapshot completos (somente estudo DRAFT).

Bloqueia squeeze, isolations, overcalls, reopens, outros stacks, missing events,
open size fora de 2.5/3 e states sem replay. Não toma ação direta na mesa.
"""
from __future__ import annotations
from typing import Optional

from action_ledger import HandLedger, LedgerError, Move, Round
from strict_observation import Observation, validate_observation
from scenario_contract import (Facing, Policy, Position, PositionalRelation,
    PotType, ScenarioState, Street, validate_hand_class)
from vs_open_reference import (BY_PAIR, expected_open, positional_relation,
    policy_for, threebet_to_bb, expected_pot_bb)

EPS=1e-6


def prepare_vs_open(ledger:HandLedger, seen:Observation, hand_class:str)->Optional[Policy]:
    """Policy DRAFT apenas se um único raise inicial não recebeu call/3bet.

    None = cenário não coberto. Exceção = evidência inconsistente/ação ilegal.
    Nenhum destes retornos pode ser convertido para um FOLD operacional.
    """
    validate_observation(ledger,seen)
    validate_hand_class(hand_class)
    hero=ledger.next_actor
    if ledger.street!=Round.PREFLOP or hero is None or len(ledger.seats)!=6:
        return None
    if any(not 95 <= seat.original_stack <= 105 for seat in ledger.seats.values()):
        return None
    if ledger.pf_facing(hero)!='VS_OPEN':
        return None
    pf=[e for e in ledger.events if e.street==Round.PREFLOP]
    # Sem um único raise (RFI puro), não existe range VS_OPEN de 2 jogadores.
    if len([e for e in pf if e.is_aggressive]) != 1:
        return None
    if any(e.move not in (Move.FOLD,Move.RAISE) for e in pf):
        return None  # limper antes do raise, caller depois do raise, all-in, etc
    opener=next(e for e in pf if e.move==Move.RAISE)
    pair=(opener.position,hero)
    if pair not in BY_PAIR or opener.street_to_bb is None:
        return None
    expected_size=expected_open(opener.position)
    if abs(opener.street_to_bb-expected_size)>EPS:
        return None
    # Total real já inclui blinds: SB 3BB + BB 1BB = 4BB.
    if abs(ledger.pot_bb - expected_pot_bb(opener.position))>EPS:
        return None
    if abs(ledger.bet_level-expected_size)>EPS:
        return None
    stack=min(ledger.seats[hero].original_stack,ledger.seats[opener.position].original_stack)
    position_relation=positional_relation(*pair)
    scenario=ScenarioState(
        hand_id=ledger.hand_id,street=Street.PREFLOP,
        hero_position=Position(hero),hand_class=hand_class,
        dealt_players=6, active_players=len(ledger.alive),
        effective_stack_bb=stack,pot_bb=ledger.pot_bb,
        to_call_bb=ledger.to_call(hero),pot_type=PotType.SRP,
        facing=Facing.VS_OPEN,positional_relation=position_relation,
        opponent_position=Position(opener.position),
        prev_line=ledger.history_key(),aggressor=opener.position,
        source_quality='HIGH'
    )
    p=policy_for(scenario)
    if p is None:
        return None
    for a in p.actions:
        if a.action.value=='RAISE':
            t=a.raise_to_bb
            if t is None or t < ledger.min_raise_to()-EPS or t > ledger.seats[hero].balance + ledger.seats[hero].contrib + EPS:
                raise LedgerError('3bet inválido para stack mínimo/posição/sizing')
        elif a.action.value=='CALL' and not (ledger.to_call(hero)>0 and ledger.seats[hero].balance>=ledger.to_call(hero)-EPS):
            raise LedgerError('CALL inválido no nó VS_OPEN')
    return p
