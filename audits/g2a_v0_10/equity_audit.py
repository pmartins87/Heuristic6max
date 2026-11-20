"""HJ->CO 3bet: physical-card preflop showdown-equity audit, not a poker solver.

External optional source: user-supplied PreFlopEquities.zip / PreFlopEquities.txt.
Data provenance and licensing UNKNOWN; DO NOT commit the input source.

When no external dataset is supplied, --mc provides an independently runnable
stdlib-only Monte Carlo equity *estimate*. Neither mode models realization,
postflop EV, rake distribution, cold actions or a GTO solution.
"""
from __future__ import annotations

import argparse
from array import array
import csv
import hashlib
import itertools
import math
from pathlib import Path
import random
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'gto6_heuristic_v0_6_1'
V09 = ROOT / 'audits' / 'g2a_v0_9'
if not BASE.is_dir() or not V09.is_dir():
    raise RuntimeError('GitHub snapshot v0.6.1 and audit v0.9 required')
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(V09))
from vs3_blocker_audit_v0_6 import BY_CLASS, COMBOS, hand_class, RANKS
from vs_3bet_reference import RANGES as HERO
from vs_open_reference import RANGES as OPPONENT
import hj_co_frontier as front

PAIR = ('HJ', 'CO')
V3 = OPPONENT[PAIR]
H = HERO[PAIR]
CANDIDATES = front.CANDIDATES
SUITS='cdhs'
CARDS={r+s: 4*i+j for i,r in enumerate(RANKS) for j,s in enumerate(SUITS)}
EXPECTED_ORDERED_PHYSICAL_MATCHUPS = 1326*1225
REFERENCE_ZIP_SHA256 = '52a0a87174b0d7cabd5b16fe43387b0807a6abd036e5a61c1aafbc008ecf50c2'
REFERENCE_INNER_SHA256 = '9dd539e2720010684d0006981207489e4f753b1d628f7e0443003b2c7f3e6c9f'

# Combinations indexed as pairs of canonical ascending integers.
COMBO_INDEX = {combo:i for i,combo in enumerate(COMBOS)}
COMBO_CLASS = tuple(hand_class(x) for x in COMBOS)
V3_WEIGHTS = tuple(V3[c].threebet for c in COMBO_CLASS)


def parse_equity_line(raw: bytes):
    """Parse a physical matchup: 'AcAd:AhAs=50.00'. Equity in [0,1]."""
    line = raw.strip()
    if len(line)<14 or len(line)>16 or line[4:5]!=b':' or line[9:10]!=b'=':
        raise ValueError(f'bad equity row format: {line[:50]!r}')
    try:
        c1,c2,c3,c4=(CARDS[line[i:i+2].decode('ascii')] for i in (0,2,5,7))
        value = float(line[10:].decode('ascii')) / 100
    except (KeyError, UnicodeError, ValueError) as exc:
        raise ValueError(f'bad cards or number: {line[:50]!r}') from exc
    if len({c1,c2,c3,c4})!=4 or not math.isfinite(value) or not 0<=value<=1:
        raise ValueError(f'overlap or invalid probability: {line[:50]!r}')
    return tuple(sorted((c1,c2))), tuple(sorted((c3,c4))), value


