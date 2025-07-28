class Tile:
    def __init__(self, x, y, terrain_type="plains", movement_cost=1):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.movement_cost = movement_cost
        self.unit = None

    def is_walkable(self):
        return self.unit is None and self.terrain_type != "mountain"

    def get_symbol(self):
        if self.unit:
            return self.unit.name[0].upper()
        terrain_symbols = {
            "plains": ".",
            "forest": "F",
            "mountain": "M",
        }
        return terrain_symbols.get(self.terrain_type, ".")  # 🔧 fallback to "."
