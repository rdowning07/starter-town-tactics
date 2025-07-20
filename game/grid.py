"""Grid module for handling the game board logic."""

from random import choice

class Tile:
    """Represents a single tile on the grid."""
    def __init__(self, x, y, terrain_type="plains", movement_cost=1):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.movement_cost = movement_cost
        self.unit = None  # Reference to Unit object on this tile

    def is_occupied(self):
        return self.unit is not None

    def get_symbol(self):
        """Return a character representing the terrain type or unit."""
        if self.unit:
            return self.unit.name[0].upper()
        terrain_symbols = {
            "plains": ".",
            "forest": "F",
            "mountain": "M",
        }
        return terrain_symbols.get(self.terrain_type, "?")

class Grid:
    """Represents a 2D grid of tiles for the game."""

    TERRAIN_TYPES = [
        ("plains", 1),
        ("forest", 2),
        ("mountain", 3)
    ]

    def __init__(self, width, height):
        """
        Initialize the grid with the specified width and height.

        Args:
            width (int): Number of columns in the grid.
            height (int): Number of rows in the grid.
        """
        self.width = width
        self.height = height
        self.tiles = [
            [Tile(x, y, *choice(self.TERRAIN_TYPES)) for x in range(width)]
            for y in range(height)
        ]

    def get_tile(self, x, y):
        """Safely return the tile at the given coordinates, or None if out of bounds."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.tiles[y][x]
        return None

    def print_ascii(self):
        """Print an ASCII representation of the grid."""
        print("Game Map:")
        for row in self.tiles:
            print(" ".join(tile.get_symbol() for tile in row))
