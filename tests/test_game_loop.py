"""Tests for the enhanced game loop implementation."""

import pytest
from unittest.mock import Mock, patch
import time

from game.game_loop import (
    game_loop, process_player_input, handle_triggered_events,
    handle_reinforcement_effects, handle_storm_effects, handle_boss_phase_effects,
    render_game_state, demo_game_loop
)
from game.game_state import GameState


@pytest.fixture
def game_state():
    """Create a GameState for testing."""
    return GameState()


@pytest.fixture
def mock_game_state():
    """Create a mock GameState for testing."""
    game_state = Mock()
    game_state.is_game_over.return_value = False
    game_state.advance_turn.return_value = None
    game_state.get_current_objective.return_value = "Defeat all enemies!"
    game_state.get_turn_count.return_value = 1
    game_state.get_triggered_events.return_value = []
    game_state.has_won.return_value = False
    game_state.has_lost.return_value = False
    
    # Mock units
    mock_units = Mock()
    mock_units.get_all_units.return_value = {
        "player1": {"team": "player", "hp": 10},
        "enemy1": {"team": "enemy", "hp": 8}
    }
    mock_units.is_alive.return_value = True
    game_state.units = mock_units
    
    return game_state


def test_process_player_input_player_turn(mock_game_state):
    """Test processing player input during player turn."""
    mock_game_state.is_ai_turn.return_value = False
    
    # Should not raise any exceptions
    process_player_input(mock_game_state)


def test_process_player_input_ai_turn(mock_game_state):
    """Test processing player input during AI turn."""
    mock_game_state.is_ai_turn.return_value = True
    
    # Should not raise any exceptions
    process_player_input(mock_game_state)


def test_handle_triggered_events_empty(mock_game_state):
    """Test handling empty triggered events list."""
    # Should not raise any exceptions
    handle_triggered_events(mock_game_state, [])


def test_handle_triggered_events_reinforcements(mock_game_state):
    """Test handling reinforcements event."""
    with patch('game.game_loop.handle_reinforcement_effects') as mock_handler:
        handle_triggered_events(mock_game_state, ["reinforcements"])
        mock_handler.assert_called_once_with(mock_game_state)


def test_handle_triggered_events_storm(mock_game_state):
    """Test handling storm event."""
    with patch('game.game_loop.handle_storm_effects') as mock_handler:
        handle_triggered_events(mock_game_state, ["storm"])
        mock_handler.assert_called_once_with(mock_game_state)


def test_handle_triggered_events_boss_phase(mock_game_state):
    """Test handling boss phase event."""
    with patch('game.game_loop.handle_boss_phase_effects') as mock_handler:
        handle_triggered_events(mock_game_state, ["boss_phase"])
        mock_handler.assert_called_once_with(mock_game_state)


def test_handle_triggered_events_multiple(mock_game_state):
    """Test handling multiple events."""
    with patch('game.game_loop.handle_reinforcement_effects') as mock_reinforcements, \
         patch('game.game_loop.handle_storm_effects') as mock_storm:
        
        handle_triggered_events(mock_game_state, ["reinforcements", "storm"])
        
        mock_reinforcements.assert_called_once_with(mock_game_state)
        mock_storm.assert_called_once_with(mock_game_state)


def test_handle_reinforcement_effects(mock_game_state):
    """Test reinforcement effects handler."""
    # Should not raise any exceptions
    handle_reinforcement_effects(mock_game_state)


def test_handle_storm_effects(mock_game_state):
    """Test storm effects handler."""
    # Should not raise any exceptions
    handle_storm_effects(mock_game_state)


def test_handle_boss_phase_effects(mock_game_state):
    """Test boss phase effects handler."""
    # Should not raise any exceptions
    handle_boss_phase_effects(mock_game_state)


def test_render_game_state(mock_game_state):
    """Test rendering game state."""
    # Should not raise any exceptions
    render_game_state(mock_game_state)


def test_render_game_state_empty_units(mock_game_state):
    """Test rendering game state with no units."""
    mock_game_state.units.get_all_units.return_value = {}
    
    # Should not raise any exceptions
    render_game_state(mock_game_state)


def test_game_loop_single_turn(mock_game_state):
    """Test game loop for a single turn."""
    # Set up mock to return True after first call (game over)
    mock_game_state.is_game_over.side_effect = [False, True]
    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = False
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        game_loop(mock_game_state, max_turns=1)
    
    # Verify that advance_turn was called
    mock_game_state.advance_turn.assert_called_once()


