# @api
# @refactor - Using key normalization via InputState methods
class MCP:
    def __init__(self, input_state):
        self.input_state = input_state

    def process_input(self, event):
        if event["type"] == "keydown":
            self.input_state.set_key_down(event["key"])
        elif event["type"] == "keyup":
            self.input_state.set_key_up(event["key"])
        elif event["type"] == "mousebuttondown":
            self.input_state.set_mouse_click(event["pos"])
