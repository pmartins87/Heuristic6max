"""Deterministic source-only merger. OpenPPL remains the sole decision policy.

This builds an ISO-1 DRAFT; it does NOT verify native OH symbols or actual action.
"""
from __future__ import annotations
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'p3bet_multiway_v1' / 'preflop_srp_limp_3bet_multiway_draft.oppl'
HAND = HERE / 'iso_handlist.oppl'
PREFLOP = HERE / 'iso_preflop_capture.oppl'
TOPOLOGY = HERE / 'iso_topology.oppl'
POLICY = HERE / 'iso_policy.oppl'
COMBINED = HERE / 'iso_integrated_draft.oppl'
STREETS = ('flop', 'turn', 'river')


def chunks(text: str) -> tuple[str, dict[str, str]]:
    parts = re.split(r'^//@STREET (flop|turn|river)\s*$', text, flags=re.M)
    if len(parts) != 7 or tuple(parts[i] for i in (1, 3, 5)) != STREETS:
        raise ValueError('expected one ordered marker for each street')
    return parts[0], {parts[i]: parts[i + 1].strip() for i in (1, 3, 5)}


def render() -> str:
    old = PARENT.read_text(encoding='utf-8')
    hand = HAND.read_text(encoding='utf-8').rstrip()
    pf = PREFLOP.read_text(encoding='utf-8').rstrip()
    topo = TOPOLOGY.read_text(encoding='utf-8').rstrip()
    helper, streets = chunks(POLICY.read_text(encoding='utf-8'))
    if 'f$H6ISOValid' in old or old.count('##f$preflop##') != 1:
        raise ValueError('unexpected parent')
    if any(old.count('##f$' + s + '##') != 1 for s in STREETS):
        raise ValueError('unexpected parent street headers')
    if '##listH6ISOCORE##' not in hand:
        raise ValueError('missing exact new ISO handlist')
    for part in (hand, pf, topo, helper, *streets.values()):
        if 'WHEN Others Fold FORCE' in part:
            raise ValueError('ungated global fallback')
    now = old.replace('##f$preflop##', hand + '\n##f$preflop##\n' + pf, 1)
    now = now.replace('##f$flop##', topo + '\n' + helper.rstrip() + '\n##f$flop##', 1)
    for s in STREETS:
        now = now.replace('##f$' + s + '##', '##f$' + s + '##\n' + streets[s], 1)
    for s in ('preflop', *STREETS):
        if now.count('##f$' + s + '##') != 1:
            raise ValueError('repeated street action callback')
    before = [x for x in old.splitlines() if x.startswith('WHEN ')]
    after = [x for x in now.splitlines() if x.startswith('WHEN ')]
    cursor = 0
    for line in before:
        while cursor < len(after) and after[cursor] != line:
            cursor += 1
        if cursor >= len(after):
            raise ValueError('ancestral WHEN removed or reordered')
        cursor += 1
    return now


def build() -> tuple[int, int]:
    output = render()
    COMBINED.write_text(output, encoding='utf-8', newline='\n')
    policy = POLICY.read_text(encoding='utf-8')
    return len(re.findall(r'^WHEN \(', policy, flags=re.M)), len(output.encode('utf-8'))


if __name__ == '__main__':
    print('ISO-1 native postflop rules, integrated bytes:', build())
