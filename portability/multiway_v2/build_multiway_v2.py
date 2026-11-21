"""Offline composition of frozen p3way tree with 4-6way and HU-transition layers."""
from pathlib import Path
import csv
from multiway_interpreter import CROWDED,TRANSITION,parse_file

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'p3way_srp_v1'/'preflop_srp_3bet_3way_draft.oppl'
COMBINED=HERE/'preflop_multiway_v2_draft.oppl'
COVERAGE=HERE/'MULTIWAY_V2_TOPOLOGY.csv'


def extract(text):
    parts={'helpers':[],'flop':[],'turn':[],'river':[]};section='helpers'
    for line in text.splitlines():
        if line.startswith('//@STREET '):section=line.split(' ',1)[1]
        else:parts[section].append(line)
    if any(not parts[x] for x in parts):raise ValueError('incomplete module')
    return parts


def build():
    original=PREVIOUS.read_text(encoding='utf-8')
    if any(original.count('##f$'+x+'##')!=1 for x in ('preflop','flop','turn','river')):
        raise ValueError('unexpected upstream street layout')
    model=parse_file()
    blocks=[extract(x.read_text(encoding='utf-8')) for x in (CROWDED,TRANSITION)]
    helpers='\n'.join('\n'.join(x['helpers']).rstrip() for x in blocks)+'\n'
    updated=original.replace('##f$flop##',helpers+'\n##f$flop##',1)
    for street in ('flop','turn','river'):
        rules='\n'.join('\n'.join(x[street]).strip() for x in blocks)+'\n'
        updated=updated.replace(f'##f${street}##',f'##f${street}##\n'+rules,1)
    for street in ('preflop','flop','turn','river'):
        if updated.count('##f$'+street+'##')!=1:raise ValueError('street duplicated')
    if any(y not in updated for y in original.splitlines() if y.startswith('WHEN ')):
        raise ValueError('upstream WHEN changed')
    COMBINED.write_text(updated,encoding='utf-8',newline='\n')
    with COVERAGE.open('w',encoding='utf-8',newline='') as output:
        writer=csv.writer(output)
        writer.writerow(('OpponentsOnFlop','OpponentsLeft','Family','IntentRole','ExpectedDomain','Caveat'))
        for initial in range(1,6):
            for left in range(0,initial+1):
                for role in ('RFI_PFR','VS_OPEN_CALLER'):
                    if initial in (3,4,5) and left==initial:domain='CROWDED_SRP_V1'
                    elif initial>=2 and left==1:domain='MULTIWAY_TO_HU_V1'
                    else:domain='NOT_IN_NEW_LAYER'
                    writer.writerow((initial,left,f'{initial+1}WAY_ON_FLOP',role,domain,
                          'STATIC_ONLY_NEEDS_OPENHOLDEM_REPLAY'))
    return sum(len(model.rules[s]) for s in ('flop','turn','river')),len(model.helpers)

if __name__=='__main__':print('Multiway v2 actions, helpers:',build())
