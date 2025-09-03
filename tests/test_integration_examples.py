"""Integration test examples for the enhanced gameflow system."""

from unittest.mock import MagicMock, Mock

import pytest

from game.ai_controller import AIController
from game.event_manager import EventManager
from game.game_state import GameState
from game.objectives_manager import ObjectivesManager, update_objective_flow


@pytest.fixture
def game_state():
    """Create a real GameState for integration testing."""
    return GameState()


@pytest.fixture
def objectives_manager(game_state):
    """Create ObjectivesManager with real GameState."""
    return ObjectivesManager(game_state)


@pytest.fixture
def event_manager(game_state):
    """Create EventManager with real GameState."""
    return EventManager(game_state)


@pytest.fixture
def ai_controller():
    """Create AIController for testing."""
    return AIController([])


def test_objective_update_on_battle_win(game_state, objectives_manager):
    """Test objective update when player wins the battle."""
    # Mock the has_won method to return True
    game_state.has_won = Mock(return_value=True)
    game_state.has_lost = Mock(return_value=False)

    update_objective_flow(game_state, objectives_manager)

    assert objectives_manager.current_objective == "Victory! The enemies have been defeated."


def test_ai_retreat_when_low_health(ai_controller, game_state):
    """Test AI retreat behavior when health is low."""
    # Setup AI controller with game state
    ai_controller.set_game_state(game_state)

    # Create a mock unit with defensive AI and low health
    ai_unit = MagicMock()
    ai_unit.hp = 4
    ai_unit.max_hp = 10
    ai_unit.ai = "defensive"
    ai_unit.name = "defensive_unit"
    ai_unit.x = 5  # Set position attributes
    ai_unit.y = 5

    # Mock the move_to method that retreat uses
    ai_unit.move_to = MagicMock()

    # Call decide_action
    ai_controller.decide_action(ai_unit)

    # Check that move_to was called (retreat behavior)
    ai_unit.move_to.assert_called_once()


def test_reinforcements_triggered_after_5_turns(event_manager, game_state):
    """Test that reinforcements are triggered after 5 turns."""
    # Mock the add_unit method to track calls
    game_state.add_unit = Mock()

    # Simulate 5 turns
    for _ in range(5):
        event_manager.advance_turn()

    # Check if reinforcements event was triggered
    assert "reinforcements" in event_manager.triggered_events

    # Check that the specific reinforcement units were added
    game_state.add_unit.assert_any_call("reinforcement_1", "player", ap=3, hp=15)
    game_state.add_unit.assert_any_call("reinforcement_2", "player", ap=3, hp=15)

    # Verify exactly 2 units were added
    assert game_state.add_unit.call_count == 2


def test_game_loop_integration(game_state):
    """Test the integrated game loop functionality."""
    # Add some units to make the game state valid
    game_state.add_unit("player1", "player", ap=3, hp=10)
    game_state.add_unit("enemy1", "enemy", ap=3, hp=10)

    # Test advancing turns
    for turn in range(1, 6):  # Advance 5 turns
        game_state.advance_turn()

        # Check turn count
        assert game_state.get_turn_count() == turn

        # Check that objectives are being updated
        current_objective = game_state.get_current_objective()
        assert current_objective in [
            "Defeat all enemies!",
            "Survive until reinforcements arrive!",
            "Victory! The enemies have been defeated.",
            "Defeat. You lost the battle.",
        ]

    # Check that reinforcements were triggered
    assert game_state.has_event_triggered("reinforcements")


def test_ai_behavior_integration(ai_controller, game_state):
    """Test AI behavior integration with different personality types."""
    # Setup AI controller
    ai_controller.set_game_state(game_state)

    # Add some units for AI to interact with
    game_state.add_unit("player1", "player", ap=3, hp=10)

    # Test aggressive AI
    aggressive_unit = MagicMock()
    aggressive_unit.hp = 10
    aggressive_unit.max_hp = 10
    aggressive_unit.ai = "aggressive"
    aggressive_unit.name = "aggressive_unit"

    ai_controller.decide_action(aggressive_unit)
    # Should print aggressive behavior message

    # Test defensive AI with low health
    defensive_unit = MagicMock()
    defensive_unit.hp = 3
    defensive_unit.max_hp = 10
    defensive_unit.ai = "defensive"
    defensive_unit.name = "defensive_unit"
    defensive_unit.x = 5  # Set position attributes
    defensive_unit.y = 5
    defensive_unit.move_to = MagicMock()

    ai_controller.decide_action(defensive_unit)
    # Should trigger retreat behavior
    defensive_unit.move_to.assert_called_once()


def test_event_sequence_integration(event_manager, game_state):
    """Test that events trigger in the correct sequence."""
    # Mock add_unit and trigger_fx
    game_state.add_unit = Mock()
    game_state.trigger_fx = Mock()

    # Advance through all event triggers
    for turn in range(1, 16):  # Advance to turn 15
        event_manager.advance_turn()

        if turn == 5:
            # Check reinforcements triggered
            assert "reinforcements" in event_manager.triggered_events
            assert game_state.add_unit.call_count == 2

        if turn == 10:
            # Check storm triggered
            assert "storm" in event_manager.triggered_events
            assert game_state.trigger_fx.call_count >= 1

        if turn == 15:
            # Check boss phase triggered
            assert "boss_phase" in event_manager.triggered_events
            assert game_state.trigger_fx.call_count >= 2

    # Verify all events were triggered
    assert len(event_manager.triggered_events) == 3
    assert "reinforcements" in event_manager.triggered_events
    assert "storm" in event_manager.triggered_events
    assert "boss_phase" in event_manager.triggered_events


def test_objective_history_tracking(objectives_manager):
    """Test that objective history is properly tracked."""
    # Set initial objective
    objectives_manager.set_objective("Initial Objective")

    # Change objective
    objectives_manager.set_objective("Second Objective")

    # Check history
    history = objectives_manager.get_objective_history()
    assert len(history) == 2
    assert history[0] == ""  # Initial empty state
    assert history[1] == "Initial Objective"


def test_event_history_tracking(event_manager, game_state):
    """Test that event history is properly tracked."""
    # Mock add_unit
    game_state.add_unit = Mock()

    # Trigger reinforcements
    event_manager.turn_count = 4
    event_manager.advance_turn()

    # Check event history
    history = event_manager.get_event_history()
    assert len(history) == 1
    assert history[0]["event"] == "reinforcements"
    assert history[0]["turn"] == 5
    assert "reinforcements" in history[0]["description"]
