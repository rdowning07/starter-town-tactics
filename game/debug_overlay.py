import pygame


def draw_debug_overlay(surface, font, game, input_state):
    lines = [
        f"Turn: {game.current_turn}",
        f"Camera: ({game.camera_x}, {game.camera_y})",
        f"Cursor: ({input_state.cursor_x}, {input_state.cursor_y})",
    ]
    if input_state.selected_unit:
        lines.append(f"Selected: {input_state.selected_unit.name}")
    lines.append("Log:")
    lines += input_state.get_log()

    for i, line in enumerate(lines):
        surface.blit(font.render(line, True, (255, 255, 255)), (5, 5 + i * 15))
