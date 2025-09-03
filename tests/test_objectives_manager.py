"""Tests for ObjectivesManager."""

from unittest.mock import Mock

import pytest

from game.objectives_manager import ObjectivesManager


@pytest.fixture
def mock_game_state():
    """Mock game state for testing."""
    game_state = Mock()
    game_state.units = Mock()
    return game_state


@pytest.fixture
def objectives_manager(mock_game_state):
    """ObjectivesManager instance for testing."""
    return ObjectivesManager(mock_game_state)


def test_objectives_manager_initialization(objectives_manager):
    """Test that ObjectivesManager initializes correctly."""
    assert objectives_manager.current_objective == ""
    assert objectives_manager.objective_history == []
    assert objectives_manager.game_state is not None


def test_set_objective(objectives_manager):
    """Test setting an objective."""
    objectives_manager.set_objective("Test Objective")
    assert objectives_manager.current_objective == "Test Objective"
    assert len(objectives_manager.objective_history) == 1
    assert objectives_manager.objective_history[0] == ""


def test_set_objective_no_duplicate(objectives_manager):
    """Test that setting the same objective doesn't add to history."""
    objectives_manager.set_objective("Test Objective")
    objectives_manager.set_objective("Test Objective")
    assert objectives_manager.current_objective == "Test Objective"
    assert len(objectives_manager.objective_history) == 1


def test_get_current_objective(objectives_manager):
    """Test getting the current objective."""
    objectives_manager.set_objective("Test Objective")
    assert objectives_manager.get_current_objective() == "Test Objective"


def test_get_objective_history(objectives_manager):
    """Test getting objective history."""
    objectives_manager.set_objective("Objective 1")
    objectives_manager.set_objective("Objective 2")
    history = objectives_manager.get_objective_history()
    assert history == ["", "Objective 1"]


def test_update_objectives_victory(objectives_manager, mock_game_state):
    """Test objective update when player wins."""
    mock_game_state.has_won.return_value = True
    mock_game_state.has_lost.return_value = False

    objectives_manager.update_objectives()

    assert objectives_manager.current_objective == "Victory! The enemies have been defeated."


def test_update_objectives_defeat(objectives_manager, mock_game_state):
    """Test objective update when player loses."""
    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = True

    objectives_manager.update_objectives()

    assert objectives_manager.current_objective == "Defeat. You lost the battle."


def test_update_objectives_survive(objectives_manager, mock_game_state):
    """Test objective update when all enemies defeated but game continues."""
    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = False
    mock_game_state.units.any_effectively_alive.return_value = False

    objectives_manager.update_objectives()

    assert objectives_manager.current_objective == "Survive until reinforcements arrive!"


def test_update_objectives_defeat_enemies(objectives_manager, mock_game_state):
    """Test objective update when enemies still alive."""
    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = False
    mock_game_state.units.any_effectively_alive.return_value = True

    objectives_manager.update_objectives()

    assert objectives_manager.current_objective == "Defeat all enemies!"


def test_reset(objectives_manager):
    """Test resetting objectives."""
    objectives_manager.set_objective("Test Objective")
    objectives_manager.reset()

    assert objectives_manager.current_objective == ""
    assert objectives_manager.objective_history == []


def test_objective_flow_victory(mock_game_state):
    """Test the objective flow function with victory."""
    from game.objectives_manager import update_objective_flow

    mock_game_state.has_won.return_value = True
    mock_game_state.has_lost.return_value = False

    objectives_manager = ObjectivesManager(mock_game_state)
    update_objective_flow(mock_game_state, objectives_manager)

    assert objectives_manager.current_objective == "Victory! The enemies have been defeated."


def test_objective_flow_defeat(mock_game_state):
    """Test the objective flow function with defeat."""
    from game.objectives_manager import update_objective_flow

    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = True

    objectives_manager = ObjectivesManager(mock_game_state)
    update_objective_flow(mock_game_state, objectives_manager)

    assert objectives_manager.current_objective == "Defeat. You lost the battle."


def test_objective_flow_ongoing(mock_game_state):
    """Test the objective flow function with ongoing game."""
    from game.objectives_manager import update_objective_flow

    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = False
    mock_game_state.units.any_effectively_alive.return_value = True

    objectives_manager = ObjectivesManager(mock_game_state)
    update_objective_flow(mock_game_state, objectives_manager)

    assert objectives_manager.current_objective == "Defeat all enemies!"
