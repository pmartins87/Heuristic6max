"""Deterministic BLISO-2 OpenPPL merger. Source is native OpenPPL, not Python strategy."""
from __future__ import annotations
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'iso_raise_v1'/'iso_integrated_draft.oppl'
HAND=HERE/'blind_iso_handlist.oppl'
PREFLOP=HERE/'blind_iso_preflop_capture.oppl'
TOPOLOGY=HERE/'blind_iso_topology.oppl'
POLICY=HERE/'blind_iso_policy.oppl'
COMBINED=HERE/'blind_iso_integrated_draft.oppl'
STREETS=('flop','turn','river')


def chunks(raw:str)->tuple[str,dict[str,str]]:
    parts=re.split(r'^//@STREET (flop|turn|river)\s*$',raw,flags=re.M)
    if len(parts)!=7 or tuple(parts[i] for i in (1,3,5))!=STREETS:
        raise ValueError('invalid OpenPPL street policy')
    return parts[0],{parts[i]:parts[i+1].strip() for i in (1,3,5)}


def render()->str:
    old=PARENT.read_text(encoding='utf-8')
    hand=HAND.read_text(encoding='utf-8').rstrip()
    pf=PREFLOP.read_text(encoding='utf-8').rstrip()
    topo=TOPOLOGY.read_text(encoding='utf-8').rstrip()
    helpers,streets=chunks(POLICY.read_text(encoding='utf-8'))
    if 'f$H6BISOValid' in old or '##listH6BISOCORE##' in old:
        raise ValueError('BLISO code already integrated into parent')
    for street in ('preflop',*STREETS):
        if old.count(f'##f${street}##')!=1:
            raise ValueError('parent callback missing/duplicated')
    for text in (hand,pf,topo,helpers,*streets.values()):
        if 'WHEN Others Fold FORCE' in text or 'WHEN Others Check FORCE' in text:
            raise ValueError('unscoped fallback')
    now=old.replace('##f$preflop##',hand+'\n##f$preflop##\n'+pf,1)
    now=now.replace('##f$flop##',topo+'\n'+helpers.rstrip()+'\n##f$flop##',1)
    for street in STREETS:
        now=now.replace('##f$'+street+'##','##f$'+street+'##\n'+streets[street],1)
    for street in ('preflop',*STREETS):
        if now.count(f'##f${street}##')!=1:
            raise ValueError('duplicate callback')
    before=[line for line in old.splitlines() if line.startswith('WHEN ')]
    after=[line for line in now.splitlines() if line.startswith('WHEN ')]
    i=0
    for line in before:
        while i<len(after) and after[i]!=line:
            i+=1
        if i==len(after):
            raise ValueError('ancestral action/helper changed or reordered')
        i+=1
    return now


def build()->tuple[int,int]:
    c=render()
    COMBINED.write_text(c,encoding='utf-8',newline='\n')
    _,streets=chunks(POLICY.read_text(encoding='utf-8'))
    actions=sum(len(re.findall(r'^WHEN \(',s,flags=re.M)) for s in streets.values())
    return actions,len(c.encode('utf-8'))


if __name__=='__main__':
    print('BLISO-2 postflop action count and integrated byte length:',build())
