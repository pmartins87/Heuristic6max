"""Offline compiler v0.6.1 VS_3BET -> OpenPPL and integrated preflop draft.

Only this generator imports the Python heuristic reference; the test interpreter
consumes exact OpenPPL text. Do not change historical strategy or normalize to a
solver benchmark. 4bet and call/fold mixtures preserved numerically.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
import csv
import sys
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from portability.vs_3bet_mvp import vs3_source_interpreter as p
sys.path.insert(0,str(ROOT/'gto6_heuristic_v0_6_1'))
from vs_3bet_reference import RANGES,SPECS,fourbet_to_bb,expected_pot_bb,threebet_to_bb
from scenario_contract import all_hand_classes


def bucket(row)->tuple[str,int|None]:
    a,b,c=row.fourbet,row.call,row.fold
    if row.open_probability==0:
        if (a,b,c)!=(0,0,0):raise ValueError('unreachable class has nonzero action')
        return ('NOT_REACHABLE',None)
    if (a,b,c)==(1,0,0):return ('P4',None)
    if (a,b,c)==(0,1,0):return ('PC',None)
    if (a,b,c)==(0,0,1):return ('PF',None)
    if 0<a<1 and b>0 and c==0 and abs(a+b-1)<1e-10:return ('M4C',int(round(a*100)))
    if 0<a<1 and c>0 and b==0 and abs(a+c-1)<1e-10:return ('M4F',int(round(a*100)))
    if 0<b<1 and a==0 and c>0 and abs(b+c-1)<1e-10:return ('MCF',int(round(b*100)))
    raise ValueError('unexpected strategic distribution: '+str(row))


def listname(op,bt,tag,pct):return f'listV3{op}{bt}{tag}'+(f'{pct:02d}' if pct is not None else '')


def rules(op,bt,ln,tag,pct):
    cond='WHEN ('+' AND '.join((*p.guard(op,bt),ln))
    to=f'{fourbet_to_bb(op,bt):g}'
    if pct is None:
        action={'P4':f'RaiseTo {to}','PC':'Call','PF':'Fold'}[tag]
        return [cond+f') {action} FORCE']
    first=f'RaiseTo {to}' if tag in ('M4C','M4F') else 'Call'
    other='Call' if tag=='M4C' else 'Fold'
    return [cond+f' AND randomhand < {pct/100:.2f}) {first} FORCE',
            cond+f' AND randomhand >= {pct/100:.2f}) {other} FORCE']


def generate():
    if len(SPECS)!=15 or {tuple((s.opener,s.threebettor)) for s in SPECS}!=set(p.PAIRS):
        raise ValueError('expect 15 position pairs')
    lists=[];out_rules=[];mapping=[]
    for sp in SPECS:
        op,bt=sp.opener,sp.threebettor
        bins=defaultdict(list)
        for hand in sorted(all_hand_classes()):
            row=RANGES[(op,bt)][hand]
            tag,pct=bucket(row)
            if pct is not None:
                prob=row.fourbet if tag in ('M4C','M4F') else row.call
                if abs(prob-pct/100)>1e-12:raise ValueError('unsupported percentage')
            if tag!='NOT_REACHABLE':bins[tag,pct].append(hand)
            mapping.append((op,bt,hand,f'{100*row.open_probability:.8f}',
                'YES' if row.open_probability>0 else 'NO',
                *(f'{100*v:.8f}' for v in (row.fourbet,row.call,row.fold)),
                f'{threebet_to_bb(op,bt):.2f}' if row.open_probability>0 else '',
                f'{fourbet_to_bb(op,bt):.2f}' if row.open_probability>0 else '',
                tag, listname(op,bt,tag,pct) if tag!='NOT_REACHABLE' else '', row.bucket))
        if len(bins)!=6 or sum(len(v) for v in bins.values())!=sum(r.open_probability>0 for r in RANGES[(op,bt)].values()):
            raise ValueError('invalid conditional hand partition '+str((op,bt)))
        for tag in p.TAGS:
            for (cat,pct),hands in sorted(bins.items(),key=lambda item:(item[0][0],item[0][1] or -1)):
                if cat!=tag:continue
                ln=listname(op,bt,tag,pct)
                lists.append((ln,hands))
                out_rules.extend(rules(op,bt,ln,tag,pct))
    if len(mapping)!=2535:raise ValueError('unexpected 15x169 size')
    text=[
        '// VS_3BET v0.6.1 DRAFT: 15 positional trees after our own RFI.',
        '// 1647 NOT_REACHABLE_FROM_RFI hands intentionally have NO action here.',
        '// OpenPPL Raises counts OPPONENT raises: 1 (not 2) after our RFI.',
        '// BotRaisedBeforeFlop and RaisesSinceLastPlay require real OH replay validation.',
        '// Current-round-start stack avoids excluding Hero after investing the RFI.',
        '// Do NOT load as standalone bot: no-match can invoke default.bot.',
    ]
    for name,hands in lists:
        text.append(f'##{name}##')
        text.extend(' '.join(hands[i:i+12]) for i in range(0,len(hands),12))
    text.extend(['##f$preflop##',*out_rules,''])
    standalone='\n'.join(text)
    p.SOURCE.write_text(standalone,encoding='utf-8',newline='\n')
    # Reuse prior published RFI + VS_OPEN source in full. This is a single f$preflop.
    from portability.vs_open_mvp.generate_vs_open_mvp import combine
    old=(ROOT/'portability/vs_open_mvp/preflop_rfi_vsopen_draft.oppl').read_text(encoding='utf-8')
    merged=combine(old,standalone)
    (HERE/'preflop_rfi_vsopen_vs3_draft.oppl').write_text(merged,encoding='utf-8',newline='\n')
    with (HERE/'VS3_2535_MAPPING.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        w.writerow(('Opener','Threebettor','Hand','RFI_open_pct','Reachable',
                    'Fourbet_pct','Call_pct','Fold_pct','ThreebetTo_BB','FourbetTo_BB',
                    'ActionBucket','Handlist','BaselineBucket'))
        w.writerows(mapping)
    return len(mapping),sum(x[4]=='YES' for x in mapping),len(lists),len(out_rules)

if __name__=='__main__':print('VS3 mapped/reachable/lists/rules:',generate())
