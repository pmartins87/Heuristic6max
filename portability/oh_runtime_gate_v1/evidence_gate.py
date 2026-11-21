"""OH-G1G6-1: OFFLINE evidence preflight, not an OpenHoldem runtime emulator.

Only archived evidence can be checked. This code never opens an app, chooses a
poker action, uploads evidence or changes the R10d release/portability gates.
A successful consistency preflight is not proof that OpenHoldem actually acted.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MATRIX=HERE/'CASE_MATRIX.json'
PROTOCOL='OH-G1G6-1'
SHA=re.compile(r'^[a-f0-9]{64}$')
LINE=re.compile(
    r'^\s*(?:(?P<timestamp>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\s+-\s+)?'
    r'(?P<kind>Best action|Action taken):\s*(?P<action>[^\r\n]+?)\s*$',re.I|re.M)
DEBUG=re.compile(r'^\s*(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>[^\r\n]+?)\s*$',re.M)
ARTIFACT_EXT={
    'pre_html':'.html','pre_bmp':'.bmp',
    'post_html':'.html','post_bmp':'.bmp',
    'debug_txt':'.txt','debug_png':'.png','decision_log':'.log'}
CAPTURE_MODES={'SYNTHETIC','OH_REPLAY','OH_MANUALMODE'}
MAIN_KEYS={'protocol','capture_mode','offline_attested','connected_live',
           'openholdem_version','openholdem_exe_sha256','tablemap_sha256',
           'loaded_oppl_sha256','cases'}
CASE_KEYS={'case_id','session_id','hand_id','eval_index','street','symbols',
           'reported_best_action','reported_action_taken','artifacts'}
MAX_ARTIFACT=50_000_000

class EvidenceError(ValueError):
    pass


def catalog()->tuple[dict,dict[str,dict]]:
    cfg=json.loads(MATRIX.read_text(encoding='utf-8'))
    if set(cfg)!={'protocol','source','catalog'} or cfg['protocol']!=PROTOCOL:
        raise EvidenceError('catalog schema mismatch')
    source=(ROOT/cfg['source']).resolve()
    if not source.is_relative_to(ROOT.resolve()) or not source.is_file():
        raise EvidenceError('catalog source unavailable')
    text=source.read_text(encoding='utf-8')
    cases={}
    for entry in cfg['catalog']:
        key=entry['case_id']
        if key in cases:raise EvidenceError('duplicate catalog id')
        if any(x not in text for x in entry['source_markers']):
            raise EvidenceError('source no longer contains required marker: '+key)
        if not entry['required_symbols']:raise EvidenceError('empty symbol checklist')
        cases[key]=entry
    return cfg,cases


def source_digest(cfg:dict)->str:
    src=ROOT/cfg['source']
    return hashlib.sha256(src.read_bytes()).hexdigest()


def require_shape(data,expected,context):
    if not isinstance(data,dict) or set(data)!=expected:
        raise EvidenceError(context+': keys missing or unexpected')


def safe_read(root:Path,record:dict,ext:str)->tuple[bytes|None,str]:
    if not isinstance(record,dict) or set(record)!={'path','sha256'}:
        return None,'missing artifact metadata'
    name,digest=record['path'],record['sha256']
    if not isinstance(name,str) or not name or not isinstance(digest,str) or not SHA.fullmatch(digest):
        return None,'missing artifact path or digest'
    p=Path(name)
    if p.is_absolute() or any(x in ('.','..') for x in p.parts) or '\\' in name or ':' in name:
        return None,'unsafe evidence path'
    if p.suffix.lower()!=ext:return None,'unexpected file extension'
    base=root.resolve()
    real=(base/p).resolve()
    if not real.is_relative_to(base):
        return None,'evidence path escaped root'
    if not real.is_file():return None,'missing evidence file'
    if not 0<real.stat().st_size<=MAX_ARTIFACT:
        return None,'empty or oversize evidence'
    hasher=hashlib.sha256()
    with real.open('rb') as src:
        for block in iter(lambda:src.read(1024*1024),b''):
            hasher.update(block)
    if hasher.hexdigest()!=digest:return None,'evidence SHA256 mismatch'
    # File signatures detect mistaken exports, not authenticity.
    body=real.read_bytes()
    if ext=='.bmp' and not body.startswith(b'BM'):
        return None,'invalid BMP signature'
    if ext=='.png' and not body.startswith(b'\\x89PNG\\r\\n\\x1a\\n'):
        return None,'invalid PNG signature'
    if ext=='.html' and b'<html' not in body[:4096].lower() and b'<!doctype html' not in body[:4096].lower():
        return None,'HTML replay does not contain HTML document tag'
    return body,'sha256 and file signature match (authenticity unverified)'


def _equal_text(a:str,b:str)->bool:
    try:
        x,y=Decimal(a),Decimal(b)
        if x.is_finite() and y.is_finite():return x==y
    except (InvalidOperation,TypeError,ValueError):pass
    return str(a).strip().lower()==str(b).strip().lower()


def raw_log_actions(text:str)->tuple[dict[str,str]|None,str]:
    items=list(LINE.finditer(text))
    if len(items)!=2:
        return None,'must contain exactly one Best action and one Action taken'
    actions={}
    stamps=[]
    for item in items:
        name=item['kind'].lower()
        if name in actions:
            return None,'duplicate action type in log excerpt'
        actions[name]=item['action'].strip()
        stamps.append(item['timestamp'])
    if set(actions)!={'best action','action taken'}:
        return None,'best/taken pair incomplete'
    if not stamps[0] or not stamps[1] or stamps[0]!=stamps[1]:
        return None,'best/taken lack same logged timestamp'
    return actions,'one correlated timestamped OH Basic Info action pair'


def symbol_text(text:str,required:list[str],claimed:dict)->tuple[str,str]:
    data={}
    for m in DEBUG.finditer(text):
        if m['symbol'] in data and not _equal_text(data[m['symbol']],m['value']):
            return 'SYMBOL_CONFLICT','duplicate inconsistent debug symbol: '+m['symbol']
        data[m['symbol']]=m['value']
    for key in required:
        if key not in claimed or not isinstance(claimed[key],str) or not claimed[key].strip():
            return 'INCOMPLETE','symbol observation missing: '+key
        if claimed[key].strip().lower() in {'unknown','nan','none','?','undefined'}:
            return 'INCOMPLETE','symbol value unobserved: '+key
        if key not in data:
            return 'INCOMPLETE','debug export lacks measured symbol: '+key
        if not _equal_text(data[key],claimed[key]):
            return 'SYMBOL_CONFLICT','debug mismatch for symbol: '+key
    return 'OK','symbol transcription matches debug text (not authenticated)'


def audit(data:dict,evidence_root:Path)->dict:
    require_shape(data,MAIN_KEYS,'bundle')
    cfg,cases=catalog()
    if data['protocol']!=PROTOCOL:raise EvidenceError('protocol mismatch')
    if data['capture_mode'] not in CAPTURE_MODES:raise EvidenceError('capture mode invalid')
    if type(data['offline_attested']) is not bool or type(data['connected_live']) is not bool:
        raise EvidenceError('offline/live indicators must be booleans')
    if not isinstance(data['cases'],list) or not data['cases']:
        raise EvidenceError('empty cases')
    if not evidence_root.is_dir():raise EvidenceError('evidence root directory absent')
    actual_sha=source_digest(cfg)
    result=[]
    seen=set()
    per_hand_last={}
    per_hand_random={}
    for case in data['cases']:
        require_shape(case,CASE_KEYS,'case')
        key=case['case_id']
        if key not in cases:raise EvidenceError('unknown case id: '+str(key))
        item=cases[key]
        if case['street']!=item['street']:
            raise EvidenceError('case street not in catalog: '+key)
        if not isinstance(case['session_id'],str) or not case['session_id'].strip():
            raise EvidenceError('session_id required')
        if not isinstance(case['hand_id'],str) or not case['hand_id'].strip():
            raise EvidenceError('hand_id required')
        if type(case['eval_index']) is not int or case['eval_index']<0:
            raise EvidenceError('eval_index must be nonnegative integer')
        if not isinstance(case['symbols'],dict):
            raise EvidenceError('symbols object required')
        if not isinstance(case['artifacts'],dict) or set(case['artifacts'])!=set(ARTIFACT_EXT):
            raise EvidenceError('all seven artifact metadata keys required')
        handle=(case['session_id'],case['hand_id'])
        event=handle+(case['eval_index'],)
        if event in seen:raise EvidenceError('duplicate decision evaluation')
        seen.add(event)
        if handle in per_hand_last and case['eval_index']<=per_hand_last[handle]:
            raise EvidenceError('non-monotonic decision index')
        per_hand_last[handle]=case['eval_index']
        rnd=case['symbols'].get('randomhand')
        if rnd is not None:
            if not isinstance(rnd,str):raise EvidenceError('randomhand must be string')
            try:v=Decimal(rnd)
            except InvalidOperation as e:raise EvidenceError('invalid randomhand') from e
            if not v.is_finite() or not 0<=v<1:raise EvidenceError('invalid randomhand domain')
            if handle in per_hand_random and v!=per_hand_random[handle]:
                result.append({'case_id':key,'verdict':'MISMATCH_RANDOM',
                               'reason':'randomhand changed within same session/hand'})
                continue
            per_hand_random[handle]=v
        report={'case_id':key,'verdict':'INCOMPLETE','reason':'no offline evidence'}
        if data['connected_live'] or not data['offline_attested']:
            report.update(verdict='BLOCKED_LIVE_CONTEXT',
                          reason='offline-only attestation missing or live connection reported')
        elif data['loaded_oppl_sha256']!=actual_sha:
            report.update(verdict='SOURCE_MISMATCH',reason='loaded profile digest differs from integrated source')
        elif data['capture_mode']=='SYNTHETIC':
            report.update(verdict='STATIC_ONLY',reason='synthetic case; not OpenHoldem runtime evidence')
        elif any(not isinstance(data[k],str) or
                 (k.endswith('_sha256') and not SHA.fullmatch(data[k]))
                 for k in ('openholdem_version','openholdem_exe_sha256','tablemap_sha256')):
            report.update(reason='runtime executable/version/tablemap identity missing')
        elif data['capture_mode']=='OH_MANUALMODE':
            # ManualMode can test symbols, not demonstrate autoplayer-history
            # counters after an OH action. Never turn it into a runtime pass.
            report.update(verdict='OBSERVATION_ONLY',reason='ManualMode differs from autoplayer history')
        else:
            collected={}
            for label,ext in ARTIFACT_EXT.items():
                body,reason=safe_read(evidence_root,case['artifacts'][label],ext)
                if body is None:
                    status='EVIDENCE_CONFLICT' if any(w in reason for w in
                          ('unsafe','escaped','SHA256 mismatch','extension')) else 'INCOMPLETE'
                    report.update(verdict=status,reason=label+': '+reason)
                    break
                collected[label]=body
            else:
                def stem(label):
                    return Path(case['artifacts'][label]['path']).with_suffix('')
                if stem('pre_html')!=stem('pre_bmp') or stem('post_html')!=stem('post_bmp'):
                    report.update(verdict='EVIDENCE_CONFLICT',reason='HTML/BMP frame basename mismatch')
                elif stem('pre_html')==stem('post_html'):
                    report.update(verdict='INCOMPLETE',reason='same replay frame used for pre/post action')
                else:
                    status,reason=symbol_text(collected['debug_txt'].decode('utf-8',errors='replace'),
                                              item['required_symbols'],case['symbols'])
                    if status!='OK':
                        report.update(verdict=status,reason=reason)
                    else:
                        actions,why=raw_log_actions(collected['decision_log'].decode('utf-8',errors='replace'))
                        if actions is None:
                            report.update(reason='OH log: '+why)
                        elif not isinstance(case['reported_best_action'],str) or not isinstance(case['reported_action_taken'],str):
                            report.update(verdict='EVIDENCE_CONFLICT',reason='action transcription must be strings')
                        elif not _equal_text(actions['best action'],case['reported_best_action']) or not _equal_text(actions['action taken'],case['reported_action_taken']):
                            report.update(verdict='EVIDENCE_CONFLICT',reason='Basic Info best/taken differs from transcribed action')
                        elif not _equal_text(actions['best action'],actions['action taken']):
                            report.update(verdict='FALLBACK_OBSERVED',reason='OH Basic Info best action differs from action taken')
                        else:
                            report.update(verdict='READY_FOR_HUMAN_REVIEW',
                                          reason='files/hashes/symbols/action pair internally consistent; provenance, legal sizing and final post-state NOT verified')
        result.append(report)
    counter=Counter(x['verdict'] for x in result)
    return {'protocol':PROTOCOL,'profile_source':cfg['source'],
            'active_profile_sha256':actual_sha,
            'case_catalog_size':len(cases),'case_ids_observed':sorted({x['case_id'] for x in result}),
            'catalog_cases_missing':sorted(set(cases)-{x['case_id'] for x in result}),
            'results':result,'verdict_counts':dict(sorted(counter.items())),
            'runtime_approved':False,'G1':'OPEN','G6':'PENDING',
            'R10d_release':'BLOCKED',
            'note':'This is a private evidence preflight. Even READY_FOR_HUMAN_REVIEW is NOT proof of OH execution.'}


def main(argv=None):
    ap=argparse.ArgumentParser(description='Offline OH evidence check only; never performs actions')
    ap.add_argument('--bundle',type=Path,required=True)
    ap.add_argument('--evidence-root',type=Path,required=True)
    ap.add_argument('--out',type=Path)
    args=ap.parse_args(argv)
    try:
        bundle=json.loads(args.bundle.read_text(encoding='utf-8'))
        report=audit(bundle,args.evidence_root)
    except (EvidenceError,OSError,ValueError) as e:
        print('INVALID_EVIDENCE_BUNDLE:',e,file=sys.stderr)
        return 2
    output=json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
    if args.out:
        args.out.write_text(output,encoding='utf-8')
    else:
        print(output,end='')
    return 0


if __name__=='__main__':raise SystemExit(main())
