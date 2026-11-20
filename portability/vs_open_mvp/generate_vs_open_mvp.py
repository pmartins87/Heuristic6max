"""Offline compiler: immutable VS_OPEN v0.6.1 -> native OpenPPL decision source.

This script is AUTHORING TOOLING, never code executed by OpenHoldem.
No strategic adjustments. The combined source uses the already published RFI
OpenPPL text verbatim, avoiding two implementations of the same policy.
"""
from __future__ import annotations
import csv
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'gto6_heuristic_v0_6_1'))
from vs_open_reference import RANGES, expected_open, expected_pot_bb, threebet_to_bb, SPECS
from scenario_contract import all_hand_classes

# 6-handed documented FirstRaiserPosition: UTG/LJ=5, HJ/MP3=4, CO=3,
# BTN=2, SB=1. InUTG etc. refer to CURRENT hero, not opener.
POSITION={
    'LJ':('InUTG',5,0),
    'HJ':('InMiddlePosition3',4,0),
    'CO':('InCutOff',3,0),
    'BTN':('InButton',2,0),
    'SB':('InSmallBlind',1,0.5),
    'BB':('InBigBlind',0,1.),
}
CATEGORIES=('3BET','CALL','FOLD','M3C','M3F','MCF')


def category(row):
    a,b,c=row.threebet,row.call,row.fold
    if (a,b,c)==(1,0,0):return ('3BET',None)
    if (a,b,c)==(0,1,0):return ('CALL',None)
    if (a,b,c)==(0,0,1):return ('FOLD',None)
    if 0<a<1 and b>0 and c==0 and abs(a+b-1)<1e-9:return ('M3C',int(round(100*a)))
    if 0<a<1 and c>0 and b==0 and abs(a+c-1)<1e-9:return ('M3F',int(round(100*a)))
    if 0<b<1 and c>0 and a==0 and abs(b+c-1)<1e-9:return ('MCF',int(round(100*b)))
    raise ValueError('Unsupported 3-way/uncalibrated mixture: '+str(row))


def listname(op,hero,tag,pct):
    return f'listVO{op}{hero}{tag}'+(f'{pct:02d}' if pct is not None else '')


def guard(op,hero):
    hero_symbol=POSITION[hero][0]
    opener_pos=POSITION[op][1]
    open_to=expected_open(op)
    invested=POSITION[hero][2]
    call=open_to-invested
    pot=expected_pot_bb(op)
    return ('IsPreflop','nplayersdealt = 6',hero_symbol,'Raises = 1','Calls = 0',
            f'FirstRaiserPosition = {opener_pos}',f'LastRaiserPosition = {opener_pos}',
            f'PotSize = {pot:g}',f'AmountToCall = {call:g}',
            'NOT StackUnknown','StackSize >= 95','StackSize <= 105',
            'MinOpponentStackSize >= 95','MaxOpponentStackSize <= 105')


def rule(op,hero,ln,tag,pct):
    pre='WHEN ('+' AND '.join((*guard(op,hero),ln))
    size=f'{threebet_to_bb(op,hero):g}'
    if pct is None:
        action={'3BET':f'RaiseTo {size}','CALL':'Call','FOLD':'Fold'}[tag]
        return [pre+f') {action} FORCE']
    first='RaiseTo '+size if tag in ('M3C','M3F') else 'Call'
    second='Call' if tag=='M3C' else 'Fold'
    return [pre+f' AND randomhand < {pct/100:.2f}) {first} FORCE',
            pre+f' AND randomhand >= {pct/100:.2f}) {second} FORCE']


def split_source(txt):
    if txt.count('##f$preflop##')!=1:raise ValueError('preflop section must occur once')
    head,tail=txt.split('##f$preflop##')
    return head.strip(),tail.strip()


def combine(rfi_text,vs_text):
    # One preflop entry point; handlists and decision lines are copied in order.
    rfi_lists,rfi_rules=split_source(rfi_text)
    vo_lists,vo_rules=split_source(vs_text)
    return ('// SOURCE MERGE ONLY: RFI first (Raises=0), VS_OPEN second (Raises=1).\n'
            '// NOT a complete OpenHoldem bot; no-match may trigger default.bot.\n'
            +rfi_lists+'\n'+vo_lists+'\n##f$preflop##\n'
            +rfi_rules+'\n'+vo_rules+'\n')


def generate():
    specs=[(x.opener,x.hero) for x in SPECS]
    if len(specs)!=15 or len(set(specs))!=15:raise ValueError('15 pairs required')
    lists=[];rules=[];mapping=[]
    for op,hero in specs:
        bins={}
        for h in sorted(all_hand_classes()):
            row=RANGES[(op,hero)][h]
            tag,pct=category(row)
            if pct is not None:
                p=(row.threebet if tag in ('M3C','M3F') else row.call)
                if abs(p-pct/100)>1e-12:
                    raise ValueError(f'Unrepresentable mixture: {op}/{hero}/{h}: {p}')
            bins.setdefault((tag,pct),[]).append(h)
            mapping.append((op,hero,h,*[f'{100*x:.8f}' for x in (row.threebet,row.call,row.fold)],
                            f'{threebet_to_bb(op,hero):.2f}',listname(op,hero,tag,pct),
                            row.bucket))
        for tag in CATEGORIES:
            for (cat,pct),members in sorted(bins.items(),key=lambda x:(x[0][0],x[0][1] or 0)):
                if cat!=tag:continue
                ln=listname(op,hero,cat,pct)
                lists.append((ln,members))
                rules.extend(rule(op,hero,ln,cat,pct))
        if sum(len(members) for (tag,pct),members in bins.items())!=169:
            raise ValueError('Partition failure')
    if len(mapping)!=2535:raise ValueError(f'Expected 2535, got {len(mapping)}')
    pre=['// VS_OPEN-MVP: 15 x 169, 100BB, first open only. DRAFT; not a complete bot.',
         '// Snapshot v0.6.1; no strategy changes. 3bet takes precedence over overlapping call seeds.',
         '// Documented FirstRaiserPosition numbers in 6-max: LJ=5 HJ=4 CO=3 BTN=2 SB=1.',
         '// randomhand is constant within a hand; action/sizing/fallback in target OH not verified.',
         '// No-match can delegate to OpenHoldem default.bot. DO NOT LOAD LIVE.']
    for ln,members in lists:
        pre.append(f'##{ln}##')
        pre.extend(' '.join(members[i:i+12]) for i in range(0,len(members),12))
    pre.extend(['##f$preflop##',*rules,''])
    vo='\n'.join(pre)
    (HERE/'vs_open_6max_mvp.oppl').write_text(vo,encoding='utf-8',newline='\n')
    rfi_path=ROOT/'portability/rfi_mvp/rfi_6max_mvp.oppl'
    rfi=rfi_path.read_text(encoding='utf-8')
    (HERE/'preflop_rfi_vsopen_draft.oppl').write_text(combine(rfi,vo),encoding='utf-8',newline='\n')
    with (HERE/'VS_OPEN_2535_MAPPING.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(('Opener','Hero','Hand','Threebet_pct','Call_pct','Fold_pct','RaiseTo_BB','Handlist','Bucket'));w.writerows(mapping)
    return len(mapping),len(lists),len(rules)

if __name__=='__main__':
    print('mapped, lists, rules:',generate())
