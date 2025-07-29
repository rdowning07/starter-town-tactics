from game.gamepad_controller import GamepadController
from game.input_state import InputState


def test_gamepad_movement_buttons():
    input_state = InputState()
    controller = GamepadController(input_state)
    controller.update({0})  # Simulate up
    assert "UP" in input_state.keys_pressed
