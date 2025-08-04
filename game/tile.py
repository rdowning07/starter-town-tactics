# @api
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.unit import Unit

# Constants
TILE_SIZE = 32

class Tile:
    """
    Represents a single tile on the game grid.
    Supports both terrain-based and unit-based functionality.
    """

    def __init__(self, x: int, y: int, **kwargs):
        self.x = x
        self.y = y
        self.terrain = kwargs.get("terrain", "G")  # G, F, W, R, etc.
        self.terrain_type = kwargs.get(
            "terrain_type", "plains"
        )  # plains, forest, mountain, etc.
        self.movement_cost = kwargs.get("movement_cost", 1)
        self.unit: Optional["Unit"] = None  # Unit object (for compatibility)
        self.unit_id: Optional[str] = None  # Unit ID string

    def is_walkable(self) -> bool:
        """Check if the tile can be walked on."""
        return self.unit is None and self.terrain_type != "mountain"

    def is_occupied(self) -> bool:
        """Check if the tile is occupied by a unit."""
        return self.unit_id is not None or self.unit is not None

    def get_symbol(self) -> str:
        """Get the display symbol for this tile."""
        if self.unit:
            return self.unit.name[0].upper()
        if self.unit_id is not None:
            return self.unit_id[0].upper()

        # Terrain-based symbols
        terrain_symbols = {
            "plains": ".",
            "forest": "F",
            "mountain": "M",
        }

        # If terrain_type is explicitly set to something other than plains, use it
        if self.terrain_type != "plains":
            return terrain_symbols.get(self.terrain_type, ".")

        # Otherwise, use terrain-based symbols
        if self.terrain in ["G", "F", "W", "R"]:
            return self.terrain.lower()

        return terrain_symbols.get(self.terrain_type, ".")

    def get_movement_cost(self) -> int:
        """Get the movement cost for this tile."""
        # Terrain-based costs
        terrain_costs = {
            "G": 1,
            "R": 1,
            "F": 2,
            "W": 3,
        }

        # Check terrain first, then fall back to movement_cost attribute
        return terrain_costs.get(self.terrain, self.movement_cost)
