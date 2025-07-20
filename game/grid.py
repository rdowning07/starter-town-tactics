from random import choice

from game.tile import Tile
from game.unit import Unit


class Grid:
    def __init__(self, width, height, terrain_layout=None):
        self.width = width
        self.height = height
        self.tiles = []

        for y in range(height):
            row = []
            for x in range(width):
                if terrain_layout:
                    terrain_type = terrain_layout[y][x]
                    if terrain_type == "plains":
                        movement_cost = 1
                    elif terrain_type == "forest":
                        movement_cost = 2
                    elif terrain_type == "mountain":
                        movement_cost = 3
                    else:
                        raise ValueError(f"Unknown terrain type: {terrain_type}")
                    tile = Tile(
                        x, y, terrain_type=terrain_type, movement_cost=movement_cost
                    )
                else:
                    tile = Tile(x, y)
                row.append(tile)
            self.tiles.append(row)

    def get_tile(self, x, y):
        if self.is_within_bounds(x, y):
            return self.tiles[y][x]
        else:
            return None

    def is_within_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def place_unit(self, unit):
        if self.is_within_bounds(unit.x, unit.y):
            self.tiles[unit.y][unit.x].unit = unit
        else:
            raise ValueError(f"Unit position out of bounds: ({unit.x}, {unit.y})")

    def print_ascii(self, show_title=True):
        if show_title:
            print("Game Map:")
        for row in self.tiles:
            print(" ".join(tile.get_symbol() for tile in row))
