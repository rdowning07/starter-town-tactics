import os
import tempfile
import time

import pytest
import yaml

from devtools.scenario_loader import load_scenario
from game.game_state import GameState


def test_gamestate_metadata_defaults():
    """Test that GameState has correct default metadata values."""
    gs = GameState()
    assert gs.name == ""
    assert gs.map_id == "default_map"
    assert gs.objective == "Defeat all enemies"
    assert gs.max_turns == 20


def test_add_unit_and_team_tracking():
    """Test that units are properly added and team tracking works."""
    gs = GameState()
    gs.add_unit(unit_id="p1", team="player", hp=10, ap=2)
    gs.add_unit(unit_id="e1", team="ai", hp=5, ap=2)

    assert gs.units.is_alive("p1")
    assert gs.units.get_team("p1") == "player"
    assert gs.units.get_team("e1") == "ai"


def test_win_and_loss_conditions():
    """Test win and loss condition logic."""
    gs = GameState()
    gs.max_turns = 3
    gs.turn_controller.current_turn = 2

    gs.add_unit("p1", "player", hp=10, ap=2)
    gs.add_unit("e1", "ai", hp=10, ap=2)  # Alive AI initially

    # Initially no one has won or lost
    assert gs.has_won() is False
    assert gs.has_lost() is False

    # Kill AI unit - player should win
    gs.damage_unit("e1", 10)
    assert gs.has_won() is True
    assert gs.has_lost() is False

    # Kill player unit - player should lose
    gs.damage_unit("p1", 10)
    assert gs.has_lost() is True


def test_loss_on_turn_limit():
    """Test that player loses when turn limit is exceeded."""
    gs = GameState()
    gs.add_unit("p1", "player", hp=10, ap=2)
    gs.add_unit("e1", "ai", hp=10, ap=2)

    gs.max_turns = 2
    gs.turn_controller.current_turn = 3  # Exceeded

    assert gs.has_lost() is True
    assert gs.has_won() is False


def test_set_metadata():
    """Test the set_metadata method."""
    gs = GameState()
    gs.set_metadata("Test Scenario", "test_map", "Test Objective", 15)

    assert gs.name == "Test Scenario"
    assert gs.map_id == "test_map"
    assert gs.objective == "Test Objective"
    assert gs.max_turns == 15


def test_multiple_units_win_condition():
    """Test win condition with multiple AI units."""
    gs = GameState()
    gs.add_unit("p1", "player", hp=10, ap=2)
    gs.add_unit("ai1", "ai", hp=10, ap=2)
    gs.add_unit("ai2", "ai", hp=10, ap=2)

    # Initially no win
    assert gs.has_won() is False

    # Kill one AI unit - still no win
    gs.damage_unit("ai1", 10)
    assert gs.has_won() is False

    # Kill second AI unit - now win
    gs.damage_unit("ai2", 10)
    assert gs.has_won() is True


def test_any_alive_method():
    """Test the any_alive method in UnitManager."""
    gs = GameState()
    gs.add_unit("p1", "player", hp=10, ap=2)
    gs.add_unit("p2", "player", hp=10, ap=2)
    gs.add_unit("ai1", "ai", hp=10, ap=2)

    # All teams have alive units
    assert gs.units.any_alive("player") is True
    assert gs.units.any_alive("ai") is True

    # Kill one player unit - still alive
    gs.damage_unit("p1", 10)
    assert gs.units.any_alive("player") is True

    # Kill all player units - none alive
    gs.damage_unit("p2", 10)
    assert gs.units.any_alive("player") is False


# === Edge Case Tests ===


def test_empty_scenario_no_units():
    """Test edge case: scenario with no units."""
    gs = GameState()

    # With no units, player wins by default (no AI units to defeat)
    # but also loses because there are no player units
    assert gs.has_won() is True
    assert gs.has_lost() is True

    # Check team status
    assert gs.units.any_alive("player") is False
    assert gs.units.any_alive("ai") is False


def test_invalid_team_names():
    """Test edge case: invalid team names."""
    gs = GameState()
    gs.add_unit("u1", "invalid_team", hp=10, ap=2)

    # Should handle invalid team names gracefully
    assert gs.units.any_alive("invalid_team") is True
    assert gs.units.any_alive("player") is False
    assert gs.units.any_alive("ai") is False


def test_negative_hp_values():
    """Test edge case: negative HP values raises ValueError."""
    gs = GameState()
    with pytest.raises(ValueError, match="HP must be positive"):
        gs.add_unit("u1", "player", hp=-5, ap=2)


def test_zero_hp_unit():
    """Test edge case: unit with 0 HP raises ValueError."""
    gs = GameState()
    with pytest.raises(ValueError, match="HP must be positive"):
        gs.add_unit("u1", "player", hp=0, ap=2)


