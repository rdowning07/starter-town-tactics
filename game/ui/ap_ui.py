"""
AP UI - draws action point bars above units with full architecture integration.
Integrated with GameState and includes validation and logging.
"""

from typing import Dict, Optional, Tuple

import pygame

from game.ui.ui_state import UIState


# @api
# @refactor
class APUI:
    """Draws action point bars above units with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.font = pygame.font.Font(None, 14)
        self.ap_cache = {}  # Cache for AP values to detect changes

    def draw_ap_bar(
        self,
        screen: pygame.Surface,
        unit_id: str,
        unit_data: Dict,
        tile_size: int = 32,
        x_offset: int = 0,
        y_offset: int = -15,
    ):
        """Draw AP bar above unit with validation and logging."""
        if not unit_data or not unit_data.get("alive", True):
            return

        # Get unit position
        x, y = unit_data.get("x", 0), unit_data.get("y", 0)
        screen_x = x * tile_size + x_offset
        screen_y = y * tile_size + y_offset

        # Get AP values (default to 3 if not set)
        max_ap = unit_data.get("max_ap", 3)
        current_ap = unit_data.get("ap", max_ap)

        # Validate AP values
        if current_ap < 0:
            current_ap = 0
        if current_ap > max_ap:
            current_ap = max_ap

        # Calculate AP bar dimensions
        bar_width = tile_size
        bar_height = 4
        fill_ratio = max(0, current_ap / max_ap) if max_ap > 0 else 0

        # AP bar color (blue theme)
        fill_color = (0, 150, 255)  # Blue for action points

        # Draw AP bar background
        bg_rect = pygame.Rect(screen_x, screen_y, bar_width, bar_height)
        pygame.draw.rect(screen, (30, 30, 50), bg_rect)
        pygame.draw.rect(screen, (60, 60, 80), bg_rect, 1)

        # Draw AP bar fill
        if fill_ratio > 0:
            fill_rect = pygame.Rect(screen_x, screen_y, bar_width * fill_ratio, bar_height)
            pygame.draw.rect(screen, fill_color, fill_rect)

        # Draw AP text (smaller than health text)
        ap_text = f"AP: {current_ap}/{max_ap}"
        text_surface = self.font.render(ap_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_x + bar_width // 2, screen_y + bar_height // 2))
        screen.blit(text_surface, text_rect)

        # Log AP changes
        self._log_ap_change(unit_id, current_ap, max_ap, fill_ratio)

    def draw_all_ap_bars(self, screen: pygame.Surface, game_state, ui_state: UIState, tile_size: int = 32):
        """Draw AP bars for all alive units."""
        if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
            return

        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                self.draw_ap_bar(screen, unit_id, unit_data, tile_size)

    def _log_ap_change(self, unit_id: str, current_ap: int, max_ap: int, fill_ratio: float):
        """Log AP changes for debugging and metrics."""
        if self.logger:
            self.logger.info(
                {
                    "event": "ap_bar_drawn",
                    "unit_id": unit_id,
                    "current_ap": current_ap,
                    "max_ap": max_ap,
                    "fill_ratio": fill_ratio,
                }
            )

    def get_ap_summary(self, game_state) -> Dict[str, int]:
        """Get AP summary for all units."""
        if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
            return {}

        summary = {}
        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                current_ap = unit_data.get("ap", 3)
                max_ap = unit_data.get("max_ap", 3)
                summary[unit_id] = {"current": current_ap, "max": max_ap}

        return summary
