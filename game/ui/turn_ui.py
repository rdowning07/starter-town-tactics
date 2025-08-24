"""
Turn UI - displays current turn indicator with full architecture integration.
Integrated with GameState, SimRunner, and TurnController.
"""

import pygame
from typing import Optional, Tuple
from game.ui.ui_state import UIState

# @api
# @refactor
class TurnUI:
    """Displays current turn indicator with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

    def draw_turn_indicator(self, screen: pygame.Surface, game_state, ui_state: UIState,
                           width: int = 800, height: int = 30):
        """Draw turn indicator with full game state integration."""
        if not hasattr(game_state, 'sim_runner') or not hasattr(game_state, 'turn_controller'):
            return

        # Get current turn info
        current_unit = game_state.turn_controller.get_current_unit()
        turn_count = getattr(game_state.sim_runner, 'turn_count', 0)
        is_ai_turn = game_state.sim_runner.is_ai_turn()

        # Determine current team
        current_team = "AI" if is_ai_turn else "Player"
        if current_unit and hasattr(game_state, 'units') and hasattr(game_state.units, 'units'):
            unit_data = game_state.units.units.get(current_unit, {})
            current_team = unit_data.get("team", "Unknown").title()

        # Create turn indicator background
        indicator_rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(screen, (0, 0, 0, 200), indicator_rect)
        pygame.draw.rect(screen, (255, 255, 255), indicator_rect, 1)

        # Draw turn label
        label = f"Turn {turn_count} | Current: {current_team}"
        text_surface = self.font.render(label, True, (255, 255, 255))
        screen.blit(text_surface, (10, 5))

        # Draw turn status indicator
        status_color = (255, 0, 0) if is_ai_turn else (0, 255, 0)
        status_text = "AI TURN" if is_ai_turn else "YOUR TURN"
        status_surface = self.small_font.render(status_text, True, status_color)
        screen.blit(status_surface, (width - 120, 8))

        # Log turn change if needed
        if self.logger and hasattr(self, '_last_turn_count') and self._last_turn_count != turn_count:
            self.logger.log_event("turn_changed", {
                "turn_count": turn_count,
                "current_team": current_team,
                "is_ai_turn": is_ai_turn,
                "current_unit": current_unit
            })

        self._last_turn_count = turn_count

    def draw_unit_turn_highlight(self, screen: pygame.Surface, game_state, ui_state: UIState,
                                tile_size: int = 32):
        """Highlight the unit whose turn it is."""
        if not hasattr(game_state, 'turn_controller'):
            return

        current_unit = game_state.turn_controller.get_current_unit()
        if not current_unit or not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return

        unit_data = game_state.units.units.get(current_unit, {})
        if not unit_data or not unit_data.get("alive", True):
            return

        # Draw turn indicator above current unit
        x, y = unit_data.get("x", 0), unit_data.get("y", 0)
        screen_x = x * tile_size
        screen_y = y * tile_size - 15

        # Draw turn indicator
        indicator_color = (255, 255, 0) if game_state.sim_runner.is_ai_turn() else (0, 255, 255)
        pygame.draw.circle(screen, indicator_color, (screen_x + tile_size // 2, screen_y), 8)
        pygame.draw.circle(screen, (0, 0, 0), (screen_x + tile_size // 2, screen_y), 8, 2)

        # Draw turn text
        turn_text = "AI" if game_state.sim_runner.is_ai_turn() else "TURN"
        text_surface = self.small_font.render(turn_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(screen_x + tile_size // 2, screen_y))
        screen.blit(text_surface, text_rect)

    def draw_turn_progress(self, screen: pygame.Surface, game_state, ui_state: UIState,
                          x: int = 10, y: int = 40):
        """Draw turn order and progress."""
        if not hasattr(game_state, 'turn_controller'):
            return

        # Get turn order
        turn_order = getattr(game_state.turn_controller, 'turn_order', [])
        current_unit = game_state.turn_controller.get_current_unit()

        if not turn_order:
            return

        # Draw turn order
        label = "Turn Order:"
        label_surface = self.small_font.render(label, True, (255, 255, 255))
        screen.blit(label_surface, (x, y))

        for i, unit_id in enumerate(turn_order):
            unit_data = game_state.units.units.get(unit_id, {})
            if not unit_data or not unit_data.get("alive", True):
                continue

            # Determine color based on team and current turn
            if unit_id == current_unit:
                color = (255, 255, 0)  # Yellow for current
            elif unit_data.get("team") == "player":
                color = (0, 255, 0)    # Green for player
            else:
                color = (255, 0, 0)    # Red for enemy

            # Draw unit in turn order
            unit_text = f"{i+1}. {unit_id}"
            unit_surface = self.small_font.render(unit_text, True, color)
            screen.blit(unit_surface, (x + 10, y + 20 + i * 15))
