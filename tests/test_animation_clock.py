"""
Tests for AnimationClock component.
"""

import time
import unittest
from unittest.mock import patch

from game.animation_clock import AnimationClock


class TestAnimationClock(unittest.TestCase):
    """Test cases for AnimationClock."""

    def setUp(self):
        """Set up test fixtures."""
        self.clock = AnimationClock()

    def test_get_elapsed_ms(self):
        """Test elapsed time calculation."""
        # Should return a positive integer
        elapsed = self.clock.get_elapsed_ms()
        self.assertIsInstance(elapsed, int)
        self.assertGreaterEqual(elapsed, 0)

    def test_get_frame_index_basic(self):
        """Test basic frame index calculation."""
        meta = {"frame_duration_ms": 100, "frames": 4, "loop": True}

        # At 0ms, should be frame 0
        with patch.object(self.clock, "get_elapsed_ms", return_value=0):
            frame_idx = self.clock.get_frame_index(meta)
            self.assertEqual(frame_idx, 0)

        # At 150ms, should be frame 1
        with patch.object(self.clock, "get_elapsed_ms", return_value=150):
            frame_idx = self.clock.get_frame_index(meta)
            self.assertEqual(frame_idx, 1)

    def test_get_frame_index_looping(self):
        """Test looping animation frame calculation."""
        meta = {"frame_duration_ms": 100, "frames": 4, "loop": True}

        # At 500ms (5 frames), should loop back to frame 1
        with patch.object(self.clock, "get_elapsed_ms", return_value=500):
            frame_idx = self.clock.get_frame_index(meta)
            self.assertEqual(frame_idx, 1)

    def test_get_frame_index_non_looping(self):
        """Test non-looping animation frame calculation."""
        meta = {"frame_duration_ms": 100, "frames": 4, "loop": False}

        # At 500ms, should be clamped to last frame (3)
        with patch.object(self.clock, "get_elapsed_ms", return_value=500):
            frame_idx = self.clock.get_frame_index(meta)
            self.assertEqual(frame_idx, 3)

    def test_individual_animation_tracking(self):
        """Test individual animation state tracking."""
        meta = {"frame_duration_ms": 100, "frames": 4, "loop": False}

        animation_id = "test_anim"

        # Start animation
        self.clock.start_animation(animation_id, meta)

        # Update animation
        self.clock.update_animation(animation_id)

        # Get frame index for this specific animation
        frame_idx = self.clock.get_frame_index(meta, animation_id)
        self.assertIsInstance(frame_idx, int)
        self.assertGreaterEqual(frame_idx, 0)
        self.assertLess(frame_idx, 4)

    def test_animation_finished_check(self):
        """Test animation finished detection."""
        meta = {"frame_duration_ms": 100, "frames": 2, "loop": False}

        animation_id = "test_anim"

        # Start animation
        self.clock.start_animation(animation_id, meta)

        # Initially not finished
        self.assertFalse(self.clock.is_animation_finished(animation_id))

        # Simulate time passing beyond animation duration
        with patch.object(self.clock, "get_elapsed_ms", return_value=300):
            self.clock.update_animation(animation_id)
            self.assertTrue(self.clock.is_animation_finished(animation_id))

    def test_looping_animation_never_finished(self):
        """Test that looping animations are never considered finished."""
        meta = {"frame_duration_ms": 100, "frames": 4, "loop": True}

        animation_id = "test_anim"

        # Start animation
        self.clock.start_animation(animation_id, meta)

        # Simulate time passing
        with patch.object(self.clock, "get_elapsed_ms", return_value=1000):
            self.clock.update_animation(animation_id)
            self.assertFalse(self.clock.is_animation_finished(animation_id))

    def test_reset_animation(self):
        """Test animation reset functionality."""
        meta = {"frame_duration_ms": 100, "frames": 4, "loop": False}

        animation_id = "test_anim"

        # Start animation
        self.clock.start_animation(animation_id, meta)

        # Simulate time passing
        with patch.object(self.clock, "get_elapsed_ms", return_value=200):
            self.clock.update_animation(animation_id)
            frame_idx = self.clock.get_frame_index(meta, animation_id)
            self.assertEqual(frame_idx, 2)

        # Reset animation
        self.clock.reset_animation(animation_id)

        # Should be back to frame 0 (reset sets elapsed_ms to 0)
        frame_idx = self.clock.get_frame_index(meta, animation_id)
        self.assertEqual(frame_idx, 0)

    def test_clear_animation(self):
        """Test animation clearing functionality."""
        meta = {"frame_duration_ms": 100, "frames": 4, "loop": False}

        animation_id = "test_anim"

        # Start animation
        self.clock.start_animation(animation_id, meta)
        self.assertIn(animation_id, self.clock._animation_states)

        # Clear animation
        self.clock.clear_animation(animation_id)
        self.assertNotIn(animation_id, self.clock._animation_states)

    def test_default_values(self):
        """Test default metadata values."""
        meta = {}  # Empty metadata

        # Should use defaults
        frame_idx = self.clock.get_frame_index(meta)
        self.assertEqual(frame_idx, 0)  # Default frame duration is 100ms, so at 0ms = frame 0


if __name__ == "__main__":
    unittest.main()
