"""Fail-closed VS_3BET: only one RFI and one genuine 3-bet, heads-up, 100BB.

Imports the unchanged, validated 6-max action ledger and strict observation.
This is NOT an OpenHoldem scraper or an operational poker bot.
"""
from __future__ import annotations
from typing import Optional
from action_ledger import HandLedger, LedgerError, Move, Round
from strict_observation import Observation, validate_observation
from scenario_contract import (Action, Facing, Policy, Position, PotType,
    ScenarioState, Street, validate_hand_class)
from vs_open_reference import expected_open, threebet_to_bb
from vs_3bet_reference import (BY_PAIR, fourbet_to_bb, opener_relation, policy_for, expected_pot_bb)

EPS=1e-6


def prepare_vs_3bet(ledger:HandLedger, seen:Observation, hand_class:str)->Optional[Policy]:
    """None = unsupported/unreachable. LedgerError = contradictory evidence/state.

    Never convert None to Fold/Check. No call or shove can be emitted for a
    misidentified squeeze/multiway 3-bet or an unreconciled screenshot.
    """
    validate_observation(ledger,seen)
    validate_hand_class(hand_class)
    opener=ledger.next_actor
    if ledger.street!=Round.PREFLOP or opener is None or len(ledger.seats)!=6:
        return None
    if any(not 95<=s.original_stack<=105 for s in ledger.seats.values()):
        return None
    if ledger.pf_facing(opener)!='VS_3BET':
        return None
    pf=[e for e in ledger.events if e.street==Round.PREFLOP]
    raises=[e for e in pf if e.is_aggressive]
    if len(raises)!=2 or any(e.move not in (Move.FOLD,Move.RAISE) for e in pf):
        return None
    first,second=raises
    pair=(first.position,second.position)
    if pair not in BY_PAIR or opener!=first.position:
        return None
    if len(ledger.alive)!=2 or set(ledger.alive)!={*pair}:
        return None
    if first.street_to_bb is None or second.street_to_bb is None:
        return None
    if first.move!=Move.RAISE or second.move!=Move.RAISE or second.is_squeeze:
        return None
    if abs(first.street_to_bb-expected_open(pair[0]))>EPS:
        return None
    if abs(second.street_to_bb-threebet_to_bb(*pair))>EPS:
        return None
    if abs(ledger.bet_level-threebet_to_bb(*pair))>EPS:
        return None
    if abs(ledger.pot_bb-expected_pot_bb(*pair))>EPS:
        return None
    if any(ledger.seats[p].allin for p in pair):
        return None
    effective_stack=min(ledger.seats[p].original_stack for p in pair)
    scenario=ScenarioState(
        hand_id=ledger.hand_id,street=Street.PREFLOP,
        hero_position=Position(opener),hand_class=hand_class,
        dealt_players=6,active_players=len(ledger.alive),
        effective_stack_bb=effective_stack,pot_bb=ledger.pot_bb,
        to_call_bb=ledger.to_call(opener),pot_type=PotType.THREE_BET,
        facing=Facing.VS_3BET,positional_relation=opener_relation(*pair),
        opponent_position=Position(second.position),
        prev_line=ledger.history_key(),aggressor=second.position,
        source_quality='HIGH')
    p=policy_for(scenario)
    if p is None:
        return None
    for action in p.actions:
        if action.action==Action.RAISE:
            size=action.raise_to_bb
            if (size is None or abs(size-fourbet_to_bb(*pair))>EPS
                or size < ledger.min_raise_to()-EPS
                or size > ledger.seats[opener].contrib + ledger.seats[opener].balance + EPS):
                raise LedgerError('4bet-to inválido no ledger')
        elif action.action==Action.CALL:
            if not (ledger.to_call(opener)>EPS and
                    ledger.seats[opener].balance+EPS>=ledger.to_call(opener)):
                raise LedgerError('CALL inválido no ledger')
        elif action.action!=Action.FOLD:
            raise LedgerError('ação inesperada em VS_3BET')
    return p
