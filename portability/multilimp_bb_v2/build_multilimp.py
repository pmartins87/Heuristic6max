"""OpenPPL-only BB option versus 2..5 limpers; includes street-start topology.

All preflop tags are generated from strict BB open-option contexts. Strategy
choices are written ONLY in multilimp_policy.oppl, not computed here.
"""
from pathlib import Path
import csv
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'multiway_transitions_v3'/'preflop_multiway_partial_v3_draft.oppl'
STRATEGY=HERE/'multilimp_policy.oppl'
HELPERS=HERE/'multilimp_topology.oppl'
CAPTURE=HERE/'multilimp_preflop_capture.oppl'
COMBINED=HERE/'preflop_multiway_partial_multilimp_v2_draft.oppl'
MATRIX=HERE/'MULTILIMP_TOPOLOGY.csv'
STREETS=('flop','turn','river')
INTENTS=tuple((n,typ, f'user_H6_ML{n}{typ}') for n in range(2,6) for typ in ('SB','Other') if n<5 or typ=='SB')
BASE=('IsPreflop','nplayersdealt = 6','InBigBlind','Raises = 0',
      'StillToAct = 0','AmountToCall = 0','NOT StackUnknown',
      'StackSize >= 95','StackSize <= 105',
      'MinOpponentStackSize >= 95','MaxOpponentStackSize <= 105')

def pot_for(n,typ):return (n+1) if typ=='SB' else (n+1.5)

def capture():
    lines=['// New multi-limper BB check options, not isolated/raised pots.',
           '// These intents require a later BotCheckedPreflop observation.',
           '// The two pot totals reflect whether SB completed its half blind.', '']
    for n,typ,tag in INTENTS:
        atoms=BASE+(f'Calls = {n}',f'PotSize = {pot_for(n,typ):g}')
        clause='('+' AND '.join(atoms)+')'
        lines.append('WHEN '+clause+' Set '+tag)
        lines.append('WHEN '+clause+' Check FORCE')
    return '\n'.join(lines)+'\n'

def topologies():
    """Enumerate all legal monotone street-start/player-left states after limps.

    n OpponentsOnFlop (all limpers reached flop); 1 <= alive <= n.
    """
    for street in STREETS:
        for n in range(2,6):
            for left in range(1,n+1):
                if street=='flop':yield street,n,None,None,left
                elif street=='turn':
                    for t in range(left,n+1):yield street,n,t,None,left
                else:
                    for t in range(left,n+1):
                        for r in range(left,t+1):yield street,n,t,r,left


def helper_source():
    flags=[tag for _,_,tag in INTENTS]
    lines=['// Native OpenPPL 6-max multi-limp BB provenance and chronology. DRAFT.',
           '// Unlike SRP/3bet, BB checked free against 2-5 limpers.',
           '// Persistent Set flags are intent only, requiring actual BB CHECK.', '']
    for n in range(2,6):
        name=f'f$H6MLOrigin{n}'
        lines.append(f'##{name}##')
        for m,typ,tag in INTENTS:
            if m!=n:continue
            atoms=['nplayersdealt = 6',f'OpponentsOnFlop = {n}',
                   'NumberOfOpponentsAllin = 0','NOT StackUnknown',
                   'BotCheckedPreflop','NOT BotRaisedBeforeFlop',
                   'NOT BotCalledBeforeFlop','NumberOfRaisesBeforeFlop = 0',tag]
            atoms.extend('NOT '+x for x in flags if x!=tag)
            atoms.extend(('NOT user_H6_LimpSBIntent','NOT user_H6_LimpOtherIntent',
                          'NOT user_H6_RFIIntent','NOT user_H6_3betIntent',
                          'NOT user_H6_VSOpenCallIntent'))
            lines.append('WHEN ('+' AND '.join(atoms)+') RETURN TRUE FORCE')
        lines+=['WHEN Others RETURN FALSE FORCE','']
    lines.append('##f$H6MLValid##')
    for street,n,t,r,left in topologies():
        atoms=[f'Is{street.title()}',f'OpponentsOnFlop = {n}']
        if t is not None:atoms.append(f'OpponentsOnTurn = {t}')
        if r is not None:atoms.append(f'OpponentsOnRiver = {r}')
        atoms.extend((f'OpponentsLeft = {left}',f'f$H6MLOrigin{n}'))
        lines.append('WHEN ('+' AND '.join(atoms)+') RETURN TRUE FORCE')
    lines+=['WHEN Others RETURN FALSE FORCE','']
    for tier,pairs in (('HU',(1,)),('Two',(2,)),('Crowded',(3,4,5))):
        lines.append(f'##f$H6ML{tier}##')
        for left in pairs:
            lines.append(f'WHEN (f$H6MLValid AND OpponentsLeft = {left}) RETURN TRUE FORCE')
        lines+=['WHEN Others RETURN FALSE FORCE','']
    return '\n'.join(lines)

