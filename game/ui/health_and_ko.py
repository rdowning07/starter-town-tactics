"""
Health bars and KO markers for tactical combat.
Shows health bars above units and KO markers for defeated units.
"""

from typing import Dict

import pygame


class HealthAndKOOverlay:
    """Health bars and KO markers overlay for units."""

    def __init__(self):
        """Initialize the health overlay."""
        self.health_bar_height = 4
        self.health_bar_width = 24
        self.ko_fade_alpha = 128
        self.ko_cross_size = 16

        # Colors
        self.health_full_color = (0, 255, 0)  # Green
        self.health_damaged_color = (255, 165, 0)  # Orange
        self.health_critical_color = (255, 0, 0)  # Red
        self.ko_cross_color = (255, 0, 0)  # Red cross
        self.ko_overlay_color = (0, 0, 0)  # Black overlay

    def draw_health_bar(
        self, surface: pygame.Surface, x: int, y: int, current_hp: int, max_hp: int, tile_size: int = 32
    ) -> None:
        """Draw a health bar above a unit.

        Args:
            surface: Pygame surface to draw on
            x, y: Unit position in pixels
            current_hp: Current health points
            max_hp: Maximum health points
            tile_size: Size of each tile
        """
        if max_hp <= 0:
            return

        # Calculate health percentage
        health_ratio = current_hp / max_hp

        # Choose color based on health
        if health_ratio > 0.6:
            color = self.health_full_color
        elif health_ratio > 0.3:
            color = self.health_damaged_color
        else:
            color = self.health_critical_color

        # Position health bar above unit
        bar_x = x + (tile_size - self.health_bar_width) // 2
        bar_y = y - 8

        # Draw background (black)
        pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, self.health_bar_width, self.health_bar_height))

        # Draw health bar
        health_width = int(self.health_bar_width * health_ratio)
        if health_width > 0:
            pygame.draw.rect(surface, color, (bar_x, bar_y, health_width, self.health_bar_height))

    def draw_ko_marker(self, surface: pygame.Surface, x: int, y: int, tile_size: int = 32) -> None:
        """Draw a KO marker (red cross) over a defeated unit.

        Args:
            surface: Pygame surface to draw on
            x, y: Unit position in pixels
            tile_size: Size of each tile
        """
        # Center the cross on the unit
        center_x = x + tile_size // 2
        center_y = y + tile_size // 2
        half_size = self.ko_cross_size // 2

        # Draw red cross
        pygame.draw.line(
            surface,
            self.ko_cross_color,
            (center_x - half_size, center_y - half_size),
            (center_x + half_size, center_y + half_size),
            3,
        )
        pygame.draw.line(
            surface,
            self.ko_cross_color,
            (center_x - half_size, center_y + half_size),
            (center_x + half_size, center_y - half_size),
            3,
        )

    def draw_ko_overlay(self, surface: pygame.Surface, x: int, y: int, tile_size: int = 32) -> None:
        """Draw a dark overlay over a defeated unit.

        Args:
            surface: Pygame surface to draw on
            x, y: Unit position in pixels
            tile_size: Size of each tile
        """
        # Create a semi-transparent overlay
        overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        overlay.fill((*self.ko_overlay_color, self.ko_fade_alpha))
        surface.blit(overlay, (x, y))

    def draw_unit_health(
        self, surface: pygame.Surface, unit_data: Dict, camera_x: int = 0, camera_y: int = 0, tile_size: int = 32
    ) -> None:
        """Draw health bar and KO marker for a single unit.

        Args:
            surface: Pygame surface to draw on
            unit_data: Unit data dictionary with 'x', 'y', 'hp', 'max_hp', 'alive'
            camera_x, camera_y: Camera offset
            tile_size: Size of each tile
        """
        if not unit_data:
            return

        # Calculate screen position
        screen_x = unit_data.get("x", 0) * tile_size - camera_x
        screen_y = unit_data.get("y", 0) * tile_size - camera_y

        # Check if unit is alive
        is_alive = unit_data.get("alive", True)
        current_hp = unit_data.get("hp", 0)
        max_hp = unit_data.get("max_hp", 10)

        if is_alive and current_hp > 0:
            # Draw health bar for living units
            self.draw_health_bar(surface, screen_x, screen_y, current_hp, max_hp, tile_size)
        else:
            # Draw KO marker and overlay for defeated units
            self.draw_ko_overlay(surface, screen_x, screen_y, tile_size)
            self.draw_ko_marker(surface, screen_x, screen_y, tile_size)

    def draw_all_units(
        self, surface: pygame.Surface, units: Dict[str, Dict], camera_x: int = 0, camera_y: int = 0, tile_size: int = 32
    ) -> None:
        """Draw health bars and KO markers for all units.

        Args:
            surface: Pygame surface to draw on
            units: Dictionary of unit data
            camera_x, camera_y: Camera offset
            tile_size: Size of each tile
        """
        for unit_data in units.values():
            self.draw_unit_health(surface, unit_data, camera_x, camera_y, tile_size)
