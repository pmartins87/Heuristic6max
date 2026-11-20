"""G2-a / v0.7: auditoria de pressão de 3-bet contra a defesa heurística v0.6.1.

Não é solver e NÃO altera decisões de poker. Calcula P(Hero fold | RFI,
vilão possui cartas específicas) com card removal físico, pondera apenas
3-bets previstas no modelo interno e estima o EV de uma 3-bet com equidade
*zero* se o Hero continuar, assumindo todos os demais jogadores fora.

A métrica é condicional e serve à triagem de vulnerabilidades, não à
inferência de EV real no NLHE multiway ou à GTO.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'gto6_heuristic_v0_6_1'
if not BASE.is_dir():
    raise RuntimeError(f'Versão-base v0.6.1 ausente: {BASE}')
sys.path.insert(0, str(BASE))
from vs3_blocker_audit_v0_6 import (COMBOS, hand_class, adjusted_action_percentages)  # noqa: E402
from vs_3bet_reference import (RANGES as HERO, SPECS as HERO_SPECS)  # noqa: E402
from vs_open_reference import (RANGES as VILLAIN, expected_open, threebet_to_bb)  # noqa: E402

KEY_PAIRS = (
    ('LJ', 'HJ'), ('LJ', 'CO'), ('LJ', 'BTN'), ('HJ', 'CO'),
    ('HJ', 'BTN'), ('CO', 'BTN'), ('BTN', 'SB'), ('SB', 'BB')
)
PAIRS = tuple((s.opener, s.threebettor) for s in HERO_SPECS)


@dataclass(frozen=True)
class Spot:
    opener: str
    threebettor: str
    threebet_to_bb: float
    invested_bb: float
    pot_before_bb: float
    breakeven_fold_pct: float
    model_fold_pct: float
    zero_equity_EV_bb: float
    villain_combo_weight_pct_above_threshold: float
    distinct_threebet_combos: int
    flagged: bool


def preaction_pot_bb(opener: str) -> float:
    # Blinds SB=0.5, BB=1, no ante and no callers. Before the 3bet,
    # preflop open has replaced its own blind if the opener is the SB.
    return expected_open(opener) + (1.0 if opener == 'SB' else 1.5)


def villain_posted_bb(threebettor: str) -> float:
    return {'SB': 0.5, 'BB': 1.0}.get(threebettor, 0.0)


def breakeven_metrics(opener: str, threebettor: str) -> tuple[float, float, float, float]:
    pot = preaction_pot_bb(opener)
    size = threebet_to_bb(opener, threebettor)
    add = size - villain_posted_bb(threebettor)
    if add <= 0 or pot <= 0:
        raise ValueError('Aposta/pote não positivos')
    # EV relative to FOLD for villain. When Hero calls/4bets, assume
    # villain loses its incremental investment and wins zero additional
    # chips; an extremely conservative simplification.
    return size, add, pot, 100.0 * add / (add + pot)


def hero_masses(opener: str, threebettor: str):
    rows = HERO[(opener, threebettor)]
    open_mass = [0.] * 52
    fold_mass = [0.] * 52
    own_open: dict[tuple[int, int], float] = {}
    own_fold: dict[tuple[int, int], float] = {}
    total_open = total_fold = 0.
    for a, b in COMBOS:
        row = rows[hand_class((a, b))]
        o = row.open_probability
        f = row.open_probability * row.fold
        own_open[(a, b)] = o
        own_fold[(a, b)] = f
        total_open += o
        total_fold += f
        open_mass[a] += o
        open_mass[b] += o
        fold_mass[a] += f
        fold_mass[b] += f
    if total_open <= 0: raise ValueError('RFI sem suporte')
    return total_open, total_fold, open_mass, fold_mass, own_open, own_fold


def villain_combo_weights(opener: str, threebettor: str):
    """Returns a tuple per physical combo (a, b, w3, den_open, p_fold).

    w3 is the villain strategy's probability of 3bet for its class.
    The *joint* mass of villain 3bet + Hero RFI is w3*den_open,
    not merely w3: this corrects conditional averaging with blockers.
    """
    total, folded, oc, fc, op, fd = hero_masses(opener, threebettor)
    v = VILLAIN[(opener, threebettor)]
    for a, b in COMBOS:
        w3 = v[hand_class((a, b))].threebet
        if w3 == 0: continue
        den = total - oc[a] - oc[b] + op[(a, b)]
        num = folded - fc[a] - fc[b] + fd[(a, b)]
        if den <= 0 or not -1e-9 <= num <= den + 1e-9:
            raise ValueError('Erro nas massas físicas condicionais')
        yield a, b, w3, den, max(0., min(1., num / den))


def audit_spot(opener: str, threebettor: str) -> Spot:
    size, risk, pot, threshold = breakeven_metrics(opener, threebettor)
    denom = numer_fold = weighted_profitable = 0.
    physical = 0
    for _, _, w3, den, p_fold in villain_combo_weights(opener, threebettor):
        weight = w3 * den
        denom += weight
        numer_fold += weight * p_fold
        weighted_profitable += weight * (p_fold > threshold / 100.0 + 1e-12)
        physical += 1
    if denom <= 0: raise ValueError('Sem 3bet no modelo adversário')
    p_fold = numer_fold / denom
    reference, _, _ = adjusted_action_percentages(opener, threebettor)
    if abs(p_fold * 100 - reference['FOLD']) > 1e-8:
        raise ValueError('A nova contabilidade diverge da v0.6')
    zero_equity_ev = pot * p_fold - risk * (1.0 - p_fold)
    # This flag describes an *isolated conditional* vulnerability only.
    return Spot(opener, threebettor, size, risk, pot, threshold,
                p_fold * 100, zero_equity_ev,
                100 * weighted_profitable / denom, physical, zero_equity_ev > 1e-10)


def class_details(opener: str, threebettor: str):
    _, risk, pot, _ = breakeven_metrics(opener, threebettor)
    groups = {}
    for a, b, w3, den, p_fold in villain_combo_weights(opener, threebettor):
        hand = hand_class((a, b))
        g = groups.setdefault(hand, [0., 0., 0, 0])
        effective = w3 * den
        g[0] += effective
        g[1] += effective * p_fold
        g[2] += w3
        g[3] += 1
    total = sum(g[0] for g in groups.values())
    for hand, (weight, folded, all_3, combos) in sorted(groups.items(), key=lambda x: (-x[1][0], x[0])):
        p = folded / weight
        yield (hand, combos, 100 * weight / total, 100 * p,
               pot * p - risk * (1 - p), 100 * all_3 / combos)


def export(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    all_nodes = [audit_spot(*p) for p in PAIRS]
    with (output_dir / '3BET_PRESSURE_ALL_15_v0_7.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(('Opener','Threebettor','3betTo_BB','VillainAdditionalRisk_BB',
                    'PotBefore_BB','WorstCaseZeroEquityBreakevenFold_pct',
                    'OurHeroFoldGivenVillainModel3bet_pct','WorstCaseZeroEquityBluffEV_BB',
                    'WeightedShareVillain3betsAboveThreshold_pct',
                    'Physical3betCombos','ConditionalPressureFlag','Caveat'))
        for x in all_nodes:
            w.writerow((x.opener,x.threebettor,*[round(v, 8) for v in (
                x.threebet_to_bb,x.invested_bb,x.pot_before_bb,
                x.breakeven_fold_pct,x.model_fold_pct,x.zero_equity_EV_bb,
                x.villain_combo_weight_pct_above_threshold)],
                x.distinct_threebet_combos,'CONDITIONAL_PRESSURE' if x.flagged else 'NO_IMMEDIATE_PRESSURE',
                'isolated_vs_Hero_only; zero_equity_after_continue; others_fold; not_real_EV'))
    with (output_dir / '3BET_PRESSURE_HANDS_8_v0_7.csv').open('w', encoding='utf-8', newline='') as f:
        w=csv.writer(f)
        w.writerow(('Opener','Threebettor','VillainHandClass','Physical3betCombos',
                    'ShareOfVillain3betsWhenHeroRFI_pct','HeroFoldGivenVillainHand_pct',
                    'WorstCaseZeroEquityEV_BB','MeanVillain3betProbability_pct','Caveat'))
        for op, vi in KEY_PAIRS:
            for h, n, share, fold, ev, w3 in class_details(op, vi):
                w.writerow((op, vi, h, n, round(share, 8), round(fold, 8),
                            round(ev, 8), round(w3, 8), 'not_solver_EV'))
    return all_nodes


if __name__ == '__main__':
    for x in export(Path(__file__).resolve().parent):
        print(f'{x.opener:3s} vs {x.threebettor:3s} | fold {x.model_fold_pct:6.2f}%'
              f' | break-even {x.breakeven_fold_pct:6.2f}%'
              f' | isolated zero-equity EV {x.zero_equity_EV_bb:+.3f} BB')
