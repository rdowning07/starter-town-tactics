# game/game.py

from game.grid import Grid
from game.unit import Unit


class Game:
    def __init__(self, width, height):
        self.grid = Grid(width, height)
        self.units = []
        self.current_turn = 0

    def add_unit(self, unit):
        tile = self.grid.get_tile(unit.x, unit.y)
        if tile.unit is None:
            tile.unit = unit
            self.units.append(unit)
            return True
        return False

    def next_turn(self):
        self.current_turn += 1
