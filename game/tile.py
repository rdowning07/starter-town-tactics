"""Represents a single tile on the game grid."""

from typing import Optional

from game.unit import Unit


class Tile:
    def __init__(
        self, x: int, y: int, terrain_type: str = "plains", movement_cost: int = 1
    ):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.movement_cost = movement_cost
        self.unit: Optional[Unit] = None

    def is_walkable(self) -> bool:
        """Return True if no unit is present on this tile."""
        return self.unit is None

    def get_symbol(self) -> str:
        """Return a symbol representing this tile's current state."""
        if self.unit:
            return self.unit.name[0].upper()
        if self.terrain_type == "forest":
            return "F"
        if self.terrain_type == "mountain":
            return "M"
        return "."
