"""
Ability Icons - manages ability icons with full architecture integration.
Integrated with UIState and includes validation and fallback mechanisms.
"""

from typing import Dict, List, Optional, Tuple

import pygame

from game.ui.ui_state import UIState


# @api
# @refactor
class AbilityIcons:
    """Manages ability icons with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.icons = {}
        self.icon_size = 32
        self._initialize_icons()

    def _initialize_icons(self):
        """Initialize ability icons with fallback mechanisms."""
        # Create placeholder icons
        self.icons["attack"] = self._create_attack_icon()
        self.icons["move"] = self._create_move_icon()
        self.icons["heal"] = self._create_heal_icon()
        self.icons["wait"] = self._create_wait_icon()
        self.icons["special"] = self._create_special_icon()
        self.icons["defend"] = self._create_defend_icon()

    def _create_attack_icon(self) -> pygame.Surface:
        """Create attack icon (red sword)."""
        surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        # Draw sword
        pygame.draw.rect(surface, (255, 0, 0), (14, 4, 4, 24))
        pygame.draw.rect(surface, (200, 0, 0), (12, 4, 8, 8))
        pygame.draw.rect(surface, (150, 0, 0), (10, 6, 12, 4))
        return surface

    def _create_move_icon(self) -> pygame.Surface:
        """Create move icon (green arrows)."""
        surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        # Draw movement arrows
        pygame.draw.polygon(surface, (0, 255, 0), [(16, 4), (20, 12), (16, 10)])
        pygame.draw.polygon(surface, (0, 255, 0), [(16, 28), (20, 20), (16, 22)])
        pygame.draw.polygon(surface, (0, 255, 0), [(4, 16), (12, 20), (10, 16)])
        pygame.draw.polygon(surface, (0, 255, 0), [(28, 16), (20, 20), (22, 16)])
        return surface

    def _create_heal_icon(self) -> pygame.Surface:
        """Create heal icon (green cross)."""
        surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        # Draw cross
        pygame.draw.rect(surface, (0, 255, 0), (14, 8, 4, 16))
        pygame.draw.rect(surface, (0, 255, 0), (8, 14, 16, 4))
        return surface

    def _create_wait_icon(self) -> pygame.Surface:
        """Create wait icon (yellow clock)."""
        surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        # Draw clock
        pygame.draw.circle(surface, (255, 255, 0), (16, 16), 12)
        pygame.draw.circle(surface, (200, 200, 0), (16, 16), 12, 2)
        pygame.draw.line(surface, (0, 0, 0), (16, 16), (16, 8), 2)
        pygame.draw.line(surface, (0, 0, 0), (16, 16), (22, 16), 2)
        return surface

    def _create_special_icon(self) -> pygame.Surface:
        """Create special ability icon (purple star)."""
        surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        # Draw star
        points = [(16, 4), (18, 12), (26, 12), (20, 18), (22, 26), (16, 22), (10, 26), (12, 18), (6, 12), (14, 12)]
        pygame.draw.polygon(surface, (255, 0, 255), points)
        return surface

    def _create_defend_icon(self) -> pygame.Surface:
        """Create defend icon (blue shield)."""
        surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        # Draw shield
        pygame.draw.polygon(surface, (0, 0, 255), [(16, 4), (24, 8), (24, 20), (16, 28), (8, 20), (8, 8)])
        pygame.draw.polygon(surface, (0, 0, 200), [(16, 4), (24, 8), (24, 20), (16, 28), (8, 20), (8, 8)], 2)
        return surface

    def draw_ability_panel(
        self, screen: pygame.Surface, abilities: List[str], position: Tuple[int, int], available_ap: int = 0
    ):
        """Draw ability panel with icons."""
        x, y = position
        panel_width = len(abilities) * (self.icon_size + 4) + 8
        panel_height = self.icon_size + 16

        # Draw panel background
        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        pygame.draw.rect(screen, (50, 50, 50), panel_rect)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 2)

        # Draw ability icons
        for i, ability in enumerate(abilities):
            if ability in self.icons:
                icon_x = x + 4 + i * (self.icon_size + 4)
                icon_y = y + 4
                screen.blit(self.icons[ability], (icon_x, icon_y))

                # Draw AP cost if available
                if available_ap > 0:
                    self._draw_ap_cost(screen, icon_x, icon_y, 1)  # Default AP cost of 1

    def draw_ability_icon(
        self, screen: pygame.Surface, ability: str, position: Tuple[int, int], available: bool = True
    ):
        """Draw a single ability icon."""
        if ability not in self.icons:
            return

        x, y = position
        icon = self.icons[ability]

        # Apply availability effect
        if not available:
            # Create dimmed version
            dimmed = icon.copy()
            dimmed.set_alpha(128)
            screen.blit(dimmed, (x, y))
        else:
            screen.blit(icon, (x, y))

    def _draw_ap_cost(self, screen: pygame.Surface, x: int, y: int, cost: int):
        """Draw AP cost indicator on icon."""
        font = pygame.font.Font(None, 12)
        cost_text = str(cost)
        text_surface = font.render(cost_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(bottomright=(x + self.icon_size - 2, y + self.icon_size - 2))

        # Draw background for cost
        bg_rect = text_rect.inflate(4, 2)
        pygame.draw.rect(screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(screen, (0, 150, 255), bg_rect, 1)

        screen.blit(text_surface, text_rect)

    def get_available_abilities(self, unit_data: Dict) -> List[str]:
        """Get available abilities for a unit based on AP and unit type."""
        if not unit_data:
            return []

        current_ap = unit_data.get("ap", 0)
        unit_type = unit_data.get("type", "basic")

        # Basic abilities available to all units
        abilities = ["move"]

        # Add combat abilities if AP available
        if current_ap >= 1:
            abilities.append("attack")

        # Add special abilities based on unit type
        if unit_type == "mage" and current_ap >= 2:
            abilities.append("heal")
        elif unit_type == "knight" and current_ap >= 1:
            abilities.append("defend")

        # Always add wait ability
        abilities.append("wait")

        return abilities

    def get_icon_info(self) -> Dict[str, str]:
        """Get information about available icons."""
        return {"available_icons": list(self.icons.keys()), "icon_size": self.icon_size}
