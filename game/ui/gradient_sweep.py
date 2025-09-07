"""
Gradient Sweep Overlay for Starter Town Tactics.

Provides cinematic gradient overlays for victory and defeat states.
"""

import time
from typing import Optional, Tuple

import pygame


class GradientSweep:
    """Gradient sweep overlay for dramatic effect."""

    def __init__(self):
        """Initialize the gradient sweep system."""
        self.active = False
        self.sweep_type: Optional[str] = None  # "victory" or "defeat"
        self.duration = 0.0
        self.start_time: Optional[float] = None
        self.screen_width = 0
        self.screen_height = 0

    def trigger(self, sweep_type: str, duration: float = 2.0) -> None:
        """Trigger a gradient sweep effect.

        Args:
            sweep_type: Type of sweep ("victory" or "defeat")
            duration: How long the effect lasts in seconds
        """
        self.active = True
        self.sweep_type = sweep_type
        self.duration = duration
        self.start_time = time.time()
        print(f"Gradient sweep triggered: {sweep_type} for {duration}s")

    def update_screen_size(self, width: int, height: int) -> None:
        """Update the screen dimensions for proper rendering.

        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the gradient sweep overlay.

        Args:
            screen: The pygame surface to draw on
        """
        if not self.active or self.start_time is None or self.sweep_type is None:
            return

        # Update screen size if needed
        if self.screen_width == 0 or self.screen_height == 0:
            self.update_screen_size(screen.get_width(), screen.get_height())

        elapsed = time.time() - self.start_time

        # Check if effect should end
        if elapsed >= self.duration:
            self.active = False
            self.sweep_type = None
            self.start_time = None
            return

        # Calculate progress (0.0 to 1.0)
        progress = min(elapsed / self.duration, 1.0)

        # Create gradient overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        if self.sweep_type == "victory":
            # Gold gradient from top to bottom
            self._draw_victory_gradient(overlay, progress)
        elif self.sweep_type == "defeat":
            # Red gradient from edges inward
            self._draw_defeat_gradient(overlay, progress)

        screen.blit(overlay, (0, 0))

    def _draw_victory_gradient(self, overlay: pygame.Surface, progress: float) -> None:
        """Draw victory gradient (gold sweep from top)."""
        # Gold colors
        gold_start = (255, 215, 0, 80)  # Gold with transparency
        gold_end = (255, 255, 255, 0)  # White with no transparency

        # Calculate sweep height
        sweep_height = int(self.screen_height * progress)

        # Draw gradient from top
        for y in range(sweep_height):
            # Interpolate color
            ratio = y / max(sweep_height, 1)
            r = int(gold_start[0] * (1 - ratio) + gold_end[0] * ratio)
            g = int(gold_start[1] * (1 - ratio) + gold_end[1] * ratio)
            b = int(gold_start[2] * (1 - ratio) + gold_end[2] * ratio)
            a = int(gold_start[3] * (1 - ratio) + gold_end[3] * ratio)

            color = (r, g, b, a)
            pygame.draw.line(overlay, color, (0, y), (self.screen_width, y))

    def _draw_defeat_gradient(self, overlay: pygame.Surface, progress: float) -> None:
        """Draw defeat gradient (red sweep from edges)."""
        # Red colors
        red_start = (139, 0, 0, 100)  # Dark red with transparency
        red_end = (255, 0, 0, 0)  # Bright red with no transparency

        # Calculate sweep distance from edges
        max_sweep = min(self.screen_width, self.screen_height) // 2
        sweep_distance = int(max_sweep * progress)

        # Draw gradient from all edges
        for distance in range(sweep_distance):
            # Interpolate color
            ratio = distance / max(sweep_distance, 1)
            r = int(red_start[0] * (1 - ratio) + red_end[0] * ratio)
            g = int(red_start[1] * (1 - ratio) + red_end[1] * ratio)
            b = int(red_start[2] * (1 - ratio) + red_end[2] * ratio)
            a = int(red_start[3] * (1 - ratio) + red_end[3] * ratio)

            color = (r, g, b, a)

            # Top edge
            if distance < self.screen_height:
                pygame.draw.line(overlay, color, (0, distance), (self.screen_width, distance))
            # Bottom edge
            if distance < self.screen_height:
                pygame.draw.line(
                    overlay,
                    color,
                    (0, self.screen_height - 1 - distance),
                    (self.screen_width, self.screen_height - 1 - distance),
                )
            # Left edge
            if distance < self.screen_width:
                pygame.draw.line(overlay, color, (distance, 0), (distance, self.screen_height))
            # Right edge
            if distance < self.screen_width:
                pygame.draw.line(
                    overlay,
                    color,
                    (self.screen_width - 1 - distance, 0),
                    (self.screen_width - 1 - distance, self.screen_height),
                )

    def is_active(self) -> bool:
        """Check if gradient sweep is currently active.

        Returns:
            True if gradient sweep is active, False otherwise
        """
        return self.active
