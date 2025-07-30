from game.input_state import InputState


# @api
# @refactor - Fixed key casing contract drift
class KeyboardController:
    """
    Handles keyboard events and updates the InputState accordingly.

    Args:
        input_state (InputState): The input state to update.
    """

    def __init__(self, input_state: InputState):
        self.input_state = input_state

    def handle_event(self, event: dict) -> None:
        """
        Handle a keyboard event.

        Args:
            event (dict): Should have keys 'type' ('keydown' or 'keyup') and 'key' (str).
        """
        if event["type"] == "keydown":
            self.input_state.set_key_down(event["key"])
        elif event["type"] == "keyup":
            self.input_state.set_key_up(event["key"])
