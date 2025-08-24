"""
Cursor Manager - manages custom cursors with full architecture integration.
Integrated with UIState and includes validation and fallback mechanisms.
"""

import pygame
from typing import Optional, Tuple, Dict
from game.ui.ui_state import UIState

# @api
# @refactor
class CursorManager:
    """Manages custom cursors with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.cursors = {}
        self.current_cursor = "default"
        self.custom_cursor_surface = None
        self._initialize_cursors()

    def _initialize_cursors(self):
        """Initialize cursor types with fallback mechanisms."""
        # Create default cursor (simple crosshair)
        self.cursors["default"] = self._create_default_cursor()
        self.cursors["select"] = self._create_select_cursor()
        self.cursors["move"] = self._create_move_cursor()
        self.cursors["attack"] = self._create_attack_cursor()
        self.cursors["invalid"] = self._create_invalid_cursor()

        # Set initial cursor
        self.set_cursor("default")

    def _create_default_cursor(self) -> pygame.Surface:
        """Create a default cursor (crosshair)."""
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Draw crosshair
        pygame.draw.line(surface, (255, 255, 255), (8, 0), (8, 16), 2)
        pygame.draw.line(surface, (255, 255, 255), (0, 8), (16, 8), 2)
        return surface

    def _create_select_cursor(self) -> pygame.Surface:
        """Create a selection cursor (pointer)."""
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Draw pointer
        pygame.draw.polygon(surface, (255, 255, 0), [(0, 0), (16, 8), (0, 16)])
        return surface

    def _create_move_cursor(self) -> pygame.Surface:
        """Create a movement cursor (arrows)."""
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Draw movement arrows
        pygame.draw.polygon(surface, (0, 255, 0), [(8, 0), (12, 8), (8, 6)])
        pygame.draw.polygon(surface, (0, 255, 0), [(8, 16), (12, 8), (8, 10)])
        pygame.draw.polygon(surface, (0, 255, 0), [(0, 8), (8, 12), (6, 8)])
        pygame.draw.polygon(surface, (0, 255, 0), [(16, 8), (8, 12), (10, 8)])
        return surface

    def _create_attack_cursor(self) -> pygame.Surface:
        """Create an attack cursor (sword)."""
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Draw sword
        pygame.draw.rect(surface, (255, 0, 0), (7, 0, 2, 16))
        pygame.draw.rect(surface, (200, 0, 0), (6, 0, 4, 4))
        return surface

    def _create_invalid_cursor(self) -> pygame.Surface:
        """Create an invalid action cursor (X)."""
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Draw X
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (16, 16), 3)
        pygame.draw.line(surface, (255, 0, 0), (16, 0), (0, 16), 3)
        return surface

    def set_cursor(self, cursor_type: str):
        """Set the current cursor type."""
        if cursor_type in self.cursors:
            self.current_cursor = cursor_type
            self.custom_cursor_surface = self.cursors[cursor_type]
            if self.logger:
                self.logger.info({
                    "event": "cursor_changed",
                    "cursor_type": cursor_type
                })
        else:
            # Fallback to default
            self.current_cursor = "default"
            self.custom_cursor_surface = self.cursors["default"]
            if self.logger:
                self.logger.warning({
                    "event": "cursor_fallback",
                    "requested": cursor_type,
                    "fallback": "default"
                })

    def update_cursor(self, ui_state: UIState, mouse_pos: Tuple[int, int]):
        """Update cursor based on UI state and mouse position."""
        # Determine cursor type based on UI state
        if ui_state.selected_unit:
            if ui_state.show_movement_range:
                self.set_cursor("move")
            elif ui_state.show_attack_targets:
                self.set_cursor("attack")
            else:
                self.set_cursor("select")
        else:
            self.set_cursor("default")

    def draw_cursor(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """Draw the custom cursor at mouse position."""
        if self.custom_cursor_surface:
            # Hide system cursor
            pygame.mouse.set_visible(False)

            # Draw custom cursor
            cursor_rect = self.custom_cursor_surface.get_rect(center=mouse_pos)
            screen.blit(self.custom_cursor_surface, cursor_rect)
        else:
            # Show system cursor if no custom cursor
            pygame.mouse.set_visible(True)

    def reset_cursor(self):
        """Reset to default cursor and show system cursor."""
        self.set_cursor("default")
        pygame.mouse.set_visible(True)

    def get_cursor_info(self) -> Dict[str, str]:
        """Get current cursor information."""
        return {
            "current_cursor": self.current_cursor,
            "available_cursors": list(self.cursors.keys())
        }
