class Unit:
    def __init__(self, name, x, y, team, symbol=None, move_range=1, health=10):
        self.name = name
        self.x = x
        self.y = y
        self.team = team
        self.symbol = symbol or name[0].upper()
        self.move_range = move_range
        self.health = health

    def __repr__(self):
        return f"<Unit {self.name} ({self.team}) at ({self.x}, {self.y})>"

    def move(self, new_x, new_y, grid):
        distance = abs(self.x - new_x) + abs(self.y - new_y)
        if distance > self.move_range:
            return False

        if not grid.is_within_bounds(new_x, new_y):
            return False

        dest_tile = grid.get_tile(new_x, new_y)
        if dest_tile.unit or dest_tile.movement_cost > self.move_range:
            return False

        grid.get_tile(self.x, self.y).unit = None
        dest_tile.unit = self
        self.x, self.y = new_x, new_y
        return True

    def move_to(self, x, y, grid=None):
        # Optional passthrough for interface similarity if not using grid logic
        self.x = x
        self.y = y
