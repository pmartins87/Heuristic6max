"""Auditoria de composição VS_3BET v0.5.

Não produz novas decisões: isola as contribuições de 4bet por classe,
com checks de probabilidade, alcançabilidade e proveniência. A comparação
externa (árvore/rake distintos) é sinal de triagem, não alvo de otimização.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from scenario_contract import combo_count
from vs_3bet_reference import RANGES, SPECS, aggregate_conditional

ROOT=Path(__file__).resolve().parent
BLUFF_BUCKET={'4BET_BLUFF_FOLD_MIX'}
VALUE_BUCKET={'4BET_VALUE_PURE','4BET_CALL_MIX'}

@dataclass(frozen=True)
class Mass:
    opener:str
    threebettor:str
    open_mass:float
    fourbet_mass:float
    value_mass:float
    bluff_mass:float
    call_mass:float
    fold_mass:float
    pure_fold_mass:float
    reached_classes:int

    @property
    def fourbet_pct(self): return 100*self.fourbet_mass/self.open_mass
    @property
    def call_pct(self): return 100*self.call_mass/self.open_mass
    @property
    def fold_pct(self): return 100*self.fold_mass/self.open_mass
    @property
    def bluff_share_pct(self): return 100*self.bluff_mass/self.fourbet_mass if self.fourbet_mass else 0


def audit_node(opener:str,threebettor:str)->Mass:
    rows=RANGES[(opener,threebettor)]
    mass=lambda hand,row: combo_count(hand)*row.open_probability
    den=sum(mass(h,r) for h,r in rows.items())
    if den<=0: raise ValueError('sem RFI alcançável')
    four=sum(mass(h,r)*r.fourbet for h,r in rows.items())
    val=sum(mass(h,r)*r.fourbet for h,r in rows.items() if r.bucket in VALUE_BUCKET)
    bluff=sum(mass(h,r)*r.fourbet for h,r in rows.items() if r.bucket in BLUFF_BUCKET)
    call=sum(mass(h,r)*r.call for h,r in rows.items())
    fold=sum(mass(h,r)*r.fold for h,r in rows.items())
    purefold=sum(mass(h,r)*r.fold for h,r in rows.items() if r.bucket=='FOLD_PURE')
    assert abs(den-(four+call+fold))<1e-8, (opener,threebettor,'mass discrepancy')
    assert abs(four-(val+bluff))<1e-8, (opener,threebettor,'4bet unexplained')
    assert abs(100*four/den-aggregate_conditional(opener,threebettor,'4BET'))<1e-8
    return Mass(opener,threebettor,den,four,val,bluff,call,fold,purefold,
                sum(r.open_probability>0 for r in rows.values()))


def top_contributions(opener:str,threebettor:str,action:str='4BET'):
    if action not in {'4BET','CALL','FOLD'}: raise ValueError('ação inválida')
    field={'4BET':'fourbet','CALL':'call','FOLD':'fold'}[action]
    rows=RANGES[(opener,threebettor)]
    den=sum(combo_count(h)*r.open_probability for h,r in rows.items())
    output=[]
    for hand,r in rows.items():
        weight=combo_count(hand)*r.open_probability*getattr(r,field)
        if weight>0:
            output.append((hand,r.bucket,round(100*weight/den,6),round(100*getattr(r,field),4)))
    return sorted(output,key=lambda v:(-v[2],v[0]))


def export_audit(root:Path=ROOT):
    root=Path(root)
    with (root/'G2_VS3_Hand_Contributions_v0_5.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.writer(f)
        wr.writerow(['Opener','Threebettor','Hand','Bucket','OpenPct','Conditional4betPct',
            'ConditionalCallPct','ConditionalFoldPct','Contribution4bet_pp','ContributionCall_pp',
            'ContributionFold_pp','Source','Status'])
        for s in SPECS:
            pair=(s.opener,s.threebettor)
            rows=RANGES[pair]
            den=sum(combo_count(h)*r.open_probability for h,r in rows.items())
            for h,r in rows.items():
                w=combo_count(h)*r.open_probability/den
                wr.writerow([*pair,h,r.bucket,round(100*r.open_probability,6),
                    round(100*r.fourbet,6),round(100*r.call,6),round(100*r.fold,6),
                    round(100*w*r.fourbet,6),round(100*w*r.call,6),
                    round(100*w*r.fold,6),'V0.4_EXPLICIT_HEURISTIC','HOLD_UNCALIBRATED'])
    with (root/'G2_VS3_Composition_Summary_v0_5.csv').open('w',newline='',encoding='utf-8') as f:
        wr=csv.writer(f)
        wr.writerow(['Opener','Threebettor','RFI_weighted_combo_mass','ReachableClasses',
            'Conditional4betPct','ConditionalCallPct','ConditionalFoldPct',
            '4betValueSharePct','4betBluffSharePct','PureFoldShareOfRFI_Pct',
            'Top4betContributors','Status'])
        for s in SPECS:
            a=audit_node(s.opener,s.threebettor)
            wr.writerow([s.opener,s.threebettor,round(a.open_mass,4),a.reached_classes,
                round(a.fourbet_pct,4),round(a.call_pct,4),round(a.fold_pct,4),
                round(100*a.value_mass/a.fourbet_mass,4),round(a.bluff_share_pct,4),
                round(100*a.pure_fold_mass/a.open_mass,4),
                ' '.join(f'{h}:{pp:.2f}pp' for h,_,pp,_ in top_contributions(s.opener,s.threebettor)[:8]),
                'HOLD_STRATEGIC_REVIEW'])

if __name__=='__main__':
    export_audit()
    for sp in SPECS:
        a=audit_node(sp.opener,sp.threebettor)
        print(f'{sp.opener} vs {sp.threebettor}: 4bet={a.fourbet_pct:.1f}%, bluff_share={a.bluff_share_pct:.1f}%')
