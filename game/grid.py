# game/grid.py

from game.tile import Tile


class Grid:
    def __init__(self, width, height, terrain_layout=None):
        self.width = width
        self.height = height
        self.tiles = [[None for _ in range(height)] for _ in range(width)]
        for x in range(width):
            for y in range(height):
                terrain = "plains"
                cost = 1
                if terrain_layout:
                    terrain = terrain_layout[y][x]
                    cost = (
                        3 if terrain == "mountain" else 2 if terrain == "forest" else 1
                    )
                self.tiles[x][y] = Tile(x, y, terrain_type=terrain, movement_cost=cost)

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y]
        return None

    def is_within_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def place_unit(self, unit):
        if not self.is_within_bounds(unit.x, unit.y):
            raise ValueError("Position out of bounds")
        tile = self.get_tile(unit.x, unit.y)
        if tile.unit:
            raise ValueError("Tile already occupied")
        tile.unit = unit

    def print_ascii(self, show_title=True):
        """Prints a basic ASCII representation of the grid."""
        if show_title:
            print("Game Map:")

        for y in range(self.height):
            row = []
            for x in range(self.width):
                symbol = self.tiles[x][y].get_symbol()
                row.append(symbol)
            print(" ".join(row))
