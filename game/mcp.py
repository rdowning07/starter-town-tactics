# game/mcp.py

class MCP:
    """Map-Command-Predict AI engine stub."""

    def decide_action(self, unit, game):
        """Very basic MCP strategy:
        Move the unit one tile closer to the nearest enemy.
        """
        targets = [u for u in game.units if u.team != unit.team]
        if not targets:
            return unit.x, unit.y  # No-op

        closest = self._find_nearest(unit, targets)
        dx = closest.x - unit.x
        dy = closest.y - unit.y

        move_x = unit.x + (1 if dx > 0 else -1 if dx < 0 else 0)
        move_y = unit.y + (1 if dy > 0 else -1 if dy < 0 else 0)

        return move_x, move_y

    def _find_nearest(self, unit, targets):
        closest = None
        min_dist = float("inf")
        for target in targets:
            dist = abs(unit.x - target.x) + abs(unit.y - target.y)
            if dist < min_dist:
                min_dist = dist
                closest = target
        return closest
