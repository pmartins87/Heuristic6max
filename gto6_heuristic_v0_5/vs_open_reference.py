"""PF VS_OPEN 6-max, 100BB — PROTÓTIPO HEURÍSTICO, NÃO OPERACIONAL.

15 pares posicionais; 169 classes por par. Mãos e misturas são estimativas
explícitas do projeto, NÃO tabelas GTO exatas, nem copiadas de um solver.
Blocos de call podem incluir mãos de 3-bet por legibilidade; há precedência
explícita (3BET > CALL), sombra registrada na auditoria, nenhuma soma duplicada.
Aplicabilidade: 6 jogadores, todos com 95–105BB iniciais, sem ante,
open sem limpers/callers, valor de abertura exatamente 2.5BB ou 3BB (SB),
nenhum 3-bet anterior. Sizing sem rake calibrado -> DRAFT.
"""
from __future__ import annotations
from dataclasses import dataclass
import csv
from pathlib import Path
from typing import Optional

from scenario_contract import (Action, Facing, Policy, PositionalRelation, Position,
    PotType, ScenarioState, Street, WeightedAction, all_hand_classes,
    combo_count, pick_action, validate_hand_class, ContractError)
from rfi_reference import expand_range

VERSION = 'v0.3-DRAFT'
POSITIONS = ('LJ','HJ','CO','BTN','SB','BB')
# Hand groups: hard-coded by opponent/hero pair; conservative default = FOLD.
# Intepretation: CORE 3bet 100%; MIX3C 3bet 65%/call35%; MIX3F 3bet 60%/fold40%;
# CALL 100%; MIXCF call 55%/fold45%. Rates are design hypotheses, not solver outputs.
# Call includes broad seed pools; 3bet buckets take precedence; shadow count audited.
@dataclass(frozen=True)
class Spec:
    opener: str
    hero: str
    core: str
    mix3c: str
    mix3f: str
    call: str
    mixcf: str
    note: str
    p3c: float = .65
    p3f: float = .60
    pcf: float = .55

