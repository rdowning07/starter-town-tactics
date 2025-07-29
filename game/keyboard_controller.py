# @api
# @refactor - Fixed key casing contract drift
class KeyboardController:
    def __init__(self, input_state):
        self.input_state = input_state

    def handle_event(self, event):
        if event["type"] == "keydown":
            self.input_state.set_key_down(event["key"])
        elif event["type"] == "keyup":
            self.input_state.set_key_up(event["key"])
