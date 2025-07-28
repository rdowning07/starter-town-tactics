from game.input_state import InputState
from game.keyboard_controller import KeyboardController


def test_key_press_tracking():
    input_state = InputState()
    controller = KeyboardController(input_state)
    controller.handle_event({"type": "keydown", "key": "a"})
    assert "a" in input_state.keys_pressed

    controller.handle_event({"type": "keyup", "key": "a"})
    assert "a" not in input_state.keys_pressed
