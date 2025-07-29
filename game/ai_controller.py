"""AI behavior logic."""

from __future__ import annotations

from game.grid import Grid
from game.unit import Unit


class AIController:
    def __init__(self, units: list[Unit]):
        self.units = units

    def update(self, grid: Grid):
        for unit in self.units:
            if unit.hp <= 0:
                continue
            new_x, new_y = unit.x, min(grid.height - 1, unit.y + 1)
            unit.move(new_x, new_y, grid)
