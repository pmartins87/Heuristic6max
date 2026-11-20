"""Exporta derivados de v0.3; também imprime hashes de preservação.
Não altera nenhum arquivo original das versões anteriores.
"""
from __future__ import annotations
import csv
from pathlib import Path
from vs_open_reference import (SPECS, RANGES, SHADOWS, aggregate, threebet_to_bb,
                                expected_open, export_csv)
from rfi_reference import aggregate as rfi_aggregate
from scenario_contract import Position

ROOT=Path(__file__).resolve().parent
SIMPLE_GTO_URL='https://simplegto.com/learn/preflop-statistics'
ART_GTO_URL='https://artgto.com/learn/ranges/'
BB_SIMPLE={'LJ':(5.8,20.7),'HJ':(7.5,21.5),'CO':(9.5,24.2),'BTN':(13.4,32.5),'SB':(16.2,41.8)}
# ESTATÍSTICAS PÚBLICAS de outro modelo; são comparação, NÃO alvo uniforme de calibragem.
ART_GTO_3BET={
    ('LJ','CO'):8.6,('HJ','CO'):10.0,
    ('LJ','BTN'):7.0,('HJ','BTN'):8.7,('CO','BTN'):11.3,
    ('LJ','SB'):6.9,('HJ','SB'):8.1,('CO','SB'):10.3,('BTN','SB'):14.5}


def main():
    export_csv(ROOT/'VS_OPEN_100BB_15x169_DRAFT.csv')
    with (ROOT/'G2_Nodes_Inventory.csv').open('w',encoding='utf-8',newline='') as fh:
        w=csv.writer(fh);w.writerow(['Node','Family','Opener','Hero','Entries','Status','AvailableActions','Applicability'])
        for pos in ('LJ','HJ','CO','BTN','SB'):
            w.writerow([f'PF.RFI.{pos}','RFI','',pos,169,'DRAFT','RAISE/LIMP/FOLD',
                        '6MAX; all stacks 95-105 BB; folded to Hero'])
        for sp in SPECS:
            w.writerow([f'PF.VS_OPEN.{sp.opener}.{sp.hero}','VS_OPEN',sp.opener,sp.hero,169,'DRAFT','3BET/CALL/FOLD',
                        '6MAX; all stacks 95-105 BB; single 2.5BB RFI (SB 3BB); no callers/limpers; FULL VERIFIED REPLAY'])
    with (ROOT/'G2_Benchmark_Crosscheck.csv').open('w',encoding='utf-8',newline='') as fh:
        w=csv.writer(fh)
        w.writerow(['Opener','Hero','Our3bet_pct','OurCall_pct','OurFold_pct','Ref3bet_pct','RefCall_pct',
                    'AbsDifference3bet_pp','AbsDifferenceCall_pp','ModelSource','ComparableRake','AuditFlag','Status'])
        for sp in SPECS:
            pair=sp.opener,sp.hero
            own3=aggregate(*pair,'3BET'); owncall=aggregate(*pair,'CALL'); ownfold=aggregate(*pair,'FOLD')
            if sp.hero=='BB':
                tgt3,tgtcall=BB_SIMPLE[sp.opener];source=SIMPLE_GTO_URL
            else:
                tgt3=ART_GTO_3BET.get(pair);tgtcall=None;source=ART_GTO_URL if tgt3 is not None else ''
            d3=abs(own3-tgt3) if tgt3 is not None else None
            dc=abs(owncall-tgtcall) if tgtcall is not None else None
            flag='REVIEW' if (d3 is not None and d3>3) or (dc is not None and dc>3) else 'CROSSCHECK_ONLY'
            w.writerow([*pair,f'{own3:.4f}',f'{owncall:.4f}',f'{ownfold:.4f}',
                        f'{tgt3:.4f}' if tgt3 is not None else '',
                        f'{tgtcall:.4f}' if tgtcall is not None else '',
                        f'{d3:.4f}' if d3 is not None else '',
                        f'{dc:.4f}' if dc is not None else '',source,'NO','%s'%flag,'DRAFT'])
    with (ROOT/'G2_Shadowed_Hand_Review.csv').open('w',encoding='utf-8',newline='') as fh:
        w=csv.writer(fh);w.writerow(['Opener','Hero','ShadowedHand','Description','Status'])
        for pair,hands in SHADOWS.items():
            for hand in hands:
                w.writerow([*pair,hand,'Mão do conjunto CALL já coberta por bloco 3BET; precedência 3BET aplicada','DOCUMENTED'])

if __name__=='__main__':
    main()
