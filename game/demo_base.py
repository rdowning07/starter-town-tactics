"""
Base Demo Class - Provides standardized timeout functionality for all demos.
"""

import time
from typing import Optional

import pygame


class DemoBase:
    """Base class for all demos with standardized timeout functionality."""

    def __init__(self, timeout_seconds: int = 30, auto_exit: bool = True):
        """
        Initialize the demo base.

        Args:
            timeout_seconds: Number of seconds before auto-exit (0 = no timeout)
            auto_exit: Whether to automatically exit after timeout
        """
        self.timeout_seconds = timeout_seconds
        self.auto_exit = auto_exit
        self.start_time = time.time()
        self.running = True

    def should_exit(self) -> bool:
        """Check if demo should exit due to timeout or user input."""
        if not self.running:
            return True

        if self.auto_exit and self.timeout_seconds > 0:
            elapsed = time.time() - self.start_time
            if elapsed >= self.timeout_seconds:
                print(f"⏰ Demo timeout reached ({self.timeout_seconds}s)")
                return True

        return False

    def handle_exit_events(self, event: pygame.event.Event) -> bool:
        """
        Handle exit events (ESC, Q, window close).

        Args:
            event: Pygame event to check

        Returns:
            True if exit was requested, False otherwise
        """
        if event.type == pygame.QUIT:
            print("🖱️ Window closed")
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                print("⌨️ Exit key pressed")
                return True
        return False

    def get_remaining_time(self) -> Optional[float]:
        """Get remaining time before timeout."""
        if self.timeout_seconds <= 0:
            return None
        elapsed = time.time() - self.start_time
        remaining = max(0, self.timeout_seconds - elapsed)
        return remaining

    def draw_timeout_info(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw timeout information on the surface."""
        if self.timeout_seconds <= 0:
            return

        remaining = self.get_remaining_time()
        if remaining is not None:
            # Draw timeout info in top-right corner
            timeout_text = f"Auto-exit: {remaining:.1f}s"
            text_surface = font.render(timeout_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.topright = (surface.get_width() - 10, 10)

            # Draw background for better visibility
            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(surface, (0, 0, 0, 128), bg_rect)
            pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)

            surface.blit(text_surface, text_rect)

    def stop(self) -> None:
        """Stop the demo."""
        self.running = False
