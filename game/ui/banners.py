"""
Victory/Defeat banners and cut-in text for tactical combat.
Provides visual feedback for major game events.
"""

import time
from typing import Tuple

import pygame


class VictoryBanner:
    """Victory or defeat banner that appears at the end of battle."""

    def __init__(self):
        """Initialize the victory banner."""
        self.is_visible = False
        self.banner_type = "victory"  # "victory" or "defeat"
        self.start_time = 0.0
        self.duration = 3.0  # Show for 3 seconds
        self.fade_duration = 0.5  # Fade in/out duration

        # Colors
        self.victory_color = (0, 255, 0)  # Green
        self.defeat_color = (255, 0, 0)  # Red
        self.background_color = (0, 0, 0, 180)  # Semi-transparent black

        # Font
        self.font = None
        self.title_font = None

    def show_victory(self) -> None:
        """Show victory banner."""
        self.is_visible = True
        self.banner_type = "victory"
        self.start_time = time.time()

    def show_defeat(self) -> None:
        """Show defeat banner."""
        self.is_visible = True
        self.banner_type = "defeat"
        self.start_time = time.time()

    def hide(self) -> None:
        """Hide the banner."""
        self.is_visible = False

    def update(self, dt: float) -> None:
        """Update banner state."""
        if not self.is_visible:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time

        # Auto-hide after duration
        if elapsed >= self.duration:
            self.hide()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the banner."""
        if not self.is_visible:
            return

        # Initialize fonts if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 48)
            self.title_font = pygame.font.Font(None, 72)

        current_time = time.time()
        elapsed = current_time - self.start_time

        # Calculate alpha based on fade timing
        if elapsed < self.fade_duration:
            # Fade in
            pass  # Alpha is already 255
        elif elapsed > self.duration - self.fade_duration:
            # Fade out
            fade_out_time = elapsed - (self.duration - self.fade_duration)
            # Alpha would be calculated here if needed

        # Choose colors
        if self.banner_type == "victory":
            text_color = self.victory_color
            title_text = "VICTORY!"
        else:
            text_color = self.defeat_color
            title_text = "DEFEAT!"

        # Get surface dimensions
        screen_width, screen_height = surface.get_size()

        # Draw semi-transparent background
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill(self.background_color)
        surface.blit(overlay, (0, 0))

        # Draw title
        title_surface = self.title_font.render(title_text, True, text_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 20))
        surface.blit(title_surface, title_rect)

        # No subtitle - victory banner auto-exits after 3 seconds


class TurnBanner:
    """Turn banner showing whose turn it is."""

    def __init__(self):
        """Initialize the turn banner."""
        self.is_visible = False
        self.turn_text = ""
        self.start_time = 0.0
        self.duration = 1.5  # Show for 1.5 seconds

        # Colors
        self.player_color = (0, 100, 255)  # Blue
        self.ai_color = (255, 100, 0)  # Orange
        self.background_color = (0, 0, 0, 150)  # Semi-transparent black

        # Font
        self.font = None

    def show_turn(self, turn_text: str) -> None:
        """Show turn banner with text."""
        self.is_visible = True
        self.turn_text = turn_text
        self.start_time = time.time()

    def hide(self) -> None:
        """Hide the banner."""
        self.is_visible = False

    def update(self, dt: float) -> None:
        """Update banner state."""
        if not self.is_visible:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time

        # Auto-hide after duration
        if elapsed >= self.duration:
            self.hide()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the banner."""
        if not self.is_visible:
            return

        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 36)

        # Choose color based on turn type
        if "player" in self.turn_text.lower() or "fighter" in self.turn_text.lower():
            text_color = self.player_color
        else:
            text_color = self.ai_color

        # Get surface dimensions
        screen_width, screen_height = surface.get_size()

        # Draw semi-transparent background
        overlay = pygame.Surface((screen_width, 60), pygame.SRCALPHA)
        overlay.fill(self.background_color)
        surface.blit(overlay, (0, 0))

        # Draw turn text
        text_surface = self.font.render(self.turn_text, True, text_color)
        text_rect = text_surface.get_rect(center=(screen_width // 2, 30))
        surface.blit(text_surface, text_rect)


class CutInText:
    """Cut-in text for special events like critical hits."""

    def __init__(self):
        """Initialize the cut-in text."""
        self.is_visible = False
        self.text = ""
        self.text_color = (255, 255, 255)  # Default white
        self.start_time = 0.0
        self.duration = 1.0  # Show for 1 second

        # Colors
        self.critical_color = (255, 255, 0)  # Yellow
        self.heal_color = (0, 255, 255)  # Cyan
        self.background_color = (0, 0, 0, 200)  # Semi-transparent black

        # Font
        self.font = None

    def show_critical_hit(self) -> None:
        """Show critical hit cut-in."""
        self.show_text("CRITICAL HIT!", self.critical_color)

    def show_heal(self) -> None:
        """Show heal cut-in."""
        self.show_text("HEALED!", self.heal_color)

    def show_text(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """Show custom cut-in text."""
        self.is_visible = True
        self.text = text
        self.text_color = color
        self.start_time = time.time()

    def hide(self) -> None:
        """Hide the cut-in text."""
        self.is_visible = False

    def update(self, dt: float) -> None:
        """Update cut-in text state."""
        if not self.is_visible:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time

        # Auto-hide after duration
        if elapsed >= self.duration:
            self.hide()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the cut-in text."""
        if not self.is_visible:
            return

        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 48)

        # Get surface dimensions
        screen_width, screen_height = surface.get_size()

        # Draw semi-transparent background
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill(self.background_color)
        surface.blit(overlay, (0, 0))

        # Draw cut-in text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        surface.blit(text_surface, text_rect)
