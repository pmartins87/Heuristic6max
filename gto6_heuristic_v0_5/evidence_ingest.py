"""Importador CANÔNICO de ações verificadas manualmente (não extrai OCR/log bruto).

Schema input JSON: {hand_id,seats,events:[{actor,move,to_bb?,verified:true}],
observation:{...}}. Sem verified:true em TODOS eventos -> rejeita.
O argumento de observação vem de outra fonte e deve ser estável e completo;
a própria importação não declara um scrape como confiável.
"""
from __future__ import annotations
import json
from pathlib import Path
from action_ledger import HandLedger, LedgerError, Move, Round
from strict_observation import Observation, SeenSeat, validate_observation


def load_verified_fixture(path:str|Path)->tuple[HandLedger,Observation]:
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(obj,dict) or not all(k in obj for k in ('hand_id','seats','events','observation')):
        raise LedgerError('fixture sem cabeçalho obrigatório')
    ledger=HandLedger(obj['hand_id'],obj['seats'])
    if not isinstance(obj['events'],list):
        raise LedgerError('events deve ser uma lista')
    for idx,e in enumerate(obj['events']):
        if e.get('verified') is not True or e.get('source')!='MANUAL_VERIFIED':
            raise LedgerError(f'evento #{idx} sem confirmação independente')
        try:
            move=Move(e['move'])
        except (KeyError, ValueError):
            raise LedgerError(f'evento #{idx} inválido') from None
        ledger.act(e['actor'],move,e.get('to_bb'))
    o=obj['observation']
    obs=Observation(
        hand_id=o['hand_id'],street=Round(o['street']),
        hero_position=o['hero_position'],hero_turn=o['hero_turn'],
        pot_bb=o['pot_bb'],hero_to_call_bb=o['hero_to_call_bb'],
        seats={p:SeenSeat(**s) for p,s in o['seats'].items()},
        complete_history=bool(o.get('complete_history',False)),
        stable_scrape=bool(o.get('stable_scrape',False)))
    validate_observation(ledger,obs)
    return ledger,obs
