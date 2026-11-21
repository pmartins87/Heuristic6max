"""OH-SRC1: independent *static* OpenPPL/source semantics risk ledger.

Scans the actual integrated OpenPPL rules. Does NOT evaluate poker hands,
alter an action, infer live installed-build behaviour or approve runtime.
Reference facts come from OpenHoldem OpenPPL manuals + C++ source review.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BASELINE=ROOT/'benchmarks/r10d_floor/CURRENT_GAP_REPORT.json'
REPORT=HERE/'SOURCE_FINDINGS.json'
PRE=ROOT/'portability/iso_defense_v1/defense_preflop_capture.oppl'
MAIN_HEADINGS=('##f$preflop##','##f$flop##','##f$turn##','##f$river##')
WHEN=re.compile(r'^\s*WHEN\b')
POT_EXACT=re.compile(r'\bPotSize\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)\b')
CALL_EXACT=re.compile(r'\bAmountToCall\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)\b')
RESEARCH_CONTRACT='OH_SOURCE_ONLY_NOT_OPENHOLDEM_RUNTIME_PARITY'


class SourceAuditError(ValueError):
    pass


def active_source()->Path:
    report=json.loads(BASELINE.read_text(encoding='utf-8'))
    path=report.get('heuristic_active_file')
    if not isinstance(path,str):raise SourceAuditError('no active formula in R10d benchmark')
    full=(ROOT/path).resolve()
    if not full.is_relative_to(ROOT.resolve()) or full.suffix!='.oppl' or not full.is_file():
        raise SourceAuditError('invalid active OpenPPL source path')
    return full


def action_sections(source:str)->dict[str,str]:
    for head in MAIN_HEADINGS:
        if source.count(head)!=1:raise SourceAuditError('missing or duplicate '+head)
    out={}
    positions=[source.index(h) for h in MAIN_HEADINGS]
    if positions!=sorted(positions):raise SourceAuditError('main action callbacks out of order')
    for i,head in enumerate(MAIN_HEADINGS):
        end=positions[i+1] if i+1<len(positions) else len(source)
        out[head]=source[positions[i]+len(head):end]
    return out


def exact_counts(lines:list[str])->dict:
    result={'total_when':0,'pot_exact_rules':0,
            'amount_to_call_exact_zero':0,'amount_to_call_exact_nonzero':0,
            'still_to_act_rules':0,'first_raiser_position_rules':0}
    pot_vals=Counter()
    for line in lines:
        if not WHEN.match(line):continue
        result['total_when']+=1
        p=POT_EXACT.findall(line)
        if p:
            result['pot_exact_rules']+=1
            pot_vals.update(p)
        calls=CALL_EXACT.findall(line)
        if any(float(v)==0 for v in calls):
            result['amount_to_call_exact_zero']+=1
        if any(float(v)!=0 for v in calls):
            result['amount_to_call_exact_nonzero']+=1
        if re.search(r'\bStillToAct\s*(?:=|<|>)',line):
            result['still_to_act_rules']+=1
        if re.search(r'\bFirstRaiserPosition\s*(?:=|<|>)',line):
            result['first_raiser_position_rules']+=1
    return result|{'pot_exact_values':dict(sorted(pot_vals.items(),key=lambda e:float(e[0])))}


def validate_iso_defense_preflop(raw:str)->dict:
    lines=[x for x in raw.splitlines() if WHEN.match(x)]
    if len(lines)!=10:raise SourceAuditError('isodef 2 x 5 source contracts changed')
    summary={}
    for i,name in ((0,'BTN'),(5,'BB')):
        group=lines[i:i+5]
        if len(group)!=5:raise SourceAuditError('incomplete defense group')
        if not all(('Raises = 1' in x and 'Calls = 1' in x and
                    'PotSize = 7' in x and 'NOT StackUnknown' in x)
                   for x in group):
            raise SourceAuditError('source guard disappeared: '+name)
        if name=='BTN':
            required=('InButton','NOT InBigBlind','StillToAct = 2',
                      'FirstRaiserPosition = 3','LastRaiserPosition = 3',
                      'AmountToCall = 4.5')
        else:
            required=('InBigBlind','NOT InButton','StillToAct = 0',
                      'FirstRaiserPosition = 2','LastRaiserPosition = 2',
                      'AmountToCall = 3.5')
        if not all(all(needle in x for needle in required) for x in group):
            raise SourceAuditError('seat/aggressor/pricing guard changed: '+name)
        head=re.match(r'^WHEN \((.*?)\) Set user_H6_DEF_[A-Z0-9]+$',group[0])
        raise_line=re.match(r'^WHEN \((.*?)\) RaiseTo (.*?) FORCE$',group[1])
        call_set=re.match(r'^WHEN \((.*?)\) Set user_H6_DEF_[A-Z0-9]+$',group[2])
        call_line=re.match(r'^WHEN \((.*?)\) Call FORCE$',group[3])
        fold_line=re.match(r'^WHEN \((.*?)\) Fold FORCE$',group[4])
        if not all((head,raise_line,call_set,call_line,fold_line)):
            raise SourceAuditError('unexpected guard/action shape: '+name)
        if head[1]!=raise_line[1] or call_set[1]!=call_line[1]:
            raise SourceAuditError('Set intention has no identical real action guard')
        if not head[1].endswith(' AND listH6DEF3BET') or not call_set[1].endswith(' AND listH6DEFCALL'+name):
            raise SourceAuditError('3bet vs call source range order changed')
        if fold_line[1]!=head[1].removesuffix(' AND listH6DEF3BET') or fold_line[1]!=call_set[1].removesuffix(' AND listH6DEFCALL'+name):
            raise SourceAuditError('fold fallback broadened or changed')
        summary[name]={'actions':5,'set_then_raise_guard_identical':True,
                       'set_then_call_guard_identical':True,
                       'fallback_guarded':True,
                       'sample_size_is_fixed':True}
    return summary


def produce()->dict:
    path=active_source()
    blob=path.read_bytes()
    source=blob.decode('utf-8')
    sections=action_sections(source)
    metrics=exact_counts(source.splitlines())
    modules=validate_iso_defense_preflop(PRE.read_text(encoding='utf-8'))
    return {
        'contract':RESEARCH_CONTRACT,
        'source_path':str(path.relative_to(ROOT)),
        'source_sha256':sha256(blob).hexdigest(),
        'source_bytes':len(blob),
        'main_callback_count':len(sections),
        'metrics':metrics,
        'iso_defense_contracts':modules,
        'source_facts':{
            'user_flags_reset':'CSymbolEngineOpenPPLUserVariables::UpdateOnHandreset clears _user_variables; depends on reliable handreset triggering',
            'set_is_intent':'OpenPPL manual: Set user variable continues evaluation until first matching action',
            'calls_not_raw_limper_count':'OpenPPL Library: Calls delegates to CallsBeforeOurFirstAction / nopponentscalling, else memory plus CallsSinceLastPlay',
            'first_orbit_stilltoact':'OpenPPL Library: StillToAct uses BotsActionsOnThisRoundIncludingChecks; later orbits emit hint/0',
            'preflop_raises_stateful':'OpenPPL Library: NumberOfRaisesBeforeFlop returns Raises preflop else me_re_MemRaisesBeforeFlop',
            'pot_equals_float_risk':'OpenPPL manual warns on comparisons of real-valued amounts; strict = can reject nearby numeric states',
            'fallback_not_failclosed':'OpenPPL manual/OpenHoldem: no-match can enter a default/technical fallback rather than Python None'
        },
        'finding_ids':['F1_POT_EXACT_MATCH','F2_CALLS_STATEFUL','F3_STILLTOACT_FIRST_ORBIT',
                       'F4_USER_RESET_ENGINE','F5_SET_THEN_ACTION',
                       'F6_FALLBACK_ENGINEDRIVEN'],
        'automatic_runtime_approval':False,
        'strategy_changed':False,
        'recommended_next_gate':'audit each distinct PotSize equality domain before any tolerance rewrite; no broad global replacement'
    }


def rendered()->str:
    return json.dumps(produce(),indent=2,sort_keys=True,ensure_ascii=False)+'\n'


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description='OpenPPL source-risk ledger; no runtime approval')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args(argv)
    try:
        fresh=rendered()
        if args.check:
            if REPORT.read_text(encoding='utf-8')!=fresh:
                raise SourceAuditError('SOURCE_FINDINGS.json stale; regenerate and review')
            print('OH-SRC1 report matches active source; this is NOT executable OH proof')
        else:
            REPORT.write_text(fresh,encoding='utf-8',newline='\n')
            print('OH-SRC1 updated from source; no OpenPPL rules modified')
    except (SourceAuditError,OSError,ValueError) as exc:
        print('OH-SRC1 FAILED:',exc,file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
