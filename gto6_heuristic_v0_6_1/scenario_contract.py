"""GTO Heuristic 6-Max / v0.1 — contrato de estados e auditoria.

NÃO É UM BOT JOGÁVEL: não há ranges nem políticas instaladas.
Esta camada desacopla classificação de contexto, política estratégica e
tradução futura para OpenPPL. Python 3.10+; biblioteca-padrão.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import math
import re
from typing import Optional, Sequence


class Street(str, Enum):
    PREFLOP = 'PF'
    FLOP = 'F'
    TURN = 'T'
    RIVER = 'R'


class Position(str, Enum):
    LJ = 'LJ'
    HJ = 'HJ'
    CO = 'CO'
    BTN = 'BTN'
    SB = 'SB'
    BB = 'BB'


class PotType(str, Enum):
    UNOPENED = 'UNOPENED'
    LIMPED = 'LIMPED'
    SRP = 'SRP'
    THREE_BET = '3BET'
    FOUR_BET = '4BET'
    FIVE_BET_PLUS = '5BET+'


class Facing(str, Enum):
    RFI = 'RFI'               # primeiro aumento voluntário preflop
    VS_LIMP = 'VS_LIMP'
    VS_OPEN = 'VS_OPEN'
    VS_3BET = 'VS_3BET'
    VS_4BET = 'VS_4BET'
    VS_5BET = 'VS_5BET'
    VS_SQUEEZE = 'VS_SQUEEZE'
    VS_SHOVE = 'VS_SHOVE'
    CHECKED_TO = 'CHECKED_TO' # sem aposta a enfrentar pós-flop
    VS_BET = 'VS_BET'
    VS_RAISE = 'VS_RAISE'


class PositionalRelation(str, Enum):
    IP = 'IP'
    OOP = 'OOP'
    MIXED = 'MIXED'           # multiway: em posição contra um, fora contra outro
    UNKNOWN = 'UNKNOWN'


class BoardFamily(str, Enum):
    NONE = 'NONE'
    ACE_HIGH = 'A_HIGH'
    KING_HIGH = 'K_HIGH'
    QUEEN_HIGH = 'Q_HIGH'
    JACK_HIGH = 'J_HIGH'
    TEN_HIGH_OR_LOWER = 'T_LOW'


class Suits(str, Enum):
    NA = 'NA'
    RAINBOW = 'RAINBOW'
    TWO_TONE = 'TWO_TONE'
    MONOTONE = 'MONOTONE'
    FOUR_FLUSH = 'FOUR_FLUSH'
    FIVE_FLUSH = 'FIVE_FLUSH'


class Pairing(str, Enum):
    NA = 'NA'
    UNPAIRED = 'UNPAIRED'
    PAIRED = 'PAIRED'
    DOUBLE_PAIRED = 'DOUBLE_PAIRED'
    TRIPS_BOARD = 'TRIPS_BOARD'
    QUADS_BOARD = 'QUADS_BOARD'


class Connectivity(str, Enum):
    NA = 'NA'
    DISCONNECTED = 'DISCONNECTED'
    SEMI_CONNECTED = 'SEMI_CONNECTED'
    CONNECTED = 'CONNECTED'
    MADE_STRAIGHT_ON_BOARD = 'STRAIGHT_BOARD'


class MadeHand(str, Enum):
    NA = 'NA'
    AIR = 'AIR'
    A_HIGH = 'ACE_HIGH'
    UNDERPAIR = 'UNDERPAIR'
    BOTTOM_PAIR = 'BOTTOM_PAIR'
    MIDDLE_PAIR = 'MIDDLE_PAIR'
    TOP_PAIR = 'TOP_PAIR'
    OVERPAIR = 'OVERPAIR'
    TWO_PAIR = 'TWO_PAIR'
    TRIPS = 'TRIPS'
    SET = 'SET'
    STRAIGHT = 'STRAIGHT'
    FLUSH = 'FLUSH'
    FULL_HOUSE = 'FULL_HOUSE'
    QUADS = 'QUADS'
    STRAIGHT_FLUSH = 'STRAIGHT_FLUSH'


class Draw(str, Enum):
    NONE = 'NONE'
    BDFD = 'BDFD'
    BD_STRAIGHT = 'BD_STRAIGHT'
    GUTSHOT = 'GUTSHOT'
    OESD = 'OESD'
    FD = 'FD'
    NUT_FD = 'NUT_FD'
    COMBO = 'COMBO'


class Action(str, Enum):
    FOLD = 'FOLD'
    CHECK = 'CHECK'
    CALL = 'CALL'
    LIMP = 'LIMP'
    BET = 'BET'
    RAISE = 'RAISE'
    SHOVE = 'SHOVE'


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class BoardState:
    family: BoardFamily
    suits: Suits
    pairing: Pairing
    connectivity: Connectivity
    turned_flush_complete: bool = False
    turned_straight_complete: bool = False
    river_overcard: bool = False


@dataclass(frozen=True)
class HeroHandState:
    made: MadeHand
    draw: Draw
    nut_rank: str = 'UNKNOWN'    # ex.: NUTS, SECOND_NUTS, NON_NUTS
    kicker: str = 'NA'           # ex.: TOP, GOOD, WEAK
    blocker: str = 'NONE'        # avaliado contra range, nunca só A na mão
    sd_value: str = 'UNKNOWN'    # HIGH, MEDIUM, LOW


_VALID_PRE_HAND = re.compile(r'^(?:[AKQJT98765432]{2}|[AKQJT98765432]{2}[so])$')
_RANK_ORDER = 'AKQJT98765432'


def validate_hand_class(hand: str) -> str:
    h = hand.upper()
    if not _VALID_PRE_HAND.fullmatch(hand):
        raise ContractError(f'hand class inválida: {hand!r} (ex.: AKs, AKo, QQ)')
    if h[0] == h[1] and len(h) == 2:
        return hand
    if h[0] == h[1] or len(h) != 3 or _RANK_ORDER.index(h[0]) >= _RANK_ORDER.index(h[1]):
        raise ContractError(f'hand class mal ordenada: {hand!r}')
    return hand


def all_hand_classes() -> tuple[str, ...]:
    out = []
    for r in _RANK_ORDER:
        out.append(r+r)
    for i, hi in enumerate(_RANK_ORDER):
        for lo in _RANK_ORDER[i+1:]:
            out.extend((hi+lo+'s', hi+lo+'o'))
    assert len(out) == 169
    return tuple(out)


def combo_count(hand: str) -> int:
    validate_hand_class(hand)
    return 6 if len(hand) == 2 else 4 if hand.endswith('s') else 12


@dataclass(frozen=True)
class ScenarioState:
    hand_id: str
    street: Street
    hero_position: Position
    hand_class: str
    dealt_players: int
    active_players: int
    effective_stack_bb: float
    pot_bb: float
    to_call_bb: float
    pot_type: PotType
    facing: Facing
    positional_relation: PositionalRelation
    opponent_position: Optional[Position] = None
    board: Optional[BoardState] = None
    hero_hand: Optional[HeroHandState] = None
    prev_line: str = 'NONE'   # histórico canônico calculado por máquina de estados
    aggressor: str = 'UNKNOWN'
    source_quality: str = 'HIGH'

    def __post_init__(self):
        validate_hand_class(self.hand_class)
        if not self.hand_id.strip():
            raise ContractError('hand_id não pode ser vazio: necessário para mixed strategy estável')
        if not (2 <= self.dealt_players <= 6):
            raise ContractError('dealt_players fora de 2..6')
        if not (1 <= self.active_players <= self.dealt_players):
            raise ContractError('active_players inválido')
        for name in ('effective_stack_bb', 'pot_bb', 'to_call_bb'):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ContractError(f'{name} negativo ou não finito')
        if self.effective_stack_bb == 0 or self.pot_bb == 0:
            raise ContractError('stack/pote ausente: não emitir decisão estratégica')
        if self.street == Street.PREFLOP:
            if self.board is not None or self.hero_hand is not None:
                raise ContractError('pré-flop não possui board/força pós-flop')
            if self.facing in (Facing.CHECKED_TO, Facing.VS_BET, Facing.VS_RAISE):
                raise ContractError('facing inválido para pré-flop')
        else:
            if self.board is None or self.hero_hand is None:
                raise ContractError('pós-flop exige classificação board e mão')
            if self.facing not in (Facing.CHECKED_TO, Facing.VS_BET, Facing.VS_RAISE, Facing.VS_SHOVE):
                raise ContractError('facing inválido para pós-flop')
        if self.facing in (Facing.VS_BET, Facing.VS_RAISE, Facing.VS_SHOVE, Facing.VS_OPEN,
                           Facing.VS_3BET, Facing.VS_4BET, Facing.VS_5BET, Facing.VS_SQUEEZE) and self.to_call_bb <= 0:
            raise ContractError('há aposta a enfrentar, mas to_call_bb = 0')
        if self.facing == Facing.CHECKED_TO and self.to_call_bb != 0:
            raise ContractError('CHECKED_TO não pode ter call positivo')

    @property
    def spr(self) -> float:
        return self.effective_stack_bb / self.pot_bb

    @property
    def bet_to_pot_ratio(self) -> float:
        # Assume pot_bb é o pote visto pelo Hero, incluindo aposta adversária.
        # É uma proxy de tamanho, não o sizing exato do vilão; obter esta última
        # via histórico do pote quando o adaptador OpenHoldem for implementado.
        return self.to_call_bb / self.pot_bb

    def key(self) -> str:
        parts = [self.street.value, f'{self.dealt_players}D', self.hero_position.value,
                 self.pot_type.value, self.facing.value, f'N{self.active_players}',
                 self.positional_relation.value, self.opponent_position.value if self.opponent_position else 'V?',
                 stack_band(self.effective_stack_bb), self.hand_class]
        if self.street != Street.PREFLOP:
            assert self.board and self.hero_hand
            parts += [spr_band(self.spr), self.board.family.value,
                      self.board.suits.value, self.board.pairing.value,
                      self.board.connectivity.value, self.hero_hand.made.value,
                      self.hero_hand.draw.value, self.hero_hand.nut_rank,
                      self.prev_line, bet_band(self.bet_to_pot_ratio)]
        return '|'.join(parts)


def stack_band(bb: float) -> str:
    if bb < 15: return 'S00_15'
    if bb < 30: return 'S15_30'
    if bb < 50: return 'S30_50'
    if bb < 80: return 'S50_80'
    if bb <= 120: return 'S80_120'
    if bb <= 200: return 'S120_200'
    return 'S200P'


def spr_band(spr: float) -> str:
    if spr < 1: return 'SPR0_1'
    if spr < 2: return 'SPR1_2'
    if spr < 4: return 'SPR2_4'
    if spr < 8: return 'SPR4_8'
    return 'SPR8P'


def bet_band(ratio: float) -> str:
    if ratio == 0: return 'NO_BET'
    if ratio <= 0.2: return 'SMALL'
    if ratio <= 0.36: return 'THIRDISH'
    if ratio <= 0.55: return 'HALFISH'
    if ratio <= 0.85: return 'THREEFOURTHISH'
    if ratio <= 1.2: return 'POTISH'
    return 'OVERBET'


@dataclass(frozen=True)
class WeightedAction:
    action: Action
    weight: float
    size_pot: Optional[float] = None      # pós-flop: fração do pote (sizing pendente de adaptador)
    raise_to_bb: Optional[float] = None   # pré-flop: valor TOTAL da aposta/raise em BB


@dataclass(frozen=True)
class Policy:
    rule_id: str
    actions: tuple[WeightedAction, ...]
    rationale: str
    provenance: str
    status: str = 'DRAFT'


def validate_policy(policy: Policy, scenario: ScenarioState) -> None:
    if not policy.rule_id or not policy.provenance or not policy.rationale:
        raise ContractError('regra sem identificador, justificativa ou proveniência')
    if policy.status not in ('DRAFT','REVIEWED','TESTED','RELEASED'):
        raise ContractError('status desconhecido')
    if not policy.actions or abs(sum(a.weight for a in policy.actions) - 1) > 1e-8:
        raise ContractError('probabilidades não somam 100%')
    if any(a.weight < 0 or a.weight > 1 for a in policy.actions):
        raise ContractError('peso inválido')
    for a in policy.actions:
        if a.action in (Action.BET, Action.RAISE):
            defined = int(a.size_pot is not None) + int(a.raise_to_bb is not None)
            if defined != 1 or (a.size_pot is not None and a.size_pot <= 0) or (a.raise_to_bb is not None and a.raise_to_bb <= 0):
                raise ContractError('BET/RAISE precisa de exatamente um sizing positivo')
            if scenario.street == Street.PREFLOP and a.raise_to_bb is None:
                raise ContractError('pré-flop RAISE requer raise_to_bb (valor TOTAL em BB)')
            if scenario.street != Street.PREFLOP and a.size_pot is None:
                raise ContractError('pós-flop BET/RAISE requer size_pot (fração do pote)')
        elif a.size_pot is not None or a.raise_to_bb is not None:
            raise ContractError('sizing indevido para ação não agressiva')
        if scenario.facing == Facing.RFI and a.action not in (Action.FOLD, Action.RAISE, Action.LIMP):
            raise ContractError('ação incompatível com RFI')
        if scenario.facing == Facing.CHECKED_TO and a.action not in (Action.CHECK, Action.BET):
            raise ContractError('ação incompatível com check-to')
        if scenario.facing not in (Facing.RFI, Facing.CHECKED_TO, Facing.VS_LIMP) and a.action in (Action.CHECK, Action.LIMP, Action.BET):
            raise ContractError('ação incompatível quando enfrenta aposta')


def stable_uniform(hand_id: str, scenario_key: str, rule_id: str) -> float:
    """RNG de 1 decisão por mão/nó; nunca reamostrar a cada screenshot."""
    encoded = f'GTO6-v0.1\x1f{hand_id}\x1f{scenario_key}\x1f{rule_id}'.encode('utf-8')
    return int.from_bytes(sha256(encoded).digest()[:8], 'big') / (1 << 64)


def pick_action(policy: Policy, scenario: ScenarioState) -> WeightedAction:
    validate_policy(policy, scenario)
    x = stable_uniform(scenario.hand_id, scenario.key(), policy.rule_id)
    cutoff = 0.0
    for aw in policy.actions:
        cutoff += aw.weight
        if x < cutoff:
            return aw
    return policy.actions[-1]  # ruído de ponto flutuante


def policy_or_none(policies: dict[str, Policy], scenario: ScenarioState) -> Optional[WeightedAction]:
    """Sem política: None. NÃO converte cenário desconhecido em CHECK/FOLD."""
    policy = policies.get(scenario.key())
    return pick_action(policy, scenario) if policy else None


if __name__ == '__main__':
    print('Contrato GTO6 v0.1 carregado. Classes pré-flop:', len(all_hand_classes()))
    print('Políticas estratégicas instaladas: ZERO; não utilizar para operar.')
