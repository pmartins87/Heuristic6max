"""G2-a v0.11: read-only admissibility gate for externally sourced preflop charts.

NOT a strategy selector or OpenPPL converter. It prevents accidental promotion of
charts with unmatched rake, sizing, node, license or stack to operational policy.
The in-repository Python baseline remains immutable and DRAFT.
"""
from __future__ import annotations
import csv
import json
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

REQUIRED_FIELDS = frozenset({
    'game','seats','effective_stack_bb','node','opener','aggressor',
    'open_to_bb','threebet_to_bb','rake_id','rake_cap_bb',
})


@dataclass(frozen=True)
class Verdict:
    source_id: str
    result: str
    gaps: tuple[str,...]
    reference_only: bool


def load_registry(path:Path=HERE/'source_candidates.json'):
    with path.open(encoding='utf-8') as fh: registry=json.load(fh)
    if set(registry) != {'target', 'sources'}:
        raise ValueError('Registry root must contain target and sources only')
    target = registry['target']
    if set(target) != REQUIRED_FIELDS:
        raise ValueError(f'Target contract mismatch: {sorted(REQUIRED_FIELDS.symmetric_difference(target))}')
    if target['rake_id'] is None or target['rake_cap_bb'] is None:
        # Missing rake is intentional and must not be silently treated as 0.
        pass
    if len(registry['sources']) < 1:
        raise ValueError('Source candidates absent')
    ids=[x['id'] for x in registry['sources']]
    if len(ids)!=len(set(ids)):
        raise ValueError('Repeated source id')
    return registry


def evaluate(target:dict, source:dict)->Verdict:
    """Fail closed. An exact match additionally requires node, license and evidence."""
    for key in REQUIRED_FIELDS:
        if key not in target or key not in source:
            raise ValueError(f'Missing schema key {key}')
    gaps=[]
    for key in ('game','seats','effective_stack_bb','node','opener','aggressor',
                'open_to_bb','threebet_to_bb','rake_id','rake_cap_bb'):
        want=target[key];actual=source[key]
        if want is None or actual is None:
            gaps.append(f'{key}:UNKNOWN')
        elif key in ('open_to_bb','threebet_to_bb','rake_cap_bb','effective_stack_bb'):
            if abs(float(want)-float(actual))>1e-8:
                gaps.append(f'{key}:MISMATCH')
        elif want != actual:
            gaps.append(f'{key}:MISMATCH')
    if not source.get('specific_node_verified',False): gaps.append('node_evidence:UNVERIFIED')
    if not source.get('explicit_derivative_rights',False): gaps.append('rights:UNVERIFIED')
    if not source.get('range_frequencies_accessible',False): gaps.append('frequencies:UNAVAILABLE')
    if source.get('origin')!='INDEPENDENT_SOLVED_SOURCE': gaps.append('origin:NOT_SOLVER_EVIDENCE')
    if gaps:
        return Verdict(source['id'],'REFERENCE_ONLY',tuple(sorted(set(gaps))),True)
    return Verdict(source['id'],'ELIGIBLE_FOR_MANUAL_REVIEW',(),False)


def baseline_contract():
    """Read the actual strategy sources; do not duplicate its bet sizes as truth."""
    import sys
    base=ROOT/'gto6_heuristic_v0_6_1'
    if not base.exists(): raise RuntimeError('Baseline source checkout missing')
    sys.path.insert(0,str(base))
    from vs_open_reference import expected_open, threebet_to_bb
    from vs_3bet_reference import RANGES
    return {'open_to_bb':float(expected_open('HJ')),
            'threebet_to_bb':float(threebet_to_bb('HJ','CO')),
            'defense_classes':len(RANGES[('HJ','CO')])}


def run(output:Path=HERE/'SOURCE_APPLICABILITY_v0_11.csv'):
    reg=load_registry()
    true=baseline_contract()
    if (true['open_to_bb']!=reg['target']['open_to_bb'] or
        true['threebet_to_bb']!=reg['target']['threebet_to_bb'] or
        true['defense_classes']!=169):
        raise RuntimeError('Registry target drifted from immutable Python baseline')
    records=[evaluate(reg['target'],s) for s in reg['sources']]
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,lineterminator='\n')
        w.writerow(('Source','Verdict','ReferenceOnly','UnresolvedMismatches'))
        for x in records:
            w.writerow((x.source_id,x.result,int(x.reference_only),';'.join(x.gaps)))
    return records

if __name__=='__main__':
    for row in run():
        print(row.source_id, row.result, '; '.join(row.gaps))
