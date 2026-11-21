"""Generate OpenPPL-only 3bet HU v1 overlay on frozen HIST-v3.

Python performs source extraction and assembly, NEVER reimplements poker policy.
Preflop origin markers express observed INTENT and must be cross-checked against
native actual-action history on later streets. Not validated in real OH.
"""
from __future__ import annotations
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'srp_history_v3'/'preflop_srp_history_v3.oppl'
POLICY=HERE/'threebet_hu_postflop.oppl'
OUT=HERE/'preflop_srp_and_3bet_hu_draft.oppl'
ORIGIN=HERE/'preflop_intent_capture.oppl'
HEADER=re.compile(r'^##f\$[A-Za-z0-9_]+##$')
RAISE=re.compile(r'^WHEN (?P<cond>\([^()]+\)) RaiseTo (?P<size>\d+(?:\.\d+)?) FORCE$')


def capture_rules(preflop_text:str)->tuple[list[str],list[str]]:
    rfi=[];threebet=[];in_pre=False
    for line in preflop_text.splitlines():
        if line=='##f$preflop##':
            if in_pre:raise ValueError('duplicate preflop header')
            in_pre=True;continue
        if in_pre and HEADER.fullmatch(line):break
        if not in_pre:continue
        m=RAISE.fullmatch(line)
        if not m:continue
        condition=m['cond']
        if (' AND Raises = 0 AND Calls = 0 AND ' in condition and
            'BotRaisedBeforeFlop' not in condition):
            rfi.append('WHEN '+condition+' Set user_H6_RFIIntent')
        elif (' AND Raises = 1 AND Calls = 0 AND ' in condition and
              'FirstRaiserPosition' in condition and
              'BotRaisedBeforeFlop' not in condition and
              'RaisesSinceLastPlay' not in condition):
            threebet.append('WHEN '+condition+' Set user_H6_3betIntent')
    if len(rfi)!=9 or len(threebet)<20:
        raise ValueError(f'Unreviewed preflop raise classifications: RFI={len(rfi)}, 3bet={len(threebet)}')
    if len(set(rfi))!=len(rfi) or len(set(threebet))!=len(threebet):
        raise ValueError('Overlapping identical origin-intent rules')
    return rfi,threebet


def split_policy(source:str):
    chunks={'HELPERS':[],'flop':[],'turn':[],'river':[]};section='HELPERS'
    for line in source.splitlines():
        if line.startswith('//@STREET '):
            section=line.split(' ',1)[1]
            if section not in ('flop','turn','river'):raise ValueError('Unexpected street')
        else:chunks[section].append(line)
    if not all(chunks.values()):raise ValueError('Missing 3bet policy sections')
    return chunks


def generate()->tuple[int,int,int]:
    old=PREVIOUS.read_text(encoding='utf-8')
    if any(old.count(f'##f${x}##')!=1 for x in ('preflop','flop','turn','river')):
        raise ValueError('Previous integrated OpenPPL streets drifted')
    if 'user_H6_RFIIntent' in old or 'f$H6ThreeBetHU' in old:
        raise ValueError('Source already contains v1 tags')
    rfi,threebet=capture_rules(old)
    pre_capture=([
        '// Generated from exact RFI and VS_OPEN RaiseTo decisions; pre-action INTENT only.',
        '// Native postflop BotRaisedBeforeFlop / BotCalledBeforeFlop are REQUIRED.',
        *rfi,*threebet,''])
    ORIGIN.write_text('\n'.join(pre_capture),encoding='utf-8',newline='\n')
    chunks=split_policy(POLICY.read_text(encoding='utf-8'))
    combined=old.replace('##f$preflop##','##f$preflop##\n'+'\n'.join(pre_capture),1)
    combined=combined.replace('##f$flop##','\n'.join(chunks['HELPERS']).rstrip()+'\n\n##f$flop##\n'+'\n'.join(chunks['flop']).rstrip(),1)
    for street in ('turn','river'):
        combined=combined.replace(f'##f${street}##',f'##f${street}##\n'+'\n'.join(chunks[street]).rstrip(),1)
    if any(combined.count(f'##f${x}##')!=1 for x in ('preflop','flop','turn','river')):
        raise ValueError('Output duplicated action functions')
    if combined.count('Set user_H6_RFIIntent')!=len(rfi) or combined.count('Set user_H6_3betIntent')!=len(threebet):
        raise ValueError('Lost provenance capture')
    OUT.write_text(combined,encoding='utf-8',newline='\n')
    return len(rfi),len(threebet),sum(len([x for x in chunks[k] if x.startswith('WHEN ')]) for k in ('flop','turn','river'))

if __name__=='__main__': print('3bet HU INTENT and policy:',generate())