def test_game_loop_max_turns(mock_game_state):
    """Test game loop with maximum turns limit."""
    # Game never ends, but max_turns should stop it
    mock_game_state.is_game_over.return_value = False
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        game_loop(mock_game_state, max_turns=3)
    
    # Verify that advance_turn was called 3 times
    assert mock_game_state.advance_turn.call_count == 3


def test_game_loop_victory(mock_game_state):
    """Test game loop ending with victory."""
    mock_game_state.is_game_over.side_effect = [False, True]
    mock_game_state.has_won.return_value = True
    mock_game_state.has_lost.return_value = False
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        game_loop(mock_game_state, max_turns=1)
    
    mock_game_state.advance_turn.assert_called_once()


def test_game_loop_defeat(mock_game_state):
    """Test game loop ending with defeat."""
    mock_game_state.is_game_over.side_effect = [False, True]
    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = True
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        game_loop(mock_game_state, max_turns=1)
    
    mock_game_state.advance_turn.assert_called_once()


def test_game_loop_with_events(mock_game_state):
    """Test game loop with triggered events."""
    mock_game_state.is_game_over.side_effect = [False, True]
    mock_game_state.get_triggered_events.return_value = ["reinforcements"]
    mock_game_state.has_won.return_value = False
    mock_game_state.has_lost.return_value = False
    
    with patch('time.sleep'), \
         patch('game.game_loop.handle_reinforcement_effects') as mock_handler:
        
        game_loop(mock_game_state, max_turns=1)
        
        mock_handler.assert_called_once_with(mock_game_state)


@patch('devtools.scenario_manager.create_scenario_manager')
def test_demo_game_loop_success(mock_create_scenario_manager, mock_game_state):
    """Test successful demo game loop."""
    # Mock scenario manager
    mock_scenario_manager = Mock()
    mock_scenario_manager.load_scenario.return_value = mock_game_state
    mock_create_scenario_manager.return_value = mock_scenario_manager
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        demo_game_loop("test_scenario.yaml", max_turns=1)
    
    mock_scenario_manager.load_scenario.assert_called_once_with("test_scenario.yaml")


@patch('devtools.scenario_manager.create_scenario_manager')
def test_demo_game_loop_file_not_found(mock_create_scenario_manager):
    """Test demo game loop with missing scenario file."""
    # Mock scenario manager to raise FileNotFoundError
    mock_scenario_manager = Mock()
    mock_scenario_manager.load_scenario.side_effect = FileNotFoundError("File not found")
    mock_create_scenario_manager.return_value = mock_scenario_manager
    
    demo_game_loop("missing_scenario.yaml", max_turns=1)
    # Should handle the error gracefully


@patch('devtools.scenario_manager.create_scenario_manager')
def test_demo_game_loop_general_error(mock_create_scenario_manager):
    """Test demo game loop with general error."""
    # Mock scenario manager to raise general exception
    mock_scenario_manager = Mock()
    mock_scenario_manager.load_scenario.side_effect = Exception("General error")
    mock_create_scenario_manager.return_value = mock_scenario_manager
    
    demo_game_loop("error_scenario.yaml", max_turns=1)
    # Should handle the error gracefully


def test_game_loop_integration_with_real_game_state():
    """Test game loop integration with real GameState."""
    game_state = GameState()
    
    # Add some units to make the game state valid
    game_state.add_unit("player1", "player", ap=3, hp=10)
    game_state.add_unit("enemy1", "enemy", ap=3, hp=10)
    
    # Mock the game to end after one turn
    original_is_game_over = game_state.is_game_over
    
    def mock_is_game_over():
        # Return True after first call to end the game
        if not hasattr(mock_is_game_over, 'called'):
            mock_is_game_over.called = True
            return False
        return True
    
    game_state.is_game_over = mock_is_game_over
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        game_loop(game_state, max_turns=1)
    
    # Verify that the turn was advanced
    assert game_state.get_turn_count() == 1


def test_game_loop_objective_updates():
    """Test that objectives are updated during game loop."""
    game_state = GameState()
    
    # Add some units
    game_state.add_unit("player1", "player", ap=3, hp=10)
    game_state.add_unit("enemy1", "enemy", ap=3, hp=10)
    
    # Mock the game to end after one turn
    original_is_game_over = game_state.is_game_over
    
    def mock_is_game_over():
        if not hasattr(mock_is_game_over, 'called'):
            mock_is_game_over.called = True
            return False
        return True
    
    game_state.is_game_over = mock_is_game_over
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        game_loop(game_state, max_turns=1)
    
    # Verify that objectives were updated
    current_objective = game_state.get_current_objective()
    assert current_objective in [
        "Defeat all enemies!",
        "Survive until reinforcements arrive!",
        "Victory! The enemies have been defeated.",
        "Defeat. You lost the battle."
    ]
