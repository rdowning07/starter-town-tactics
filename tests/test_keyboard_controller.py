import pytest

from game.input_state import InputState
from game.keyboard_controller import KeyboardController
from game.overlay_manager import OverlayManager


@pytest.fixture
def input_state():
    return InputState()


@pytest.fixture
def overlay_manager():
    return OverlayManager()


def test_toggle_overlays(input_state, overlay_manager, capsys):
    # Press keys '1' and '3' to toggle movement and terrain
    input_state.set_key_down("1")
    input_state.set_key_down("3")

    controller = KeyboardController(overlay_manager, debug=True)
    controller.update(input_state)

    # Check overlay visibility toggled
    assert overlay_manager.is_visible("movement") is False
    assert overlay_manager.is_visible("terrain") is True

    # Capture print output and confirm overlays are logged
    captured = capsys.readouterr().out
    assert "Current Overlays:" in captured
    assert "- movement: ❌" in captured
    assert "- terrain: ✅" in captured


def test_ignore_keys_without_overlay(input_state, overlay_manager, capsys):
    input_state.set_key_down("5")
    input_state.set_key_down("z")
    input_state.set_key_down("q")

    controller = KeyboardController(overlay_manager, debug=True)
    controller.update(input_state)

    # No changes expected
    assert overlay_manager.is_visible("movement") is True
    assert overlay_manager.is_visible("attack") is True

    captured = capsys.readouterr().out
    assert "Current Overlays:" not in captured  # nothing toggled, no print


def test_disable_debug_print(input_state, overlay_manager, capsys):
    input_state.set_key_down("2")

    controller = KeyboardController(overlay_manager, debug=False)
    controller.update(input_state)

    assert overlay_manager.is_visible("threat") is False
    captured = capsys.readouterr().out
    # OverlayManager always prints, but KeyboardController doesn't when debug=False
    assert "[OverlayManager]" in captured  # OverlayManager prints
    assert "Current Overlays:" not in captured  # KeyboardController doesn't print


def test_rebind_overlay_key(input_state, overlay_manager):
    controller = KeyboardController(overlay_manager)
    controller.bind_overlay_key("x", "terrain")

    input_state.set_key_down("x")
    controller.update(input_state)

    assert overlay_manager.is_visible("terrain") is True


def test_snapshot_api_returns_state(overlay_manager):
    controller = KeyboardController(overlay_manager)
    snapshot = controller.get_overlay_state_snapshot()
    assert isinstance(snapshot, dict)
    assert "movement" in snapshot
    assert snapshot["movement"] is True


def test_no_overlay_manager_graceful(input_state):
    controller = KeyboardController(None, debug=True)
    input_state.set_key_down("1")
    controller.update(input_state)

    snapshot = controller.get_overlay_state_snapshot()
    assert snapshot == {}  # returns empty safely
