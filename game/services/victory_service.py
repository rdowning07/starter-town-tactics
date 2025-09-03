"""
Victory Service - Tracks battle state and determines win/lose conditions.
"""

from __future__ import annotations

from enum import Enum
from typing import Callable, Dict, List, Optional, Set


class BattleOutcome(Enum):
    """Possible battle outcomes."""

    ONGOING = "ongoing"
    PLAYER_WIN = "player_win"
    PLAYER_LOSE = "player_lose"


class VictoryService:
    """Service for tracking battle state and victory conditions."""

    def __init__(
        self,
        player_team_id: int,
        enemy_team_ids: Set[int],
        initial_counts: Dict[int, int],
    ):
        self.player_team_id = player_team_id
        self.enemy_team_ids = enemy_team_ids
        self.alive_counts = initial_counts.copy()
        self.outcome = BattleOutcome.ONGOING
        self.observers: List[Callable] = []

    def subscribe(self, observer: Callable[[BattleOutcome], None]):
        """Subscribe to battle outcome changes."""
        self.observers.append(observer)

    def on_unit_defeated(self, team_id: int):
        """Handle a unit being defeated."""
        if team_id in self.alive_counts:
            self.alive_counts[team_id] = max(0, self.alive_counts[team_id] - 1)
            self._check_victory_conditions()

    def _check_victory_conditions(self):
        """Check if victory conditions have been met."""
        if self.outcome != BattleOutcome.ONGOING:
            return

        # Check if all enemies are defeated
        all_enemies_defeated = all(self.alive_counts.get(team_id, 0) <= 0 for team_id in self.enemy_team_ids)

        if all_enemies_defeated:
            self.outcome = BattleOutcome.PLAYER_WIN
            self._notify_observers()
            return

        # Check if player team is defeated
        if self.alive_counts.get(self.player_team_id, 0) <= 0:
            self.outcome = BattleOutcome.PLAYER_LOSE
            self._notify_observers()

    def _notify_observers(self):
        """Notify all observers of the battle outcome."""
        for observer in self.observers:
            try:
                observer(self.outcome)
            except Exception as e:
                print(f"Observer notification failed: {e}")

    def get_outcome(self) -> BattleOutcome:
        """Get current battle outcome."""
        return self.outcome

    def get_alive_counts(self) -> Dict[int, int]:
        """Get current alive counts by team."""
        return self.alive_counts.copy()

    def is_battle_over(self) -> bool:
        """Check if the battle has ended."""
        return self.outcome != BattleOutcome.ONGOING
