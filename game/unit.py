"""Defines the Unit class for game entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.grid import Grid


class Unit:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        team: str,
        symbol: str | None = None,
        move_range: int = 1,
        health: int = 10,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.team = team
        self.symbol = symbol or name[0].upper()
        self.move_range = move_range
        self.health = health
        self.remaining_moves = move_range

    def __repr__(self) -> str:
        return f"<Unit {self.name} ({self.team}) at ({self.x}, {self.y})>"

    def move(self, new_x: int, new_y: int, grid: Grid) -> bool:
        distance = abs(self.x - new_x) + abs(self.y - new_y)
        if distance > self.remaining_moves:
            return False

        if not grid.is_within_bounds(new_x, new_y):
            return False

        dest_tile = grid.get_tile(new_x, new_y)
        if dest_tile.unit or dest_tile.movement_cost > self.remaining_moves:
            return False

        grid.get_tile(self.x, self.y).unit = None
        dest_tile.unit = self
        self.x, self.y = new_x, new_y
        self.remaining_moves -= distance
        return True

    def move_to(self, x: int, y: int, grid: Grid | None = None) -> None:
        self.x = x
        self.y = y

    def reset_movement(self) -> None:
        """Reset the remaining movement points for a new turn."""
        self.remaining_moves = self.move_range
