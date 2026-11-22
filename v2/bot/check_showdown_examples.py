"""Poker RULE invariants only, NOT a poker solver or an OpenHoldem emulator.
Run: python v2/bot/check_showdown_examples.py
Uses independent five-card scoring to distinguish improving the board from ties.
"""
from collections import Counter
from itertools import combinations

RANK = {r: i for i, r in enumerate("23456789TJQKA", 2)}

def score5(cards):
    assert len(cards) == 5 and len(set(cards)) == 5
    r = [RANK[c[0]] for c in cards]
    c = Counter(r)
    counts = sorted(((v, k) for k, v in c.items()), reverse=True)
    ranks = set(r)
    if 14 in ranks:
        ranks.add(1)
    straight = max((v for v in range(5, 15) if all(v - i in ranks for i in range(5))), default=0)
    flush = len({card[1] for card in cards}) == 1
    if flush and straight:
        return (8, straight)
    if counts[0][0] == 4:
        return (7, counts[0][1], max(k for k in r if k != counts[0][1]))
    if counts[0][0] == 3 and counts[1][0] >= 2:
        return (6, counts[0][1], counts[1][1])
    if flush:
        return (5, *sorted(r, reverse=True))
    if straight:
        return (4, straight)
    if counts[0][0] == 3:
        return (3, counts[0][1], *sorted((k for k in r if k != counts[0][1]), reverse=True))
    if counts[0][0] == 2 and counts[1][0] == 2:
        pairs = sorted((counts[0][1], counts[1][1]), reverse=True)
        return (2, *pairs, max(k for k in r if k not in pairs))
    if counts[0][0] == 2:
        return (1, counts[0][1], *sorted((k for k in r if k != counts[0][1]), reverse=True))
    return (0, *sorted(r, reverse=True))

def best7(board, hole):
    return max(score5(c) for c in combinations(board + hole, 5))

# name, board, Hero, whether best five out of seven strictly beats board's five.
EXAMPLES = [
    ("shared-straight-better-9high", "3c 4d 5h 6s 7c", "8d 9s", True),
    ("shared-straight-better-8high", "3c 4d 5h 6s 7c", "8d 2s", True),
    ("shared-straight-tie", "3c 4d 5h 6s 7c", "Kh Qs", False),
    ("board-flush-better-with-Ah", "2h 4h 6h 8h Th", "Ah Ks", True),
    ("board-flush-tie", "2h 4h 6h 8h Th", "Ks Qd", False),
    ("board-quads-tie-with-ace", "7c 7d 7h 7s Ac", "2d 3h", False),
    ("board-quads-better-A-kicker", "7c 7d 7h 7s 2c", "Ah Kd", True),
    ("shared-straightflush", "5h 6h 7h 8h 9h", "Ac Kd", False),
    ("higher-straightflush", "5h 6h 7h 8h 9h", "Th Kd", True),
    ("boat-four-flush", "Qs Js Ts 9s Qh", "Qd 9d", True),
    ("boat-board-tie", "Qc Qd Qh 9s 9d", "As Kc", False),
    ("boat-board-better-pocket-AA", "Qc Qd Qh 9s 9d", "As Ah", True),
]
for name, b, h, expected in EXAMPLES:
    board, hero = b.split(), h.split()
    assert len(set(board + hero)) == 7, name
    actual = best7(board, hero) > score5(board)
    assert actual == expected, (name, best7(board, hero), score5(board))
print("12 poker showdown invariants: OK; no EV/strategy/engine conclusions")
