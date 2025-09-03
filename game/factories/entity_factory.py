"""
Entity Factory for spawning teams of units.

This module provides a factory pattern for creating teams of units with
configurable layouts and positioning.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class UnitConfig:
    """Configuration for a unit."""

    name: str
    team: int
    sprite: str
    x: int
    y: int
    hp: int = 10
    ap: int = 3
    attack_range: int = 1
    is_player: bool = False
    team_name: str = ""


@dataclass
class TeamConfig:
    """Configuration for a team."""

    team_id: int
    team_name: str
    units: List[UnitConfig]
    is_player_team: bool = False


class EntityFactory:
    """Factory for creating teams of units."""

    def __init__(self, unit_ctor=None):
        """Initialize the factory.

        Args:
            unit_ctor: Unit constructor class (optional)
        """
        self.unit_ctor = unit_ctor

    def spawn_team(
        self,
        team_id: int,
        unit_type: str,
        count: int,
        start_xy: Tuple[int, int] = (0, 0),
        layout: str = "line",
        step: Tuple[int, int] = (1, 0),
        is_player: bool = False,
        team_name: str = "",
        **unit_kwargs,
    ) -> TeamConfig:
        """Spawn a team of units.

        Args:
            team_id: Team identifier
            unit_type: Type of unit to spawn
            count: Number of units to spawn
            start_xy: Starting position (x, y)
            layout: Layout pattern ("line", "grid", "random")
            step: Step size for positioning (dx, dy)
            is_player: Whether this is the player team
            team_name: Name of the team
            **unit_kwargs: Additional unit configuration

        Returns:
            TeamConfig with spawned units
        """
        units = []
        start_x, start_y = start_xy
        dx, dy = step

        for i in range(count):
            if layout == "line":
                x = start_x + i * dx
                y = start_y + i * dy
            elif layout == "grid":
                cols = int(count**0.5) + (1 if count % int(count**0.5) > 0 else 0)
                x = start_x + (i % cols) * dx
                y = start_y + (i // cols) * dy
            else:  # random or default to line
                x = start_x + i * dx
                y = start_y + i * dy

            unit_name = f"{unit_type}_{i+1}" if count > 1 else unit_type

            unit_config = UnitConfig(
                name=unit_name,
                team=team_id,
                sprite=unit_type,
                x=x,
                y=y,
                is_player=is_player and i == 0,  # First unit is player
                team_name=team_name,
                **unit_kwargs,
            )
            units.append(unit_config)

        return TeamConfig(team_id=team_id, team_name=team_name, units=units, is_player_team=is_player)

    def create_demo_teams(self) -> Tuple[TeamConfig, TeamConfig]:
        """Create demo teams for 4v4 tactical combat.

        Returns:
            Tuple of (allies_team, bandits_team)
        """
        # Player team (Allies)
        allies = self.spawn_team(
            team_id=1,
            unit_type="fighter",
            count=4,
            start_xy=(2, 2),
            layout="line",
            step=(1, 0),
            is_player=True,
            team_name="Allies",
            hp=10,
            ap=6,
            attack_range=1,
        )

        # Override individual unit types for variety
        allies.units[0].sprite = "fighter"
        allies.units[0].name = "fighter"
        allies.units[1].sprite = "mage"
        allies.units[1].name = "mage"
        allies.units[1].attack_range = 3
        allies.units[2].sprite = "healer"
        allies.units[2].name = "healer"
        allies.units[2].attack_range = 2
        allies.units[3].sprite = "ranger"
        allies.units[3].name = "ranger"
        allies.units[3].attack_range = 2

        # Enemy team (Bandits)
        bandits = self.spawn_team(
            team_id=2,
            unit_type="bandit",
            count=4,
            start_xy=(10, 10),
            layout="line",
            step=(1, 0),
            is_player=False,
            team_name="Bandits",
            hp=8,
            ap=6,
            attack_range=1,
        )

        return allies, bandits
