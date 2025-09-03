"""
Translates Pygame events to a command for human turns
"""
from typing import Any

import pygame

from core.command import Attack, EndTurn, Move


class InputController:
    def __init__(self):
        self.selected_unit_id: str | None = None
        self.cursor_pos: tuple[int, int] = (0, 0)

    def decide(self, game_state: Any) -> Move | Attack | EndTurn:
        """
        Process pygame events and return appropriate command.

        Args:
            game_state: Current game state

        Returns:
            Command to execute (Move, Attack, or EndTurn)
        """
        # If not player's turn, return EndTurn stub
        if game_state.current_side() != "player":
            return EndTurn(game_state.current_unit().id)

        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return EndTurn(game_state.current_unit().id)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_SPACE:
                    # Select/deselect unit
                    if self.selected_unit_id:
                        self.selected_unit_id = None
                    else:
                        self.selected_unit_id = game_state.current_unit().id

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Convert mouse position to tile coordinates
                    mouse_pos = pygame.mouse.get_pos()
                    tile_pos = self._pixel_to_tile(mouse_pos)

                    if self.selected_unit_id:
                        # Check if clicking on enemy unit (attack)
                        target_unit = game_state.get_unit_at(tile_pos)
                        if target_unit and target_unit.team != "player":
                            return Attack(self.selected_unit_id, target_unit.id)
                        else:
                            # Move to empty tile
                            return Move(self.selected_unit_id, tile_pos)
                    else:
                        # Select unit at clicked position
                        unit = game_state.get_unit_at(tile_pos)
                        if unit and unit.team == "player":
                            self.selected_unit_id = unit.id

        # Handle keyboard movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.cursor_pos = (self.cursor_pos[0] - 1, self.cursor_pos[1])
        elif keys[pygame.K_RIGHT]:
            self.cursor_pos = (self.cursor_pos[0] + 1, self.cursor_pos[1])
        elif keys[pygame.K_UP]:
            self.cursor_pos = (self.cursor_pos[0], self.cursor_pos[1] - 1)
        elif keys[pygame.K_DOWN]:
            self.cursor_pos = (self.cursor_pos[0], self.cursor_pos[1] + 1)

        # Default: end turn
        return EndTurn(game_state.current_unit().id)

    def _pixel_to_tile(self, pixel_pos: tuple[int, int]) -> tuple[int, int]:
        """
        Convert pixel coordinates to tile coordinates.

        Args:
            pixel_pos: (x, y) in pixels

        Returns:
            (x, y) in tile coordinates
        """
        # Assuming 32x32 tile size - adjust as needed
        tile_size = 32
        return (pixel_pos[0] // tile_size, pixel_pos[1] // tile_size)
