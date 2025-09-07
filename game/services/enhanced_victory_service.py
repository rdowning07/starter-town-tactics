"""
Enhanced Victory Service for Starter Town Tactics.

Provides multiple victory conditions for dynamic and engaging gameplay.
"""

import time
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from game.services.victory_service import GameOutcome, VictoryService


class VictoryType(Enum):
    """Types of victory conditions."""

    ELIMINATION = "elimination"  # Defeat all enemies
    SURVIVAL = "survival"  # Survive X turns
    OBJECTIVE = "objective"  # Reach specific location
    DAMAGE = "damage"  # Deal X total damage
    TERRITORY = "territory"  # Control specific tiles


class EnhancedVictoryService(VictoryService):
    """Enhanced victory service with multiple victory conditions."""

    def __init__(
        self,
        player_team_id: int,
        enemy_team_ids: Set[int],
        alive_by_team: Dict[int, int],
    ):
        """Initialize enhanced victory service.

        Args:
            player_team_id: ID of the player team
            enemy_team_ids: Set of enemy team IDs
            alive_by_team: Initial alive counts by team
        """
        super().__init__(player_team_id, enemy_team_ids, alive_by_team)

        # Victory condition tracking
        self.turn_count = 0
        self.survival_turns = 30  # Victory after 30 turns
        self.total_damage_dealt = 0
        self.damage_threshold = 50  # Victory after 50 damage
        self.objective_tiles = [(9, 9), (8, 9), (9, 8)]  # Top-right corner
        self.territory_tiles = [(5, 5), (6, 5), (5, 6), (6, 6)]  # Center control

        # Victory condition states
        self.victory_conditions = {
            VictoryType.ELIMINATION: True,  # Always check elimination
            VictoryType.SURVIVAL: True,  # Check survival
            VictoryType.OBJECTIVE: True,  # Check objective
            VictoryType.DAMAGE: True,  # Check damage
            VictoryType.TERRITORY: False,  # Disabled by default
        }

        # Game state tracking
        self.unit_positions: Dict[str, Tuple[int, int]] = {}
        self.controlled_tiles: Set[Tuple[int, int]] = set()

        print("🎯 Enhanced Victory Service initialized with multiple conditions:")
        print(f"   • Elimination: Defeat all enemies")
        print(f"   • Survival: Survive {self.survival_turns} turns")
        print(f"   • Objective: Reach tiles {self.objective_tiles}")
        print(f"   • Damage: Deal {self.damage_threshold} total damage")

    def on_turn_start(self) -> None:
        """Called at the start of each turn."""
        self.turn_count += 1

        # Check survival victory
        if self.victory_conditions[VictoryType.SURVIVAL]:
            if self.turn_count >= self.survival_turns:
                self._trigger_victory(GameOutcome.VICTORY, f"Survived {self.turn_count} turns!")
                return

        # Update territory control
        if self.victory_conditions[VictoryType.TERRITORY]:
            self._update_territory_control()

    def on_damage_dealt(self, damage: int, attacker_team: int) -> None:
        """Track damage dealt by player team.

        Args:
            damage: Amount of damage dealt
            attacker_team: Team ID of the attacker
        """
        if attacker_team == self.player_team_id:
            self.total_damage_dealt += damage

            # Check damage victory
            if self.victory_conditions[VictoryType.DAMAGE] and self.total_damage_dealt >= self.damage_threshold:
                self._trigger_victory(GameOutcome.VICTORY, f"Dealt {self.total_damage_dealt} damage!")
                return

    def on_unit_moved(self, unit_id: str, new_position: Tuple[int, int], team_id: int) -> None:
        """Track unit movement for objective and territory victories.

        Args:
            unit_id: ID of the unit that moved
            new_position: New (x, y) position
            team_id: Team ID of the unit
        """
        self.unit_positions[unit_id] = new_position

        # Check objective victory (player units reaching objective tiles)
        if self.victory_conditions[VictoryType.OBJECTIVE] and team_id == self.player_team_id:
            if new_position in self.objective_tiles:
                self._trigger_victory(GameOutcome.VICTORY, f"Reached objective at {new_position}!")
                return

    def check_enhanced_victory_conditions(self) -> Optional[GameOutcome]:
        """Check all enhanced victory conditions.

        Returns:
            GameOutcome if victory/defeat achieved, None if ongoing
        """
        # Check elimination victory (inherited from base class)
        outcome = self.get_outcome()
        if outcome != GameOutcome.ONGOING:
            return outcome

        # Check territory victory
        if (
            self.victory_conditions[VictoryType.TERRITORY] and len(self.controlled_tiles) >= 3
        ):  # Control 3+ center tiles
            self._trigger_victory(
                GameOutcome.VICTORY,
                f"Controlled {len(self.controlled_tiles)} strategic tiles!",
            )
            return GameOutcome.VICTORY

        return None

    def _update_territory_control(self) -> None:
        """Update which tiles are controlled by player units."""
        self.controlled_tiles.clear()

        for unit_id, position in self.unit_positions.items():
            # Check if this unit is on a player team (simplified check)
            if position in self.territory_tiles:
                self.controlled_tiles.add(position)

    def _trigger_victory(self, outcome: GameOutcome, message: str) -> None:
        """Trigger victory with custom message.

        Args:
            outcome: Victory outcome
            message: Victory message
        """
        print(f"🏆 VICTORY ACHIEVED: {message}")
        # Force the outcome in the base class
        self._outcome = outcome
        # Notify subscribers using the base class method
        if hasattr(self, "subscribers"):
            for subscriber in self.subscribers:
                subscriber(outcome)

    def get_victory_stats(self) -> Dict[str, any]:
        """Get current victory condition statistics.

        Returns:
            Dictionary of victory stats
        """
        return {
            "turn_count": self.turn_count,
            "survival_progress": f"{self.turn_count}/{self.survival_turns}",
            "damage_dealt": self.total_damage_dealt,
            "damage_progress": f"{self.total_damage_dealt}/{self.damage_threshold}",
            "controlled_tiles": len(self.controlled_tiles),
            "objective_tiles": self.objective_tiles,
            "territory_tiles": self.territory_tiles,
        }

    def enable_victory_condition(self, condition: VictoryType, enabled: bool = True) -> None:
        """Enable or disable a specific victory condition.

        Args:
            condition: Victory condition type
            enabled: Whether to enable the condition
        """
        self.victory_conditions[condition] = enabled
        status = "enabled" if enabled else "disabled"
        print(f"🎯 Victory condition '{condition.value}' {status}")

    def set_survival_turns(self, turns: int) -> None:
        """Set the survival victory turn requirement.

        Args:
            turns: Number of turns to survive
        """
        self.survival_turns = turns
        print(f"🎯 Survival victory set to {turns} turns")

    def set_damage_threshold(self, threshold: int) -> None:
        """Set the damage victory threshold.

        Args:
            threshold: Total damage required for victory
        """
        self.damage_threshold = threshold
        print(f"🎯 Damage victory threshold set to {threshold}")
