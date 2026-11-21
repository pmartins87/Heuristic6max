"""Source-preserving offline builder of HIST-v3; no alternate poker policy."""
from pathlib import Path
from chronological_history import export

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'srp_history_v2'/'srp_hu_history_v2.oppl'
PREVIOUS_COMBINED=HERE.parent/'srp_history_v2'/'preflop_srp_history_v2.oppl'
GATES=HERE/'hist3_gate_helpers.oppl'
CAPTURE=HERE/'history_memory_capture.oppl'
SOURCE=HERE/'srp_hu_history_v3.oppl'
COMBINED=HERE/'preflop_srp_history_v3.oppl'


def generate():
    old=PREVIOUS.read_text(encoding='utf-8')
    oldcombined=PREVIOUS_COMBINED.read_text(encoding='utf-8')
    gates=GATES.read_text(encoding='utf-8')
    captures=[x for x in CAPTURE.read_text(encoding='utf-8').splitlines() if x.startswith('WHEN ')]
    if len(captures)!=4 or oldcombined.count(old)!=1 or not oldcombined.endswith(old):
        raise ValueError('Source snapshot drift or malformed memory captures')
    if any(old.count('##'+x+'##')!=1 for x in ('f$flop','f$turn','f$river')):
        raise ValueError('Street source drift')
    # Replace ONLY invocations in WHEN lines. Do not change original helper definitions.
    text=[]
    for l in old.splitlines():
        if l.startswith('WHEN '):
            l=l.replace('f$HLFlopRaiseCall','f$H3FlopRaiseCallObserved')
            l=l.replace('f$HLFlopCheckRaiseCall','f$H3FlopCheckRaiseCallObserved')
            l=l.replace('f$HLTurnRaiseCall','f$H3TurnRaiseCallObserved')
            l=l.replace('f$HLTurnCheckRaiseCall','f$H3TurnCheckRaiseCallObserved')
            l=l.replace('f$HLFlopBetRaisedCall','f$H3FlopBetRaisedCallStrict')
            l=l.replace('f$HLTurnBetRaisedCall','f$H3TurnBetRaisedCallStrict')
            l=l.replace('f$HLTurnDomainV2','f$H3TurnDomain')
            l=l.replace('f$HLRiverDomainV2','f$H3RiverDomain')
        text.append(l)
    rewritten='\n'.join(text).rstrip()+'\n'
    for header in ('##f$flop##','##f$turn##'):
        if rewritten.count(header)!=1:raise ValueError('missing street')
    rewritten=rewritten.replace('##f$flop##','##f$flop##\n'+'\n'.join(captures[:2]),1)
    rewritten=rewritten.replace('##f$turn##','##f$turn##\n'+'\n'.join(captures[2:]),1)
    rewritten=rewritten.replace('##f$flop##',gates.rstrip()+'\n\n##f$flop##',1)
    combined=oldcombined[:-len(old)]+rewritten
    for name in ('##f$preflop##','##f$flop##','##f$turn##','##f$river##'):
        if combined.count(name)!=1:raise ValueError(f'street duplicated {name}')
    SOURCE.write_text(rewritten,encoding='utf-8',newline='\n')
    COMBINED.write_text(combined,encoding='utf-8',newline='\n')
    n=export()
    from routing_coverage import export as export_routing
    if export_routing()!=(484,100):raise ValueError('HIST3 coverage drift')
    return n,len(captures),sum(x.startswith('##f$') for x in gates.splitlines())

if __name__=='__main__':print('HIST3',generate())
