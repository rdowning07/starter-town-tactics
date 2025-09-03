# @api: Status effects tick deterministically on turn and/or on tick
from enum import Enum, auto

from ..state import GameState, UnitRef


class Status(Enum):
    POISON = auto()
    SLOW = auto()


def on_unit_turn_start(s: GameState, uref: UnitRef) -> None:
    u = s.unit(uref)
    if Status.POISON in u.status:
        u.stats.hp = max(0, u.stats.hp - 2)  # v1 fixed dot
    # SLOW handled by turn controller: skip every other turn
