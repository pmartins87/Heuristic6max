"""v0.6 G2-a: auditoria condicionada à 3-bet efetivamente observada, com card removal.

Somente diagnóstico: não muda ranges nem roteamento de ações. O peso de
uma classe do Hero após RFI + 3bet é proporcional a
  P(RFI | hero_class) * sum_{hero combos} sum_{villain combos sem colisão}
                                     P(3bet | villain_class).
O modelo do vilão vem de VS_OPEN; NÃO é inferência sobre um humano real nem GTO.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import csv
from scenario_contract import combo_count
from vs_open_reference import RANGES as VILLAIN_VS_OPEN
from vs_3bet_reference import RANGES as HERO_VS_3BET, SPECS
from vs3_strategy_audit import audit_node

RANKS = '23456789TJQKA'
SUITS = 'cdhs'
CARDS = tuple(range(52))
COMBOS = tuple(combinations(CARDS, 2))


def hand_class(cards: tuple[int, int]) -> str:
    a,b = cards
    ra, rb = a // 4, b // 4
    if ra == rb: return RANKS[ra] * 2
    hi,lo = sorted((ra,rb), reverse=True)
    return RANKS[hi]+RANKS[lo]+('s' if a % 4 == b % 4 else 'o')

BY_CLASS: dict[str,tuple[tuple[int,int],...]] = {
    hand:tuple(combo for combo in COMBOS if hand_class(combo)==hand)
    for hand in HERO_VS_3BET[('LJ','HJ')]
}
assert sum(len(x) for x in BY_CLASS.values()) == 1326
assert all(len(x) == combo_count(hand) for hand,x in BY_CLASS.items())

@dataclass(frozen=True)
class AdjustedNode:
    opener:str
    threebettor:str
    old_4bet:float
    new_4bet:float
    old_call:float
    new_call:float
    old_fold:float
    new_fold:float
    bluff_share:float
    new_bluff_share:float
    model_3bet_unconditional:float
    reachable:int

    @property
    def delta4(self):return self.new_4bet-self.old_4bet
    @property
    def delta_fold(self):return self.new_fold-self.old_fold


def villain_mass_by_hero_combo(opener:str,threebettor:str):
    villain=VILLAIN_VS_OPEN[(opener,threebettor)]
    card_mass=[0.]*52
    pair_mass={}
    total=0.
    for a,b in COMBOS:
        w=villain[hand_class((a,b))].threebet
        pair_mass[(a,b)]=w
        total+=w
        card_mass[a]+=w
        card_mass[b]+=w
    # Includes the same physical two-card combination in both card sums,
    # so it must be added back exactly once (inclusion-exclusion).
    return {(a,b):max(0., total-card_mass[a]-card_mass[b]+pair_mass[a,b])
            for a,b in COMBOS},total


def adjusted_action_percentages(opener:str,threebettor:str):
    weight_by_combo,total=villain_mass_by_hero_combo(opener,threebettor)
    hero=HERO_VS_3BET[(opener,threebettor)]
    den=0.
    numer={k:0. for k in ('4BET','CALL','FOLD')}
    contrib={}
    for hand,row in hero.items():
        mass=row.open_probability*sum(weight_by_combo[c] for c in BY_CLASS[hand])
        contrib[hand]=mass
        den+=mass
        numer['4BET']+=mass*row.fourbet
        numer['CALL']+=mass*row.call
        numer['FOLD']+=mass*row.fold
    if den<=0:raise ValueError('nó sem suporte RFI+3BET')
    if abs(sum(numer.values())/den-1)>1e-10:
        raise ValueError('massa não conservada no nó')
    return {k:100*v/den for k,v in numer.items()},total/1326*100,contrib


def audit_pair(opener:str,threebettor:str)->AdjustedNode:
    old=audit_node(opener,threebettor)
    new,opp3,contrib=adjusted_action_percentages(opener,threebettor)
    rows=HERO_VS_3BET[(opener,threebettor)]
    bluff_4_mass=sum(contrib[h]*r.fourbet for h,r in rows.items()
                     if r.bucket=='4BET_BLUFF_FOLD_MIX')
    all_4_mass=sum(contrib[h]*r.fourbet for h,r in rows.items())
    adjusted_bluff_share=100*bluff_4_mass/all_4_mass if all_4_mass else 0.
    return AdjustedNode(opener,threebettor,old.fourbet_pct,new['4BET'],
                        old.call_pct,new['CALL'],old.fold_pct,new['FOLD'],
                        old.bluff_share_pct,adjusted_bluff_share,opp3,old.reached_classes)


def export_reports(output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    nodes=[audit_pair(sp.opener,sp.threebettor) for sp in SPECS]
    with (output_dir/'G2A_VS3_BLOCKER_15_NODES_v0_6.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['Opener','Threebettor','VillainModel3betPct','Old4betPct_condRFI',
            'BlockerCond4betPct','Delta4bet_pp','OldCallPct_condRFI','BlockerCondCallPct',
            'OldFoldPct_condRFI','BlockerCondFoldPct','DeltaFold_pp','OldBluffSharePct',
            'NewBluffSharePct','ReachableClasses','Status'])
        for n in nodes:
            w.writerow([n.opener,n.threebettor,*[round(x,6) for x in (
                n.model_3bet_unconditional,n.old_4bet,n.new_4bet,n.delta4,
                n.old_call,n.new_call,n.old_fold,n.new_fold,n.delta_fold,
                n.bluff_share,n.new_bluff_share)],n.reachable,'HOLD_NO_EV_VALIDATION'])
    with (output_dir/'G2A_VS3_BLOCKER_TOP_HANDS_v0_6.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['Opener','Threebettor','Hand','RFI_open_probability','HeroClassWeightPost3betPct',
                    'FourbetPctWhenReached','CallPctWhenReached','FoldPctWhenReached'])
        for n in nodes:
            pair=(n.opener,n.threebettor)
            _,_,contrib=adjusted_action_percentages(*pair)
            den=sum(contrib.values())
            for hand,mass in sorted(contrib.items(),key=lambda x:(-x[1],x[0])):
                if mass<=0:continue
                row=HERO_VS_3BET[pair][hand]
                w.writerow([*pair,hand,round(row.open_probability,6),round(100*mass/den,6),
                           round(100*row.fourbet,6),round(100*row.call,6),round(100*row.fold,6)])
    benchmark_path=output_dir/'G2_VS3_Benchmark_Crosscheck.csv'
    if benchmark_path.exists():
        with benchmark_path.open(newline='',encoding='utf-8') as rf, (output_dir/'G2A_MAJOR_REVIEW_8_NODES_v0_6.csv').open('w',newline='',encoding='utf-8') as wf:
            rows=list(csv.DictReader(rf))
            w=csv.writer(wf)
            w.writerow(['Opener','Threebettor','OriginalBenchmarkFlag','PublishedReference4betPct',
                        'PreCardRemoval4betPct','PostCardRemoval4betPct','NewGapPP',
                        'ReferenceSameRakeTree','Verdict'])
            for row in rows:
                if row['Flag']!='MAJOR_REVIEW':continue
                n=audit_pair(row['Opener'],row['Threebettor'])
                ref=float(row['Ref4bet_pct'])
                w.writerow([n.opener,n.threebettor,row['Flag'],round(ref,6),
                            round(n.old_4bet,6),round(n.new_4bet,6),round(n.new_4bet-ref,6),
                            row['SameRakeAndTree'],'HOLD_INCOMPARABLE_ASSUMPTIONS'])
    return nodes

if __name__=='__main__':
    output=Path(__file__).resolve().parent
    nodes=export_reports(output)
    for n in nodes:
        print(f'{n.opener}-{n.threebettor} 4bet {n.old_4bet:.3f}% -> {n.new_4bet:.3f}%'
              f' (delta {n.delta4:+.3f}pp); fold {n.old_fold:.3f}% -> {n.new_fold:.3f}%')
