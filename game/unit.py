# game/unit.py

from game.grid import Grid

class Unit:
    """Represents a unit on the grid."""

    def __init__(self, name, x, y, team, move_range=3, can_move_diagonally=False):
        """
        Initialize a unit with basic attributes.

        Args:
            name (str): Name of the unit.
            x (int): X-coordinate on the grid.
            y (int): Y-coordinate on the grid.
            team (str): Team affiliation.
            move_range (int): Max number of tiles the unit can move.
            can_move_diagonally (bool): Whether the unit can move diagonally.
        """
        self.name = name
        self.x = x
        self.y = y
        self.team = team
        self.move_range = move_range
        self.can_move_diagonally = can_move_diagonally

    def move(self, new_x, new_y, grid: Grid) -> bool:
        """
        Attempt to move the unit to a new tile on the grid.

        Args:
            new_x (int): Destination x-coordinate.
            new_y (int): Destination y-coordinate.
            grid (Grid): The game grid.

        Returns:
            bool: True if movement was successful, False otherwise.
        """
        target_tile = grid.get_tile(new_x, new_y)

        # Check 1: bounds
        if target_tile is None:
            return False

        # Check 2: occupied
        if target_tile.unit is not None:
            return False

        # Check 3: same position
        if (new_x, new_y) == (self.x, self.y):
            return False

        # Check 4: movement range
        dx = abs(self.x - new_x)
        dy = abs(self.y - new_y)

        # Prevent diagonal if not allowed
        if not self.can_move_diagonally and dx != 0 and dy != 0:
            return False

        manhattan_distance = dx + dy
        if manhattan_distance > self.move_range:
            return False

        # Check 5: terrain movement cost
        if target_tile.movement_cost > self.move_range:
            return False

        # Execute move
        current_tile = grid.get_tile(self.x, self.y)
        if current_tile:
            current_tile.unit = None
        target_tile.unit = self
        self.x = new_x
        self.y = new_y

        return True

    def __repr__(self):
        return f"<{self.team} {self.name} at ({self.x}, {self.y})>"
