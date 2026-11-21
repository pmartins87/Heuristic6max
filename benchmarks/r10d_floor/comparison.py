"""Factual engineering comparison, NOT solver, NOT poker runtime.

The frozen DeepCrusher R10d reference was measured from the exact GitHub blob,
not guessed from an unrelated R10 source or from header-count summaries.
Heuristic policy is scanned from its actual integrated OpenPPL, not test code.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
R10D=HERE/'R10D_REFERENCE.json'
PROMOTION=HERE/'PROMOTION_GATE.json'
MATRIX=HERE/'CAPABILITY_MATRIX.csv'
SOURCE=ROOT/'portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl'
REPORT=HERE/'CURRENT_GAP_REPORT.json'
HEAD=re.compile(r'^##(?P<kind>f\$|list)[^#]+##$',re.I|re.M)
WHEN=re.compile(r'^\s*WHEN\s+',re.I|re.M)
SET=re.compile(r'^\s*WHEN\b[^\r\n]*\bSet\s+user_[A-Za-z0-9_]+\s*$',re.I|re.M)
USER=re.compile(r'\buser_[A-Za-z0-9_]+\b')
FUNC=re.compile(r'^##f\$([^#]+)##$',re.I|re.M)


def inventory(text:str)->dict:
    lines=text.splitlines()
    functions=[m.group(1) for m in FUNC.finditer(text)]
    result={
        'bytes':len(text.encode('utf-8')),
        'lines':len(lines),
        'function_headers':sum(x.startswith('##f$') for x in lines),
        'list_headers':sum(x.startswith('##list') for x in lines),
        'when_rules':len(WHEN.findall(text)),
        'set_user_lines':len(SET.findall(text)),
        'distinct_user_symbols':len(set(USER.findall(text))),
        'f_game_functions':sum(x.lower().startswith('game_') for x in functions),
        'f_pot_functions':sum(x.lower().startswith('pot_') for x in functions),
        'f_hand_functions':sum(x.lower().startswith('hand_') for x in functions),
        'f_board_functions':sum(x.lower().startswith('board_') for x in functions),
        'f_stack_functions':sum(x.lower().startswith('stack_') for x in functions),
        'f_move_functions':sum(x.lower().startswith('move_') for x in functions),
        'f_pt_functions':sum(x.lower().startswith('pt_') for x in functions),
    }
    result['total_formula_and_list_headers']=result['function_headers']+result['list_headers']
    return result


def measure(reference_path:Path|None=None)->dict:
    with R10D.open(encoding='utf-8') as f:reference=json.load(f)
    if reference_path is not None:
        data=reference_path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=reference['sha256_documented']:
            raise ValueError('The supplied reference is not exact frozen R10d')
        scanned=inventory(data.decode('utf-8-sig'))
        for key in ('bytes','lines','function_headers','list_headers','when_rules',
                    'set_user_lines','distinct_user_symbols'):
            if scanned[key]!=reference[key]:raise ValueError(f'Frozen R10d mismatch: {key}')
    h=inventory(SOURCE.read_text(encoding='utf-8'))
    with MATRIX.open(encoding='utf-8',newline='') as stream:
        rows=list(csv.DictReader(stream))
    if len(rows)!=14 or len(set(r['CapabilityID'] for r in rows))!=14:
        raise ValueError('Acceptance checklist incomplete/duplicated')
    required=['M%02d'%i for i in range(1,15)]
    if [r['CapabilityID'] for r in rows]!=required:raise ValueError('Acceptance requirements changed/order drift')
    allowed={'VERIFIED','PARTIAL','MISSING'}
    if any(r['CurrentStatus'] not in allowed for r in rows):raise ValueError('Unknown capability status')
    numerics={k:{'R10d':reference[k],'Heuristic':h[k]} for k in
              ('bytes','lines','function_headers','list_headers',
               'total_formula_and_list_headers','when_rules','set_user_lines',
               'distinct_user_symbols','f_game_functions','f_pot_functions')}
    missing=[r['CapabilityID'] for r in rows if r['CurrentStatus']!='VERIFIED']
    attestation=json.loads(PROMOTION.read_text(encoding='utf-8'))
    expected_flags={'runtime_replay_verified','comparative_coverage_review_approved','strategic_quality_acceptance_approved'}
    if set(attestation)!=expected_flags or any(type(attestation[k]) is not bool for k in attestation):
        raise ValueError('Invalid promotion evidence schema')
    promoted=not missing and all(attestation.values())
    return {'reference':{'repo':reference['source_repository'],
                         'file':reference['source_path'],
                         'git_blob_sha':reference['github_blob_sha'],
                         'sha256':reference['sha256_documented']},
            'heuristic_active_file':str(SOURCE.relative_to(ROOT)),
            'metrics':numerics,
            'capabilities_total':len(rows),
            'verified_capabilities':len(rows)-len(missing),
            'unmet_capabilities':missing,
            'surpasses_R10d':promoted,
            'release_gate':'ELIGIBLE_FOR_FINAL_REVIEW' if promoted else 'BLOCKED_MORE_CAPABILITY_AND_REAL_OH_TESTS_REQUIRED',
            'note':'Counts are reference only; strong dominance must be established via verified functional scope and practical play, not rules per line.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference-file',type=Path)
    ap.add_argument('--release-check',action='store_true')
    args=ap.parse_args()
    info=measure(args.reference_file)
    if args.release_check:
        print('RELEASE_ELIGIBLE' if info['surpasses_R10d'] else 'BLOCKED: Heuristic6max is not yet demonstrably >= R10d in functional coverage')
        return 0 if info['surpasses_R10d'] else 2
    REPORT.write_text(json.dumps(info,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('R10d gap:',len(info['unmet_capabilities']),'of',info['capabilities_total'],'minimum capabilities unmet; output updated')
    return 0

if __name__=='__main__':raise SystemExit(main())
