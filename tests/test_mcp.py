from game.input_state import InputState
from game.mcp import MCP


def test_mouse_and_key_input():
    input_state = InputState()
    mcp = MCP(input_state)

    mcp.process_input({"type": "keydown", "key": "up"})
    assert "UP" in input_state.keys_pressed

    mcp.process_input({"type": "keyup", "key": "up"})
    assert "UP" not in input_state.keys_pressed

    mcp.process_input({"type": "mousebuttondown", "pos": (2, 3)})
    assert input_state.mouse_click == (2, 3)
