from game.input_state import InputState

# Button constants for gamepad
UP_BUTTON = 0
DOWN_BUTTON = 1
LEFT_BUTTON = 2
RIGHT_BUTTON = 3
CONFIRM_BUTTON = 4
CANCEL_BUTTON = 5

class GamepadController:
    def __init__(self, input_state: InputState):
        self.input_state = input_state

    def update(self, pressed_buttons: set[int]):
        if UP_BUTTON in pressed_buttons:
            self.input_state.move_cursor(0, -1)
        if DOWN_BUTTON in pressed_buttons:
            self.input_state.move_cursor(0, 1)
        if LEFT_BUTTON in pressed_buttons:
            self.input_state.move_cursor(-1, 0)
        if RIGHT_BUTTON in pressed_buttons:
            self.input_state.move_cursor(1, 0)
        if CONFIRM_BUTTON in pressed_buttons:
            self.input_state.confirm_selection()
        if CANCEL_BUTTON in pressed_buttons:
            self.input_state.cancel_selection()