def accumulate_lines(lines):
    """All 1,624,350 ordered disjoint matchups, each once. Pure stdlib."""
    n=len(COMBOS)
    seen=bytearray(n*n)
    cents=array("H", [0])*(n*n)  # two-decimal % representation
    total=[0.] * 169
    equity=[0.] * 169
    classes=sorted(H)
    cls_to_id={v:i for i,v in enumerate(classes)}
    count=0
    hasher=hashlib.sha256()
    for raw in lines:
        hasher.update(raw)
        h,v,e=parse_equity_line(raw)
        hi=COMBO_INDEX[h];vi=COMBO_INDEX[v]
        idx=hi*n+vi
        if seen[idx]: raise ValueError(f'duplicate ordered matchup: {h}, {v}')
        seen[idx]=1
        cents[idx]=round(e*10000)
        count+=1
        weight=V3_WEIGHTS[vi]
        if weight:
            i=cls_to_id[COMBO_CLASS[hi]]
            total[i]+=weight
            equity[i]+=weight*e
    if count != EXPECTED_ORDERED_PHYSICAL_MATCHUPS:
        raise ValueError(f'incomplete source: {count} != {EXPECTED_ORDERED_PHYSICAL_MATCHUPS}')
    if any(not seen[a*n+b] or abs(cents[a*n+b]+cents[b*n+a]-10000)>2
           for a in range(n) for b in range(a+1,n) if seen[a*n+b] or seen[b*n+a]):
        raise ValueError('Missing reverse matchup or inconsistent complementary equity')
    result={cls: (equity[i]/total[i] if total[i]>0 else None, total[i])
            for i,cls in enumerate(classes)}
    if any(v[0] is None for v in result.values()):
        raise ValueError('Empty villain 3bet model against some class')
    return result, hasher.hexdigest(), count


def load_reference(path: Path):
    if path.suffix.lower()=='.zip':
        if hashlib.sha256(path.read_bytes()).hexdigest()!=REFERENCE_ZIP_SHA256:
            raise ValueError('External zip SHA-256 mismatch')
        with zipfile.ZipFile(path) as z, z.open('PreFlopEquities.txt') as f:
            result,sha,n=accumulate_lines(f)
    else:
        with path.open('rb') as f:
            result,sha,n=accumulate_lines(f)
    if sha!=REFERENCE_INNER_SHA256:
        raise ValueError('External PreFlopEquities.txt SHA-256 mismatch')
    return result,n


def straight_high(mask: int):
    # Ranks 2...A stored in bits 0..12. Wheel A2345 handled separately.
    for i in range(12,3,-1):
        if mask & (31 << (i-4)) == (31 << (i-4)):
            return i+2
    if (mask & (1<<12)) and mask & 15 == 15:
        return 5
    return 0


def score7(cards):
    """Standard exact *showdown hand ranking* for seven known cards."""
    counts=[0]*13
    suit_masks=[0]*4
    all_mask=0
    for c in cards:
        r=c//4;s=c%4
        counts[r]+=1
        suit_masks[s]|=1<<r
        all_mask|=1<<r
    for suit_mask in suit_masks:
        if suit_mask.bit_count()>=5:
            sf=straight_high(suit_mask)
            if sf:return (8,sf)
    quads=[r for r in range(12,-1,-1) if counts[r]==4]
    if quads:
        k=max(r for r in range(13) if r!=quads[0] and counts[r]>0)
        return (7,quads[0],k)
    trips=[r for r in range(12,-1,-1) if counts[r]>=3]
    if trips:
        pairs=[r for r in range(12,-1,-1) if r!=trips[0] and counts[r]>=2]
        if pairs:return (6,trips[0],pairs[0])
    for suit_mask in suit_masks:
        if suit_mask.bit_count()>=5:
            return (5,)+tuple(r for r in range(12,-1,-1) if suit_mask>>r & 1)[:5]
    st=straight_high(all_mask)
    if st:return (4,st)
    if trips:
        k=tuple(r for r in range(12,-1,-1) if counts[r] and r!=trips[0])[:2]
        return (3,trips[0],*k)
    pairs=[r for r in range(12,-1,-1) if counts[r]>=2]
    if len(pairs)>=2:
        k=max(r for r in range(13) if counts[r] and r not in pairs[:2])
        return (2,pairs[0],pairs[1],k)
    if pairs:
        k=tuple(r for r in range(12,-1,-1) if counts[r] and r!=pairs[0])[:3]
        return (1,pairs[0],*k)
    return (0,)+tuple(r for r in range(12,-1,-1) if counts[r])[:5]


