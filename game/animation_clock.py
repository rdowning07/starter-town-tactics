"""
Animation Clock - Handles frame timing for animations.
"""

import time
from typing import Dict, Optional


class AnimationClock:
    """Handles frame timing for animations with deterministic behavior."""

    def __init__(self):
        """Initialize the animation clock."""
        self.start_time = time.time() * 1000  # Convert to milliseconds
        self._animation_states: Dict[str, Dict] = {}

    def get_elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds since clock start."""
        return int((time.time() * 1000) - self.start_time)

    def get_frame_index(self, meta: Dict, animation_id: Optional[str] = None) -> int:
        """
        Calculate current frame index for an animation.

        Args:
            meta: Animation metadata with frame_duration_ms, frames, loop
            animation_id: Optional ID for tracking individual animation state

        Returns:
            Current frame index (0-based)
        """
        frame_duration = meta.get("frame_duration_ms", 100)
        total_frames = meta.get("frames", 1)
        loop = meta.get("loop", True)

        if animation_id and animation_id in self._animation_states:
            # Use individual animation timing
            elapsed = self._animation_states[animation_id]["elapsed_ms"]
        else:
            # Use global timing
            elapsed = self.get_elapsed_ms()

        if loop:
            return (elapsed // frame_duration) % total_frames
        else:
            return min(total_frames - 1, elapsed // frame_duration)

    def start_animation(self, animation_id: str, meta: Dict) -> None:
        """
        Start tracking an individual animation.

        Args:
            animation_id: Unique identifier for the animation
            meta: Animation metadata
        """
        self._animation_states[animation_id] = {
            "start_time": self.get_elapsed_ms(),
            "elapsed_ms": 0,
            "meta": meta.copy(),
        }

    def update_animation(self, animation_id: str) -> None:
        """
        Update elapsed time for an individual animation.

        Args:
            animation_id: Animation identifier to update
        """
        if animation_id in self._animation_states:
            self._animation_states[animation_id]["elapsed_ms"] = (
                self.get_elapsed_ms() - self._animation_states[animation_id]["start_time"]
            )

    def is_animation_finished(self, animation_id: str) -> bool:
        """
        Check if a non-looping animation has finished.

        Args:
            animation_id: Animation identifier to check

        Returns:
            True if animation is finished, False otherwise
        """
        if animation_id not in self._animation_states:
            return True

        state = self._animation_states[animation_id]
        meta = state["meta"]

        if meta.get("loop", True):
            return False

        frame_duration = meta.get("frame_duration_ms", 100)
        total_frames = meta.get("frames", 1)
        total_duration = frame_duration * total_frames

        return state["elapsed_ms"] >= total_duration

    def reset_animation(self, animation_id: str) -> None:
        """
        Reset an animation to start.

        Args:
            animation_id: Animation identifier to reset
        """
        if animation_id in self._animation_states:
            self._animation_states[animation_id]["start_time"] = self.get_elapsed_ms()
            self._animation_states[animation_id]["elapsed_ms"] = 0

    def clear_animation(self, animation_id: str) -> None:
        """
        Remove animation tracking.

        Args:
            animation_id: Animation identifier to clear
        """
        if animation_id in self._animation_states:
            del self._animation_states[animation_id]
