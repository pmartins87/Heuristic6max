"""OFFLINE generation from immutable v0.6.1 RFI into OPPL source (not runtime)."""
from __future__ import annotations
from pathlib import Path
import csv
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from portability.port2 import port2_interpreter as p
sys.path.insert(0,str(ROOT/'gto6_heuristic_v0_6_1'))
from rfi_reference import RANGES  # noqa: E402
from scenario_contract import Position  # noqa: E402
HERE=Path(__file__).resolve().parent


def generate()->tuple[int,int,int]:
    rows=RANGES[Position.LJ]
    raises=[];folds=[];mixed=[]
    for hand in sorted(p.ALL_HANDS):
        weight=rows[hand]['RAISE']
        if weight==1:raises.append(hand)
        elif weight==0:folds.append(hand)
        elif weight==.4 and hand=='KJo':mixed.append(hand)
        else:raise ValueError(f'Unreviewed mixed class: {hand}:{weight}')
    if (len(raises),len(folds),mixed)!=(43,125,['KJo']):
        raise ValueError('RFI source changed: must review before generating')
    def wrap(xs):return [' '.join(xs[i:i+12]) for i in range(0,len(xs),12)]
    source=[
        '// PORT-2 STATIC PROOF ONLY. NOT A LOADABLE / VALIDATED OPENHOLDEM BOT.',
        '// Source for 169 LJ first-in 100BB classes, incl. KJo 40%/60%.',
        '// randomhand is sampled once per hand in documented OpenHoldem;',
        '// symbol behavior and no-match must still be verified on target executable.',
        '// No WHEN Others or unconditional fallback: out-of-domain is UNSAFE in OH.',
        *[line for name,xs in ((p.RAISE,raises),(p.FOLD,folds),(p.MIX,mixed))
          for line in (f'##{name}##',*wrap(xs))],
        '##f$preflop##',
        'WHEN ('+' AND '.join((*p.GUARD,p.RAISE))+') RaiseTo 2.5 FORCE',
        'WHEN ('+' AND '.join((*p.GUARD,p.FOLD))+') Fold FORCE',
        'WHEN ('+' AND '.join((*p.GUARD,p.MIX,'randomhand < 0.40'))+') RaiseTo 2.5 FORCE',
        'WHEN ('+' AND '.join((*p.GUARD,p.MIX,'randomhand >= 0.40'))+') Fold FORCE',''
    ]
    p.SOURCE.write_text('\n'.join(source),encoding='utf-8',newline='\n')
    with (HERE/'PORT2_LJ_169_MAPPING.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        w.writerow(['Hand','RFI_raise_pct','RFI_fold_pct','Port2_decision','Portability'])
        for hand in sorted(p.ALL_HANDS):
            r=rows[hand]['RAISE']
            code='RAISETO_2_5' if r==1 else 'FOLD' if r==0 else 'MIX_RANDOMHAND_LT_0_40'
            w.writerow([hand,f'{r*100:.8f}',f'{(1-r)*100:.8f}',code,
                        'STATIC_COVERED' if r in (0,1) else 'STATIC_MIX_NEEDS_OH_RUNTIME'])
    return len(raises),len(folds),len(mixed)

if __name__=='__main__':print('PORT-2 classes',generate())
