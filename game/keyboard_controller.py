class KeyboardController:
    def __init__(self, input_state):
        self.input_state = input_state

    def handle_event(self, event):
        if event["type"] == "keydown":
            self.input_state.key_states.add(event["key"])
        elif event["type"] == "keyup":
            self.input_state.key_states.discard(event["key"])