def test_very_large_turn_counts():
    """Test edge case: very large turn counts."""
    gs = GameState()
    gs.add_unit("p1", "player", hp=10, ap=2)
    gs.add_unit("ai1", "ai", hp=10, ap=2)
    gs.max_turns = 1000

    # Set to just under limit
    gs.turn_controller.current_turn = 999
    assert gs.has_lost() is False

    # Set to exactly at limit
    gs.turn_controller.current_turn = 1000
    assert gs.has_lost() is False

    # Set to over limit
    gs.turn_controller.current_turn = 1001
    assert gs.has_lost() is True


def test_extreme_hp_values():
    """Test edge case: extreme HP values."""
    gs = GameState()
    gs.add_unit("u1", "player", hp=999999, ap=2)

    # Unit should be alive with very high HP
    assert gs.units.is_alive("u1") is True
    assert gs.units.get_hp("u1") == 999999

    # Massive damage should kill it
    gs.damage_unit("u1", 1000000)
    assert gs.units.is_alive("u1") is False


def test_duplicate_unit_ids():
    """Test edge case: adding units with duplicate IDs."""
    gs = GameState()
    gs.add_unit("u1", "player", hp=10, ap=2)
    gs.add_unit("u1", "ai", hp=5, ap=3)  # Same ID, different team

    # Second add should overwrite the first
    assert gs.units.get_team("u1") == "ai"
    assert gs.units.get_hp("u1") == 5


def test_damage_nonexistent_unit():
    """Test edge case: damaging a unit that doesn't exist."""
    gs = GameState()

    # Should not raise an exception
    gs.damage_unit("nonexistent", 10)

    # Unit should not exist
    assert gs.units.is_alive("nonexistent") is False


def test_get_team_nonexistent_unit():
    """Test edge case: getting team of nonexistent unit returns None."""
    gs = GameState()

    # Should return None for nonexistent unit
    assert gs.units.get_team("nonexistent") is None


def test_get_hp_nonexistent_unit():
    """Test edge case: getting HP of nonexistent unit returns None."""
    gs = GameState()

    # Should return None for nonexistent unit
    assert gs.units.get_hp("nonexistent") is None


# === Integration Tests ===


