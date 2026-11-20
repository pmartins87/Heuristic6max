"""G2-a v0.9: economic sensitivity of HJ RFI -> CO 3bet.

Diagnostic-only. No edits to preflop policies, no solver, no claimed EV.
The 3bettor model is the existing VS_OPEN tree, with physical card removal.
All 'call' and '4bet' estimates are algebraic required thresholds under
explicitly artificial no-future-betting / zero-equity-if-called cases.
"""
from __future__ import annotations

from pathlib import Path
import csv
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
V08 = ROOT / 'audits' / 'g2a_v0_8'
BASE = ROOT / 'gto6_heuristic_v0_6_1'
if not (V08 / 'defense_composition.py').is_file() or not (BASE / 'vs3_blocker_audit_v0_6.py').is_file():
    raise RuntimeError('Checkout sem dependencias da v0.8/v0.6.1')
sys.path.insert(0, str(V08))
import defense_composition as d  # noqa: E402
from vs3_blocker_audit_v0_6 import BY_CLASS, villain_mass_by_hero_combo  # noqa: E402

PAIR = ('HJ','CO')
HERO = d.p.HERO[PAIR]
CANDIDATES = ('A9o','KJo','AJo','KQo','ATo','AQo',
              '22','44','66','JTs','T9s','QJs','A5s','99','TT')
# Illustrative examples, NOT observed site rake/realization or recommendations.
RAKES = ((0.0,0.0,'NO_RAKE'), (0.05,3.0,'HYPOTHETICAL_5PCT_CAP3BB'),
         (0.08,3.0,'HYPOTHETICAL_8PCT_CAP3BB'))
REALIZATION = (0.60,0.75,0.90,1.0)
THREEBET_TO_BB = (8.0,9.5,11.0)
OPEN_TO_BB = d.p.expected_open('HJ')
DEAD_BLINDS = 1.5


def exposure_by_class(hand: str, available=None):
    """P(CO 3bet | Hero holds this class, CO random hand), NOT observed frequency.

    Enumerates all physical Hero combos and 1,225 possible nonoverlapping
    CO combinations, weighted uniformly within Hero's hand class. Does not
    condition on actions of other seats, their hands or CO opponent tendencies.
    """
    if hand not in HERO: raise ValueError('Classe invalida')
    if available is None: available, _ = villain_mass_by_hero_combo(*PAIR)
    return sum(available[combo] for combo in BY_CLASS[hand]) / (1225 * len(BY_CLASS[hand]))


def class_screen():
    posterior = d.exact_hero_class_weights(*PAIR)
    base_fold = sum(posterior[h]*HERO[h].fold for h in HERO)
    available, _ = villain_mass_by_hero_combo(*PAIR)
    result=[]
    for hand in sorted(HERO):
        row=HERO[hand]
        p=posterior[hand]
        exposure=exposure_by_class(hand,available)
        note = ('TOP_REVIEW_NO_ACTION' if hand in CANDIDATES
                else 'NO_AUTO_ACTION')
        result.append({
            'HeroHand':hand,
            'PhysicalCombos':len(BY_CLASS[hand]),
            'RFI_pct':100*row.open_probability,
            'ModelCO3betGivenHeroCards_pct':100*exposure,
            'HeroShareGivenRFIAnd3bet_pct':100*p,
            'VS3_Fold_pct':100*row.fold,
            'VS3_Call_pct':100*row.call,
            'VS3_4bet_pct':100*row.fourbet,
            'FoldContribution_pp':100*p*row.fold,
            'Model3bet_ExposureCostIfFold_BB':OPEN_TO_BB*exposure*row.fold,
            'Caveat':note,
        })
    return result


def baseline():
    posterior=d.exact_hero_class_weights(*PAIR)
    return {a:100*sum(posterior[h]*getattr(HERO[h], attr) for h in HERO)
            for a,attr in [('FOLD','fold'),('CALL','call'),('4BET','fourbet')]}


def change_one_class(hand: str, *, open_multiplier: float=1.,
                     fold_to_call: float=0., fold_to_4bet: float=0.):
    """Exact joint-mass counterfactual holding villain strategy unchanged.

    open_multiplier applies ONLY to RFI probability for one class;
    fold_to_call/fold_to_4bet move absolute probability from existing
    VS3 fold for that class. This is NEVER a poker strategy recommendation.
    """
    if hand not in HERO: raise ValueError('Classe desconhecida')
    if not 0 <= open_multiplier <= 1: raise ValueError('open multiplier')
    row=HERO[hand]
    if min(fold_to_call,fold_to_4bet)<0 or fold_to_call+fold_to_4bet>row.fold+1e-12:
        raise ValueError('Nao ha massa FOLD suficiente')
    base=d.exact_hero_class_weights(*PAIR)
    old_weight=base[hand]
    den=1-old_weight+old_weight*open_multiplier
    if den<=0: raise ValueError('Sem suporte apos corte')
    def probs(h):
        r=HERO[h]
        if h==hand:
            return (r.fold-fold_to_call-fold_to_4bet,
                    r.call+fold_to_call,r.fourbet+fold_to_4bet)
        return r.fold,r.call,r.fourbet
    numer=[0.,0.,0.]
    for h,w in base.items():
        w *= open_multiplier if h==hand else 1.
        for i,prob in enumerate(probs(h)):
            numer[i] += w*prob
    folds,calls,fourbets=(100*n/den for n in numer)
    # RFI total mass over 1326 starting combos changes, but EV unknown.
    rfi_delta_pp = 100*(open_multiplier-1)*row.open_probability*len(BY_CLASS[hand])/1326
    return {'Fold_pct':folds,'Call_pct':calls,'Fourbet_pct':fourbets,
            'DeltaFold_pp':folds-baseline()['FOLD'],
            'DeltaRFI_total_pp':rfi_delta_pp,
            'RetainedConditionalMass_pct':100*den}


