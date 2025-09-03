"""
Tests for the core rules engine.
"""
from unittest.mock import MagicMock, Mock

import pytest

from core.rules.combat import DamageResult, apply_attack, calc_facing_bonus, calc_height_bonus
from core.rules.move import a_star, heuristic, terrain_cost
from core.rules.status import Status, on_unit_turn_start


class TestCombatRules:
    def test_calc_height_bonus(self):
        """Test height bonus calculation with clamping."""
        # Same height = no bonus
        assert calc_height_bonus(5, 5) == 0

        # Attacker higher = negative bonus (target gets advantage)
        assert calc_height_bonus(7, 5) == -2  # Clamped to -2

        # Attacker lower = positive bonus (attacker gets advantage)
        assert calc_height_bonus(3, 7) == 2  # Clamped to +2

        # Extreme differences are clamped
        assert calc_height_bonus(1, 10) == 2  # Clamped to +2
        assert calc_height_bonus(10, 1) == -2  # Clamped to -2

    def test_calc_facing_bonus(self):
        """Test facing bonus calculation."""
        # Adjacent positions get FRONT bonus (0)
        assert calc_facing_bonus("N", (5, 5), (5, 6)) == 0
        assert calc_facing_bonus("N", (5, 5), (6, 5)) == 0

        # Non-adjacent positions get SIDE bonus (1)
        assert calc_facing_bonus("N", (5, 5), (7, 7)) == 1

    def test_damage_result(self):
        """Test DamageResult dataclass."""
        result = DamageResult(amount=5, killed=False)
        assert result.amount == 5
        assert result.killed == False

        result = DamageResult(amount=10, killed=True)
        assert result.amount == 10
        assert result.killed == True


class TestStatusRules:
    def test_status_enum(self):
        """Test Status enum values."""
        assert Status.POISON != Status.SLOW
        assert str(Status.POISON) == "Status.POISON"
        assert str(Status.SLOW) == "Status.SLOW"


class TestMoveRules:
    def test_heuristic(self):
        """Test Manhattan distance heuristic."""
        assert heuristic((0, 0), (3, 4)) == 7  # 3 + 4
        assert heuristic((1, 1), (1, 1)) == 0  # Same position
        assert heuristic((5, 5), (2, 8)) == 6  # 3 + 3

    def test_terrain_cost_mock(self):
        """Test terrain cost with mocked game state."""
        mock_state = Mock()
        mock_tile = Mock()
        mock_tile.move_cost = 3
        mock_state.map.tile.return_value = mock_tile

        assert terrain_cost(mock_state, (5, 5)) == 3

    def test_a_star_simple_path(self):
        """Test A* with a simple open path."""
        mock_state = Mock()
        mock_tile = Mock()
        mock_tile.move_cost = 1
        mock_state.map.tile.return_value = mock_tile
        mock_state.map.in_bounds.return_value = True
        mock_state.map.blocked.return_value = False

        path = a_star(mock_state, (0, 0), (2, 2), 10)
        assert path is not None
        assert path[0] == (0, 0)  # Start
        assert path[-1] == (2, 2)  # Goal
        assert len(path) > 2  # Should have intermediate steps

    def test_a_star_no_path(self):
        """Test A* when no path exists."""
        mock_state = Mock()
        mock_tile = Mock()
        mock_tile.move_cost = 1
        mock_state.map.tile.return_value = mock_tile
        mock_state.map.in_bounds.return_value = True
        mock_state.map.blocked.return_value = True  # All tiles blocked

        path = a_star(mock_state, (0, 0), (2, 2), 10)
        assert path is None

    def test_a_star_max_cost_exceeded(self):
        """Test A* when path cost exceeds maximum."""
        mock_state = Mock()
        mock_tile = Mock()
        mock_tile.move_cost = 5  # High cost
        mock_state.map.tile.return_value = mock_tile
        mock_state.map.in_bounds.return_value = True
        mock_state.map.blocked.return_value = False

        path = a_star(mock_state, (0, 0), (2, 2), 3)  # Low max cost
        assert path is None
