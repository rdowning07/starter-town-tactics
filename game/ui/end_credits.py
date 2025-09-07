"""
End Credits UI Component for Starter Town Tactics.

This module provides an end credits display with automatic timeout
and integration with the game's UI system.
"""

import time
from pathlib import Path
from typing import Optional

import pygame


class EndCredits:
    """End credits component that displays for a specified duration."""

    def __init__(self, duration_seconds: float = 5.0):
        """Initialize the end credits.

        Args:
            duration_seconds: How long to display the end credits
        """
        self.duration_seconds = duration_seconds
        self.start_time: Optional[float] = None
        self.credits_image: Optional[pygame.Surface] = None
        self.is_active = False
        self._load_credits_image()

    def _load_credits_image(self) -> None:
        """Load the end credits image."""
        try:
            # Try to load from the assets directory
            image_path = (
                Path(__file__).parent.parent.parent / "assets" / "ui" / "title" / "Start Town Tactics End Credits.png"
            )
            if image_path.exists():
                self.credits_image = pygame.image.load(str(image_path))
                print(f"Loaded end credits image: {image_path}")
            else:
                print(f"End credits image not found at: {image_path}")
                self._create_fallback_credits()
        except pygame.error as e:
            print(f"Failed to load end credits image: {e}")
            self._create_fallback_credits()

    def _create_fallback_credits(self) -> None:
        """Create a fallback end credits screen if image loading fails."""
        # Create a simple fallback surface
        self.credits_image = pygame.Surface((800, 600))
        self.credits_image.fill((0, 0, 0))  # Black background

        # Add simple text
        font = pygame.font.Font(None, 48)
        title_text = font.render("STARTER TOWN TACTICS", True, (255, 255, 255))
        credits_text = font.render("END CREDITS", True, (255, 255, 255))

        # Center the text
        title_rect = title_text.get_rect(center=(400, 250))
        credits_rect = credits_text.get_rect(center=(400, 350))

        self.credits_image.blit(title_text, title_rect)
        self.credits_image.blit(credits_text, credits_rect)

    def start(self) -> None:
        """Start displaying the end credits."""
        self.start_time = time.time()
        self.is_active = True
        print(f"End credits started - will display for {self.duration_seconds} seconds")

    def update(self) -> bool:
        """Update the end credits state.

        Returns:
            True if credits are still active, False if they've finished
        """
        if not self.is_active or self.start_time is None:
            return False

        elapsed = time.time() - self.start_time
        if elapsed >= self.duration_seconds:
            self.is_active = False
            print("End credits completed")
            return False

        return True

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the end credits on the screen.

        Args:
            screen: The pygame surface to draw on
        """
        if not self.is_active or self.credits_image is None:
            return

        # Get screen dimensions
        screen_width, screen_height = screen.get_size()

        # Scale the image to fit the screen while maintaining aspect ratio
        image_width, image_height = self.credits_image.get_size()

        # Calculate scaling factor
        scale_x = screen_width / image_width
        scale_y = screen_height / image_height
        scale = min(scale_x, scale_y)

        # Scale the image
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)
        scaled_image = pygame.transform.scale(self.credits_image, (new_width, new_height))

        # Center the image on the screen
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2

        screen.blit(scaled_image, (x, y))

    def skip(self) -> None:
        """Skip the end credits."""
        if self.is_active:
            self.is_active = False
            print("End credits skipped")
