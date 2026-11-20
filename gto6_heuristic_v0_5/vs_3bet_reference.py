"""Defesa do RFI original quando um adversário aplica 3-bet — v0.4 DRAFT.

Jogo: NLHE cash 6-max, todos 95-105BB, sem ante/limp/caller/squeeze;
RFI 2.5BB (LJ/HJ/CO/BTN), 3BB SB; 3-bets estritamente iguais aos
sizings VS_OPEN da versão anterior. Sem solver/EV validado; NÃO OPERACIONAL.

As respostas condicionais só existem para classes com p(RAISE_RFI)>0; não
tratamos mãos que nunca são abertas como folds triviais de defesa à 3-bet.
4BET é raise-to normal, nunca SHOVE nesta família.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv

from scenario_contract import (Action, Facing, Policy, PositionalRelation, Position,
    PotType, ScenarioState, Street, WeightedAction, all_hand_classes, combo_count,
    pick_action, ContractError)
from rfi_reference import RANGES as RFI_RANGES, expand_range
from vs_open_reference import SPECS as OPEN_SPECS, threebet_to_bb, expected_open

VERSION='v0.4-DRAFT'

@dataclass(frozen=True)
class Spec:
    opener: str
    threebettor: str
    pure4: str
    mix4call: str
    mix4fold: str
    purecall: str
    mixcallfold: str
    rationale: str
    p4call: float=.65
    p4fold: float=.25
    pcallfold: float=.55

# EXPLICIT hand classes, independently auditable in each of the 15 positional trees.
# Mixed frequencies are design hypotheses, not extracted frequencies from a solver.
SPECS: tuple[Spec,...] = (
    Spec('LJ','HJ','AA KK AKs','QQ AKo','A5s A4s',
         'JJ TT AQs','99 88 AJs KQs',
         'LJ OOP vs HJ: continue tight; premium 4bets, selective broadway calls',.65,.25,.55),
    Spec('LJ','CO','AA KK AKs','QQ AKo','A5s A4s',
         'JJ TT AQs','99 88 AJs KQs ATs',
         'LJ OOP vs CO: 4bet premium; marginal pairs mix call/fold',.65,.25,.55),
    Spec('LJ','BTN','AA KK AKs','QQ AKo','A5s A4s',
         'JJ TT AQs','99 88 AJs KQs ATs',
         'LJ OOP vs BTN: balanced value/blockers, avoid over-defending',.65,.30,.55),
    Spec('LJ','SB','AA KK AKs','QQ AKo','A5s A4s',
         'JJ TT AQs AQo AJs KQs 99 88','77 66 ATs KJs QJs JTs',
         'LJ IP vs SB: more calls with equity realization and suits',.60,.25,.60),
    Spec('LJ','BB','AA KK AKs','QQ AKo','A5s A4s',
         'JJ TT AQs AQo AJs KQs 99 88','77 66 ATs KJs QJs JTs',
         'LJ IP vs BB: defend wider than versus IP 3bettor',.60,.25,.60),
    Spec('HJ','CO','AA KK AKs','QQ AKo','A5s A4s',
         'JJ TT AQs AJs KQs','99 88 ATs KJs QJs',
         'HJ OOP vs CO: preserve a conservative call region',.65,.25,.55),
    Spec('HJ','BTN','AA KK AKs','QQ AKo','A5s A4s',
         'JJ TT AQs AJs KQs','99 88 ATs KJs QJs JTs',
         'HJ OOP vs BTN: separate premium 4bet from bluff 4bet',.65,.30,.55),
    Spec('HJ','SB','AA KK AKs','QQ AKo','A5s A4s A3s',
         'JJ TT 99 AQs AQo AJs KQs KJs QJs','88 77 ATs JTs T9s',
         'HJ IP vs SB: suited and pair calls increase',.60,.30,.60),
    Spec('HJ','BB','AA KK AKs','QQ AKo','A5s A4s A3s',
         'JJ TT 99 AQs AQo AJs KQs KJs QJs','88 77 ATs JTs T9s',
         'HJ IP vs BB: mix suited ace blockers into 4bet bluffs',.60,.30,.60),
    Spec('CO','BTN','AA KK AKs','QQ JJ AKo','A5s A4s A3s',
         'TT 99 88 AQs AQo AJs KQs KJs QJs JTs',
         '77 66 ATo ATs 98s 87s',
         'CO OOP vs BTN: wider defense, but protect low suited connectors',.65,.30,.55),
    Spec('CO','SB','AA KK AKs','QQ JJ AKo','A5s A4s A3s',
         'TT 99 88 AQs AQo AJs ATs KQs KJs QJs JTs T9s',
         '77 66 A9s AJo 98s 87s',
         'CO IP vs SB: more suited and broadway calls, 4bet not shove',.60,.30,.60),
    Spec('CO','BB','AA KK AKs','QQ JJ AKo','A5s A4s A3s',
         'TT 99 88 AQs AQo AJs ATs KQs KJs QJs JTs T9s',
         '77 66 A9s AJo 98s 87s',
         'CO IP vs BB: consider 3bet size/pot price explicitly',.60,.30,.60),
    Spec('BTN','SB','AA KK AKs','QQ JJ AKo','A5s A4s A3s A2s K5s',
         'TT 99 88 77 AQs AQo AJs ATs KQs KJs QJs JTs T9s 98s AJo KQo',
         '66 55 44 A9s A8s KTs QTs J9s 87s 76s',
         'BTN IP vs SB: wide call region with mix, premium 4bets',.55,.35,.60),
    Spec('BTN','BB','AA KK AKs','QQ JJ AKo','A5s A4s A3s A2s K5s',
         'TT 99 88 77 66 55 AQs AQo AJs ATs KQs KJs KTs QJs QTs JTs T9s 98s 87s KQo AJo',
         '44 33 22 A9s A8s A7s A6s K9s Q9s J9s T8s 76s 65s ATo KJo',
         'BTN IP vs BB: highest BTN continue density; not every suited trash hand',.55,.35,.60),
    Spec('SB','BB','AA KK AKs','QQ JJ AKo','A5s A4s A3s A2s K5s',
         'TT 99 88 77 AQs AQo AJs ATs KQs KJs QJs JTs T9s 98s KQo AJo ATo',
         '66 55 44 A9s A8s KTs QTs 87s 76s KJo QJo',
         'SB OOP vs BB: separate RFI-raise line from SB limps',.60,.35,.55),
)
BY_PAIR={(x.opener,x.threebettor):x for x in SPECS}
assert len(SPECS)==15 and len(BY_PAIR)==15
assert set(BY_PAIR)=={(x.opener,x.hero) for x in OPEN_SPECS}

@dataclass(frozen=True)
class Row:
    fourbet: float
    call: float
    fold: float
    bucket: str
    open_probability: float


def opener_relation(opener:str,threebettor:str)->PositionalRelation:
    # Ação pós-flop: qualquer agressor nos blinds joga OOP contra opener,
    # EXCETO SB originalmente abrindo e BB aplicando 3bet (SB permanece OOP).
    return (PositionalRelation.IP if threebettor in ('SB','BB') and opener!='SB'
            else PositionalRelation.OOP)


def fourbet_to_bb(opener:str,threebettor:str)->float:
    three_to=threebet_to_bb(opener,threebettor)
    factor=2.30 if opener_relation(opener,threebettor)==PositionalRelation.IP else 2.65
    return round(three_to*factor+1e-8,2)


def expected_pot_bb(opener:str,threebettor:str)->float:
    # Pot includes both final street contributions; blinds already included.
    seats={opener,threebettor}
    return (expected_open(opener)+threebet_to_bb(opener,threebettor)
            +(0.5 if 'SB' not in seats else 0.0)
            +(1.0 if 'BB' not in seats else 0.0))


def _build():
    ranges={}
    audit=[]
    for sp in SPECS:
        pair=sp.opener,sp.threebettor
        groups={key:expand_range(getattr(sp,key)) for key in ('pure4','mix4call','mix4fold','purecall','mixcallfold')}
        for key in groups:
            for other in groups:
                if key>=other:
                    continue
                dup=groups[key]&groups[other]
                if dup:
                    raise ContractError(f'VS_3BET overlapping ranges {pair} {key}/{other}: {sorted(dup)}')
        if not (0<=sp.p4call<=1 and 0<=sp.p4fold<=1 and 0<=sp.pcallfold<=1):
            raise ContractError(f'probabilidade mista inválida {pair}')
        unknown=[(key,hand) for key,hs in groups.items() for hand in hs
                 if RFI_RANGES[Position(sp.opener)][hand]['RAISE']==0]
        if unknown:
            raise ContractError(f'mão não aberta em RFI aparece em defesa VS_3BET {pair}: {unknown}')
        rows={}
        for h in all_hand_classes():
            open_p=RFI_RANGES[Position(sp.opener)][h]['RAISE']
            if open_p<=0:
                row=Row(0,0,0,'NOT_REACHABLE_FROM_RFI',0)
            elif h in groups['pure4']:
                row=Row(1,0,0,'4BET_VALUE_PURE',open_p)
            elif h in groups['mix4call']:
                row=Row(sp.p4call,1-sp.p4call,0,'4BET_CALL_MIX',open_p)
            elif h in groups['mix4fold']:
                row=Row(sp.p4fold,0,1-sp.p4fold,'4BET_BLUFF_FOLD_MIX',open_p)
            elif h in groups['purecall']:
                row=Row(0,1,0,'CALL_PURE',open_p)
            elif h in groups['mixcallfold']:
                row=Row(0,sp.pcallfold,1-sp.pcallfold,'CALL_FOLD_MIX',open_p)
            else:
                row=Row(0,0,1,'FOLD_PURE',open_p)
            if abs(row.fourbet+row.call+row.fold-(1 if open_p>0 else 0))>1e-10:
                raise ContractError(f'soma inválida {pair} {h}')
            rows[h]=row
        if not all(rows[h].fourbet==1 for h in ('AA','KK')):
            raise ContractError(f'AA/KK não são 4bet valor puro {pair}')
        ranges[pair]=rows
        audit.append((pair, sum(r.open_probability>0 for r in rows.values())))
    return ranges,audit

RANGES, REACHABILITY_AUDIT=_build()


def aggregate_conditional(opener:str,threebettor:str,action:str)->float:
    """Distribuição de defesa condicional à classe ter RFI, ponderada por combos.

    Não é probabilidade de chegar ao nó: depende ainda de 3bet adversária e blockers.
    """
    col={'4BET':'fourbet','CALL':'call','FOLD':'fold'}[action]
    rows=RANGES[(opener,threebettor)]
    denom=sum(combo_count(h)*row.open_probability for h,row in rows.items())
    return 100*sum(combo_count(h)*row.open_probability*getattr(row,col) for h,row in rows.items())/denom


def policy_for(s:ScenarioState):
    if (s.street!=Street.PREFLOP or s.facing!=Facing.VS_3BET
        or s.pot_type!=PotType.THREE_BET or s.dealt_players!=6
        or s.opponent_position is None or s.source_quality!='HIGH'
        or not 95<=s.effective_stack_bb<=105):
        return None
    pair=(s.hero_position.value,s.opponent_position.value)
    if pair not in RANGES or s.positional_relation!=opener_relation(*pair):
        return None
    if (abs(s.pot_bb-expected_pot_bb(*pair))>1e-6 or
        abs(s.to_call_bb-(threebet_to_bb(*pair)-expected_open(pair[0])))>1e-6):
        return None
    row=RANGES[pair][s.hand_class]
    if row.open_probability<=0:
        return None  # impossible if our baseline RFI was followed; fail closed
    actions=[]
    if row.fourbet>0:
        actions.append(WeightedAction(Action.RAISE,row.fourbet,raise_to_bb=fourbet_to_bb(*pair)))
    if row.call>0:
        actions.append(WeightedAction(Action.CALL,row.call))
    if row.fold>0:
        actions.append(WeightedAction(Action.FOLD,row.fold))
    return Policy(f'PF.VS_3BET.{pair[0]}.{pair[1]}.{s.hand_class}.{VERSION}',tuple(actions),
        BY_PAIR[pair].rationale+'; 100BB; strategy DRAFT; conditioned on opened RFI, no multiway.',
        'HEURISTIC_EXPLICIT_15_TREES_NO_SOLVER',status='DRAFT')


def decide(s:ScenarioState):
    p=policy_for(s)
    return pick_action(p,s) if p is not None else None


def export_csv(path:Path|str):
    with Path(path).open('w',encoding='utf-8',newline='') as fh:
        w=csv.writer(fh)
        w.writerow(['Opener','Threebettor','Hand','Combos','RFI_open_probability_pct',
            'Reachable','Fourbet_pct_given_open','Call_pct_given_open','Fold_pct_given_open',
            'Fourbet_to_bb','Bucket','Provenance','Status'])
        for pair,rows in RANGES.items():
            for hand,r in rows.items():
                w.writerow([*pair,hand,combo_count(hand),f'{100*r.open_probability:.8f}',
                    'YES' if r.open_probability>0 else 'NO',
                    *[f'{100*x:.8f}' for x in (r.fourbet,r.call,r.fold)],
                    f'{fourbet_to_bb(*pair):.2f}' if r.open_probability>0 else '',
                    r.bucket,'MANUAL_HEURISTIC_NO_SOLVER','DRAFT'])

if __name__=='__main__':
    for (op,bet),rows in RANGES.items():
        print(op,bet,'reachable',sum(r.open_probability>0 for r in rows.values()),
              *(f'{action}={aggregate_conditional(op,bet,action):.1f}%' for action in ('4BET','CALL','FOLD')))
