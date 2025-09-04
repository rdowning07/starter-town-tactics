"""
Screen effects like shake, flash, and other visual feedback.
Provides juice for combat actions and events.
"""

import math
import time
from typing import Optional, Tuple

import pygame


class ScreenShake:
    """Screen shake effect for impacts and hits."""

    def __init__(self):
        """Initialize screen shake."""
        self.is_active = False
        self.intensity = 0.0
        self.duration = 0.0
        self.start_time = 0.0
        self.frequency = 20.0  # Shake frequency

    def shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        """Start screen shake.

        Args:
            intensity: How strong the shake is (pixels)
            duration: How long to shake (seconds)
        """
        self.is_active = True
        self.intensity = intensity
        self.duration = duration
        self.start_time = time.time()

    def update(self, dt: float) -> Tuple[float, float]:
        """Update shake and return offset.

        Args:
            dt: Delta time in seconds

        Returns:
            Tuple of (x_offset, y_offset) for camera
        """
        if not self.is_active:
            return (0.0, 0.0)

        current_time = time.time()
        elapsed = current_time - self.start_time

        if elapsed >= self.duration:
            self.is_active = False
            return (0.0, 0.0)

        # Calculate shake intensity (fade out over time)
        remaining_time = self.duration - elapsed
        fade_factor = remaining_time / self.duration
        current_intensity = self.intensity * fade_factor

        # Generate shake offset using sine waves
        x_offset = math.sin(elapsed * self.frequency) * current_intensity
        y_offset = math.cos(elapsed * self.frequency * 1.3) * current_intensity

        return (x_offset, y_offset)


class ScreenFlash:
    """Screen flash effect for critical hits and special events."""

    def __init__(self):
        """Initialize screen flash."""
        self.is_active = False
        self.color = (255, 255, 255)  # White flash
        self.alpha = 0
        self.duration = 0.0
        self.start_time = 0.0

    def flash(self, color: Tuple[int, int, int] = (255, 255, 255), duration: float = 0.2) -> None:
        """Start screen flash.

        Args:
            color: Flash color (RGB)
            duration: Flash duration (seconds)
        """
        self.is_active = True
        self.color = color
        self.duration = duration
        self.start_time = time.time()

    def update(self, dt: float) -> Optional[pygame.Surface]:
        """Update flash and return overlay surface.

        Args:
            dt: Delta time in seconds

        Returns:
            Flash overlay surface or None if not active
        """
        if not self.is_active:
            return None

        current_time = time.time()
        elapsed = current_time - self.start_time

        if elapsed >= self.duration:
            self.is_active = False
            return None

        # Calculate flash alpha (fade out over time)
        remaining_time = self.duration - elapsed
        fade_factor = remaining_time / self.duration
        self.alpha = int(255 * fade_factor)

        # Create flash overlay (will be created by caller with proper size)
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw flash overlay.

        Args:
            surface: Surface to draw flash on
        """
        if not self.is_active or self.alpha <= 0:
            return

        # Create flash overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, self.alpha))
        surface.blit(overlay, (0, 0))


class ScreenEffects:
    """Combined screen effects manager."""

    def __init__(self):
        """Initialize screen effects."""
        self.shake = ScreenShake()
        self.flash = ScreenFlash()

    def hit_impact(self, intensity: float = 3.0) -> None:
        """Trigger hit impact effects."""
        self.shake.shake(intensity, 0.2)
        self.flash.flash((255, 255, 0), 0.1)  # Yellow flash

    def critical_hit(self, intensity: float = 8.0) -> None:
        """Trigger critical hit effects."""
        self.shake.shake(intensity, 0.4)
        self.flash.flash((255, 0, 0), 0.2)  # Red flash

    def unit_defeated(self, intensity: float = 5.0) -> None:
        """Trigger unit defeated effects."""
        self.shake.shake(intensity, 0.3)
        self.flash.flash((255, 0, 0), 0.15)  # Red flash

    def heal_effect(self) -> None:
        """Trigger heal effect."""
        self.flash.flash((0, 255, 255), 0.2)  # Cyan flash

    def update(self, dt: float) -> Tuple[float, float]:
        """Update all effects.

        Args:
            dt: Delta time in seconds

        Returns:
            Tuple of (x_offset, y_offset) for camera shake
        """
        # Update shake
        shake_offset = self.shake.update(dt)

        # Update flash
        self.flash.update(dt)

        return shake_offset

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all screen effects.

        Args:
            surface: Surface to draw effects on
        """
        self.flash.draw(surface)