def test_gamestate_with_scenario_loader():
    """Test GameState integration with scenario loader."""
    scenario_data = {
        "name": "Integration Test",
        "description": "Test scenario for integration",
        "metadata": {
            "objective": "Test objective",
            "map": "test_map",
            "max_turns": 10,
        },
        "units": [
            {"id": "p1", "team": "player", "hp": 10, "ap": 2},
            {"id": "ai1", "team": "ai", "hp": 8, "ap": 3},
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as tf:
        yaml.dump(scenario_data, tf)
        path = tf.name

    try:
        gs = load_scenario(path)

        # Test that GameState was properly configured
        assert gs.name == "Integration Test"
        assert gs.objective == "Test objective"
        assert gs.max_turns == 10

        # Test that units were properly added
        assert gs.units.get_team("p1") == "player"
        assert gs.units.get_team("ai1") == "ai"
        assert gs.units.get_hp("p1") == 10
        assert gs.units.get_hp("ai1") == 8

        # Test win/loss conditions
        assert gs.has_won() is False
        assert gs.has_lost() is False

        # Test that killing AI unit triggers win
        gs.damage_unit("ai1", 8)
        assert gs.has_won() is True

    finally:
        os.remove(path)


def test_gamestate_with_turn_controller_integration():
    """Test GameState integration with turn controller."""
    gs = GameState()
    gs.add_unit("p1", "player", hp=10, ap=2)
    gs.add_unit("ai1", "ai", hp=10, ap=2)

    # Test that units are in turn controller
    assert "p1" in gs.turn_controller.units
    assert "ai1" in gs.turn_controller.units

    # Test current unit
    current_unit = gs.get_current_unit()
    assert current_unit in ["p1", "ai1"]

    # Test AI turn detection
    if current_unit == "ai1":
        assert gs.is_ai_turn() is True
    else:
        assert gs.is_ai_turn() is False


def test_gamestate_with_action_points_integration():
    """Test GameState integration with action points."""
    gs = GameState()
    gs.add_unit("p1", "player", hp=10, ap=3)

    # Test that AP was properly registered
    assert gs.ap_manager.get_ap("p1") == 3

    # Test that turn controller can check AP
    assert gs.turn_controller.can_act(1) is True
    assert gs.turn_controller.can_act(3) is True
    assert gs.turn_controller.can_act(4) is False


def test_gamestate_with_sim_runner_integration():
    """Test GameState integration with sim runner."""
    gs = GameState()
    gs.add_unit("p1", "player", hp=10, ap=2)
    gs.add_unit("ai1", "ai", hp=10, ap=2)

    # Test initial game state
    assert gs.is_game_over() is False

    # Test that sim runner tracks the game state
    assert gs.sim_runner.phase == "INIT"

    # Test that unit death is tracked in sim runner
    gs.damage_unit("ai1", 10)
    assert "ai1" in gs.sim_runner.dead_units


# === Performance Tests ===


def test_performance_large_number_of_units():
    """Test performance with large number of units."""
    gs = GameState()

    # Add 100 units (50 player, 50 AI)
    start_time = time.time()

    for i in range(50):
        gs.add_unit(f"p{i}", "player", hp=10, ap=2)
        gs.add_unit(f"ai{i}", "ai", hp=10, ap=2)

    add_time = time.time() - start_time

    # Test win condition calculation performance
    start_time = time.time()
    win_result = gs.has_won()
    win_time = time.time() - start_time

    # Test loss condition calculation performance
    start_time = time.time()
    loss_result = gs.has_lost()
    loss_time = time.time() - start_time

    # Performance assertions (should complete within reasonable time)
    assert add_time < 1.0  # Adding 100 units should take less than 1 second
    assert win_time < 0.1  # Win check should be very fast
    assert loss_time < 0.1  # Loss check should be very fast

    # Functional assertions
    assert win_result is False  # AI units are still alive
    assert loss_result is False  # Player units are still alive

    # Test performance of killing all AI units
    start_time = time.time()
    for i in range(50):
        gs.damage_unit(f"ai{i}", 10)
    kill_time = time.time() - start_time

    # Check win condition after killing all AI
    start_time = time.time()
    win_result = gs.has_won()
    win_check_time = time.time() - start_time

    assert kill_time < 1.0  # Killing 50 units should be fast
    assert win_check_time < 0.1  # Win check should still be fast
    assert win_result is True  # Should win after killing all AI


def test_performance_any_alive_method():
    """Test performance of any_alive method with many units."""
    gs = GameState()

    # Add 1000 units (500 player, 500 AI)
    for i in range(500):
        gs.add_unit(f"p{i}", "player", hp=10, ap=2)
        gs.add_unit(f"ai{i}", "ai", hp=10, ap=2)

    # Test performance of any_alive checks
    start_time = time.time()
    player_alive = gs.units.any_alive("player")
    player_time = time.time() - start_time

    start_time = time.time()
    ai_alive = gs.units.any_alive("ai")
    ai_time = time.time() - start_time

    # Performance assertions
    assert player_time < 0.1  # Should be very fast even with 1000 units
    assert ai_time < 0.1  # Should be very fast even with 1000 units

    # Functional assertions
    assert player_alive is True
    assert ai_alive is True


def test_performance_metadata_operations():
    """Test performance of metadata operations."""
    gs = GameState()

    # Test set_metadata performance
    start_time = time.time()
    for i in range(1000):
        gs.set_metadata(f"Scenario {i}", f"map_{i}", f"Objective {i}", i)
    metadata_time = time.time() - start_time

    # Test metadata access performance
    start_time = time.time()
    for i in range(1000):
        name = gs.name
        map_id = gs.map_id
        objective = gs.objective
        max_turns = gs.max_turns
    access_time = time.time() - start_time

    # Performance assertions
    assert metadata_time < 1.0  # Setting metadata 1000 times should be fast
    assert access_time < 0.1  # Accessing metadata should be very fast


def test_memory_usage_large_scenarios():
    """Test memory usage with large scenarios (basic test)."""
    gs = GameState()

    # Add many units to test memory usage
    for i in range(1000):
        gs.add_unit(f"unit_{i}", "player" if i % 2 == 0 else "ai", hp=10, ap=2)

    # Test that all operations still work
    assert gs.has_won() is False
    assert gs.has_lost() is False
    assert gs.units.any_alive("player") is True
    assert gs.units.any_alive("ai") is True

    # Test that we can still add more units
    gs.add_unit("extra_unit", "player", hp=10, ap=2)
    assert gs.units.is_alive("extra_unit") is True


# === Stress Tests ===


def test_stress_concurrent_operations():
    """Test stress: many concurrent operations."""
    gs = GameState()

    # Add units
    for i in range(100):
        gs.add_unit(f"unit_{i}", "player" if i % 2 == 0 else "ai", hp=10, ap=2)

    # Perform many operations rapidly
    start_time = time.time()
    for i in range(1000):
        # Alternate between different operations
        if i % 4 == 0:
            gs.has_won()
        elif i % 4 == 1:
            gs.has_lost()
        elif i % 4 == 2:
            gs.units.any_alive("player")
        else:
            gs.units.any_alive("ai")

    total_time = time.time() - start_time

    # Should complete within reasonable time
    assert total_time < 5.0  # 1000 operations should complete in under 5 seconds


def test_stress_rapid_unit_death():
    """Test stress: rapidly killing many units."""
    gs = GameState()

    # Add many units
    for i in range(200):
        gs.add_unit(f"unit_{i}", "player" if i % 2 == 0 else "ai", hp=10, ap=2)

    # Rapidly kill all units
    start_time = time.time()
    for i in range(200):
        gs.damage_unit(f"unit_{i}", 10)
    kill_time = time.time() - start_time

    # Check win/loss conditions after mass death
    start_time = time.time()
    win_result = gs.has_won()
    loss_result = gs.has_lost()
    check_time = time.time() - start_time

    # Performance assertions
    assert kill_time < 2.0  # Killing 200 units should be fast
    assert check_time < 0.1  # Win/loss check should be very fast

    # Functional assertions
    assert win_result is True  # All AI units are dead
    assert loss_result is True  # All player units are dead
