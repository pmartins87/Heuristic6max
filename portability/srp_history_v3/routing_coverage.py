"""SOURCE-derived offline audit, NOT OpenHoldem runtime coverage.

Input comes from chronological_history's legal event words. Flags are
constructed using the archived OpenPPL library semantics. The SAME OPPL
source is read by history_v3_interpreter; no independent action policy.
"""
from __future__ import annotations
from pathlib import Path
import csv
import chronological_history as c
import history_v3_interpreter as h

HERE=Path(__file__).resolve().parent
REPORT=HERE/'HIST3_ROUTING_COVERAGE.csv'
FIELDS=('HistoryID','HeroPosition','PreflopRole','FlopEvents','TurnEvents',
        'FlopClassifiedFromSource','TurnClassifiedFromSource','RiverDomainStatus',
        'CaptureHypothesis')


def observed_flags(line:c.RoundLine,street:str):
    checked,raised,called,opp_called,no_betting,no_villain_aggression,villain_raises=c.flag_signature(line)
    return {f'BotCheckedOn{street}':checked,
            f'BotRaisedOn{street}':raised,
            f'BotCalledOn{street}':called,
            f'OpponentCalledOn{street}':opp_called,
            f'NoBettingOn{street}':no_betting,
            f'NoVillainBetOrRaisedOn{street}':no_villain_aggression,
            f'NumberOfRaisesOn{street}':villain_raises}


def previously_observed_event_flags(line:c.RoundLine,street:str,hero_ip:bool):
    """Ideal observation: only a preceding *confirmed* Bet/Raise can be stored.

    Whether target OpenHoldem actually calls the recorder at that opportunity
    MUST be proved with a real replay. This is an optimistic upper bound.
    """
    if not hero_ip:return {}
    flags={}
    e=line.moves
    for idx,(actor,action) in enumerate(e[:-2]):
        if (actor=='H' and action in ('B','R') and e[idx+1]==('V','R')
            and e[idx+2][0]=='H'):
            key=('LeadBetFacedRaise' if action=='B' else 'RaiseFacedReraise')
            flags[f'user_H3_IP_{street}{key}']=True
    return flags


def classify():
    m=h.parse_file()
    rows=[]
    for idx,(ip,pfr,flop,turn) in enumerate(c.full_two_street_paths(),1):
        obs=h.observe(Position='Last' if ip else 'First',IsRiver=True,
           BotRaisedBeforeFlop=pfr,BotCalledBeforeFlop=not pfr,
           NumberOfRaisesBeforeFlop=0 if pfr else 1,
           **observed_flags(flop,'Flop'),**observed_flags(turn,'Turn'),
           **previously_observed_event_flags(flop,'Flop',ip),
           **previously_observed_event_flags(turn,'Turn',ip))
        known_f=h.evaluate(m,'river',obs,helper='f$H3FlopKnownSafe')
        known_t=h.evaluate(m,'river',obs,helper='f$H3TurnKnownSafe')
        domain=h.evaluate(m,'river',obs,helper='f$H3RiverDomain')
        status=('MODELED_DOMAIN_ADMITTED' if domain else
                'FLOP_UNROUTED_OR_ALIAS' if not known_f else
                'TURN_UNROUTED_OR_ALIAS')
        rows.append(dict(zip(FIELDS,(f'H3-{idx:04d}','IP' if ip else 'OOP',
           'HERO_PFR' if pfr else 'HERO_CALLER',flop.word,turn.word,
           int(known_f),int(known_t),status,
           'IDEAL_PRIOR_EVENT_CAPTURE_UNVERIFIED_IN_OH'))))
    return rows


def export():
    rows=classify()
    with REPORT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader();w.writerows(rows)
    return len(rows),sum(r['RiverDomainStatus']=='MODELED_DOMAIN_ADMITTED' for r in rows)

if __name__=='__main__':print('HIST3 modeled routing',export())
