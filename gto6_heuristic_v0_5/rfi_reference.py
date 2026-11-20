"""RFI HEURÍSTICO de 100 BB para estudo e revisão (NÃO release de bot).

As frequências agregadas de referência são do Simple GTO (100BB, rake 500z).
As escolhas de mãos e misturas são aproximações explícitas próprias, NÃO output do solver.
Comparar os agregados não valida a qualidade das mãos individuais.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import math
from pathlib import Path

from scenario_contract import (Action, ContractError, Policy, Position,
                               ScenarioState, Street, Facing, PotType,
                               WeightedAction, all_hand_classes, combo_count, pick_action)

SOURCE_URL = 'https://simplegto.com/learn/preflop-statistics'
TARGETS = {
    Position.LJ: {'RAISE': 0.183, 'LIMP': 0.0},
    Position.HJ: {'RAISE': 0.225, 'LIMP': 0.0},
    Position.CO: {'RAISE': 0.293, 'LIMP': 0.0},
    Position.BTN: {'RAISE': 0.434, 'LIMP': 0.0},
    Position.SB: {'RAISE': 0.358, 'LIMP': 0.146},
}
RFI_VERSION = 'v0.2-DRAFT'
PREFLOP_SIZE = {Position.LJ:2.5, Position.HJ:2.5, Position.CO:2.5, Position.BTN:2.5, Position.SB:3.0}


def expand_range(tokens: str) -> set[str]:
    """Expande notação explícita com sufixo +; nunca usa score artificial."""
    ranks='23456789TJQKA'
    valid=set(all_hand_classes())
    out=set()
    for token in tokens.split():
        if not token.endswith('+'):
            if token not in valid:
                raise ContractError(f'classe no range inválida: {token}')
            out.add(token)
            continue
        base=token[:-1]
        if len(base)==2 and base[0]==base[1]:
            for r in ranks[ranks.index(base[0]):]:out.add(r+r)
        elif len(base)==3 and base[2] in ('s','o'):
            hi,lo,typ=base
            if ranks.index(hi)<=ranks.index(lo):
                raise ContractError(f'range malformado: {token}')
            for r in ranks[ranks.index(lo):ranks.index(hi)]:
                out.add(hi+r+typ)
        else:raise ContractError(f'range malformado: {token}')
    if not out<=valid:raise ContractError('range gerou mão inválida')
    return out


# NOTA: elaboração heurística humana, não output individual de solver.
# Os grupos cumulativos são descrições explícitas revisáveis de mãos (169 classes).
# Classes extras do SB são uma aproximação da divisão raise/limp, e serão reavaliadas.
_LJ_FULL = expand_range('22+ A2s+ K9s+ Q9s+ J9s+ T9s 98s 87s 76s ATo+ KQo')
_HJ_EXTRA_FULL = expand_range('KJo K8s Q8s J8s T8s 97s 86s 75s 65s 54s A9o')
_CO_EXTRA_FULL = expand_range('QJo A8o A7o A5o KTo QTo JTo K7s Q7s J7s')
_BTN_EXTRA_FULL = expand_range('A6o A4o A3o A2o K9o K8o Q9o J9o T9o 98o K6s K5s K4s K3s K2s Q6s Q5s Q4s J6s J5s T7s T6s 96s 85s 74s 64s')
_SB_EXTRA_RAISE_FULL = expand_range('A6o A4o A3o A2o K9o K8o K6s K5s K4s')
_SB_EXTRA_LIMP_FULL = expand_range('Q9o J9o T9o 98o K2s Q6s Q5s Q4s J6s J5s T7s T6s 96s 85s 74s 64s 53s K7o K6o K5o Q8o Q7o J8o T8o')


def _make(weights: dict[str,float]) -> dict[str,float]:
    result={h:0. for h in all_hand_classes()}
    for h,w in weights.items():
        if h not in result or not 0<=w<=1:raise ContractError(f'peso manual inválido: {h}:{w}')
        result[h]=w
    return result


def build_rfi() -> dict[Position, dict[str, dict[str,float]]]:
    # Inputs explícitos; qualquer alteração deve atualizar test_rfi_reference.py e changelog.
    lj=_make({h:1. for h in _LJ_FULL})
    lj['KJo']=0.40
    hj=dict(lj)
    hj.update({h:1. for h in _HJ_EXTRA_FULL})
    hj['QJo']=0.50
    co=dict(hj)
    co.update({h:1. for h in _CO_EXTRA_FULL})
    btn=dict(co)
    btn.update({h:1. for h in _BTN_EXTRA_FULL})
    btn['53s']=0.50
    sb=dict(co)
    sb.update({h:1. for h in _SB_EXTRA_RAISE_FULL})
    sb['K3s']=0.50
    sb_limp=_make({h:1. for h in _SB_EXTRA_LIMP_FULL})
    sb_limp['97o']=0.75
    sb_limp['K2s']=1.
    # A limp branch nunca pode se sobrepor ao raise; auditável por assert.
    if any(sb[h]+sb_limp[h]>1+1e-8 for h in all_hand_classes()):
        raise ContractError('sobreposição raise/limp SB')
    results={}
    for pos, raises in ((Position.LJ,lj),(Position.HJ,hj),(Position.CO,co),(Position.BTN,btn),(Position.SB,sb)):
        results[pos]={}
        for h in all_hand_classes():
            rw=raises[h]
            lw=sb_limp[h] if pos==Position.SB else 0.
            results[pos][h]={'RAISE':rw,'LIMP':lw,'FOLD':1-rw-lw}
    return results


def aggregate(position: Position, action: str) -> float:
    return 100 * sum(combo_count(h) * RANGES[position][h][action]
                     for h in all_hand_classes()) / 1326


RANGES = build_rfi()


def aggregate(position: Position, action: str) -> float:
    return 100 * sum(combo_count(h) * RANGES[position][h][action]
                     for h in all_hand_classes()) / 1326


def scenario_is_supported(s: ScenarioState) -> bool:
    return (s.street == Street.PREFLOP and s.facing == Facing.RFI
            and s.pot_type == PotType.UNOPENED and s.dealt_players == 6
            and 95 <= s.effective_stack_bb <= 105
            and s.hero_position in RANGES and s.active_players >= 2
            and abs(s.pot_bb - 1.5) < 1e-6)


def policy_for(s: ScenarioState) -> Policy | None:
    """None quando o cenário é fora da faixa calibrada; nunca fallback automático."""
    if not scenario_is_supported(s):
        return None
    freq = RANGES[s.hero_position][s.hand_class]
    actions = []
    for key, act in (('RAISE', Action.RAISE), ('LIMP', Action.LIMP), ('FOLD', Action.FOLD)):
        if freq[key] > 1e-12:
            actions.append(WeightedAction(act, freq[key], raise_to_bb=PREFLOP_SIZE[s.hero_position] if act==Action.RAISE else None))
    return Policy(f'PF.RFI.{s.hero_position.value}.{s.hand_class}.{RFI_VERSION}',
                  tuple(actions),
                  'RFI heurístico 100BB; ranges explícitos aproximados com comparação de massa contra estatísticas publicadas, NÃO solver por mão.',
                  f'HEURISTIC_JUDGMENT; aggregate benchmark {SOURCE_URL}', status='DRAFT')


def decide(s: ScenarioState):
    p = policy_for(s)
    return pick_action(p,s) if p else None


def export_csv(path: str | Path) -> None:
    with Path(path).open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(('Position', 'Hand', 'Combos', 'Raise_pct', 'Limp_pct', 'Fold_pct', 'RaiseTo_bb', 'Source', 'Status'))
        for pos in TARGETS:
            for h in all_hand_classes():
                weights = RANGES[pos][h]
                w.writerow((pos.value, h, combo_count(h), *(f'{100*weights[k]:.8f}' for k in ('RAISE','LIMP','FOLD')),
                            PREFLOP_SIZE[pos], 'HEURISTIC_JUDGMENT_WITH_PUBLISHED_AGGREGATE', 'DRAFT'))


if __name__ == '__main__':
    print('RFI 100BB DRAFT (frequência agregada ponderada por combos)')
    for pos in TARGETS:
        print(pos.value, {a: round(aggregate(pos,a),4) for a in ('RAISE','LIMP','FOLD')})