def mc_class(cls, n=2000, seed=20261120):
    """Independent reproducible estimate, uniform hero combos and weighted villain 3bet.

    Villain selected conditional on hero two cards via its exact physical combo
    frequencies. Sampling without replacement; ties count half.
    """
    if n<=0:raise ValueError('samples must be positive')
    rng=random.Random(f'{seed}|HJ|CO|{cls}')
    hero_combos=BY_CLASS[cls]
    options={}
    hero_mass=[]
    for h in hero_combos:
        valid=[(v,w) for v,w in zip(COMBOS,V3_WEIGHTS)
               if w and h[0] not in v and h[1] not in v]
        options[h]=([x[0] for x in valid],[x[1] for x in valid])
        hero_mass.append(sum(options[h][1]))
    value=0.
    for _ in range(n):
        h=rng.choices(hero_combos,weights=hero_mass,k=1)[0]
        vs,ws=options[h]
        v=rng.choices(vs,weights=ws,k=1)[0]
        excluded=set((*h,*v))
        board=rng.sample([c for c in range(52) if c not in excluded],5)
        sc1=score7((*h,*board));sc2=score7((*v,*board))
        value += (sc1>sc2)+(0.5 if sc1==sc2 else 0.)
    e=value/n
    se=math.sqrt(max(0.,e*(1-e))/n)  # conservative Bernoulli upper bound
    return e,se


def rows_from_reference(result):
    out=[]
    for cls in sorted(result):
        equity,weight=result[cls]
        row=H[cls]
        raw=equity
        c0=front.call_break_even(8,0,0,1)['RequiredRawEquity_pct']/100
        c5=front.call_break_even(8,.05,3,.75)['RequiredRawEquity_pct']/100
        out.append({
            'Hand':cls, 'PhysicalCombos':len(BY_CLASS[cls]),
            'HJ_RFI_pct':100*row.open_probability,
            'VS3_Fold_pct':100*row.fold,'VS3_Call_pct':100*row.call,
            'VS3_4bet_pct':100*row.fourbet,
            'ModelCO3betWeightedMatchups':round(weight,6),
            'RawPreflopShowdownEquity_pct':round(100*raw,6),
            'ToyCallFloorNoRakeFullRealization_pct':round(100*c0,6),
            'ToyCallFloor5pctCap3BB_75pctRealization_pct':round(100*c5,6),
            'ToyRawEquityAboveFullRealizationFloor':raw>=c0,
            'ToyRawEquityAbove75pctRealizationFloor':raw>=c5,
            'Interpretation':'NO_EQUITY_REALIZATION_OR_EV_OR_AUTOMATIC_CALL',
        })
    return out


def export_reference(zip_path: Path, output:Path):
    data,n=load_reference(zip_path)
    rows=rows_from_reference(data)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return rows,n


def export_mc(output:Path, classes, samples=2000):
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(('Hand','Samples','MCShowdownEquity_pct',
                  'ApproxUpperBoundSE_pp','Model','Caveat'))
        for cls in classes:
            e,se=mc_class(cls,samples)
            w.writerow((cls,samples,round(e*100,4),round(se*100,4),
                        'VS_OPEN_HJ_CO_3BET','PREFLOP_ONLY_NOT_REALIZED_EV'))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reference-zip',type=Path)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'HJ_CO_EQUITY_169_REFERENCE_v0_10.csv')
    parser.add_argument('--mc',action='store_true')
    parser.add_argument('--samples',type=int,default=2000)
    parser.add_argument('--classes',nargs='*',default=list(CANDIDATES))
    args=parser.parse_args()
    if args.reference_zip:
        rows,n=export_reference(args.reference_zip,args.output)
        print(n,'matchups; equity rows:',len(rows))
        for r in rows:
            if r['Hand'] in CANDIDATES:
                print(r['Hand'],r['RawPreflopShowdownEquity_pct'])
    elif args.mc:
        export_mc(args.output,args.classes,args.samples)
        print('MC estimate:',args.output)
    else: parser.error('provide --reference-zip or --mc (no private table in the public repo)')