SPECS: tuple[Spec,...] = (
    Spec('LJ','HJ','QQ+ AKs AKo','JJ TT AQs AQo','A5s A4s KTs',
         '99 88 77 AJs ATs KQs KJs QJs JTs','66 55 T9s 98s',
         'Tight EP versus EP: menor frequência de blefes, call seletivo com realização de equidade'),
    Spec('LJ','CO','QQ+ AKs AKo','JJ TT AQs AQo AJs KQs','A5s A4s KTs QTs 76s',
         '99 88 77 66 KJs QJs JTs T9s 98s AJs','55 44 87s 76s',
         'CO versus EP: vantagem de posição pós-flop, evitar calls dominados'),
    Spec('LJ','BTN','QQ+ AKs AKo','JJ TT AQs AQo AJs KQs','A5s A4s KTs QTs 87s',
         '99 88 77 66 55 AJs ATs KJs QJs JTs T9s 98s 87s','44 33 76s 65s',
         'BTN versus EP: call seletivo para aproveitar posição'),
    Spec('LJ','SB','JJ+ AQs+ AKo','TT AQo AJs KQs','A5s A4s A3s KTs QTs JTs',
         '', '', 'SB fora de posição: política 3bet/fold sob rake não definido; call deliberadamente ausente',p3c=.70),
    Spec('LJ','BB','JJ+ AQs+ AKo','TT AQo AJs KQs','A5s A4s A3s KTs QTs 76s 65s',
         '22+ A2s+ K6s+ Q7s+ J8s+ T8s+ 97s+ 86s+ 75s+ 64s+ 53s+ ATo+ KJo+ QJo JTo',
         'K9o Q9o J9o 98o 87o 76o',
         'BB defend mais que outras posições por pot odds; calls largos não equivalem a EV comprovado',p3c=.60,p3f=.60,pcf=.40),

    Spec('HJ','CO','QQ+ AKs AKo','JJ TT AQs AQo AJs KQs','A5s A4s KTs QTs JTs',
         '99 88 77 66 ATs KJs QJs T9s 98s 87s','55 44 76s 65s',
         'CO contra HJ: força de 3bet aumenta moderadamente versus LJ'),
    Spec('HJ','BTN','QQ+ AKs AKo','JJ TT AQs AQo AJs KQs','A5s A4s A3s KTs QTs JTs 76s',
         '99 88 77 66 55 ATs A9s KJs QJs JTs T9s 98s 87s 76s',
         '44 33 65s 54s KQo',
         'BTN contra HJ: amplia calls IP sem sobrejogar mãos dominadas'),
    Spec('HJ','SB','JJ+ AQs+ AKo','TT AQo AJs KQs','A5s A4s A3s KTs QTs JTs 98s',
         '', '', 'SB contra HJ: 3bet/fold para não criar pote dominado OOP',p3c=.75),
    Spec('HJ','BB','JJ+ AQs+ AKo','TT AQo AJs KQs','A5s A4s A3s A2s KTs QTs JTs 76s 65s',
         '22+ A2s+ K6s+ Q7s+ J8s+ T8s+ 97s+ 86s+ 75s+ 64s+ 53s+ ATo+ KJo+ QJo JTo',
         'K9o K8o Q9o J9o T9o 98o 87o',
         'BB defende mais conforme agressor abre range mais largo',p3c=.65,p3f=.65,pcf=.50),

    Spec('CO','BTN','JJ+ AQs+ AKo','TT 99 AJs AQo KQs','A5s A4s A3s A2s A9s A8s A7s KTs K9s QTs Q9s JTs J9s T9s T8s 98s 97s AJo',
         '22+ A8s+ K9s+ Q9s+ J9s+ T8s+ 98s 87s 76s AJo+ KQo',
         'A7s A6s K8s Q8s 65s 54s',
         'BTN vs CO: maior 3bet polarizado e call IP; pequenos pares e conectores para cobertura',p3c=.65,p3f=.65),
    Spec('CO','SB','TT+ AJs+ AQo+ KQs','99 ATo A5s A4s','A3s A2s KTs QTs JTs T9s 98s 87s',
         '', '', 'SB versus CO: 3bet/fold OOP; mix de blockers sem call',p3c=.75,p3f=.75),
    Spec('CO','BB','TT+ AJs+ AQo+ KQs','99 ATs AJo KJs QJs','A5s A4s A3s A2s A5o KTs T9s 98s 76s 65s',
         '22+ A2s+ K4s+ Q6s+ J7s+ T7s+ 96s+ 85s+ 74s+ 64s+ 53s+ ATo+ KTo+ QTo+ JTo T9o 98o',
         'K8o K7o Q8o J8o T8o 87o 76o',
         'BB versus CO: mais defesa de mãos suited e Ax, evitar automatizar quaisquer duas cartas',p3c=.65,p3f=.70,pcf=.60),

    Spec('BTN','SB','99+ ATs+ AJo+ KQs KJs','88 77 A9s ATo KQo QJs','A5s A4s A3s A2s KTs QTs JTs T9s 98s 87s 76s',
         '', '', 'SB versus BTN: 3bet/fold; o maior steal exige resposta mais ampla',p3c=.75,p3f=.80),
    Spec('BTN','BB','99+ ATs+ AJo+ KQs KJs','88 77 A9s ATo KQo QJs','A5s A4s A3s A2s A5o KTs K9s QTs Q9s JTs J9s T9s 98s 87s 76s',
         '22+ A2s+ K5s+ Q4s+ J5s+ T6s+ 96s+ 85s+ 74s+ 63s+ 52s+ A5o+ K7o+ Q9o+ J9o+ T8o+ 98o',
         'Q7o J7o T7o 97o 86o 75o 64o 54o',
         'BB versus BTN: range de defesa significativamente mais largo, mas offsuit marginais ficam mistos',p3c=.70,p3f=.70,pcf=.50),
    Spec('SB','BB','88+ ATs+ ATo+ KQs KJs','77 66 A9s A9o KQo KTs QJs','A5s A4s A3s A2s A5o K9s K8s K7s K6s QTs Q9s Q8s JTs J9s J8s T9s T8s 98s 87s 76s',
         '22+ A2s+ K2s+ Q2s+ J4s+ T5s+ 95s+ 84s+ 73s+ 63s+ 52s+ A5o+ K7o+ Q8o+ J7o+ T7o+ 97o+ 86o 75o 64o 54o',
         'Q6o Q5o J6o T6o 96o 85o 74o 53o',
         'BB em posição versus SB: defesa ampla; open do SB é 3BB, não 2.5BB',p3c=.70,p3f=.70,pcf=.70),
)

BY_PAIR = {(s.opener, s.hero): s for s in SPECS}
assert len(BY_PAIR) == 15 and len(SPECS) == 15

@dataclass(frozen=True)
class Row:
    threebet: float
    call: float
    fold: float
    bucket: str


def _prepare(spec: Spec):
    groups={key:expand_range(getattr(spec,key)) for key in ('core','mix3c','mix3f','call','mixcf')}
    # Ações 3bet entre si não podem se sobrepor: erro de especificação.
    for a,b in (('core','mix3c'),('core','mix3f'),('mix3c','mix3f')):
        if groups[a] & groups[b]:
            raise ContractError(f'colisão 3bet {spec.opener}->{spec.hero} {a}/{b}: {sorted(groups[a]&groups[b])}')
    # CALL pode carregar mãos da camada agressiva para auditoria, mas não revoga agressividade.
    if groups['call'] & groups['mixcf']:
        raise ContractError(f'colisão CALL e MIXCF {spec.opener}->{spec.hero}')
    return groups


