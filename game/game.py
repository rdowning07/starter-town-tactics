"""Main game logic and orchestration."""

from game.grid import Grid
from game.unit import Unit


class Game:
    def __init__(self, width: int, height: int):
        self.grid = Grid(width, height)
        self.units: list[Unit] = []
        self.current_turn = 0

    def add_unit(self, unit: Unit) -> bool:
        tile = self.grid.get_tile(unit.x, unit.y)
        if tile and tile.unit is None:
            tile.unit = unit
            self.units.append(unit)
            return True
        return False

    def next_turn(self) -> None:
        self.current_turn += 1
        for unit in self.units:
            unit.reset_movement()

    def print_state(self) -> None:
        self.grid.print_grid()
