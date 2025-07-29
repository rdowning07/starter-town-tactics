# context_registry.py

"""
Tracks canonical interfaces for game architecture modules.
Use this file to validate structure across tests, refactors, and future sessions.
"""

# @api InputState
INPUT_STATE_API = {
    "keys_pressed": set,
    "cursor_x": int,
    "cursor_y": int,
    "selected_unit": "Unit | None",
    "state": str,
    "confirm_selection()": "None",
    "move_cursor(dx: int, dy: int)": "None",
}

# @api KeyboardController
KEYBOARD_CONTROLLER_API = {
    "handle_event(event: dict)": "None",
}

# @api GamepadController
GAMEPAD_CONTROLLER_API = {
    "update(buttons: set[int])": "None",
}

# @api MCP
MCP_API = {
    "process_input(input_event: dict)": "None",
}

# @api SimRunner
SIM_RUNNER_API = {
    "run()": "None",
    "log": list,
}

# @api TurnController
TURN_CONTROLLER_API = {
    "game": "Game",
    "next_turn()": "None",
    "end_turn()": "None",
    "is_ai_turn()": bool,
}

# @api Unit
UNIT_API = {
    "x": int,
    "y": int,
    "team": str,
    "move_range": int,
    "is_alive()": bool,
    "move(x: int, y: int, grid: 'Grid')": bool,
    "move_to(x: int, y: int)": "None",
}

# @api Game
GAME_API = {
    "grid": "Grid",
    "add_unit(unit: Unit)": "None",
    "get_current_unit()": "Unit",
    "is_over()": bool,
}

# @api Tile
TILE_API = {
    "terrain_type": str,
    "movement_cost": int,
    "get_symbol()": str,
}
