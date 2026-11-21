"""Deterministic ISODEF-1 source-only merger; not a separate poker policy."""
from __future__ import annotations
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'blind_iso_v2'/'blind_iso_integrated_draft.oppl'
HAND=HERE/'defense_handlists.oppl'
PREFLOP=HERE/'defense_preflop_capture.oppl'
TOPOLOGY=HERE/'defense_topology.oppl'
POLICY=HERE/'defense_policy.oppl'
COMBINED=HERE/'iso_defense_integrated_draft.oppl'
STREETS=('flop','turn','river')


def chunks(raw:str)->tuple[str,dict[str,str]]:
    parts=re.split(r'^//@STREET (flop|turn|river)\s*$',raw,flags=re.M)
    if len(parts)!=7 or tuple(parts[i] for i in (1,3,5))!=STREETS:
        raise ValueError('incorrect source street sections')
    return parts[0],{parts[i]:parts[i+1].strip() for i in (1,3,5)}


def render()->str:
    old=PARENT.read_text(encoding='utf-8')
    hand=HAND.read_text(encoding='utf-8').rstrip()
    pf=PREFLOP.read_text(encoding='utf-8').rstrip()
    topo=TOPOLOGY.read_text(encoding='utf-8').rstrip()
    helpers,streets=chunks(POLICY.read_text(encoding='utf-8'))
    if '##f$H6DEFValid##' in old or '##listH6DEF3BET##' in old:
        raise ValueError('ISODEF-1 already integrated')
    if any(old.count(f'##f${s}##')!=1 for s in ('preflop',*STREETS)):
        raise ValueError('parent callback count is not exactly one')
    for text in (pf,topo,helpers,*streets.values()):
        if 'WHEN Others Fold FORCE' in text or 'WHEN Others Check FORCE' in text:
            raise ValueError('new unguarded fallback')
    now=old.replace('##f$preflop##',hand+'\n##f$preflop##\n'+pf,1)
    now=now.replace('##f$flop##',topo+'\n'+helpers.rstrip()+'\n##f$flop##',1)
    for street in STREETS:
        now=now.replace('##f$'+street+'##','##f$'+street+'##\n'+streets[street],1)
    for s in ('preflop',*STREETS):
        if now.count('##f$'+s+'##')!=1:
            raise ValueError('duplicate action callback')
    before=[x for x in old.splitlines() if x.startswith('WHEN ')]
    after=[x for x in now.splitlines() if x.startswith('WHEN ')]
    pos=0
    for line in before:
        while pos<len(after) and after[pos]!=line:
            pos+=1
        if pos==len(after):raise ValueError('prior WHEN removed or reordered')
        pos+=1
    return now


def build()->tuple[int,int]:
    text=render()
    COMBINED.write_text(text,encoding='utf-8',newline='\n')
    _,streets=chunks(POLICY.read_text(encoding='utf-8'))
    return sum(len(re.findall(r'^WHEN \(',s,flags=re.M)) for s in streets.values()),len(text.encode('utf-8'))


if __name__=='__main__':
    print('ISODEF-1 postflop actions + integrated bytes:',build())
