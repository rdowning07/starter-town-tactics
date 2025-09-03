"""
Input Handler - manages mouse and keyboard input with game state integration.
Integrated with GameState, SimRunner, and TurnController architecture.
"""

from typing import Callable, Optional, Tuple

import pygame

from game.ui.ui_state import UIState


# @api
# @refactor
def screen_to_tile(pos: tuple[int, int], tile_size: int) -> tuple[int, int]:
    """Convert pixel coordinates to tile coordinates."""
    x, y = pos
    return (x // tile_size, y // tile_size)


def get_unit_at_tile(game_state, tile: Tuple[int, int]) -> Optional[str]:
    """Get unit at tile position from game state."""
    if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
        return None

    # Check if any unit is at this tile
    for unit_id, unit_data in game_state.units.units.items():
        if (unit_data.get("x"), unit_data.get("y")) == tile:
            return unit_id

    return None


def handle_mouse_input(event: pygame.event.Event, ui_state: UIState, tile_size: int, game_state=None):
    """Handle mouse click/hover events with game state integration."""
    if event.type == pygame.MOUSEMOTION:
        ui_state.update_hover(screen_to_tile(event.pos, tile_size))

    elif event.type == pygame.MOUSEBUTTONDOWN:
        tile = screen_to_tile(event.pos, tile_size)

        # Try to get unit from game state if available
        unit_id = None
        if game_state:
            unit_id = get_unit_at_tile(game_state, tile)
        else:
            # Fallback to stub for Week 1 compatibility
            unit_id = get_unit_at_tile_stub(tile)

        if unit_id is not None:
            ui_state.select_unit(unit_id)
            ui_state.action_menu_pos = event.pos
        else:
            ui_state.deselect_unit()


def handle_keyboard_input(event: pygame.event.Event, ui_state: UIState, game_state=None):
    """Handle keyboard input with game state integration."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            ui_state.reset_selection()
        elif event.key == pygame.K_SPACE and game_state:
            # End turn if it's player's turn
            if hasattr(game_state, "sim_runner") and not game_state.sim_runner.is_ai_turn():
                game_state.sim_runner.run_turn()


def get_unit_at_tile_stub(tile: Tuple[int, int]) -> Optional[str]:
    """Stub get_unit_at_tile for Week 1 compatibility - return 1 if top-left tile clicked."""
    # For demo, return 1 if top-left tile clicked
    return "1" if tile == (0, 0) else None


def calculate_movement_range(game_state, unit_id: str, move_range: int = 3) -> list[Tuple[int, int]]:
    """Calculate valid movement tiles for unit."""
    if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
        return []

    unit_data = game_state.units.units.get(unit_id, {})
    if not unit_data:
        return []

    unit_x, unit_y = unit_data.get("x", 0), unit_data.get("y", 0)

    valid_tiles = []
    for dx in range(-move_range, move_range + 1):
        for dy in range(-move_range, move_range + 1):
            if abs(dx) + abs(dy) <= move_range:  # Manhattan distance
                new_x, new_y = unit_x + dx, unit_y + dy
                if is_valid_tile(new_x, new_y, game_state):
                    valid_tiles.append((new_x, new_y))

    return valid_tiles


def calculate_attack_targets(game_state, unit_id: str, attack_range: int = 1) -> list[Tuple[int, int]]:
    """Calculate valid attack targets for unit."""
    if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
        return []

    unit_data = game_state.units.units.get(unit_id, {})
    if not unit_data:
        return []

    unit_x, unit_y = unit_data.get("x", 0), unit_data.get("y", 0)

    targets = []
    for dx in range(-attack_range, attack_range + 1):
        for dy in range(-attack_range, attack_range + 1):
            if abs(dx) + abs(dy) <= attack_range:
                target_x, target_y = unit_x + dx, unit_y + dy
                target_unit = get_unit_at_tile(game_state, (target_x, target_y))
                if target_unit:
                    target_data = game_state.units.units.get(target_unit, {})
                    # Check if target is enemy
                    if target_data.get("team") != unit_data.get("team"):
                        targets.append((target_x, target_y))

    return targets


def is_valid_tile(x: int, y: int, game_state) -> bool:
    """Check if tile is valid (within bounds, not occupied, etc.)."""
    # Map bounds (assume 20x20 grid for now)
    if x < 0 or y < 0 or x >= 20 or y >= 20:
        return False

    # Check if tile is occupied by another unit
    if hasattr(game_state, "units") and hasattr(game_state.units, "units"):
        for other_unit_id, other_unit_data in game_state.units.units.items():
            if (other_unit_data.get("x"), other_unit_data.get("y")) == (x, y):
                return False

    return True
