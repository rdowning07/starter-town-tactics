"""
Always-visible control card showing game controls.
Helps new players understand what they can do.
"""

import pygame

# No additional imports needed


class ControlCard:
    """Always-visible control card showing game controls."""

    def __init__(self):
        """Initialize the control card."""
        self.is_visible = True
        self.position = (750, 10)  # Far right, top (moved to avoid game area)
        self.background_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (255, 255, 255)  # White text
        self.key_color = (255, 255, 0)  # Yellow for keys

        # Font
        self.font = None
        self.key_font = None

        # Control text
        self.controls = [
            ("WASD", "Move Fighter"),
            ("SPACE", "Attack"),
            ("ESC", "Exit"),
        ]

    def toggle_visibility(self) -> None:
        """Toggle control card visibility."""
        self.is_visible = not self.is_visible

    def set_visible(self, visible: bool) -> None:
        """Set control card visibility."""
        self.is_visible = visible

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the control card."""
        if not self.is_visible:
            return

        # Initialize fonts if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 20)
            self.key_font = pygame.font.Font(None, 18)

        # Calculate card dimensions
        padding = 10
        line_height = 30  # Increased from 25 to 30 for better spacing
        card_width = 350
        card_height = len(self.controls) * line_height + padding * 2

        # Draw background
        card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        card_surface.fill(self.background_color)

        # Draw border
        pygame.draw.rect(
            card_surface, (100, 100, 100), (0, 0, card_width, card_height), 2
        )

        # Draw title
        title_surface = self.font.render("CONTROLS", True, self.text_color)
        card_surface.blit(title_surface, (padding, padding))

        # Draw controls
        y_offset = padding + 25
        for key, action in self.controls:
            # Draw key
            key_surface = self.key_font.render(key, True, self.key_color)
            card_surface.blit(key_surface, (padding, y_offset))

            # Draw action
            action_surface = self.key_font.render(action, True, self.text_color)
            card_surface.blit(action_surface, (padding + 80, y_offset))

            y_offset += line_height

        # Blit card to main surface
        surface.blit(card_surface, self.position)
