from game.gamepad_controller import (
    CANCEL_BUTTON,
    CONFIRM_BUTTON,
    DOWN_BUTTON,
    LEFT_BUTTON,
    RIGHT_BUTTON,
    UP_BUTTON,
    GamepadController,
)
from game.input_state import InputState


def test_gamepad_up_button_moves_cursor():
    input_state = InputState()
    controller = GamepadController(input_state)
    controller.update({UP_BUTTON})
    assert "UP" in input_state.keys_pressed


def test_gamepad_down_button_moves_cursor():
    input_state = InputState()
    controller = GamepadController(input_state)
    controller.update({DOWN_BUTTON})
    assert "DOWN" in input_state.keys_pressed


def test_gamepad_left_button_moves_cursor():
    input_state = InputState()
    controller = GamepadController(input_state)
    controller.update({LEFT_BUTTON})
    assert "LEFT" in input_state.keys_pressed


def test_gamepad_right_button_moves_cursor():
    input_state = InputState()
    controller = GamepadController(input_state)
    controller.update({RIGHT_BUTTON})
    assert "RIGHT" in input_state.keys_pressed


def test_gamepad_confirm_button_confirms_selection(monkeypatch):
    input_state = InputState()
    controller = GamepadController(input_state)
    called = {}

    def fake_confirm():
        called["yes"] = True

    input_state.confirm_selection = fake_confirm
    controller.update({CONFIRM_BUTTON})
    assert "CONFIRM" in input_state.keys_pressed
    assert called.get("yes")


def test_gamepad_cancel_button_cancels_selection(monkeypatch):
    input_state = InputState()
    controller = GamepadController(input_state)
    called = {}

    def fake_cancel():
        called["yes"] = True

    input_state.cancel_selection = fake_cancel
    controller.update({CANCEL_BUTTON})
    assert "CANCEL" in input_state.keys_pressed
    assert called.get("yes")
