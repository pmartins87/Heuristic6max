"""Very narrow OpenPPL rule interpreter for testing source-level parity.

NOT a parser of all OpenPPL, NOT OH execution, NOT a poker policy.
Allowed rules are literally the OpenPPL lines in portable_rfi_probe.oppl.
The only strategy decisions are in the OPPL file; Python tests/evaluates them.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

SOURCE = Path(__file__).with_name('portable_rfi_probe.oppl')
_RULE = re.compile(
    r'^WHEN \((?P<cond>[^()]+)\) (?P<action>RaiseTo) (?P<size>\d+(?:\.\d+)?) FORCE$'
)
_REQUIRED = frozenset(('InButton', 'Raises = 0', 'Calls = 0'))
_HAND = re.compile(r'^hand\$(AA|KK)$')

class PortabilityError(ValueError):
    pass

@dataclass(frozen=True)
class Rule:
    line: int
    atoms: tuple[str, ...]
    action: str
    size_bb: float


def parse_lines(source: str) -> tuple[Rule, ...]:
    rules: list[Rule] = []
    section_seen = False
    for line_no, original in enumerate(source.splitlines(), 1):
        line = original.strip()
        if not line or line.startswith('//'):
            continue
        if line == '##f$preflop##' and not section_seen:
            section_seen = True
            continue
        if not section_seen:
            raise PortabilityError(f'line {line_no}: rules require preflop header')
        match = _RULE.fullmatch(line)
        if match is None:
            raise PortabilityError(f'line {line_no}: outside audited OPPL subset')
        atoms = tuple(match['cond'].split(' AND '))
        if len(atoms) != 4 or len(set(atoms)) != 4 or not _REQUIRED.issubset(atoms):
            raise PortabilityError(f'line {line_no}: missing/duplicated RFI guard')
        hand = tuple(atom for atom in atoms if _HAND.fullmatch(atom))
        if len(hand) != 1:
            raise PortabilityError(f'line {line_no}: unsupported hand atom')
        if float(match['size']) != 2.5:
            raise PortabilityError(f'line {line_no}: unsupported sizing')
        rules.append(Rule(line_no, atoms, 'RaiseTo', 2.5))
    if not section_seen or not rules:
        raise PortabilityError('missing preflop header or rules')
    if len({tuple(rule.atoms) for rule in rules}) != len(rules):
        raise PortabilityError('duplicate/shadowed conditions')
    return tuple(rules)


def parse_file() -> tuple[Rule, ...]:
    return parse_lines(SOURCE.read_text(encoding='utf-8'))


def evaluate(rules: tuple[Rule, ...], *, hand: str, in_button: bool,
             raises: int, calls: int) -> tuple[str, float] | None:
    """Matches source top-down; None means no rule IN THIS TEST INTERPRETER.

    OpenHoldem's runtime no-match and fallback semantics are different and must
    be verified separately, so this does NOT authorize exporting a bot.
    """
    inputs = {'InButton': in_button, 'Raises = 0': raises == 0,
              'Calls = 0': calls == 0, 'hand$AA': hand == 'AA',
              'hand$KK': hand == 'KK'}
    for rule in rules:
        if all(inputs[atom] for atom in rule.atoms):
            return rule.action, rule.size_bb
    return None


if __name__ == '__main__':
    rules = parse_file()
    print(f'{len(rules)} one-to-one OpenPPL probe rules parsed; demo only')
