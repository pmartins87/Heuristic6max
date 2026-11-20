"""Generate v0.4 VS_3BET exports, crosschecks, and cumulative node inventory.

Does not regenerate/edit inherited v0.3 reference ranges or source code.
External ART/GTO numbers are comparison-only from published site overview;
model/rake/size assumptions can differ. No solver was run.
"""
import csv
from pathlib import Path
from vs_3bet_reference import (SPECS, RANGES, aggregate_conditional,
    fourbet_to_bb, expected_pot_bb, export_csv)
from vs_open_reference import SPECS as VSOPEN_SPECS

ROOT=Path(__file__).resolve().parent
ART={
 ('LJ','HJ'):(21.3,12.8,65.9),('LJ','CO'):(22.9,12.5,64.6),
 ('LJ','BTN'):(20.7,18.6,60.6),('LJ','SB'):(13.4,26.2,60.5),
 ('LJ','BB'):(9.0,30.6,60.4),('HJ','CO'):(20.9,12.2,66.9),
 ('HJ','BTN'):(19.8,17.7,62.5),('HJ','SB'):(14.5,24.0,61.5),
 ('HJ','BB'):(8.5,31.3,60.2),('CO','BTN'):(18.9,16.1,65.0),
 ('CO','SB'):(14.4,21.2,64.4),('CO','BB'):(8.2,30.8,60.9),
 ('BTN','SB'):(11.9,26.4,61.7),('BTN','BB'):(9.2,29.3,61.5),
 ('SB','BB'):(20.6,22.0,57.3)
}
SOURCE_URLS={
 'LJ':'https://artgto.com/learn/ranges/utg/',
 'HJ':'https://artgto.com/learn/ranges/mp/',
 'CO':'https://artgto.com/learn/ranges/co/',
 'BTN':'https://artgto.com/learn/ranges/bu/',
 'SB':'https://artgto.com/learn/ranges/sb/',
}

def main():
    export_csv(ROOT/'VS_3BET_100BB_15x169_DRAFT.csv')
    with (ROOT/'G2_VS3_Benchmark_Crosscheck.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh)
        w.writerow(['Opener','Threebettor','Our4bet_pct_cond_RFI','OurCall_pct_cond_RFI',
            'OurFold_pct_cond_RFI','Ref4bet_pct','RefCall_pct','RefFold_pct',
            'Delta4bet_pp','DeltaCall_pp','DeltaFold_pp',
            'MaxAbsDiff_pp','Flag','RefURL','SameRakeAndTree','Status'])
        for sp in SPECS:
            pair=(sp.opener,sp.threebettor)
            values=[aggregate_conditional(*pair,a) for a in ('4BET','CALL','FOLD')]
            target=ART[pair]
            delta=[v-t for v,t in zip(values,target)]
            biggest=max(map(abs,delta))
            flag='MAJOR_REVIEW' if biggest>8 else 'REVIEW' if biggest>4 else 'CROSSCHECK_ONLY'
            w.writerow([*pair,*[f'{x:.4f}' for x in (*values,*target,*delta)],
                        f'{biggest:.4f}',flag,SOURCE_URLS[pair[0]],'NO','DRAFT'])
    with (ROOT/'G2_VS3_Audit_Summary.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh)
        w.writerow(['Opener','Threebettor','ReachableHandClasses','UnreachableHandClasses',
            'FourbetTo_bb','Pot_bb_at_decision','Conditional4bet_pct','ConditionalCall_pct',
            'ConditionalFold_pct','Status','Rationale'])
        for sp in SPECS:
            pair=(sp.opener,sp.threebettor)
            rows=RANGES[pair]
            reach=sum(r.open_probability>0 for r in rows.values())
            w.writerow([*pair,reach,169-reach,f'{fourbet_to_bb(*pair):.2f}',
                f'{expected_pot_bb(*pair):.2f}',
                *[f'{aggregate_conditional(*pair,act):.4f}' for act in ('4BET','CALL','FOLD')],
                'DRAFT',sp.rationale])
    with (ROOT/'G2_Nodes_Inventory.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh)
        w.writerow(['Node','Family','Opener','OtherActor','Entries','ReachableClasses',
                    'Status','AvailableActions','Applicability'])
        for pos in ('LJ','HJ','CO','BTN','SB'):
            w.writerow([f'PF.RFI.{pos}','RFI',pos,'',169,'','DRAFT','RAISE/LIMP/FOLD',
                        '6MAX, 95-105BB, unopened'])
        for sp in VSOPEN_SPECS:
            w.writerow([f'PF.VS_OPEN.{sp.opener}.{sp.hero}','VS_OPEN',sp.opener,sp.hero,
                        169,'','DRAFT','3BET/CALL/FOLD',
                        '6MAX, 95-105BB, 2.5BB RFI (SB 3BB), no caller/squeeze, verified synthetic observation'])
        for sp in SPECS:
            pair=sp.opener,sp.threebettor
            reachable=sum(r.open_probability>0 for r in RANGES[pair].values())
            w.writerow([f'PF.VS_3BET.{sp.opener}.{sp.threebettor}','VS_3BET',*pair,
                        169,reachable,'DRAFT','4BET/CALL/FOLD',
                        '6MAX, 95-105BB, exactly two raises, no callers/squeeze, 3bet sizing v0.3, verified synthetic observation'])

if __name__=='__main__':
    main()
