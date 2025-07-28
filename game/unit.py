# game/unit.py

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
        move_range: int = 3,
        health: int = 10,
        hp: int | None = None,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.team = team
        self.symbol = symbol or name[0].upper()
        self.move_range = move_range
        self.health = health
        self.hp = hp if hp is not None else health
        self.remaining_moves = move_range

    def move(self, new_x: int, new_y: int, grid: Grid) -> bool:
        if not grid.is_within_bounds(new_x, new_y):
            return False

        dest_tile = grid.get_tile(new_x, new_y)
        if dest_tile.unit:
            return False

        distance = abs(self.x - new_x) + abs(self.y - new_y)
        cost = dest_tile.movement_cost

        if cost > self.remaining_moves or distance > self.remaining_moves:
            return False

        grid.get_tile(self.x, self.y).unit = None
        dest_tile.unit = self
        self.x, self.y = new_x, new_y
        self.remaining_moves -= cost
        return True

    def move_to(self, x: int, y: int) -> None:
        """Directly sets unit's position (used in tests)."""
        self.x = x
        self.y = y

    def is_alive(self) -> bool:
        """Returns True if unit has HP > 0."""
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        """Reduces HP by amount and prevents going negative."""
        self.hp = max(0, self.hp - amount)
