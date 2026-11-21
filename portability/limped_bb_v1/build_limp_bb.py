"""Offline OpenPPL composer for BB-check versus one limper, 6-handed.

No poker-policy computation in Python. Uses the existing integrated source as-is.
"""
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'multiway_v2'/'preflop_multiway_v2_draft.oppl'
POLICY=HERE/'limped_bb_postflop.oppl'
CHECK=HERE/'limp_bb_preflop_capture.oppl'
COMBINED=HERE/'preflop_multiway_limp_bb_draft.oppl'

BASE=('IsPreflop','nplayersdealt = 6','InBigBlind','Raises = 0','Calls = 1',
      'StillToAct = 0','AmountToCall = 0','NOT StackUnknown',
      'StackSize >= 95','StackSize <= 105',
      'MinOpponentStackSize >= 95','MaxOpponentStackSize <= 105')

def build():
    src=PREV.read_text(encoding='utf-8')
    post=POLICY.read_text(encoding='utf-8')
    if any(src.count(f'##f${s}##')!=1 for s in ('preflop','flop','turn','river')):
        raise ValueError('upstream expected one street each')
    if 'user_H6_LimpSBIntent' in src or 'f$H6LimpBBHU' in src:
        raise ValueError('limp layer already merged into upstream')
    intro=['// BB-option after exactly ONE voluntary limp; two pot amounts',
           '// identify SB-vs-BB 2BB pot vs other single-limper 2.5BB pot.',
           '// Set flags denote intent; postflop requires BotCheckedPreflop.',
           '']
    capture=[]
    for size,tag in ((2,'user_H6_LimpSBIntent'),(2.5,'user_H6_LimpOtherIntent')):
        condition='('+' AND '.join((*BASE,f'PotSize = {size}'))+')'
        capture.append(('WHEN '+condition+' Set '+tag,'WHEN '+condition+' Check FORCE'))
    # Capture both tagged choices at top: avoid reliance on preflop fallback.
    check_lines=intro+[x for pair in capture for x in pair]+['']
    CHECK.write_text('\n'.join(check_lines),encoding='utf-8',newline='\n')
    parts={'helpers':[],'flop':[],'turn':[],'river':[]};section='helpers'
    for line in post.splitlines():
        if line.startswith('//@STREET '):section=line.split(' ',1)[1]
        else:parts[section].append(line)
    if any(not parts[k] for k in parts):raise ValueError('incomplete postflop')
    out=src.replace('##f$preflop##','##f$preflop##\n'+'\n'.join(check_lines),1)
    out=out.replace('##f$flop##','\n'.join(parts['helpers']).rstrip()+'\n\n##f$flop##',1)
    for street in ('flop','turn','river'):
        out=out.replace(f'##f${street}##',f'##f${street}##\n'+'\n'.join(parts[street]).strip(),1)
    for street in ('preflop','flop','turn','river'):
        if out.count(f'##f${street}##')!=1:raise ValueError('duplicate street')
    if out.count('Set user_H6_LimpSBIntent')!=1 or out.count('Set user_H6_LimpOtherIntent')!=1:
        raise ValueError('missing capture')
    COMBINED.write_text(out,encoding='utf-8',newline='\n')
    return 2,sum(x.startswith('WHEN ') for k in ('flop','turn','river') for x in parts[k])

if __name__=='__main__':print('LIMPED_BB actions',build())
