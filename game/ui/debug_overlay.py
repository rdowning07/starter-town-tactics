# game/ui/debug_overlay.py

import pygame


def draw_debug_overlay(
    surface, font, game, input_state, turn_controller, ai_controller
):
    """Draws debug information on screen for development insight."""
    lines = [
        f"Turn: {game.current_turn}",
        f"Phase: {turn_controller.get_phase().name}",
        f"Camera: ({game.camera_x}, {game.camera_y})",
        f"Cursor: ({input_state.cursor_x}, {input_state.cursor_y})",
        f"AI Action: {ai_controller.last_action}",
    ]
    if input_state.selected_unit:
        lines.append(f"Selected: {input_state.selected_unit.name}")

    lines.append("Log:")
    lines.extend(input_state.get_log())

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (255, 255, 255))
        surface.blit(text_surface, (5, 5 + i * 15))
