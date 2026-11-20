"""Offline generator: immutable 6-max RFI heuristic -> OpenPPL native rules.

NOT the bot runtime. Never edit source strategy files or infer GTO optimality.
"""
from __future__ import annotations

from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'gto6_heuristic_v0_6_1'))
from rfi_reference import RANGES, PREFLOP_SIZE  # noqa: E402
from scenario_contract import Position, all_hand_classes  # noqa: E402

# In six-handed OpenPPL, HJ is MP3; LJ is UTG/MP2.
POSITION_SYMBOL = {
    'LJ': ('InUTG', 5, 1.0),
    'HJ': ('InMiddlePosition3', 4, 1.0),
    'CO': ('InCutOff', 3, 1.0),
    'BTN': ('InButton', 2, 1.0),
    'SB': ('InSmallBlind', 1, 0.5),
}
# Name -> percent, action in tested preflop grammar.
ACTION = {'RAISE': 'RaiseTo', 'LIMP': 'Call', 'FOLD': 'Fold'}


def listname(pos: str, tag: str) -> str:
    return f'listMVP{pos}{tag}'


def guard(pos: str) -> str:
    symbol, to_act, to_call = POSITION_SYMBOL[pos]
    atoms = (
        'IsPreflop', 'nplayersdealt = 6', symbol,
        'Raises = 0', 'Calls = 0', f'StillToAct = {to_act}',
        'PotSize = 1.5', f'AmountToCall = {to_call:g}',
        'NOT StackUnknown', 'StackSize >= 95', 'StackSize <= 105',
        'MinOpponentStackSize >= 95', 'MaxOpponentStackSize <= 105',
    )
    return ' AND '.join(atoms)


def generate() -> tuple[int, int, int]:
    hands = sorted(all_hand_classes())
    all_lists = []
    all_rules = []
    mapping = []
    mixed = []
    for pos in POSITION_SYMBOL:
        rows = RANGES[Position(pos)]
        buckets: dict[str, list[str]] = {}
        for hand in hands:
            values = {a: rows[hand][a] for a in ('RAISE', 'LIMP', 'FOLD')}
            nonzero = [(a, weight) for a, weight in values.items() if weight > 0]
            if len(nonzero) == 1:
                tag = nonzero[0][0]
            elif len(nonzero) == 2 and nonzero[-1][0] == 'FOLD':
                action, probability = nonzero[0]
                if probability not in (0.4, 0.5, 0.75):
                    raise ValueError(f'Unapproved frequency: {pos} {hand} {probability}')
                tag = f'MIX{action}{round(probability*100)}'
                mixed.append((pos, hand, action, probability))
            else:
                raise ValueError(f'Unsupported three-way/mixed line: {pos} {hand} {values}')
            buckets.setdefault(tag, []).append(hand)
            mapping.append((pos, hand, *[f'{100*values[a]:.8f}' for a in ('RAISE','LIMP','FOLD')], tag))
        for tag in ('RAISE', 'LIMP', 'FOLD', 'MIXRAISE40', 'MIXRAISE50', 'MIXLIMP75'):
            if tag not in buckets:
                continue
            lname = listname(pos, tag)
            all_lists.append((lname, buckets[tag]))
            pre = f'WHEN ({guard(pos)} AND {lname}'
            if tag.startswith('MIX'):
                action = 'RAISE' if tag.startswith('MIXRAISE') else 'LIMP'
                prob = 40 if tag.endswith('40') else 50 if tag.endswith('50') else 75
                all_rules.extend([
                    f'{pre} AND randomhand < {prob/100:.2f}) '
                    + (f'RaiseTo {PREFLOP_SIZE[Position(pos)]:g}' if action=='RAISE' else 'Call')
                    + ' FORCE',
                    f'{pre} AND randomhand >= {prob/100:.2f}) Fold FORCE',
                ])
            else:
                act = (f'RaiseTo {PREFLOP_SIZE[Position(pos)]:g}' if tag == 'RAISE'
                       else 'Call' if tag == 'LIMP' else 'Fold')
                all_rules.append(f'{pre}) {act} FORCE')
    expected_mixes = {('LJ','KJo','RAISE',0.4),('HJ','QJo','RAISE',0.5),
                      ('BTN','53s','RAISE',0.5),('SB','K3s','RAISE',0.5),
                      ('SB','97o','LIMP',0.75)}
    if set(mixed) != expected_mixes or len(mapping) != 845:
        raise ValueError(f'Historical baseline changed; human review required: {mixed}')
    out = [
        '// RFI-MVP STATIC STRATEGY MODULE; NOT A COMPLETE OPENHOLDEM BOT.',
        '// Heuristic v0.6.1 preserved; 6-max first-in only, 95-105 BB target.',
        '// Mismatched state/no-match MAY invoke OpenHoldem default.bot.',
        '// Never load without preflop fallback and real OpenHoldem replay verification.',
    ]
    for lname, members in all_lists:
        out.append(f'##{lname}##')
        out.extend(' '.join(members[i:i+12]) for i in range(0,len(members),12))
    out.append('##f$preflop##')
    out.extend(all_rules)
    out.append('')
    (HERE / 'rfi_6max_mvp.oppl').write_text('\n'.join(out), encoding='utf-8', newline='\n')
    with (HERE / 'RFI_6MAX_845_MAPPING.csv').open('w',encoding='utf-8',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('Position','Hand','Raise_pct','Limp_pct','Fold_pct','OPPL_group'))
        writer.writerows(mapping)
    return len(mapping),len(all_rules),len(mixed)


if __name__ == '__main__':
    print('Mapped rows, rules, mixed classes:',generate())
