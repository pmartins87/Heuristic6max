"""PORT-3 offline evidence checker; NEVER sends actions to OpenHoldem.

Input is a manually transcribed OBSERVATION CSV, with an independent local
log/screenshot trace. This script does NOT prove it was actually collected by
OpenHoldem. READY_FOR_MANUAL_REVIEW is not operational approval.

The ONLY game policy is imported verbatim from PORT-2 .oppl via its strict
interpreter, which receives observed randomhand; no strategy reimplementation.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from portability.port2 import port2_interpreter as port2  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCES = frozenset({'SYNTHETIC', 'OH_MANUALMODE', 'OH_REPLAY'})
ACTIONS = frozenset({'RAISE','FOLD','CALL','CHECK','SHOVE'})
SCHEMA = (
    'case_id','session_id','hand_id','eval_index','capture_source',
    'openholdem_version','oppl_sha256','hand_class',
    'is_preflop','nplayersdealt','in_utg','raises','calls','still_to_act',
    'pot_bb','amount_to_call_bb','stack_unknown','hero_stack_bb',
    'min_opponent_stack_bb','max_opponent_stack_bb','randomhand',
    'observed_formula_action','observed_formula_raise_to_bb',
    'observed_final_action','observed_final_raise_to_bb',
    'evidence_file','evidence_sha256'
)
REPORT_FIELDS = (
    'case_id','session_id','hand_id','eval_index','capture_source',
    'expected_action','expected_raise_to_bb',
    'observed_formula_action','observed_final_action',
    'verdict','reason'
)

class EvidenceError(ValueError):
    pass


def _bool(value: str, name: str) -> bool:
    if value == '1': return True
    if value == '0': return False
    raise EvidenceError(f'{name}: required 1 or 0')


def _int(value: str, name: str, low: int=0) -> int:
    if not value or not value.isascii() or not value.isdecimal():
        raise EvidenceError(f'{name}: integer required')
    number=int(value)
    if number < low: raise EvidenceError(f'{name}: value below {low}')
    return number


def _num(value: str, name: str, required: bool=True) -> float|None:
    if not value and not required: return None
    if not value: raise EvidenceError(f'{name}: required')
    try: n=Decimal(value)
    except InvalidOperation as e: raise EvidenceError(f'{name}: invalid decimal') from e
    if not n.is_finite(): raise EvidenceError(f'{name}: nonfinite number')
    return float(n)


def _sha_ok(value: str) -> bool:
    return len(value)==64 and all(c in '0123456789abcdef' for c in value)


def parse_case(row: dict[str,str]) -> tuple[port2.Context,float|None]:
    """Validate explicit symbol observation values; no unobserved defaults."""
    hand=row['hand_class']
    if hand not in port2.ALL_HANDS: raise EvidenceError('hand_class: unknown class')
    u=_num(row['randomhand'],'randomhand',required=False)
    if u is not None and not 0 <= u < 1:
        raise EvidenceError('randomhand: must be in [0,1)')
    c=port2.Context(
        hand=hand,
        is_preflop=_bool(row['is_preflop'],'is_preflop'),
        nplayersdealt=_int(row['nplayersdealt'],'nplayersdealt',2),
        in_utg=_bool(row['in_utg'],'in_utg'),
        raises=_int(row['raises'],'raises'),
        calls=_int(row['calls'],'calls'),
        still_to_act=_int(row['still_to_act'],'still_to_act'),
        pot_bb=_num(row['pot_bb'],'pot_bb'),
        amount_to_call_bb=_num(row['amount_to_call_bb'],'amount_to_call_bb'),
        stack_unknown=_bool(row['stack_unknown'],'stack_unknown'),
        hero_stack_bb=_num(row['hero_stack_bb'],'hero_stack_bb'),
        min_opponent_stack_bb=_num(row['min_opponent_stack_bb'],'min_opponent_stack_bb'),
        max_opponent_stack_bb=_num(row['max_opponent_stack_bb'],'max_opponent_stack_bb'),
        randomhand=u,
    )
    return c,u


def _sizing_equal(observed: str, expected: float|None) -> bool:
    if expected is None:
        return observed == ''
    try:
        n=Decimal(observed)
        return n.is_finite() and n==Decimal(str(expected))
    except (InvalidOperation, ValueError):
        return False


def _evidence_ok(row:dict[str,str],evidence_root:Path) -> tuple[bool,str]:
    fname=row['evidence_file']
    digest=row['evidence_sha256']
    if not fname or not _sha_ok(digest):return False,'evidence trace path/SHA256 missing'
    rel=Path(fname)
    if rel.is_absolute() or '..' in rel.parts or '\\' in fname or ':' in fname:
        return False,'evidence trace path must be relative under private evidence root'
    root=evidence_root.resolve()
    target=(root/rel).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        return False,'evidence trace file absent or escaped evidence root'
    if target.stat().st_size==0 or target.stat().st_size>10_000_000:
        return False,'evidence trace empty/oversize'
    real=hashlib.sha256(target.read_bytes()).hexdigest()
    if real != digest:return False,'evidence SHA256 mismatch'
    return True,'trace digest matches (provenance still requires review)'


def _report(row:dict[str,str],expected:tuple[str,float|None]|None,
            verdict:str,reason:str)->dict[str,str]:
    return {
        'case_id':row['case_id'],'session_id':row['session_id'],
        'hand_id':row['hand_id'],'eval_index':row['eval_index'],
        'capture_source':row['capture_source'],
        'expected_action':expected[0] if expected else 'NO_MATCH',
        'expected_raise_to_bb':str(expected[1]) if expected and expected[1] is not None else '',
        'observed_formula_action':row['observed_formula_action'],
        'observed_final_action':row['observed_final_action'],
        'verdict':verdict,'reason':reason,
    }


def audit_rows(rows:list[dict[str,str]], evidence_root:Path,
               model:port2.Parsed|None=None)->list[dict[str,str]]:
    """Verdicts never mean PASS/approved, even with nominal runtime evidence.

    Any mismatch outranks missing evidence or synthetic status, so synthetic
    negative-control tests can reveal failures without being promoted as OH.
    """
    if model is None:model=port2.parse_file()
    digest=hashlib.sha256(port2.SOURCE.read_bytes()).hexdigest()
    if not rows:raise EvidenceError('Empty replay batch')
    out=[]
    last_random={}
    seen=set()
    for row in rows:
        if set(row)!=set(SCHEMA):
            raise EvidenceError('Unexpected/missing CSV columns')
        for key in ('case_id','session_id','hand_id'):
            if not row[key].strip():raise EvidenceError(f'{key}: required')
        source=row['capture_source']
        if source not in SOURCES:raise EvidenceError('capture_source: invalid')
        index=_int(row['eval_index'],'eval_index')
        identifier=(row['session_id'],row['hand_id'],index)
        if identifier in seen:raise EvidenceError('Duplicate (session,hand,eval_index)')
        seen.add(identifier)
        ctx,randomhand=parse_case(row)
        expected=port2.evaluate(model,ctx)
        rkey=(row['session_id'],row['hand_id'])
        if row['oppl_sha256']!=digest:
            out.append(_report(row,expected,'MISMATCH_SOURCE','OPPL SHA256 differs from PORT-2 source'))
            continue
        if expected is None:
            # We cannot claim fail-closed: OpenHoldem may use backup action.
            out.append(_report(row,None,'BLOCKED_NO_MATCH','OpenHoldem fallback unknown: no in-domain OPPL action'))
            continue
        if rkey not in last_random:
            last_random[rkey]=randomhand
        elif randomhand is not None:
            previous=last_random[rkey]
            if previous is None:
                last_random[rkey]=randomhand
            elif previous!=randomhand:
                out.append(_report(row,expected,'MISMATCH_RANDOM','randomhand changed within one hand'))
                continue
        fa=row['observed_formula_action']
        ra=row['observed_formula_raise_to_bb']
        final=row['observed_final_action']
        finalsize=row['observed_final_raise_to_bb']
        for action in (fa,final):
            if action and action not in ACTIONS:
                raise EvidenceError('Unknown action in observed result')
        if fa and (fa!=expected[0] or not _sizing_equal(ra,expected[1])):
            out.append(_report(row,expected,'MISMATCH_FORMULA','OpenHoldem formula disagrees with OPPL interpreter'))
            continue
        if final and (final!=expected[0] or not _sizing_equal(finalsize,expected[1])):
            out.append(_report(row,expected,'MISMATCH_FINAL','Final OpenHoldem action or RaiseTo differs'))
            continue
        if source=='SYNTHETIC':
            out.append(_report(row,expected,'STATIC_ONLY','Synthetic data cannot prove OpenHoldem behavior'))
            continue
        if not row['openholdem_version'].strip():
            out.append(_report(row,expected,'EVIDENCE_INCOMPLETE','Target OpenHoldem version missing'))
            continue
        if randomhand is None:
            out.append(_report(row,expected,'EVIDENCE_INCOMPLETE','OpenHoldem randomhand not recorded'))
            continue
        if not fa or not final:
            out.append(_report(row,expected,'EVIDENCE_INCOMPLETE','Both formula and final actions must be captured'))
            continue
        ok,detail=_evidence_ok(row,evidence_root)
        if not ok:
            out.append(_report(row,expected,'EVIDENCE_INCOMPLETE',detail))
            continue
        out.append(_report(row,expected,'READY_FOR_MANUAL_REVIEW',detail+'; not runtime approval'))
    return out


def read_csv(path:Path)->list[dict[str,str]]:
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if tuple(reader.fieldnames or ())!=SCHEMA:
            raise EvidenceError('Replay CSV columns differ from pinned schema')
        rows=list(reader)
    return rows


def export_report(rows:list[dict[str,str]],path:Path)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=REPORT_FIELDS,lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main()->int:
    parser=argparse.ArgumentParser(description='PORT-3 evidence check, not runtime OH approval')
    parser.add_argument('--input',type=Path,default=HERE/'SYNTHETIC_REPLAY_INPUT.csv')
    parser.add_argument('--output',type=Path,default=HERE/'SYNTHETIC_REPLAY_REPORT.csv')
    parser.add_argument('--evidence-root',type=Path,default=HERE/'private_evidence_not_tracked')
    args=parser.parse_args()
    result=audit_rows(read_csv(args.input),args.evidence_root)
    export_report(result,args.output)
    counts={}
    for row in result:counts[row['verdict']]=counts.get(row['verdict'],0)+1
    print(f'PORT-3 review report: {counts}. NO OH runtime approval issued.')
    return 0 if not any(row['verdict'].startswith('MISMATCH') for row in result) else 2

if __name__=='__main__':sys.exit(main())
