# game/mcp.py

import math


class MCP:
    """Map-Command-Predict AI engine"""

    def __init__(self, strategy="nearest"):
        self.strategy = strategy

    def decide_action(self, unit, game):
        """Determine best movement coordinates based on strategy."""
        targets = self._get_targets(unit, game)
        if not targets:
            return unit.x, unit.y  # No-op

        if self.strategy == "nearest":
            return self._move_toward_nearest(unit, targets)
        else:
            # Placeholder for future strategies
            return unit.x, unit.y

    def _get_targets(self, unit, game):
        return [u for u in game.units if u.team != unit.team]

    def _move_toward_nearest(self, unit, targets):
        closest = self._find_nearest(unit, targets)
        if not closest:
            return unit.x, unit.y

        dx = closest.x - unit.x
        dy = closest.y - unit.y

        move_x = unit.x + (1 if dx > 0 else -1 if dx < 0 else 0)
        move_y = unit.y + (1 if dy > 0 else -1 if dy < 0 else 0)

        return move_x, move_y

    def _find_nearest(self, unit, targets):
        return min(
            targets,
            key=lambda t: abs(unit.x - t.x) + abs(unit.y - t.y),
            default=None,
        )
