# game/grid.py

from typing import List

from game.tile import Tile


class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()

    def _initialize_tiles(self) -> None:
        """Initialize the grid with default tiles."""
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = Tile(x, y, terrain_type="plains", movement_cost=1)
                row.append(tile)
            self.tiles.append(row)

    def get_tile(self, x: int, y: int) -> Tile:
        """Get a tile at the specified coordinates."""
        if not self.is_within_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds")
        return self.tiles[y][x]

    def get_tile_rect(self, x: int, y: int) -> tuple[int, int, int, int]:
        """Get the rectangle coordinates for a tile."""
        if not self.is_within_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) out of bounds")
        # Assuming 32x32 tile size for now
        tile_size = 32
        return (x * tile_size, y * tile_size, tile_size, tile_size)

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def place_unit(self, unit) -> None:
        """Place a unit on the grid."""
        if not self.is_within_bounds(unit.x, unit.y):
            raise ValueError(
                f"Unit position ({unit.x}, {unit.y}) out of bounds"
            )
        tile = self.get_tile(unit.x, unit.y)
        if tile.unit:
            raise ValueError(f"Tile ({unit.x}, {unit.y}) already occupied")
        tile.unit = unit

    def print_ascii(self, show_title: bool = True) -> None:
        """Print the grid as ASCII art."""
        if show_title:
            print(f"Grid ({self.width}x{self.height}):")
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                tile = self.get_tile(x, y)
                row += tile.get_symbol()
            print(row)
