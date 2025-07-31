# tests/utils/dummy_game.py

from game.grid import Grid
from game.turn_controller import TurnController
from game.unit import Unit


class DummyGame:
    def __init__(self) -> None:
        self.grid = Grid(3, 3)
        self.turn_controller = TurnController(self)
        self.units: list[Unit] = []

    def add_unit(self, unit: Unit) -> None:
        self.units.append(unit)
        self.grid.get_tile(unit.x, unit.y).unit = unit
        # Add unit to turn controller
        self.turn_controller.add_unit(unit.name)
