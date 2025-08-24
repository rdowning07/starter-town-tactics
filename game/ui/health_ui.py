"""
Health UI - draws health bars above units with full architecture integration.
Integrated with GameState and includes validation and logging.
"""

import pygame
from typing import Optional, Tuple, Dict
from game.ui.ui_state import UIState

# @api
# @refactor
class HealthUI:
    """Draws health bars above units with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.font = pygame.font.Font(None, 16)
        self.health_cache = {}  # Cache for health values to detect changes

    def draw_health_bar(self, screen: pygame.Surface, unit_id: str, unit_data: Dict,
                       tile_size: int = 32, x_offset: int = 0, y_offset: int = -5):
        """Draw health bar above unit with validation and logging."""
        if not unit_data or not unit_data.get("alive", True):
            return

        # Get unit position
        x, y = unit_data.get("x", 0), unit_data.get("y", 0)
        screen_x = x * tile_size + x_offset
        screen_y = y * tile_size + y_offset

        # Get health values
        max_hp = unit_data.get("max_hp", 20)
        current_hp = unit_data.get("hp", max_hp)

        # Validate health values
        if current_hp < 0:
            current_hp = 0
        if current_hp > max_hp:
            current_hp = max_hp

        # Calculate health bar dimensions
        bar_width = tile_size
        bar_height = 6
        fill_ratio = max(0, current_hp / max_hp) if max_hp > 0 else 0

        # Determine health bar color based on health percentage
        if fill_ratio > 0.6:
            fill_color = (0, 255, 0)  # Green for healthy
        elif fill_ratio > 0.3:
            fill_color = (255, 255, 0)  # Yellow for wounded
        else:
            fill_color = (255, 0, 0)  # Red for critical

        # Draw health bar background
        bg_rect = pygame.Rect(screen_x, screen_y, bar_width, bar_height)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 1)

        # Draw health bar fill
        if fill_ratio > 0:
            fill_rect = pygame.Rect(screen_x, screen_y, bar_width * fill_ratio, bar_height)
            pygame.draw.rect(screen, fill_color, fill_rect)

        # Draw health text
        health_text = f"{current_hp}/{max_hp}"
        text_surface = self.font.render(health_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_x + bar_width // 2, screen_y + bar_height // 2))
        screen.blit(text_surface, text_rect)

        # Log health changes
        self._log_health_change(unit_id, current_hp, max_hp, fill_ratio)

    def draw_all_health_bars(self, screen: pygame.Surface, game_state, ui_state: UIState,
                            tile_size: int = 32):
        """Draw health bars for all alive units."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return

        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                self.draw_health_bar(screen, unit_id, unit_data, tile_size)

    def draw_damage_indicator(self, screen: pygame.Surface, unit_id: str, damage: int,
                             position: Tuple[int, int], duration: int = 60):
        """Draw floating damage indicator."""
        if not hasattr(self, '_damage_indicators'):
            self._damage_indicators = {}

        # Create damage indicator
        self._damage_indicators[unit_id] = {
            'damage': damage,
            'position': position,
            'duration': duration,
            'current_frame': 0
        }

    def update_damage_indicators(self, screen: pygame.Surface):
        """Update and draw damage indicators."""
        if not hasattr(self, '_damage_indicators'):
            return

        # Update and draw damage indicators
        to_remove = []
        for unit_id, indicator in self._damage_indicators.items():
            indicator['current_frame'] += 1

            if indicator['current_frame'] >= indicator['duration']:
                to_remove.append(unit_id)
                continue

            # Calculate position with upward movement
            x, y = indicator['position']
            progress = indicator['current_frame'] / indicator['duration']
            y_offset = int(progress * -30)  # Move up 30 pixels over duration

            # Draw damage text
            damage_text = f"-{indicator['damage']}"
            color = (255, 0, 0) if indicator['damage'] > 0 else (0, 255, 0)

            # Fade out effect
            alpha = int(255 * (1 - progress))
            if alpha > 0:
                text_surface = self.font.render(damage_text, True, color)
                text_surface.set_alpha(alpha)
                screen.blit(text_surface, (x, y + y_offset))

        # Remove expired indicators
        for unit_id in to_remove:
            del self._damage_indicators[unit_id]

    def draw_health_summary(self, screen: pygame.Surface, game_state, ui_state: UIState,
                           x: int = 10, y: int = 200):
        """Draw health summary for all units."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return

        # Count units by team
        player_units = []
        enemy_units = []

        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                if unit_data.get("team") == "player":
                    player_units.append((unit_id, unit_data))
                else:
                    enemy_units.append((unit_id, unit_data))

        # Draw player units
        y_offset = 0
        if player_units:
            label = "Player Units:"
            label_surface = self.font.render(label, True, (0, 255, 0))
            screen.blit(label_surface, (x, y + y_offset))
            y_offset += 20

            for unit_id, unit_data in player_units:
                hp = unit_data.get("hp", 0)
                max_hp = unit_data.get("max_hp", 20)
                unit_text = f"  {unit_id}: {hp}/{max_hp}"
                unit_surface = self.font.render(unit_text, True, (255, 255, 255))
                screen.blit(unit_surface, (x, y + y_offset))
                y_offset += 15

        # Draw enemy units
        y_offset += 10
        if enemy_units:
            label = "Enemy Units:"
            label_surface = self.font.render(label, True, (255, 0, 0))
            screen.blit(label_surface, (x, y + y_offset))
            y_offset += 20

            for unit_id, unit_data in enemy_units:
                hp = unit_data.get("hp", 0)
                max_hp = unit_data.get("max_hp", 20)
                unit_text = f"  {unit_id}: {hp}/{max_hp}"
                unit_surface = self.font.render(unit_text, True, (255, 255, 255))
                screen.blit(unit_surface, (x, y + y_offset))
                y_offset += 15

    def _log_health_change(self, unit_id: str, current_hp: int, max_hp: int, fill_ratio: float):
        """Log health changes for debugging."""
        if not self.logger:
            return

        # Check if health changed
        cache_key = f"{unit_id}_health"
        if cache_key not in self.health_cache:
            self.health_cache[cache_key] = current_hp
            return

        if self.health_cache[cache_key] != current_hp:
            # Log health change
            self.logger.log_event("health_changed", {
                "unit": unit_id,
                "old_hp": self.health_cache[cache_key],
                "new_hp": current_hp,
                "max_hp": max_hp,
                "health_percentage": fill_ratio * 100
            })

            # Update cache
            self.health_cache[cache_key] = current_hp