def candidate_counterfactuals():
    out=[]
    for hand in CANDIDATES:
        row=HERO[hand]
        candidates=[('RFI_HALF',.5,0.,0.),('RFI_REMOVE',0.,0.,0.)]
        if row.fold>=.25:
            candidates.extend([('FOLD_TO_CALL_25PP',1.,.25,0.),
                               ('FOLD_TO_4BET_25PP',1.,0.,.25)])
        for scenario,scale,call_delta,fourbet_delta in candidates:
            new=change_one_class(hand,open_multiplier=scale,
                                 fold_to_call=call_delta,fold_to_4bet=fourbet_delta)
            out.append({'HeroHand':hand,'Scenario':scenario,
                        'OldRFI_pct':100*row.open_probability,
                        'NewRFI_pct':100*row.open_probability*scale,
                        'BaselineFold_pct':baseline()['FOLD'],
                        **new,
                        'Note':'DIAGNOSTIC_ONLY_NOT_EV_AND_NOT_STRATEGY_CHANGE'})
    return out


def call_break_even(size_to_bb: float, rake_rate:float,
                    rake_cap_bb:float, realization:float):
    """Required *raw equity* in a toy single-street model.

    E(call) = equity*realization*(pot_after_call-rake) - additional_call.
    Assumes no additional betting, all called pots see flop, rake from total
    current pot at terminal comparison, no rake if no flop. Not actual EV.
    """
    if not 0 < realization <= 1 or not 0 <= rake_rate <= 1 or rake_cap_bb < 0:
        raise ValueError('Parametros invalidos')
    if size_to_bb<=OPEN_TO_BB: raise ValueError('3bet sizing invalido')
    to_call=size_to_bb-OPEN_TO_BB
    current_pot=OPEN_TO_BB+size_to_bb+DEAD_BLINDS
    after=current_pot+to_call
    rake=min(rake_rate*after,rake_cap_bb)
    prize=after-rake
    if prize<=0: raise ValueError('Pote liquido invalido')
    return {'CallAdditional_BB':to_call,'PotAfterCall_BB':after,
            'ToyRake_BB':rake,'ImmediateEquityNoRake_pct':100*to_call/after,
            'RequiredRawEquity_pct':100*to_call/(realization*prize),
            'FeasibleAt100pctEquity':to_call <= realization*prize + 1e-12}


def fourbet_zero_equity_fold_threshold(size_to_bb:float):
    """A stylized zero-equity 4bet: if not all fold, lose added risk.
    Raises to 2.65 * 3bet size, opener already invested 2.5BB.
    Ignores player(s) behind and future betting, NEVER solver frequency.
    """
    if size_to_bb<=OPEN_TO_BB: raise ValueError('3bet sizing invalido')
    raise_to=round(size_to_bb*2.65+1e-8,2)
    add=raise_to-OPEN_TO_BB
    pot=OPEN_TO_BB+size_to_bb+DEAD_BLINDS
    return {'FourbetTo_BB':raise_to,'FourbetAdditional_BB':add,
            'PotBeforeFourbet_BB':pot,
            'RequiredEveryoneFolds_pct':100*add/(add+pot)}


def price_frontier():
    out=[]
    for sizing in THREEBET_TO_BB:
        bet=fourbet_zero_equity_fold_threshold(sizing)
        for rate,cap,tag in RAKES:
            for realization in REALIZATION:
                c=call_break_even(sizing,rate,cap,realization)
                out.append({'ThreebetTo_BB':sizing,'RakeModel':tag,
                            'ToyRakeRate_pct':100*rate,'ToyRakeCap_BB':cap,
                            'EquityRealizationAssumption_pct':100*realization,
                            **c,**bet,
                            'Note':'SCENARIO_ONLY_NO_REAL_EQUITY_OR_EV'})
    return out


def export(folder:Path):
    folder.mkdir(parents=True,exist_ok=True)
    reports=[('HJ_CO_169_CLASS_SCREEN_v0_9.csv',class_screen()),
             ('HJ_CO_CANDIDATE_COUNTERFACTUALS_v0_9.csv',candidate_counterfactuals()),
             ('HJ_CO_PRICE_FRONTIER_v0_9.csv',price_frontier())]
    for name,rows in reports:
        if not rows: raise AssertionError('Sem dados')
        with (folder/name).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader()
            for row in rows:
                writer.writerow({key:round(value,8) if isinstance(value,float) else value
                                 for key,value in row.items()})
    return [p[0] for p in reports]


if __name__=='__main__':
    for name in export(Path(__file__).resolve().parent):
        print(name)
    print('Base HJ vs CO',baseline())
    print('Call floor baseline',call_break_even(8,0,0,1))
    print('4bet bluff floor baseline',fourbet_zero_equity_fold_threshold(8))
