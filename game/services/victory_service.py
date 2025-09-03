"""
Victory Service for managing game end conditions.

This module provides a service for tracking victory and defeat conditions
and notifying subscribers when the game ends.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Set


class GameOutcome(Enum):
    """Possible game outcomes."""

    VICTORY = "victory"
    DEFEAT = "defeat"
    DRAW = "draw"
    ONGOING = "ongoing"


@dataclass
class VictoryCondition:
    """Configuration for victory conditions."""

    player_team_id: int
    enemy_team_ids: Set[int]
    alive_by_team: Dict[int, int]  # Expected alive count per team


class VictoryService:
    """Service for managing victory and defeat conditions."""

    def __init__(
        self,
        player_team_id: int,
        enemy_team_ids: Set[int],
        alive_by_team: Optional[Dict[int, int]] = None,
    ):
        """Initialize the victory service.

        Args:
            player_team_id: ID of the player team
            enemy_team_ids: Set of enemy team IDs
            alive_by_team: Expected alive count per team
        """
        self.player_team_id = player_team_id
        self.enemy_team_ids = enemy_team_ids
        self.alive_by_team = alive_by_team or {}

        # Current alive counts per team
        self.current_alive: Dict[int, int] = {}
        for team_id in set([player_team_id]) | enemy_team_ids:
            self.current_alive[team_id] = self.alive_by_team.get(team_id, 0)

        # Subscribers for victory events
        self.subscribers: List[Callable[[GameOutcome], None]] = []

        # Game state
        self.game_over = False
        self.outcome = GameOutcome.ONGOING

    def subscribe(self, callback: Callable[[GameOutcome], None]) -> None:
        """Subscribe to victory events.

        Args:
            callback: Function to call when game ends
        """
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[GameOutcome], None]) -> None:
        """Unsubscribe from victory events.

        Args:
            callback: Function to remove from subscribers
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def on_unit_defeated(self, team_id: int) -> None:
        """Handle a unit being defeated.

        Args:
            team_id: Team ID of the defeated unit
        """
        if self.game_over:
            return

        # Decrease alive count for the team
        if team_id in self.current_alive:
            self.current_alive[team_id] = max(0, self.current_alive[team_id] - 1)

        # Check victory conditions
        self._check_victory_conditions()

    def on_unit_revived(self, team_id: int) -> None:
        """Handle a unit being revived.

        Args:
            team_id: Team ID of the revived unit
        """
        if self.game_over:
            return

        # Increase alive count for the team
        if team_id in self.current_alive:
            self.current_alive[team_id] += 1

        # Check victory conditions
        self._check_victory_conditions()

    def _check_victory_conditions(self) -> None:
        """Check if victory conditions have been met."""
        if self.game_over:
            return

        # Check if player team is defeated
        if self.current_alive.get(self.player_team_id, 0) <= 0:
            self._end_game(GameOutcome.DEFEAT)
            return

        # Check if all enemy teams are defeated
        all_enemies_defeated = True
        for enemy_team_id in self.enemy_team_ids:
            if self.current_alive.get(enemy_team_id, 0) > 0:
                all_enemies_defeated = False
                break

        if all_enemies_defeated:
            self._end_game(GameOutcome.VICTORY)
            return

    def _end_game(self, outcome: GameOutcome) -> None:
        """End the game with the specified outcome.

        Args:
            outcome: The game outcome
        """
        if self.game_over:
            return

        self.game_over = True
        self.outcome = outcome

        # Notify all subscribers
        for callback in self.subscribers:
            try:
                callback(outcome)
            except Exception as e:
                print(f"Victory Service: Error notifying subscriber: {e}")

    def get_current_alive_counts(self) -> Dict[int, int]:
        """Get current alive counts for all teams.

        Returns:
            Dictionary mapping team IDs to alive counts
        """
        return self.current_alive.copy()

    def get_outcome(self) -> GameOutcome:
        """Get the current game outcome.

        Returns:
            Current game outcome
        """
        return self.outcome

    def is_game_over(self) -> bool:
        """Check if the game is over.

        Returns:
            True if the game is over, False otherwise
        """
        return self.game_over

    def reset(self) -> None:
        """Reset the victory service to initial state."""
        self.game_over = False
        self.outcome = GameOutcome.ONGOING

        # Reset alive counts
        for team_id in set([self.player_team_id]) | self.enemy_team_ids:
            self.current_alive[team_id] = self.alive_by_team.get(team_id, 0)

    def get_victory_info(self) -> Dict[str, Any]:
        """Get comprehensive victory information.

        Returns:
            Dictionary with victory service information
        """
        return {
            "game_over": self.game_over,
            "outcome": self.outcome.value,
            "player_team_id": self.player_team_id,
            "enemy_team_ids": list(self.enemy_team_ids),
            "current_alive": self.current_alive.copy(),
            "expected_alive": self.alive_by_team.copy(),
            "subscriber_count": len(self.subscribers),
        }
