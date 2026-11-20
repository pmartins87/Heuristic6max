"""OFFLINE authoring tool, not strategic runtime; baseline read-only.

Reproducibly emits a *proposed* OPPL proof for the 168 pure RFI LJ classes.
The mixed class remains unsupported on purpose, to avoid lossy translation.
Do not promote the OPPL file as a loadable bot based solely on this generator.
"""
from __future__ import annotations
import csv
from pathlib import Path
import sys
from port1_interpreter import GUARD, LIST_FOLD, LIST_RAISE, ALL_HANDS

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'gto6_heuristic_v0_6_1'))
from rfi_reference import RANGES  # noqa: E402
from scenario_contract import Position  # noqa: E402
HERE=Path(__file__).resolve().parent


def generate():
    rows=RANGES[Position.LJ]
    raises=[];folds=[];blocked=[]
    for h in sorted(ALL_HANDS):
        p=rows[h]['RAISE']
        if p==1.:raises.append(h)
        elif p==0.:folds.append(h)
        else:blocked.append((h,p))
    if blocked!=[('KJo',.4)] or len(raises)+len(folds)!=168:
        raise ValueError(f'Baseline changed; re-author and review, not silent conversion: {blocked}')
    def group(xs):
        return [' '.join(xs[i:i+12]) for i in range(0,len(xs),12)]
    template=[
        '// PORT-1 STATIC PROOF ONLY. NOT A LOADABLE OH STRATEGY.',
        '// A single LJ first-in RFI subdomain at six-handed / 100BB.',
        '// KJo is deliberately UNMAPPED (RFI=40%) until mixed-action parity.',
        '// No-match in real OpenHoldem may trigger fallback. NEVER load live.',
        f'##{LIST_RAISE}##',*group(raises),f'##{LIST_FOLD}##',*group(folds),
        '##f$preflop##',
        'WHEN ('+' AND '.join((*GUARD,LIST_RAISE))+') RaiseTo 2.5 FORCE',
        'WHEN ('+' AND '.join((*GUARD,LIST_FOLD))+') Fold FORCE',''
    ]
    (HERE/'lj_rfi_pure_port1.oppl').write_text('\n'.join(template),encoding='utf-8',newline='\n')
    with (HERE/'PORT1_LJ_169_MAPPING.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['Hand','RFI_raise_pct','RFI_fold_pct','Port1_decision','Portability'])
        for h in sorted(ALL_HANDS):
            p=rows[h]['RAISE']
            w.writerow([h,f'{p*100:.8f}',f'{(1-p)*100:.8f}',
                        'RAISETO_2_5' if p==1 else 'FOLD' if p==0 else '',
                        'STATIC_COVERED' if p in (0,1) else 'BLOCKED_MIX'])
    return len(raises),len(folds)

if __name__=='__main__':print('LJ pure class counts',generate())
