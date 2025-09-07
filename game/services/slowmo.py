"""
Slow Motion System for Starter Town Tactics.

Provides cinematic slow-motion effects for dramatic moments.
"""

import time
from typing import Optional


class SlowMo:
    """Slow motion effect manager for cinematic moments."""

    def __init__(self):
        """Initialize the slow motion system."""
        self.active = False
        self.slow_factor = 1.0
        self.duration = 0.0
        self.start_time: Optional[float] = None
        self.target_slow_factor = 1.0

    def trigger(self, slow_factor: float = 0.25, duration: float = 1.0) -> None:
        """Trigger a slow motion effect.

        Args:
            slow_factor: How slow to make time (0.1 = 10% speed, 0.25 = 25% speed)
            duration: How long the effect lasts in seconds
        """
        self.active = True
        self.slow_factor = slow_factor
        self.duration = duration
        self.start_time = time.time()
        self.target_slow_factor = slow_factor
        print(f"Slow-mo triggered: {slow_factor}x speed for {duration}s")

    def apply(self, dt: float) -> float:
        """Apply slow motion to a delta time value.

        Args:
            dt: Original delta time

        Returns:
            Modified delta time with slow motion applied
        """
        if not self.active or self.start_time is None:
            return dt

        elapsed = time.time() - self.start_time

        # Check if effect should end
        if elapsed >= self.duration:
            self.active = False
            self.slow_factor = 1.0
            self.start_time = None
            print("Slow-mo effect ended")
            return dt

        # Apply slow motion
        return dt * self.slow_factor

    def is_active(self) -> bool:
        """Check if slow motion is currently active.

        Returns:
            True if slow motion is active, False otherwise
        """
        return self.active

    def get_current_factor(self) -> float:
        """Get the current slow motion factor.

        Returns:
            Current slow motion factor (1.0 = normal speed)
        """
        return self.slow_factor if self.active else 1.0
