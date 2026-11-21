"""Offline *chronological* HU poker history grammar. Never drives OpenHoldem.

It enumerates legal completed betting-round event words and STOPPED (fold)
words. This is a coverage reference, NOT a collection of OpenPPL rules.
No stacks, bet sizes, runouts or all-ins are inferred. Those need further gates.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from pathlib import Path
import csv

HERE=Path(__file__).resolve().parent
MAX_RAISES=4  # bound on per-street explicit raises, not a poker betting limit
ACTORS=('H','V')

@dataclass(frozen=True)
class RoundLine:
    moves: tuple[tuple[str,str],...]
    reaches_next: bool

    @property
    def word(self)->str:
        return ' '.join(a+':'+v for a,v in self.moves)

    @property
    def hero_actions(self)->str:
        return '-'.join(x for a,x in self.moves if a=='H')

    @property
    def villain_actions(self)->str:
        return '-'.join(x for a,x in self.moves if a=='V')

    @property
    def raises(self)->int:
        return sum(x=='R' for _,x in self.moves)


def enumerate_street(first_actor:str,max_raises:int=MAX_RAISES)->tuple[RoundLine,...]:
    """Exhaustive (at this raise cap) HU lines, starting with no bet.

    X=check; B=bet; R=raise; C=call; F=fold. Every player always
    acts legally and acts in alternation; the next street occurs only after
    a check-check or a call. Illegal check in the face of bet is excluded.
    """
    if first_actor not in ACTORS:raise ValueError('first_actor H/V required')
    if not isinstance(max_raises,int) or isinstance(max_raises,bool) or not 0<=max_raises<=8:
        raise ValueError('bounded raise cap 0..8 required')
    other={'H':'V','V':'H'}
    second=other[first_actor]
    lines=[RoundLine(((first_actor,'X'),(second,'X')),True)]
    for prefix in ((),((first_actor,'X'),)):
        bettor=first_actor if not prefix else second
        responder=other[bettor]
        stem=prefix+((bettor,'B'),)
        for n in range(max_raises+1):
            lines.append(RoundLine(stem+((responder,'C'),),True))
            lines.append(RoundLine(stem+((responder,'F'),),False))
            if n<max_raises:
                stem=stem+((responder,'R'),)
                responder=other[responder]
    assert len(lines)==1+4*(max_raises+1)
    return tuple(lines)


def full_two_street_paths(max_raises:int=MAX_RAISES):
    """Yield legal FLOP+TURN lines reaching RIVER, with position and PF role.

    The preflop role (hero PFR vs caller) distinguishes provenance, not a
    different legal betting word. It is included to prevent false merging.
    """
    for hero_ip in (False,True):
        first='V' if hero_ip else 'H'
        completed=tuple(x for x in enumerate_street(first,max_raises) if x.reaches_next)
        for hero_pfr in (False,True):
            for flop,turn in product(completed,repeat=2):
                yield (hero_ip,hero_pfr,flop,turn)


def flag_signature(line:RoundLine)->tuple[bool,bool,bool,bool,bool,bool,int]:
    """Conservative *hypothetical* summary of native OH aggregate flags.

    The archived official OpenPPL library defines OpponentCalledOnFlop/Turn
    only for the uncontested bot-bet-called line, not when villain bet first.
    This is a DOCUMENTED-SOURCE model, not an observed target OH version.
    Distinct chronological lines can still collapse onto one signature.
    """
    events=line.moves
    return (
        any(a=='H' and v=='X' for a,v in events),
        any(a=='H' and v in ('B','R') for a,v in events),
        any(a=='H' and v=='C' for a,v in events),
        (any(a=='V' and v=='C' for a,v in events)
         and not any(a=='V' and v in ('B','R') for a,v in events)
         and any(a=='H' and v=='B' for a,v in events)
         and not any(a=='H' and v in ('X','C') for a,v in events)),
        not any(v in ('B','R') for _,v in events),
        not any(a=='V' and v in ('B','R') for a,v in events),
        sum(a=='V' and v=='R' for a,v in events),
    )


def observability_groups(first_actor:str,max_raises:int=MAX_RAISES):
    groups={}
    for line in enumerate_street(first_actor,max_raises):
        if not line.reaches_next:continue
        groups.setdefault(flag_signature(line),[]).append(line.word)
    return groups


def export():
    lines=[]
    for i,(hero_ip,hero_pfr,flop,turn) in enumerate(full_two_street_paths(),1):
        lines.append((f'H3-{i:04d}','IP' if hero_ip else 'OOP',
                      'HERO_PFR' if hero_pfr else 'HERO_CALLER',flop.word,turn.word,
                      flop.hero_actions,turn.hero_actions,flop.raises,turn.raises,
                      'LEGAL_ACTION_WORD_NOT_OPENPPL_ROUTED'))
    with (HERE/'HIST3_484_CHRONOLOGICAL_PATHS.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['HistoryID','HeroPosition','PreflopRole','FlopEvents','TurnEvents','HeroActionsFlop','HeroActionsTurn','FlopRaises','TurnRaises','ImplementationStatus']);w.writerows(lines)
    with (HERE/'HIST3_OBSERVABILITY.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['HeroPosition','DerivedOpenPPLLibrarySignature','LegalHistoriesSharingSignature','HistoryExamples','Risk'])
        for hero_ip in (False,True):
            groups=observability_groups('V' if hero_ip else 'H')
            for signature,words in sorted(groups.items(),key=lambda x:str(x[0])):
                w.writerow(['IP' if hero_ip else 'OOP',str(signature),len(words),' | '.join(words),
                            'COLLISION_NEEDS_CHRONOLOGICAL_MEMORY' if len(words)>1 else 'STATIC_UNIQUE_WITHIN_BOUND'])
    return len(lines)

if __name__=='__main__':print('completed two-street words',export())
