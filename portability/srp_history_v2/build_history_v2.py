"""Offline builder. OpenPPL authored sources, never an alternative Python poker policy.
Combines frozen v1 and new OpenPPL source fragments, adding 6x6 path helpers.
"""
from pathlib import Path
import csv

HERE=Path(__file__).resolve().parent
PORT=HERE.parent
V1=PORT/'srp_history_v1'/'srp_hu_history_v1.oppl'
PREFLOP=PORT/'vs_3bet_mvp'/'preflop_rfi_vsopen_vs3_draft.oppl'
OVERLAY=HERE/'advanced_history_overlay.oppl'
SOURCE=HERE/'srp_hu_history_v2.oppl'
COMBINED=HERE/'preflop_srp_history_v2.oppl'
MATRIX=HERE/'HISTORY_FLOP_TURN_36_PATHS.csv'
CATS={
 'B':('f$HLFlopBetCall','f$HLTurnBetCall','BET_CALLED'),
 'C':('f$HLFlopCheckedThrough','f$HLTurnCheckedThrough','CHECKED_THROUGH'),
 'X':('f$HLFlopCall','f$HLTurnCall','CALLED_BET'),
 'R':('f$HLFlopRaiseCall','f$HLTurnRaiseCall','RAISE_OVER_VILLAIN_BET_CALLED'),
 'H':('f$HLFlopCheckRaiseCall','f$HLTurnCheckRaiseCall','CHECK_RAISE_CALLED'),
 'M':('f$HLFlopBetRaisedCall','f$HLTurnBetRaisedCall','BET_RAISED_CALL'),
}


def assemble():
    base=V1.read_text(encoding='utf-8')
    prefix=PREFLOP.read_text(encoding='utf-8').rstrip()
    overlay=OVERLAY.read_text(encoding='utf-8')
    for name in ('##f$flop##','##f$turn##','##f$river##'):
        if base.count(name)!=1:raise ValueError('Old street source changed '+name)
    if overlay.count('##f$turn##')!=1 or overlay.count('##f$river##')!=1:
        raise ValueError('Overlay sections changed')
    oldhelp,rest=base.split('##f$flop##')
    flop,rest=rest.split('##f$turn##')
    oldturn,oldriver=rest.split('##f$river##')
    newhelp,rest=overlay.split('##f$turn##')
    newturn,newriver=rest.split('##f$river##')
    # Combinatorial helper generation is syntax-only, defined by the six
    # *already authored* native OpenPPL predicates. It has no action policy.
    paths=[]
    for fa,(flopfunc,_,_) in CATS.items():
        for tb,(_,turnfunc,_) in CATS.items():
            paths.extend([f'##f$HLPath2{fa}{tb}##',
                          f'WHEN ({flopfunc} AND {turnfunc}) RETURN TRUE FORCE',
                          'WHEN Others RETURN FALSE FORCE'])
    oldturn=oldturn.replace('f$HLTurnDomain', 'f$HLTurnDomainV2')
    oldriver=oldriver.replace('f$HLRiverDomain', 'f$HLRiverDomainV2')
    full='\n'.join([oldhelp.rstrip(),newhelp.strip(), '\n'.join(paths),
                    '##f$flop##',flop.strip(),
                    '##f$turn##',newturn.strip(),oldturn.strip(),
                    '##f$river##',newriver.strip(),oldriver.strip()])+'\n'
    combined=prefix+'\n\n'+full
    for name in ('##f$preflop##','##f$flop##','##f$turn##','##f$river##'):
        if combined.count(name)!=1:raise ValueError('Multiple street sections '+name)
    SOURCE.write_text(full,encoding='utf-8',newline='\n')
    COMBINED.write_text(combined,encoding='utf-8',newline='\n')
    with MATRIX.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        w.writerow(['FlopLine','TurnLine','PathHelper','Status','Notes'])
        for fa,(_,_,fs) in CATS.items():
            for tb,(_,_,ts) in CATS.items():
                w.writerow([fs,ts,f'f$HLPath2{fa}{tb}','DRAFT_STATIC_ONLY',
                            'Observed flags only; no OpenHoldem runtime validation'])
    return (len(CATS)**2,sum(1 for x in full.splitlines() if x.startswith('WHEN ')))

if __name__=='__main__':print('history V2 paths and rules',assemble())