def split(source):
    result={'helpers':[], **{s:[] for s in STREETS}}
    at='helpers'
    for line in source.splitlines():
        if line.startswith('//@STREET '):
            at=line.split(' ',1)[1]
            if at not in STREETS:raise ValueError('unknown street')
        else:result[at].append(line)
    if not all(result.values()):raise ValueError('bad strategy chunks')
    return result

def build():
    src=PARENT.read_text(encoding='utf-8')
    if 'f$H6MLValid' in src or 'user_H6_ML2SB' in src:raise ValueError('duplicate multilimp module')
    if any(src.count(f'##f${s}##')!=1 for s in ('preflop',*STREETS)):
        raise ValueError('parent layout changed')
    CAPTURE.write_text(capture(),encoding='utf-8',newline='\n')
    HELPERS.write_text(helper_source(),encoding='utf-8',newline='\n')
    policy=split(STRATEGY.read_text(encoding='utf-8'))
    combo=src.replace('##f$preflop##','##f$preflop##\n'+capture(),1)
    combo=combo.replace('##f$flop##',helper_source().rstrip()+'\n'+'\n'.join(policy['helpers']).rstrip()+'\n\n##f$flop##',1)
    for street in STREETS:
        combo=combo.replace(f'##f${street}##',f'##f${street}##\n'+'\n'.join(policy[street]).strip(),1)
    if any(combo.count(f'##f${s}##')!=1 for s in ('preflop',*STREETS)):
        raise ValueError('duplicate street')
    # Source order remains: every ancestor rule must be a subsequence.
    earlier=[l for l in src.splitlines() if l.startswith('WHEN ')]
    after=[l for l in combo.splitlines() if l.startswith('WHEN ')]
    i=0
    for rule in earlier:
        while i<len(after) and after[i]!=rule:i+=1
        if i>=len(after):raise ValueError('ancestor WHEN was modified or removed')
        i+=1
    COMBINED.write_text(combo,encoding='utf-8',newline='\n')
    with MATRIX.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Street','LimperCount','SmallBlindCompletes','PreflopPotBB',
                         'OpponentsOnFlop','OpponentsOnTurn','OpponentsOnRiver',
                         'OpponentsLeft','StaticRoute','RuntimeStatus'])
        for street,n,t,r,left in topologies():
            for nn,typ,tag in INTENTS:
                if nn!=n:continue
                writer.writerow([street,n,typ=='SB',f'{pot_for(n,typ):.1f}',n,
                                 '' if t is None else t,'' if r is None else r,
                                 left,'MULTILIMP_BB_POLICY','DRAFT_NOT_OPENHOLDEM_VERIFIED'])
    return len(INTENTS),sum(x.startswith('WHEN (') for s in STREETS for x in policy[s]),sum(1 for _ in topologies())

if __name__=='__main__':print('Multi-limp options, street decisions, legal topologies',build())
