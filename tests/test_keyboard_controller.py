from game.input_state import InputState
from game.keyboard_controller import KeyboardController


def test_key_press_tracking():
    input_state = InputState()
    controller = KeyboardController(input_state)
    controller.handle_event({"type": "keydown", "key": "a"})
    assert "A" in input_state.keys_pressed  # keys_pressed is uppercase

    controller.handle_event({"type": "keyup", "key": "a"})
    assert "A" not in input_state.keys_pressed


def test_key_case_normalization():
    input_state = InputState()
    controller = KeyboardController(input_state)
    controller.handle_event({"type": "keydown", "key": "A"})
    assert "A" in input_state.keys_pressed
    controller.handle_event({"type": "keyup", "key": "A"})
    assert "A" not in input_state.keys_pressed


def test_multiple_keys():
    input_state = InputState()
    controller = KeyboardController(input_state)
    controller.handle_event({"type": "keydown", "key": "a"})
    controller.handle_event({"type": "keydown", "key": "b"})
    assert "A" in input_state.keys_pressed
    assert "B" in input_state.keys_pressed
    controller.handle_event({"type": "keyup", "key": "a"})
    assert "A" not in input_state.keys_pressed
    assert "B" in input_state.keys_pressed


def test_non_alpha_keys():
    input_state = InputState()
    controller = KeyboardController(input_state)
    controller.handle_event({"type": "keydown", "key": "1"})
    assert "1" in input_state.keys_pressed
    controller.handle_event({"type": "keyup", "key": "1"})
    assert "1" not in input_state.keys_pressed
