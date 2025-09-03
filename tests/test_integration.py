"""
Integration tests for the demo system with real game APIs.
"""

import json
import tempfile
from pathlib import Path

import pytest

from loaders.demo_loader import load_state
from tools.record_simlog import dump_simlog


def test_demo_loader_creates_valid_game_state():
    """Test that demo loader creates a properly wired GameState."""
    game_state = load_state("assets/scenarios/demo.yaml")

    # Check that all required components are present
    assert hasattr(game_state, "units")
    assert hasattr(game_state, "turn_controller")
    assert hasattr(game_state, "sim_runner")
    assert hasattr(game_state, "sprite_manager")
    assert hasattr(game_state, "fx_manager")
    assert hasattr(game_state, "sound_manager")

    # Check that units are loaded
    assert len(game_state.units.units) > 0

    # Check that sim runner is wired
    assert game_state.sim_runner.game_state == game_state


def test_simlog_recording():
    """Test that simulation logs can be recorded."""
    game_state = load_state("assets/scenarios/demo.yaml")

    # Run a few turns to generate logs
    for _ in range(5):
        game_state.sim_runner.run_turn()

    # Record logs to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        dump_simlog(game_state, f)
        temp_path = f.name

    try:
        # Verify logs were written
        with open(temp_path, "r") as f:
            lines = f.readlines()
            assert len(lines) > 0

            # Verify each line is valid JSON
            for line in lines:
                entry = json.loads(line.strip())
                assert "event" in entry
    finally:
        Path(temp_path).unlink()


def test_game_state_helpers():
    """Test that game state helper methods work correctly."""
    game_state = load_state("assets/scenarios/demo.yaml")

    # Initially not game over
    assert not game_state.is_game_over()

    # Run until game over or max turns
    for _ in range(100):
        game_state.sim_runner.run_turn()
        if game_state.is_game_over():
            break

    # Should eventually reach game over state
    assert game_state.is_game_over()


def test_overlay_state_compatibility():
    """Test that overlay state is compatible with renderer."""
    from adapters.pygame.overlay_state import OverlayState

    overlay = OverlayState()

    # Check that required fields exist
    assert hasattr(overlay, "show_movement")
    assert hasattr(overlay, "movement_tiles")
    assert hasattr(overlay, "show_threat")
    assert hasattr(overlay, "threat_tiles")

    # Check default values
    assert overlay.show_movement is True
    assert overlay.show_threat is True
    assert isinstance(overlay.movement_tiles, set)
    assert isinstance(overlay.threat_tiles, set)
