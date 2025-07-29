# game/turn_controller.py

"""Controls the flow of turns between units."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.game import Game
    from game.unit import Unit


class TurnPhase(Enum):
    PLAYER = "player"
    ENEMY = "enemy"


class TurnController:
    def __init__(self, game: Game):
        self.game = game
        self.current_turn = 0
        self.current_phase = TurnPhase.PLAYER  # Required for test_turn_cycle

    def get_current_unit(self) -> Unit | None:
        if self.game.units:
            return self.game.units[self.current_turn % len(self.game.units)]
        return None

    def next_turn(self) -> None:
        # Used by test_turn_cycle
        self.current_phase = (
            TurnPhase.ENEMY
            if self.current_phase == TurnPhase.PLAYER
            else TurnPhase.PLAYER
        )

    def end_turn(self) -> None:
        self.current_turn += 1
        self.next_turn()

    def is_ai_turn(self) -> bool:
        unit = self.get_current_unit()
        return unit is not None and unit.team == "AI"
