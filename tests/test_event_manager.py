"""Tests for EventManager."""

from unittest.mock import Mock

import pytest

from game.event_manager import EventManager


@pytest.fixture
def mock_game_state():
    """Mock game state for testing."""
    game_state = Mock()
    game_state.add_unit = Mock()
    game_state.trigger_fx = Mock()
    return game_state


@pytest.fixture
def event_manager(mock_game_state):
    """EventManager instance for testing."""
    return EventManager(mock_game_state)


def test_event_manager_initialization(event_manager):
    """Test that EventManager initializes correctly."""
    assert event_manager.turn_count == 0
    assert event_manager.triggered_events == []
    assert event_manager.event_history == []
    assert event_manager.game_state is not None


def test_advance_turn(event_manager):
    """Test advancing a turn."""
    event_manager.advance_turn()
    assert event_manager.turn_count == 1


def test_trigger_reinforcements(event_manager, mock_game_state):
    """Test triggering reinforcements."""
    event_manager.turn_count = 4  # Set to 4, so advance_turn() makes it 5
    event_manager.advance_turn()

    assert "reinforcements" in event_manager.triggered_events
    assert mock_game_state.add_unit.call_count == 2
    assert len(event_manager.event_history) == 1
    assert event_manager.event_history[0]["event"] == "reinforcements"


def test_trigger_storm(event_manager, mock_game_state):
    """Test triggering storm."""
    event_manager.turn_count = 9  # Set to 9, so advance_turn() makes it 10
    event_manager.advance_turn()

    assert "storm" in event_manager.triggered_events
    mock_game_state.trigger_fx.assert_called_once()
    assert len(event_manager.event_history) == 1
    assert event_manager.event_history[0]["event"] == "storm"


def test_trigger_boss_phase(event_manager, mock_game_state):
    """Test triggering boss phase."""
    event_manager.turn_count = 14  # Set to 14, so advance_turn() makes it 15
    event_manager.advance_turn()

    assert "boss_phase" in event_manager.triggered_events
    mock_game_state.trigger_fx.assert_called_once()
    assert len(event_manager.event_history) == 1
    assert event_manager.event_history[0]["event"] == "boss_phase"


def test_multiple_turn_advances(event_manager):
    """Test advancing multiple turns."""
    for i in range(3):
        event_manager.advance_turn()

    assert event_manager.turn_count == 3


def test_events_trigger_only_once(event_manager, mock_game_state):
    """Test that events only trigger once."""
    # Trigger reinforcements
    event_manager.turn_count = 4  # Set to 4, so advance_turn() makes it 5
    event_manager.advance_turn()

    # Try to trigger again
    event_manager.advance_turn()

    # Should only have triggered once
    assert event_manager.triggered_events.count("reinforcements") == 1
    assert mock_game_state.add_unit.call_count == 2  # Only called once


def test_get_turn_count(event_manager):
    """Test getting turn count."""
    event_manager.turn_count = 5
    assert event_manager.get_turn_count() == 5


def test_get_triggered_events(event_manager):
    """Test getting triggered events."""
    event_manager.triggered_events = ["reinforcements", "storm"]
    events = event_manager.get_triggered_events()
    assert events == ["reinforcements", "storm"]


def test_get_event_history(event_manager):
    """Test getting event history."""
    event_manager.event_history = [{"turn": 5, "event": "reinforcements", "description": "test"}]
    history = event_manager.get_event_history()
    assert history == [{"turn": 5, "event": "reinforcements", "description": "test"}]


def test_reset(event_manager):
    """Test resetting event manager."""
    event_manager.turn_count = 10
    event_manager.triggered_events = ["test"]
    event_manager.event_history = [{"test": "data"}]

    event_manager.reset()

    assert event_manager.turn_count == 0
    assert event_manager.triggered_events == []
    assert event_manager.event_history == []


def test_has_event_triggered(event_manager):
    """Test checking if event has been triggered."""
    event_manager.triggered_events = ["reinforcements"]

    assert event_manager.has_event_triggered("reinforcements") is True
    assert event_manager.has_event_triggered("storm") is False


def test_multiple_events_trigger(event_manager, mock_game_state):
    """Test that multiple events can trigger in sequence."""
    # Advance to turn 15 (should trigger reinforcements at 5, storm at 10, boss at 15)
    for i in range(15):
        event_manager.advance_turn()

    assert "reinforcements" in event_manager.triggered_events
    assert "storm" in event_manager.triggered_events
    assert "boss_phase" in event_manager.triggered_events
    assert len(event_manager.event_history) == 3


def test_event_history_structure(event_manager, mock_game_state):
    """Test that event history has correct structure."""
    event_manager.turn_count = 4  # Set to 4, so advance_turn() makes it 5
    event_manager.advance_turn()

    history_entry = event_manager.event_history[0]
    assert "turn" in history_entry
    assert "event" in history_entry
    assert "description" in history_entry
    assert history_entry["turn"] == 5  # Turn count after advance
    assert history_entry["event"] == "reinforcements"


def test_no_events_before_triggers(event_manager):
    """Test that no events trigger before their turn thresholds."""
    for i in range(4):  # Advance to turn 4
        event_manager.advance_turn()

    assert event_manager.triggered_events == []
    assert event_manager.event_history == []
