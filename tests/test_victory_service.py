"""
Tests for VictoryService.
"""

import pytest

from game.services.victory_service import BattleOutcome, VictoryService


class TestVictoryService:
    """Test VictoryService functionality."""

    def test_initial_state(self):
        """Test initial service state."""
        service = VictoryService(player_team_id=1, enemy_team_ids={2}, initial_counts={1: 4, 2: 4})

        assert service.get_outcome() == BattleOutcome.ONGOING
        assert service.get_alive_counts() == {1: 4, 2: 4}
        assert not service.is_battle_over()

    def test_enemy_defeat_sequence(self):
        """Test enemy defeat leading to victory."""
        service = VictoryService(player_team_id=1, enemy_team_ids={2}, initial_counts={1: 4, 2: 4})

        # Defeat all enemies
        for _ in range(4):
            service.on_unit_defeated(2)

        assert service.get_outcome() == BattleOutcome.PLAYER_WIN
        assert service.is_battle_over()

    def test_player_defeat_sequence(self):
        """Test player defeat leading to loss."""
        service = VictoryService(player_team_id=1, enemy_team_ids={2}, initial_counts={1: 4, 2: 4})

        # Defeat all player units
        for _ in range(4):
            service.on_unit_defeated(1)

        assert service.get_outcome() == BattleOutcome.PLAYER_LOSE
        assert service.is_battle_over()

    def test_observer_notification(self):
        """Test observer notification on outcome change."""
        outcomes = []

        def observer(outcome):
            outcomes.append(outcome)

        service = VictoryService(player_team_id=1, enemy_team_ids={2}, initial_counts={1: 4, 2: 4})
        service.subscribe(observer)

        # Trigger victory
        for _ in range(4):
            service.on_unit_defeated(2)

        assert len(outcomes) == 1
        assert outcomes[0] == BattleOutcome.PLAYER_WIN
