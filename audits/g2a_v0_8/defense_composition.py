"""G2-a v0.8: audit RFI->VS_3BET continuation by physical combos, class and family.

Diagnostic only; does not change any strategy. Cold-action calculations are
counterfactual upper/lower-model sensitivities, NOT gameplay EV or GTO.
Requires repository root with audits/g2a_v0_7 and gto6_heuristic_v0_6_1.
"""
from __future__ import annotations
import csv
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
V07 = ROOT / 'audits' / 'g2a_v0_7'
BASE = ROOT / 'gto6_heuristic_v0_6_1'
if not BASE.is_dir() or not (V07 / 'pressure_audit.py').is_file():
    raise RuntimeError('v0.6.1 ou v0.7 ausente; verificar checkout GitHub')
sys.path.insert(0, str(V07))
import pressure_audit as p  # noqa: E402
from vs3_blocker_audit_v0_6 import BY_CLASS, villain_mass_by_hero_combo  # noqa: E402

POSITIONS = ('LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB')


def hand_family(hand: str) -> str:
    if len(hand) == 2:
        rank = hand[0]
        if rank in 'AKQ': return 'PAIR_PREMIUM_QQ_PLUS'
        if rank in 'JT987': return 'PAIR_MID_77_JJ'
        return 'PAIR_LOW_22_66'
    if hand.endswith('s'):
        if hand.startswith('A'): return 'SUITED_AX'
        if hand[0] in 'KQJ' and hand[1] in 'KQJT': return 'SUITED_BROADWAY'
        return 'SUITED_OTHER'
    if hand.startswith('A'): return 'OFFSUIT_AX'
    if hand[0] in 'KQJ' and hand[1] in 'KQJT': return 'OFFSUIT_BROADWAY'
    return 'OFFSUIT_OTHER'


def exact_hero_class_weights(opener: str, threebettor: str):
    """Joint prior RFI Hero + 3bet villain with card removal; class posterior."""
    rows = p.HERO[(opener, threebettor)]
    available_mass, villain_total = villain_mass_by_hero_combo(opener, threebettor)
    unnormalized = {
        h: rows[h].open_probability * sum(available_mass[c] for c in BY_CLASS[h])
        for h in rows
    }
    denom = sum(unnormalized.values())
    if not denom > 0: raise ValueError('Joint support empty')
    norm = {h: v / denom for h, v in unnormalized.items()}
    return norm


def class_rows(opener: str, threebettor: str):
    weights = exact_hero_class_weights(opener, threebettor)
    rows = p.HERO[(opener, threebettor)]
    # Quantize only the sorting key: tiny FP roundoff differs between Python builds.
    # Preserve full-precision weights for all mass and probability calculations.
    for h, w in sorted(weights.items(), key=lambda x: (-round(x[1], 12), x[0])):
        if not w: continue
        r = rows[h]
        yield {
            'Opener': opener, 'Threebettor': threebettor, 'HeroHand': h,
            'Family': hand_family(h), 'PhysicalCombos': len(BY_CLASS[h]),
            'RFIProbability_pct': 100*r.open_probability,
            'HeroShareGivenRFIAnd3bet_pct': 100*w,
            'FourbetProbability_pct': 100*r.fourbet,
            'CallProbability_pct': 100*r.call,
            'FoldProbability_pct': 100*r.fold,
            'FoldContribution_pp': 100*w*r.fold,
            'CallContribution_pp': 100*w*r.call,
            'FourbetContribution_pp': 100*w*r.fourbet,
            'PolicyBucket': r.bucket,
        }


def aggregate_family(opener: str, threebettor: str):
    records = list(class_rows(opener, threebettor))
    groups: dict[str,dict[str,float]] = {}
    for row in records:
        g = groups.setdefault(row['Family'], {'Mass':0.,'Fold':0.,'Call':0.,'Fourbet':0.,'Classes':0})
        g['Mass'] += row['HeroShareGivenRFIAnd3bet_pct']
        g['Fold'] += row['FoldContribution_pp']
        g['Call'] += row['CallContribution_pp']
        g['Fourbet'] += row['FourbetContribution_pp']
        g['Classes'] += 1
    return groups


def price_of_call(opener: str, threebettor: str) -> tuple[float,float]:
    size, risk, pot, _ = p.breakeven_metrics(opener, threebettor)
    to_call = size - p.expected_open(opener)
    if to_call <= 0: raise ValueError('3bet non-positive price')
    pot_after_call = pot + risk + to_call
    return to_call, 100*to_call / pot_after_call


