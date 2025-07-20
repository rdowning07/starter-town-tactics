class Tile:
    def __init__(self, x, y, terrain_type="plains", movement_cost=1):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.movement_cost = movement_cost
        self.unit = None

    def is_walkable(self):
        """Return True if no unit is present."""
        return self.unit is None

    def get_symbol(self):
        """Return a symbol representing this tile's current state."""
        if self.unit:
            return self.unit.name[0].upper()  # First letter of unit's name
        if self.terrain_type == "forest":
            return "F"
        elif self.terrain_type == "mountain":
            return "M"
        return "."
