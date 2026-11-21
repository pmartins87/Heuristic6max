"""Single OpenPPL action source; add provenance to source-preserving v3+3bet.

Only offline generation, no poker decisions in Python.
"""
from __future__ import annotations
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'p3bet_hu_v1'/'preflop_srp_and_3bet_hu_draft.oppl'
POLICY=HERE/'threeway_srp_postflop.oppl'
INTENT=HERE/'preflop_coldcall_intent.oppl'
COMBINED=HERE/'preflop_srp_3bet_3way_draft.oppl'
HEADER=re.compile(r'^##f\$\w+##$')
CALL=re.compile(r'^WHEN (?P<condition>\([^()]+\)) Call FORCE$')


def capture_calls(old:str)->list[str]:
    pre=False;result=[]
    for ln in old.splitlines():
        if ln=='##f$preflop##':pre=True;continue
        if pre and HEADER.fullmatch(ln):break
        if not pre:continue
        m=CALL.fullmatch(ln)
        if not m:continue
        c=m['condition']
        if (' AND Raises = 1 AND Calls = 0 AND ' in c and 'FirstRaiserPosition' in c
            and 'BotRaisedBeforeFlop' not in c and 'RaisesSinceLastPlay' not in c):
            result.append('WHEN '+c+' Set user_H6_VSOpenCallIntent')
    if len(result)!=33 or len(set(result))!=33:
        raise ValueError(f'Unreviewed VS_OPEN Call source: {len(result)}')
    return result


def generate():
    previous=PREV.read_text(encoding='utf-8')
    if 'user_H6_VSOpenCallIntent' in previous:raise ValueError('Source already instrumented')
    capture=capture_calls(previous)
    INTENT.write_text('// H6 3way SRP caller: intent recorded from actual VS_OPEN Call branches.\n'
                      '// Crosscheck native BotCalledBeforeFlop AND BotRaisedBeforeFlop before use.\n'
                      +'\n'.join(capture)+'\n',encoding='utf-8',newline='\n')
    policy=POLICY.read_text(encoding='utf-8')
    chunks={'HELPERS':[],'flop':[],'turn':[],'river':[]};section='HELPERS'
    for l in policy.splitlines():
        if l.startswith('//@STREET '):section=l.split(' ',1)[1]
        else:chunks[section].append(l)
    if any(not chunks[k] for k in chunks):raise ValueError('Source street missing')
    merged=previous.replace('##f$preflop##','##f$preflop##\n'+'\n'.join(capture),1)
    merged=merged.replace('##f$flop##','\n'.join(chunks['HELPERS']).rstrip()+'\n\n##f$flop##\n'+'\n'.join(chunks['flop']).rstrip(),1)
    for k in ('turn','river'):
        merged=merged.replace('##f$'+k+'##','##f$'+k+'##\n'+'\n'.join(chunks[k]).rstrip(),1)
    if any(merged.count('##f$'+s+'##')!=1 for s in ('preflop','flop','turn','river')):
        raise ValueError('Duplicate sections')
    if merged.count('Set user_H6_VSOpenCallIntent')!=33:raise ValueError('Caller provenance count drift')
    COMBINED.write_text(merged,encoding='utf-8',newline='\n')
    return len(capture),sum(sum(line.startswith('WHEN ') for line in chunks[s]) for s in ('flop','turn','river'))

if __name__=='__main__':print('3way SRP',generate())