def players_yet_to_act(threebettor: str) -> int:
    if threebettor not in POSITIONS: raise ValueError('unknown position')
    return len(POSITIONS) - 1 - POSITIONS.index(threebettor)


def cold_action_sensitivity(opener: str, threebettor: str):
    spot = p.audit_spot(opener, threebettor)
    n = players_yet_to_act(threebettor)
    p_fold = spot.model_fold_pct / 100
    threshold = spot.breakeven_fold_pct / 100
    # q=P(no cold action | villain 3bet, Hero RFI). Simplified independence
    # of Hero response and intervening actions. If any intervenes, assume
    # zero-equity villain loses its additional risk (conservative model).
    q_needed = threshold / p_fold if p_fold > 0 else float('inf')
    per_player_max_cold = (100*(1-q_needed**(1/n))
                           if n>0 and q_needed<=1 else None)
    def ev(q: float):
        success = q*p_fold
        return success*spot.pot_before_bb - (1-success)*spot.invested_bb
    return {
        'Opener':opener,'Threebettor':threebettor,
        'PlayersBehind3bettor':n,
        'HeroFoldGivenModel3bet_pct':spot.model_fold_pct,
        'VillainZeroEquityFoldThreshold_pct':spot.breakeven_fold_pct,
        'RequiredPNoColdAction_pct':100*q_needed,
        'PerRemainingPlayerMaxColdAction_independent_pct':per_player_max_cold,
        'EV_if_NoColdAction_BB':ev(1.),
        'EV_if_PNoColdAction95pct_BB':ev(.95) if n else None,
        'EV_if_PNoColdAction90pct_BB':ev(.90) if n else None,
        'EV_if_PNoColdAction80pct_BB':ev(.80) if n else None,
        'N_player_independence_is_assumed':True,
        'NotRealEV':True,
    }


def report_data():
    classes = [r for pair in p.KEY_PAIRS for r in class_rows(*pair)]
    families = []
    for pair in p.PAIRS:
        to_call, pot_odds = price_of_call(*pair)
        for family, v in sorted(aggregate_family(*pair).items()):
            families.append({
                'Opener':pair[0], 'Threebettor':pair[1], 'Family':family,
                'ReachableClasses':v['Classes'],
                'HeroShareGivenRFIAnd3bet_pct':v['Mass'],
                'FoldContribution_pp':v['Fold'],
                'CallContribution_pp':v['Call'],
                'FourbetContribution_pp':v['Fourbet'],
                'HeroCallPrice_BB':to_call,
                'ImmediatePotOddsCall_pct':pot_odds,
            })
    sensitivities = [cold_action_sensitivity(*pair) for pair in p.PAIRS]
    top_folds = []
    for pair in p.KEY_PAIRS:
        rows = sorted((r for r in class_rows(*pair) if r['FoldContribution_pp']>0),
                       key=lambda x: (-round(x['FoldContribution_pp'],12),x['HeroHand']))
        for rank, r in enumerate(rows[:12], 1):
            top_folds.append({'RankWithinNode':rank,**r,'ReviewFlag':'HIGH_MASS_FOLD_NOT_AUTO_CALL'})
    return classes, families, sensitivities, top_folds


def export(output_dir: Path):
    output_dir.mkdir(exist_ok=True, parents=True)
    classes, families, sensitivities, top_folds = report_data()
    outputs = [
        ('DEFENSE_CLASSES_8_v0_8.csv', classes),
        ('DEFENSE_FAMILIES_15_v0_8.csv', families),
        ('COLD_ACTION_SENSITIVITY_15_v0_8.csv', sensitivities),
        ('TOP_FOLD_CLASSES_8_v0_8.csv', top_folds),
    ]
    for filename, rows in outputs:
        if not rows: raise ValueError('Empty report')
        with (output_dir / filename).open('w', newline='', encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader()
            for row in rows:
                w.writerow({key:(round(value,8) if isinstance(value,float) else value)
                            for key,value in row.items()})
    return [x[0] for x in outputs]

if __name__ == '__main__':
    for filename in export(Path(__file__).resolve().parent): print(filename)
    for pair in p.KEY_PAIRS:
        s=cold_action_sensitivity(*pair)
        rows=list(class_rows(*pair))
        largest=sorted(rows,key=lambda x:-x['FoldContribution_pp'])[:3]
        print(f"{pair[0]} vs {pair[1]}: remaining={s['PlayersBehind3bettor']}; "
              f"qmin={s['RequiredPNoColdAction_pct']:.2f}%; "
              f"top fold={[ (r['HeroHand'],round(r['FoldContribution_pp'],2)) for r in largest ]}")
