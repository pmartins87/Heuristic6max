"""Source-only SRP river four-flush integration (DRAFT, not a bot runner)."""
from __future__ import annotations

from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'iso_defense_v1'/'iso_defense_integrated_draft.oppl'
POLICY=HERE/'river_policy.oppl'
COMBINED=HERE/'river_fourflush_integrated_draft.oppl'

def render()->str:
    old=PARENT.read_text(encoding='utf-8')
    raw=POLICY.read_text(encoding='utf-8')
    parts=re.split(r'^//@STREET river\s*$',raw,flags=re.M)
    if len(parts)!=2:raise ValueError('expected one native river policy section')
    helper,river=(x.strip() for x in parts)
    if old.count('##f$flop##')!=1 or old.count('##f$river##')!=1:
        raise ValueError('parent callback mismatch')
    if '##f$H6RiverFourFlushNoFlush##' in old:
        raise ValueError('already integrated')
    if any(h in helper or h in river for h in ('##f$flop##','##f$turn##','##f$river##','##f$preflop##')):
        raise ValueError('new callback forbidden')
    actions=[s for s in river.splitlines() if s.startswith('WHEN ')]
    if len(actions)!=4 or any('WHEN Others ' in s for s in actions):
        raise ValueError('four tightly guarded decisions required; no global fallback')
    out=old.replace('##f$flop##',helper+'\n##f$flop##',1)
    out=out.replace('##f$river##','##f$river##\n'+river,1)
    for section in ('preflop','flop','turn','river'):
        if out.count(f'##f${section}##')!=1:
            raise ValueError('duplicate or missing callback '+section)
    old_actions=[s for s in old.splitlines() if s.startswith('WHEN ')]
    new_actions=[s for s in out.splitlines() if s.startswith('WHEN ')]
    i=0
    for action in old_actions:
        while i<len(new_actions) and new_actions[i]!=action:i+=1
        if i==len(new_actions):raise ValueError('ancestral OpenPPL action removed or reordered')
        i+=1
    if len(new_actions)!=len(old_actions)+10:
        # 4 actions + 2 origin helper cases + 2 fallback + 1 exposure + 1 fallback
        raise ValueError('unexpected rule cardinality')
    return out

def build()->int:
    new=render()
    COMBINED.write_text(new,encoding='utf-8',newline='\n')
    return len(new.encode('utf-8'))

if __name__=='__main__':
    print('SRP-RIVER-4FLUSH native integrated bytes:',build())
