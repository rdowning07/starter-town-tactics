"""Defines the Grid and handles tile access and unit placement."""

from game.tile import Tile


class Grid:
    def __init__(self, width: int, height: int, terrain_layout=None):
        self.width = width
        self.height = height
        self.tiles = []

        for y in range(height):
            row = []
            for x in range(width):
                if terrain_layout:
                    terrain_type = terrain_layout[y][x]
                    movement_cost = self._get_movement_cost(terrain_type)
                    tile = Tile(
                        x, y, terrain_type=terrain_type, movement_cost=movement_cost
                    )
                else:
                    tile = Tile(x, y)
                row.append(tile)
            self.tiles.append(row)

    def _get_movement_cost(self, terrain_type: str) -> int:
        if terrain_type == "plains":
            return 1
        elif terrain_type == "forest":
            return 2
        elif terrain_type == "mountain":
            return 3
        raise ValueError(f"Unknown terrain type: {terrain_type}")

    def get_tile(self, x: int, y: int):
        if self.is_within_bounds(x, y):
            return self.tiles[y][x]
        return None

    def is_within_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def place_unit(self, unit):
        if self.is_within_bounds(unit.x, unit.y):
            self.tiles[unit.y][unit.x].unit = unit
        else:
            raise ValueError(f"Unit position out of bounds: ({unit.x}, {unit.y})")

    def print_ascii(self, show_title: bool = True):
        if show_title:
            print("Game Map:")
        for row in self.tiles:
            print(" ".join(tile.get_symbol() for tile in row))
