"""Core game state and orchestration logic, including grid, unit management, turn progression, and camera control."""

from game.grid import Grid
from game.unit import Unit


class Game:
    def __init__(self, width: int, height: int):
        self.grid = Grid(width, height)
        self.units: list[Unit] = []
        self.current_turn: int = 0
        self.camera_x: int = 0
        self.camera_y: int = 0
        self.width = width
        self.height = height

    def add_unit(self, unit: Unit) -> bool:
        """Attempt to place a unit on the grid at its coordinates."""
        tile = self.grid.get_tile(unit.x, unit.y)
        if tile and tile.unit is None:
            tile.unit = unit
            self.units.append(unit)
            return True
        return False

    def next_turn(self) -> None:
        """Advance to the next game turn and reset unit movement."""
        self.current_turn += 1
        for unit in self.units:
            unit.reset_movement()

    def pan_camera(self, dx: int, dy: int) -> None:
        """Adjust the camera offset by (dx, dy) while staying within grid bounds."""
        self.camera_x = max(0, min(self.camera_x + dx, self.width - 1))
        self.camera_y = max(0, min(self.camera_y + dy, self.height - 1))

    def print_state(self) -> None:
        """Display the current grid state for debugging."""
        self.grid.print_ascii()
