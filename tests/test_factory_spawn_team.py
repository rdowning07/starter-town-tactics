"""
Tests for EntityFactory team spawning functionality.
"""

import pytest

from game.factories.entity_factory import EntityFactory


class TestEntityFactory:
    """Test EntityFactory team spawning."""

    def test_spawn_team_basic(self):
        """Test basic team spawning."""
        factory = EntityFactory()
        units = factory.spawn_team(1, "fighter", 3, (0, 0))

        assert len(units) == 3
        assert all(u["team"] == 1 for u in units)
        assert all(u["type"] == "fighter" for u in units)

    def test_spawn_team_positions(self):
        """Test team positioning."""
        factory = EntityFactory()
        units = factory.spawn_team(1, "fighter", 3, (5, 5), step=(1, 0))

        expected_positions = [(5, 5), (6, 5), (7, 5)]
        actual_positions = [(u["x"], u["y"]) for u in units]

        assert actual_positions == expected_positions

    def test_spawn_multiple_teams(self):
        """Test spawning multiple teams."""
        factory = EntityFactory()

        allies = factory.spawn_team(1, "fighter", 2, (0, 0), is_player=True)
        enemies = factory.spawn_team(2, "bandit", 2, (10, 0), is_player=False)

        assert len(allies) == 2
        assert len(enemies) == 2
        assert all(u["is_player"] for u in allies)
        assert not any(u["is_player"] for u in enemies)
        assert factory.get_spawned_count() == 4
