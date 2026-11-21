"""Source-first OpenPPL assembler: SRP multiway partial exits by street.

Generates only structural helpers (numeric topology). Strategic choices stay in
partial_transition_policy.oppl. Nothing here can send OpenHoldem actions.
"""
from pathlib import Path
import csv

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'limped_bb_v1' / 'preflop_multiway_limp_bb_draft.oppl'
POLICY = HERE / 'partial_transition_policy.oppl'
HELPERS = HERE / 'topology_helpers.oppl'
COMBINED = HERE / 'preflop_multiway_partial_v3_draft.oppl'
MATRIX = HERE / 'PARTIAL_TRANSITION_TOPOLOGY.csv'
STREETS = ('flop', 'turn', 'river')


def tuples_for(street, left):
    """Unique physically possible topology, no all-in, 4-6-way on flop.

    Antecedents n >= turn_start >= river_start >= left, with n > left >= 2.
    The skipped-street values are not referenced in earlier-street helpers.
    """
    for n in range(3, 6):
        if not 2 <= left < n:
            continue
        if street == 'flop':
            yield (n, left)
        elif street == 'turn':
            for turn in range(left, n + 1):
                yield (n, turn, left)
        elif street == 'river':
            for turn in range(left, n + 1):
                for river in range(left, turn + 1):
                    yield (n, turn, river, left)
        else:
            raise ValueError(street)


def render_helpers():
    lines=['// Generated topology helpers, native OpenPPL symbols; not a runtime claim.',
           '// OpponentsOnFlop/Turn/River refer to STREET-START counts from library.',
           '// OpponentsLeft means current surviving opponents.',
           '// A fall at ANY previous/current street must be evidenced: flop > left.',
           '// All helper routes require upstream SRP-only intent guards.',
           '']
    for street in STREETS:
        short={'flop':'F','turn':'T','river':'R'}[street]
        for left in (2,3,4):
            name=f'f$H6Partial{short}{left}'
            lines.append(f'##{name}##')
            for value in tuples_for(street,left):
                fields={'flop':('OpponentsOnFlop','OpponentsLeft'),
                        'turn':('OpponentsOnFlop','OpponentsOnTurn','OpponentsLeft'),
                        'river':('OpponentsOnFlop','OpponentsOnTurn','OpponentsOnRiver','OpponentsLeft')}[street]
                context=' AND '.join(f'{k} = {v}' for k,v in zip(fields,value))
                # With historic preflop role plus actual BotRaised/Called qualifiers.
                for role in ('f$H6CrowdedPFR','f$H6CrowdedCaller'):
                    lines.append(f'WHEN (Is{street.title()} AND {context} AND {role}) RETURN TRUE FORCE')
            lines.append('WHEN Others RETURN FALSE FORCE')
            lines.append('')
        lines.append(f'##f$H6Partial{short}##')
        for left in (2,3,4):
            lines.append(f'WHEN (f$H6Partial{short}{left}) RETURN TRUE FORCE')
        lines.append('WHEN Others RETURN FALSE FORCE')
        lines.append('')
    return '\n'.join(lines)


def chunks(text):
    result={'helpers':[], **{s:[] for s in STREETS}}
    where='helpers'
    for line in text.splitlines():
        if line.startswith('//@STREET '):
            where=line.split(' ',1)[1]
            if where not in STREETS:raise ValueError('unknown street')
        else:result[where].append(line)
    if not all(result.values()):raise ValueError('policy chunks incomplete')
    return result


def build():
    original=PARENT.read_text(encoding='utf-8')
    if any(original.count(f'##f${s}##')!=1 for s in ('preflop',*STREETS)):
        raise ValueError('parent sections changed')
    if 'f$H6PartialF2' in original:raise ValueError('module already integrated')
    helpers=render_helpers()
    HELPERS.write_text(helpers,encoding='utf-8',newline='\n')
    policy=chunks(POLICY.read_text(encoding='utf-8'))
    combined=original.replace('##f$flop##',helpers.rstrip()+'\n'+'\n'.join(policy['helpers']).rstrip()+'\n\n##f$flop##',1)
    for street in STREETS:
        combined=combined.replace(f'##f${street}##',f'##f${street}##\n'+'\n'.join(policy[street]).strip(),1)
    if any(combined.count(f'##f${s}##')!=1 for s in ('preflop',*STREETS)):
        raise ValueError('street duplicate')
    # Check every original WHEN in same relative order, including memory SET lines.
    earlier=[x for x in original.splitlines() if x.startswith('WHEN ')]
    now=[x for x in combined.splitlines() if x.startswith('WHEN ')]
    i=0
    for rule in earlier:
        while i<len(now) and now[i]!=rule:i+=1
        if i>=len(now):raise ValueError('parent action lost / reordered')
        i+=1
    COMBINED.write_text(combined,encoding='utf-8',newline='\n')
    with MATRIX.open('w',newline='',encoding='utf-8') as fp:
        w=csv.writer(fp)
        w.writerow(('Street','OpponentsOnFlop','OpponentsOnTurn','OpponentsOnRiver','OpponentsLeft','PolicyOwner','RuntimeStatus'))
        for street in STREETS:
            for n in range(3,6):
                for left in range(1,n+1):
                    if street=='flop':
                        paths=[(n,None,None,left)]
                    elif street=='turn':
                        paths=[(n,t,None,left) for t in range(left,n+1)]
                    else:
                        paths=[(n,t,r,left) for t in range(left,n+1) for r in range(left,t+1)]
                    for (f,t,r,k) in paths:
                        owner='NEW_PARTIAL' if 2<=k<f else 'PARENT_HU' if k==1 else 'PARENT_UNCHANGED'
                        w.writerow((street,f,'' if t is None else t,'' if r is None else r,k,owner,'STATIC_DRAFT_NOT_OH_VERIFIED'))
    return (sum(1 for s in STREETS for k in (2,3,4) for _ in tuples_for(s,k)),
            sum(line.startswith('WHEN (') for s in STREETS for line in policy[s]))

if __name__=='__main__':print('partial multiway helpers/action decisions',build())
