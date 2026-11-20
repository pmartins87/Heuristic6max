"""Offline-only assembly of OpenPPL authored history overlay + frozen G3 baseline.
The actual runtime policy is the generated OpenPPL, never a Python fork.
"""
from pathlib import Path
import csv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / 'srp_hu_mvp' / 'srp_hu_postflop_draft.oppl'
PREFLOP = ROOT / 'vs_3bet_mvp' / 'preflop_rfi_vsopen_vs3_draft.oppl'
OVERLAY = HERE / 'history_overlay.oppl'
OUT = HERE / 'srp_hu_history_v1.oppl'
COMBINED = HERE / 'preflop_srp_history_v1.oppl'
MATRIX = HERE / 'HISTORY_FLOP_TURN_9_PATHS.csv'


def assemble():
    base=BASE.read_text(encoding='utf-8')
    pre=PREFLOP.read_text(encoding='utf-8').rstrip()
    overlay=OVERLAY.read_text(encoding='utf-8')
    if any(base.count(x)!=1 for x in ('##f$flop##','##f$turn##','##f$river##')):
        raise ValueError('old G3 source has missing or repeated street')
    if overlay.count('##f$turn##')!=1 or overlay.count('##f$river##')!=1:
        raise ValueError('overlay must have turn and river exactly once')
    old_helpers,rest=base.split('##f$flop##')
    flop,rest=rest.split('##f$turn##')
    old_turn,old_river=rest.split('##f$river##')
    new_helpers,rest=overlay.split('##f$turn##')
    new_turn,new_river=rest.split('##f$river##')
    def guard_old(old: str, domain: str) -> str:
        return '\n'.join(line.replace('WHEN (','WHEN ('+domain+' AND ',1)
                         if line.startswith('WHEN (') else line
                         for line in old.strip().splitlines())
    full = ('\n'.join([old_helpers.rstrip(), new_helpers.strip(),
                       '##f$flop##',flop.strip(),
                       '##f$turn##',new_turn.strip(),guard_old(old_turn,'f$HLTurnDomain'),
                       '##f$river##',new_river.strip(),guard_old(old_river,'f$HLRiverDomain')])+'\n')
    combined=pre+'\n\n'+full
    for header in ('##f$preflop##','##f$flop##','##f$turn##','##f$river##'):
        if combined.count(header)!=1:raise ValueError('Repeated or missing '+header)
    if not full.startswith(old_helpers.rstrip()):raise ValueError('Base helper drift')
    OUT.write_text(full,encoding='utf-8',newline='\n')
    COMBINED.write_text(combined,encoding='utf-8',newline='\n')
    with MATRIX.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['flop_line','turn_line','oppl_helper','status','meaning'])
        names={'B':'BET_CALLED','C':'CHECKED_THROUGH','X':'CALLED_BET'}
        for a in 'BCX':
            for b in 'BCX':
                writer.writerow([names[a],names[b],'f$HLPath'+a+b,
                                 'DRAFT_STATIC_ONLY','History uses OH street flags; not validated in target runtime'])
    return sum(x.strip().startswith('WHEN') for x in full.splitlines()),len(full.splitlines())

if __name__=='__main__':print('history action source',assemble())
