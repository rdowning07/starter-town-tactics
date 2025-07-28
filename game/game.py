from typing import List, Optional

from game.grid import Grid
from game.unit import Unit
from game.turn_controller import TurnController
from game.ai_controller import AIController


class Game:
    def __init__(self, width: int, height: int):
        self.grid = Grid(width, height)
        self.units: List[Unit] = []
        self.current_turn: int = 0
        self.turn_controller = TurnController(self)
        self.ai_controller = AIController(self)

    def add_unit(self, unit: Unit) -> None:
        self.units.append(unit)
        tile = self.grid.get_tile(unit.x, unit.y)
        tile.unit = unit

    def get_current_unit(self) -> Optional[Unit]:
        if not self.units:
            return None
        return self.units[self.current_turn % len(self.units)]

    def is_over(self) -> bool:
        teams = {unit.team for unit in self.units if unit.is_alive()}
        return len(teams) <= 1

    def next_turn(self) -> None:
        self.current_turn += 1
        self.turn_controller.end_turn()
