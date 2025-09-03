"""
Nearest Target Strategy - Simple targeting for AI units.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class NearestTarget:
    """Strategy for finding the nearest enemy target."""

    def __init__(self, enemy_team_ids: set):
        self.enemy_team_ids = enemy_team_ids

    def select(self, me: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the nearest enemy target."""
        if not candidates:
            return None

        # Filter to only enemy units
        enemies = [u for u in candidates if u.get("team") in self.enemy_team_ids]
        if not enemies:
            return None

        # Find closest by Manhattan distance
        my_pos = (me.get("x", 0), me.get("y", 0))
        closest = None
        min_distance = float("inf")

        for enemy in enemies:
            enemy_pos = (enemy.get("x", 0), enemy.get("y", 0))
            distance = abs(my_pos[0] - enemy_pos[0]) + abs(my_pos[1] - enemy_pos[1])

            if distance < min_distance:
                min_distance = distance
                closest = enemy

        return closest

    def get_strategy_name(self) -> str:
        """Get the name of this targeting strategy."""
        return "NearestTarget"
