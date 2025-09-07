"""
Title Screen UI Component for Starter Town Tactics.

This module provides a title screen display with automatic timeout
and integration with the game's UI system.
"""

import time
from pathlib import Path
from typing import Optional

import pygame


class TitleScreen:
    """Title screen component that displays for a specified duration."""

    def __init__(self, duration_seconds: float = 20.0):
        """Initialize the title screen.

        Args:
            duration_seconds: How long to display the title screen
        """
        self.duration_seconds = duration_seconds
        self.start_time: Optional[float] = None
        self.title_image: Optional[pygame.Surface] = None
        self.is_active = False
        self._load_title_image()

    def _load_title_image(self) -> None:
        """Load the title screen image."""
        try:
            # Try to load from the assets directory
            image_path = Path(__file__).parent.parent.parent / "assets" / "ui" / "title" / "title_screen.png"
            if image_path.exists():
                self.title_image = pygame.image.load(str(image_path))
                print(f"Loaded title screen image: {image_path}")
            else:
                print(f"Title screen image not found at: {image_path}")
                self._create_fallback_title()
        except pygame.error as e:
            print(f"Failed to load title screen image: {e}")
            self._create_fallback_title()

    def _create_fallback_title(self) -> None:
        """Create a fallback title screen if image loading fails."""
        # Create a simple fallback title screen
        self.title_image = pygame.Surface((800, 600))
        self.title_image.fill((50, 50, 80))  # Dark blue background

        # Add title text
        font = pygame.font.Font(None, 72)
        title_text = font.render("STARTER TOWN TACTICS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(400, 250))
        self.title_image.blit(title_text, title_rect)

        # Add subtitle
        subtitle_font = pygame.font.Font(None, 32)
        subtitle_text = subtitle_font.render("Press Start", True, (200, 200, 255))
        subtitle_rect = subtitle_text.get_rect(center=(400, 350))
        self.title_image.blit(subtitle_text, subtitle_rect)

        # Add copyright
        copyright_font = pygame.font.Font(None, 24)
        copyright_text = copyright_font.render("2025 Rob Downing", True, (150, 150, 150))
        copyright_rect = copyright_text.get_rect(center=(400, 550))
        self.title_image.blit(copyright_text, copyright_rect)

        print("Created fallback title screen")

    def start(self) -> None:
        """Start displaying the title screen."""
        self.start_time = time.time()
        self.is_active = True
        print(f"Title screen started - will display for {self.duration_seconds} seconds")

    def update(self, dt: float) -> bool:
        """Update the title screen.

        Args:
            dt: Delta time in seconds

        Returns:
            True if title screen is still active, False if it should end
        """
        if not self.is_active or self.start_time is None:
            return False

        elapsed_time = time.time() - self.start_time

        # Check if duration has passed
        if elapsed_time >= self.duration_seconds:
            self.is_active = False
            print("Title screen duration completed")
            return False

        return True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title screen with fade effects.

        Args:
            surface: The surface to draw on
        """
        if not self.is_active or self.title_image is None:
            return

        # Get surface dimensions
        surface_width = surface.get_width()
        surface_height = surface.get_height()

        # Calculate scaling to fit the surface
        image_width = self.title_image.get_width()
        image_height = self.title_image.get_height()

        # Scale the image to fit the surface while maintaining aspect ratio
        scale_x = surface_width / image_width
        scale_y = surface_height / image_height
        scale = min(scale_x, scale_y)

        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        # Scale the image
        scaled_image = pygame.transform.scale(self.title_image, (new_width, new_height))

        # Center the image on the surface
        x = (surface_width - new_width) // 2
        y = (surface_height - new_height) // 2

        # Calculate fade effect
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            fade_duration = 1.0  # 1 second fade in/out

            if elapsed < fade_duration:
                # Fade in
                alpha = int(255 * (elapsed / fade_duration))
            elif elapsed > self.duration_seconds - fade_duration:
                # Fade out
                fade_out_time = elapsed - (self.duration_seconds - fade_duration)
                alpha = int(255 * (1.0 - (fade_out_time / fade_duration)))
            else:
                # Full opacity
                alpha = 255

            # Apply alpha to the image
            if alpha < 255:
                scaled_image.set_alpha(alpha)

        surface.blit(scaled_image, (x, y))

    def is_displaying(self) -> bool:
        """Check if the title screen is currently being displayed."""
        return self.is_active

    def get_remaining_time(self) -> float:
        """Get the remaining display time in seconds."""
        if not self.is_active or self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time
        return max(0.0, self.duration_seconds - elapsed)

    def skip(self) -> None:
        """Skip the title screen immediately."""
        self.is_active = False
        print("Title screen skipped")
