# game/ai_controller.py

import math


class AIController:
    def __init__(self, game, mcp_agent=None):
        self.game = game
        self.mcp_agent = mcp_agent
        self.last_action = "Idle"

    @classmethod
    def with_mcp(cls, game, mcp_agent):
        return cls(game, mcp_agent)

    def take_turn(self):
        ai_units = [u for u in self.game.units if u.team == "Blue"]
        targets = [u for u in self.game.units if u.team != "Blue"]

        if not ai_units or not targets:
            self.last_action = "No targets"
            return

        for unit in ai_units:
            if self.mcp_agent:
                move_x, move_y = self.mcp_agent.decide_action(unit, self.game)
                unit.move_to(move_x, move_y)
                self.last_action = f"{unit.name} used MCP"
            else:
                nearest = self._find_nearest(unit, targets)
                if nearest:
                    dx = nearest.x - unit.x
                    dy = nearest.y - unit.y
                    move_x = unit.x + (1 if dx > 0 else -1 if dx < 0 else 0)
                    move_y = unit.y + (1 if dy > 0 else -1 if dy < 0 else 0)
                    unit.move_to(move_x, move_y)
                    self.last_action = f"{unit.name} moved toward {nearest.name}"
            break  # One action per turn

        self.game.next_turn()

    def _find_nearest(self, unit, targets):
        closest = None
        min_dist = float("inf")
        for target in targets:
            dist = abs(unit.x - target.x) + abs(unit.y - target.y)
            if dist < min_dist:
                min_dist = dist
                closest = target
        return closest
