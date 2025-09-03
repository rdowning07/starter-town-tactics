"""
Tests for NearestTarget strategy.
"""

import pytest

from game.ai.targeting.nearest_target import NearestTarget


class TestNearestTarget:
    """Test NearestTarget strategy."""

    def test_select_nearest_enemy(self):
        """Test selecting the nearest enemy."""
        targeter = NearestTarget(enemy_team_ids={2})

        me = {"x": 5, "y": 5, "team": 1}
        candidates = [
            {"x": 6, "y": 5, "team": 2},  # Distance 1
            {"x": 8, "y": 5, "team": 2},  # Distance 3
            {"x": 5, "y": 7, "team": 2},  # Distance 2
        ]

        target = targeter.select(me, candidates)
        assert target is not None
        assert target["x"] == 6 and target["y"] == 5  # Closest

    def test_filter_enemies_only(self):
        """Test that only enemies are considered."""
        targeter = NearestTarget(enemy_team_ids={2})

        me = {"x": 5, "y": 5, "team": 1}
        candidates = [
            {"x": 6, "y": 5, "team": 1},  # Ally
            {"x": 7, "y": 5, "team": 2},  # Enemy
            {"x": 8, "y": 5, "team": 3},  # Other team
        ]

        target = targeter.select(me, candidates)
        assert target is not None
        assert target["team"] == 2  # Only enemy team

    def test_no_enemies(self):
        """Test behavior when no enemies exist."""
        targeter = NearestTarget(enemy_team_ids={2})

        me = {"x": 5, "y": 5, "team": 1}
        candidates = [
            {"x": 6, "y": 5, "team": 1},  # Only allies
            {"x": 7, "y": 5, "team": 1},
        ]

        target = targeter.select(me, candidates)
        assert target is None
