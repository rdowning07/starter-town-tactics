"""
Effect creation methods for the BT Fighter Demo.

This module contains the effect creation methods extracted from the main demo
to improve code organization and maintainability.
"""

from typing import Tuple

import pygame


class EffectCreation:
    """Effect creation methods for the demo."""

    def create_placeholder(
        self, width: int, height: int, color: Tuple[int, int, int, int]
    ) -> pygame.Surface:
        """Create a placeholder surface with transparency."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)
        return surface

    def create_fireball_effect(self, size: int = 32) -> pygame.Surface:
        """Create a simple fireball effect for mage attacks."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Create a glowing fireball effect
        center = size // 2
        radius = size // 3

        # Outer glow (orange)
        for r in range(radius + 4, radius - 1, -1):
            alpha = max(0, 255 - (r - radius) * 50)
            color = (255, 165, 0, alpha)  # Orange with fade
            pygame.draw.circle(surface, color, (center, center), r)

        # Core fireball (red-yellow)
        pygame.draw.circle(
            surface, (255, 255, 0, 200), (center, center), radius - 2
        )  # Yellow core
        pygame.draw.circle(
            surface, (255, 100, 0, 255), (center, center), radius - 4
        )  # Red center

        return surface

    def create_healing_effect(self, size: int = 32) -> pygame.Surface:
        """Create a simple healing effect for healer spells."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Create a glowing ethereal healing effect
        center = size // 2
        radius = size // 3

        # Outer glow (soft white-blue)
        for r in range(radius + 6, radius - 1, -1):
            alpha = max(0, 180 - (r - radius) * 30)
            color = (200, 220, 255, alpha)  # Soft white-blue with fade
            pygame.draw.circle(surface, color, (center, center), r)

        # Middle glow (pure white)
        pygame.draw.circle(
            surface, (255, 255, 255, 150), (center, center), radius
        )  # White glow

        # Core healing (bright white)
        pygame.draw.circle(
            surface, (255, 255, 255, 255), (center, center), radius - 3
        )  # Bright white core

        # Inner sparkle (cyan accent)
        pygame.draw.circle(
            surface, (100, 255, 255, 200), (center, center), radius - 6
        )  # Cyan sparkle

        return surface

    def create_arrow_projectile(self, size: int = 16) -> pygame.Surface:
        """Create a simple arrow projectile for ranger attacks."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Draw arrow shaft (brown)
        pygame.draw.rect(surface, (139, 69, 19, 255), (center - 1, center - 4, 2, 8))

        # Draw arrowhead (gray)
        points = [
            (center, center - 6),  # Tip
            (center - 2, center - 4),  # Left
            (center + 2, center - 4),  # Right
        ]
        pygame.draw.polygon(surface, (128, 128, 128, 255), points)

        # Draw fletching (red)
        pygame.draw.rect(surface, (255, 0, 0, 255), (center - 2, center + 2, 4, 2))

        return surface
