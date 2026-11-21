"""Compile source OpenPPL 3bet multiway strategy into existing integrated bot.

Reuses the already-generated 3bet origin intent flags and excludes any
3bet-HU, SRP, limped, squeeze or 4bet states outside the narrow reviewed tree.
"""
from pathlib import Path
import csv,sys
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'multilimp_bb_v2'/'preflop_multiway_partial_multilimp_v2_draft.oppl'
POLICY=HERE/'threebet_multiway_policy.oppl'
HELPERS=HERE/'threebet_multiway_topology.oppl'
COMBINED=HERE/'preflop_srp_limp_3bet_multiway_draft.oppl'
MATRIX=HERE/'THREEBET_MW_TOPOLOGY.csv'
STREETS=('flop','turn','river')

def legal():
    for street in STREETS:
        for n in range(2,6):
            for live in range(1,n+1):
                if street=='flop':yield street,n,None,None,live
                if street=='turn':
                    for t in range(live,n+1):yield street,n,t,None,live
                if street=='river':
                    for t in range(live,n+1):
                        for r in range(live,t+1):yield street,n,t,r,live

def render_helpers():
    ml_conflicts=' AND '.join('NOT user_H6_ML%d%s'%(n,typ) for n in range(2,6) for typ in ('SB','Other') if n<5 or typ=='SB')
    lines=['// 3bet MW topology: actual 3bet role, initial 3-6 players on flop.',
           '// All current street-entrant counts are native OpenPPL symbols.',
           '// A 3bet pot is not an SRP, not a limped pot, and not a 4bet pot.',
           '##f$H6ThreeBetMWAggressor##',
           'WHEN (nplayersdealt = 6 AND NumberOfOpponentsAllin = 0 AND NOT StackUnknown AND user_H6_3betIntent AND NOT user_H6_RFIIntent AND NOT user_H6_VSOpenCallIntent AND NOT user_H6_LimpSBIntent AND NOT user_H6_LimpOtherIntent AND '+ml_conflicts+' AND BotRaisedBeforeFlop AND NOT BotCalledBeforeFlop AND NumberOfRaisesBeforeFlop = 1) RETURN TRUE FORCE',
           'WHEN Others RETURN FALSE FORCE',
           '##f$H6ThreeBetMWCaller##',
           'WHEN (nplayersdealt = 6 AND NumberOfOpponentsAllin = 0 AND NOT StackUnknown AND user_H6_RFIIntent AND NOT user_H6_3betIntent AND NOT user_H6_VSOpenCallIntent AND NOT user_H6_LimpSBIntent AND NOT user_H6_LimpOtherIntent AND '+ml_conflicts+' AND BotRaisedBeforeFlop AND BotCalledBeforeFlop AND NumberOfRaisesBeforeFlop = 1) RETURN TRUE FORCE',
           'WHEN Others RETURN FALSE FORCE',
           '##f$H6ThreeBetMWOrigin##',
           'WHEN (f$H6ThreeBetMWAggressor) RETURN TRUE FORCE',
           'WHEN (f$H6ThreeBetMWCaller) RETURN TRUE FORCE',
           'WHEN Others RETURN FALSE FORCE','',
           '##f$H6ThreeBetMWValid##']
    for street,n,t,r,left in legal():
        fields=[('OpponentsOnFlop',n)]
        if t is not None:fields.append(('OpponentsOnTurn',t))
        if r is not None:fields.append(('OpponentsOnRiver',r))
        fields.append(('OpponentsLeft',left))
        atoms=[f'Is{street.title()}',*(f'{k} = {v}' for k,v in fields),'f$H6ThreeBetMWOrigin']
        lines.append('WHEN ('+' AND '.join(atoms)+') RETURN TRUE FORCE')
    lines+=['WHEN Others RETURN FALSE FORCE','']
    for tier,counts in (('HU',(1,)),('Two',(2,)),('Crowded',(3,4,5))):
        lines.append(f'##f$H6ThreeBetMW{tier}##')
        for left in counts:
            lines.append(f'WHEN (f$H6ThreeBetMWValid AND OpponentsLeft = {left}) RETURN TRUE FORCE')
        lines+=['WHEN Others RETURN FALSE FORCE','']
    return '\n'.join(lines)

def chunks(source):
    result={'helpers':[],**{s:[] for s in STREETS}}
    at='helpers'
    for line in source.splitlines():
        if line.startswith('//@STREET '):
            at=line.split(' ',1)[1]
            if at not in STREETS:raise ValueError('bad street')
        else:result[at].append(line)
    if not all(result.values()):raise ValueError('empty chunks')
    return result

def build():
    old=PARENT.read_text(encoding='utf-8')
    if 'f$H6ThreeBetMWValid' in old or any(old.count(f'##f${s}##')!=1 for s in ('preflop',*STREETS)):
        raise ValueError('unexpected previous OpenPPL tree')
    helpers=render_helpers()
    HELPERS.write_text(helpers,encoding='utf-8',newline='\n')
    parts=chunks(POLICY.read_text(encoding='utf-8'))
    now=old.replace('##f$flop##',helpers.rstrip()+'\n'+'\n'.join(parts['helpers']).rstrip()+'\n\n##f$flop##',1)
    for street in STREETS:
        now=now.replace(f'##f${street}##',f'##f${street}##\n'+'\n'.join(parts[street]).strip(),1)
    pre=[x for x in old.splitlines() if x.startswith('WHEN ')]
    new=[x for x in now.splitlines() if x.startswith('WHEN ')]
    index=0
    for line in pre:
        while index<len(new) and new[index]!=line:index+=1
        if index>=len(new):raise ValueError('previous WHEN lost/reordered')
        index+=1
    COMBINED.write_text(now,encoding='utf-8',newline='\n')
    with MATRIX.open('w',newline='',encoding='utf-8') as fp:
        writer=csv.writer(fp)
        writer.writerow(['Street','OpponentsOnFlop','OpponentsOnTurn','OpponentsOnRiver','OpponentsLeft','PreflopRole','Domain','OH_Runtime'])
        for street,n,t,r,left in legal():
            for role in ('THREEBET_AGGRESSOR','RFI_CALLER_VS_THREEBET'):
                writer.writerow([street,n,'' if t is None else t,'' if r is None else r,left,role,
                                 '3BET_MULTIWAY_REQUIRES_EXACT_HISTORY','UNVERIFIED'])
    return len(list(legal())),sum(x.startswith('WHEN (') for s in STREETS for x in parts[s])

if __name__=='__main__':print('3bet multiway topology/actions',build())
