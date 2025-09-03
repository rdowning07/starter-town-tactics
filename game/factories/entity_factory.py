"""
Entity Factory - Creates teams of units for tactical combat.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


class EntityFactory:
    """Factory for creating teams of units."""

    def __init__(self):
        self.unit_counter = 0

    def spawn_team(
        self,
        team_id: int,
        unit_type: str,
        count: int,
        start_pos: Tuple[int, int],
        layout: str = "line",
        step: Tuple[int, int] = (1, 0),
        is_player: bool = False,
    ) -> List[Dict[str, Any]]:
        """Spawn a team of units with the specified layout."""
        units = []

        for i in range(count):
            unit_id = f"{unit_type}_{team_id}_{i}"
            position = self._calculate_position(start_pos, i, layout, step)

            unit = {
                "id": unit_id,
                "type": unit_type,
                "team": team_id,
                "x": position[0],
                "y": position[1],
                "hp": 12 if unit_type == "fighter" else 10,
                "ap": 6,
                "is_player": is_player,
                "attack_range": 1,
            }

            units.append(unit)
            self.unit_counter += 1

        return units

    def _calculate_position(
        self, start_pos: Tuple[int, int], index: int, layout: str, step: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Calculate position for a unit based on layout."""
        if layout == "line":
            return (start_pos[0] + index * step[0], start_pos[1] + index * step[1])
        elif layout == "square":
            side = int(index**0.5)
            offset = index % side
            return (start_pos[0] + offset, start_pos[1] + side)
        else:
            # Default to line layout
            return (start_pos[0] + index * step[0], start_pos[1] + index * step[1])

    def get_spawned_count(self) -> int:
        """Get total number of units spawned by this factory."""
        return self.unit_counter