def build_vs_open():
    mapping={}; shadows={}
    for sp in SPECS:
        groups=_prepare(sp)
        assigned=set().union(groups['core'],groups['mix3c'],groups['mix3f'])
        shadows[(sp.opener,sp.hero)] = tuple(sorted((groups['call']|groups['mixcf']) & assigned))
        rows={}
        for h in all_hand_classes():
            if h in groups['core']:
                row=Row(1,0,0,'3BET_VALUE_PURE')
            elif h in groups['mix3c']:
                # SB, em cenário raked ainda não calibrado, não tem flat pré-flop.
                row=(Row(sp.p3c,0,1-sp.p3c,'3BET_FOLD_MIX') if sp.hero=='SB'
                     else Row(sp.p3c,1-sp.p3c,0,'3BET_CALL_MIX'))
            elif h in groups['mix3f']:
                row=Row(sp.p3f,0,1-sp.p3f,'3BET_FOLD_MIX')
            elif h in groups['call']:
                row=Row(0,1,0,'CALL_PURE')
            elif h in groups['mixcf']:
                row=Row(0,sp.pcf,1-sp.pcf,'CALL_FOLD_MIX')
            else:
                row=Row(0,0,1,'FOLD_PURE')
            if abs(row.threebet+row.call+row.fold-1)>1e-10:
                raise ContractError(f'probabilidade inválida: {sp.opener}->{sp.hero} {h}')
            rows[h]=row
        mapping[(sp.opener,sp.hero)] = rows
    return mapping,shadows

RANGES, SHADOWS = build_vs_open()


def aggregate(opener:str, hero:str, action:str) -> float:
    idx={'3BET':'threebet','CALL':'call','FOLD':'fold'}[action]
    return 100*sum(combo_count(h)*getattr(row,idx) for h,row in RANGES[(opener,hero)].items())/1326


def expected_open(opener:str)->float:
    return 3.0 if opener=='SB' else 2.5


def expected_pot_bb(opener:str)->float:
    # SB já colocou 0.5BB; o raise para 3BB acrescenta 2.5BB, não 3BB.
    return expected_open(opener) + (1.0 if opener=='SB' else 1.5)


def positional_relation(opener:str, hero:str) -> PositionalRelation:
    # IP contra opener não significa necessariamente IP se jogadores atrás entrarem.
    return PositionalRelation.IP if hero=='BTN' or (hero in ('HJ','CO') and POSITIONS.index(hero)>POSITIONS.index(opener)) or (hero=='BB' and opener=='SB') else PositionalRelation.OOP


def threebet_to_bb(opener:str,hero:str)->float:
    # Estudo de sizing total em BB, não raise-by; fora de posição maior.
    opening=expected_open(opener)
    if positional_relation(opener,hero)==PositionalRelation.IP:
        return round(opening*3.2,2)
    return round(opening*4.1,2)


def policy_for(s:ScenarioState)->Optional[Policy]:
    if (s.street!=Street.PREFLOP or s.facing!=Facing.VS_OPEN
        or s.pot_type!=PotType.SRP or s.dealt_players!=6
        or s.opponent_position is None
        or 95> s.effective_stack_bb or s.effective_stack_bb>105
        or s.hero_position.value not in POSITIONS
        or s.source_quality!='HIGH'):
        return None
    pair=(s.opponent_position.value,s.hero_position.value)
    if pair not in RANGES or s.positional_relation!=positional_relation(*pair):
        return None
    if abs(s.to_call_bb - (expected_open(pair[0]) - (0.5 if pair[1]=='SB' else 1.0 if pair[1]=='BB' else 0)))>1e-6:
        return None
    if abs(s.pot_bb-expected_pot_bb(pair[0]))>1e-6:
        return None
    w=RANGES[pair][s.hand_class]
    acts=[]
    if w.threebet>0:
        acts.append(WeightedAction(Action.RAISE,w.threebet,raise_to_bb=threebet_to_bb(*pair)))
    if w.call>0:
        acts.append(WeightedAction(Action.CALL,w.call))
    if w.fold>0:
        acts.append(WeightedAction(Action.FOLD,w.fold))
    return Policy(f'PF.VS_OPEN.{pair[0]}.{pair[1]}.{s.hand_class}.{VERSION}',tuple(acts),
        f'{BY_PAIR[pair].note}. Resposta ao primeiro open, sem limpers/callers. Não é solução GTO.',
        'HEURISTIC_MANUAL_15_NODES_WITH_AGGREGATE_CROSSCHECK',status='DRAFT')


def decide(s:ScenarioState):
    p=policy_for(s)
    return pick_action(p,s) if p else None


def export_csv(path:Path|str):
    with Path(path).open('w',encoding='utf-8',newline='') as fh:
        writer=csv.writer(fh)
        writer.writerow(['Opener','Hero','Hand','Combos','3bet_pct','Call_pct','Fold_pct','3bet_to_bb','Bucket','Provenance','Status'])
        for pair,rows in RANGES.items():
            for hand,row in rows.items():
                writer.writerow([*pair,hand,combo_count(hand),f'{100*row.threebet:.8f}',f'{100*row.call:.8f}',
                    f'{100*row.fold:.8f}',f'{threebet_to_bb(*pair):.2f}',row.bucket,'HEURISTIC_MANUAL','DRAFT'])

if __name__=='__main__':
    for pair in RANGES:
        print('%s -> %s'%pair, *(f'{act}={aggregate(*pair,act):.2f}%' for act in ('3BET','CALL','FOLD')),
              'shadows=',len(SHADOWS[pair]))
