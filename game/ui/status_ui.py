"""
Status UI - draws status effect icons above units with full architecture integration.
Integrated with GameState, StatusEffectManager, and includes validation and logging.
"""

from typing import Dict, List, Optional, Tuple

import pygame

from game.status_effects import StatusEffect
from game.ui.ui_state import UIState


# @api
# @refactor
class StatusUI:
    """Draws status effect icons above units with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.font = pygame.font.Font(None, 12)
        self.icon_cache = {}  # Cache for status icons
        self.icon_size = 16

    def draw_status_icons(
        self,
        screen: pygame.Surface,
        unit_id: str,
        unit_data: Dict,
        effects: List[StatusEffect],
        tile_size: int = 32,
        x_offset: int = 0,
        y_offset: int = -20,
    ):
        """Draw status effect icons above a unit."""
        if not effects:
            return

        # Get unit position
        x, y = unit_data.get("x", 0), unit_data.get("y", 0)
        screen_x = x * tile_size + x_offset
        screen_y = y * tile_size + y_offset

        # Draw effects in a row
        for idx, effect in enumerate(effects):
            icon_x = screen_x + (idx * (self.icon_size + 2))
            icon_y = screen_y

            # Draw effect icon
            self._draw_effect_icon(screen, effect, icon_x, icon_y)

            # Draw stack count if > 1
            if effect.stacks > 1:
                stack_text = str(effect.stacks)
                text_surface = self.font.render(stack_text, True, (255, 255, 255))
                screen.blit(text_surface, (icon_x + self.icon_size - 8, icon_y + self.icon_size - 8))

    def draw_all_status_icons(
        self, screen: pygame.Surface, game_state, status_manager, ui_state: UIState, tile_size: int = 32
    ):
        """Draw status icons for all units with effects."""
        if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
            return

        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                effects = status_manager.get_unit_effects(unit_id)
                if effects:
                    self.draw_status_icons(screen, unit_id, unit_data, effects, tile_size)

    def draw_status_tooltip(self, screen: pygame.Surface, effects: List[StatusEffect], pos: Tuple[int, int]):
        """Draw detailed tooltip for status effects."""
        if not effects:
            return

        # Calculate tooltip size
        tooltip_lines = []
        for effect in effects:
            line = f"{effect.name.title()}: {effect.description} ({effect.duration} turns)"
            tooltip_lines.append(line)

        if not tooltip_lines:
            return

        # Create tooltip surface
        line_height = 16
        max_width = max(self.font.size(line)[0] for line in tooltip_lines)
        tooltip_width = max_width + 10
        tooltip_height = len(tooltip_lines) * line_height + 10

        # Position tooltip (avoid going off screen)
        x, y = pos
        if x + tooltip_width > screen.get_width():
            x = screen.get_width() - tooltip_width
        if y + tooltip_height > screen.get_height():
            y = screen.get_height() - tooltip_height

        # Draw tooltip background
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        pygame.draw.rect(screen, (0, 0, 0, 200), tooltip_rect)
        pygame.draw.rect(screen, (255, 255, 255), tooltip_rect, 1)

        # Draw tooltip text
        for i, line in enumerate(tooltip_lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (x + 5, y + 5 + i * line_height))

    def draw_status_summary(
        self, screen: pygame.Surface, game_state, status_manager, ui_state: UIState, x: int = 10, y: int = 350
    ):
        """Draw status effect summary for all units."""
        if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
            return

        # Count effects by type
        buff_count = 0
        debuff_count = 0
        total_effects = 0

        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                effects = status_manager.get_unit_effects(unit_id)
                total_effects += len(effects)
                for effect in effects:
                    if effect.effect_type == "buff":
                        buff_count += 1
                    elif effect.effect_type == "debuff":
                        debuff_count += 1

        # Draw summary
        if total_effects > 0:
            summary_lines = [f"Active Effects: {total_effects}", f"Buffs: {buff_count}", f"Debuffs: {debuff_count}"]

            for i, line in enumerate(summary_lines):
                color = (0, 255, 0) if "Buffs" in line else (255, 0, 0) if "Debuffs" in line else (255, 255, 255)
                text_surface = self.font.render(line, True, color)
                screen.blit(text_surface, (x, y + i * 15))

    def _draw_effect_icon(self, screen: pygame.Surface, effect: StatusEffect, x: int, y: int):
        """Draw a single status effect icon."""
        # Get or create icon
        icon = self._get_or_create_icon(effect)

        # Draw icon
        icon_rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
        screen.blit(icon, icon_rect)

        # Draw duration indicator
        if effect.duration > 0:
            # Draw duration as a small bar
            bar_width = self.icon_size
            bar_height = 2
            bar_y = y + self.icon_size - bar_height

            # Duration bar background
            pygame.draw.rect(screen, (50, 50, 50), (x, bar_y, bar_width, bar_height))

            # Duration bar fill (assuming max 10 turns)
            max_duration = 10
            fill_ratio = min(1.0, effect.duration / max_duration)
            fill_width = int(bar_width * fill_ratio)

            duration_color = (0, 255, 0) if fill_ratio > 0.5 else (255, 255, 0) if fill_ratio > 0.2 else (255, 0, 0)
            pygame.draw.rect(screen, duration_color, (x, bar_y, fill_width, bar_height))

    def _get_or_create_icon(self, effect: StatusEffect) -> pygame.Surface:
        """Get or create an icon for a status effect."""
        cache_key = f"{effect.name}_{effect.effect_type}"

        if cache_key not in self.icon_cache:
            self.icon_cache[cache_key] = self._create_placeholder_icon(effect)

        return self.icon_cache[cache_key]

    def _create_placeholder_icon(self, effect: StatusEffect) -> pygame.Surface:
        """Create a placeholder icon for a status effect."""
        icon = pygame.Surface((self.icon_size, self.icon_size))

        # Color based on effect type
        if effect.effect_type == "buff":
            base_color = (0, 150, 0)  # Green
        elif effect.effect_type == "debuff":
            base_color = (150, 0, 0)  # Red
        else:
            base_color = (100, 100, 100)  # Gray

        # Fill background
        icon.fill(base_color)

        # Draw border
        pygame.draw.rect(icon, (255, 255, 255), icon.get_rect(), 1)

        # Draw effect symbol (first letter)
        if effect.name:
            symbol = effect.name[0].upper()
            text_surface = self.font.render(symbol, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.icon_size // 2, self.icon_size // 2))
            icon.blit(text_surface, text_rect)

        return icon

    def get_effect_at_position(
        self, screen_pos: Tuple[int, int], game_state, status_manager, tile_size: int = 32
    ) -> Optional[List[StatusEffect]]:
        """Get status effects at a screen position (for tooltips)."""
        if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
            return None

        x, y = screen_pos

        for unit_id, unit_data in game_state.units.units.items():
            if unit_data.get("alive", True):
                unit_x = unit_data.get("x", 0) * tile_size
                unit_y = unit_data.get("y", 0) * tile_size - 20  # Status icon offset

                effects = status_manager.get_unit_effects(unit_id)
                if effects:
                    # Check if mouse is over status icons
                    icon_area_width = len(effects) * (self.icon_size + 2)
                    icon_rect = pygame.Rect(unit_x, unit_y, icon_area_width, self.icon_size)

                    if icon_rect.collidepoint(x, y):
                        return effects

        return None
