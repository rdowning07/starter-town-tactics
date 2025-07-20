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
        if tile and not tile.is_occupied():
            tile.unit = unit
            self.units.append(unit)

    def next_turn(self):
        self.current_turn += 1

    def print_state(self):
        self.grid.print_ascii()

if __name__ == "__main__":
    game = Game(5, 5)
    unit = Unit("Hero", 2, 2, team="Red")
    game.add_unit(unit)
    game.print_state()

