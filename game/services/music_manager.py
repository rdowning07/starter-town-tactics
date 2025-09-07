"""
Music Manager for Starter Town Tactics.

Handles background music playback with fade support and looping.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pygame


class MusicManager:
    """Background music manager for looping tracks with fade support."""

    def __init__(self):
        """Initialize the music manager."""
        self.enabled = True
        self.current_track: Optional[str] = None
        self.volume = 0.6

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("Music manager initialized successfully")
        except Exception as e:
            print(f"Failed to initialize music manager: {e}")
            self.enabled = False

    def play(
        self, path: str, volume: float = None, loop: bool = True, fade_ms: int = 1000
    ) -> bool:
        """Play a track; stops any currently playing music.

        Args:
            path: Path to the music file
            volume: Volume level (0.0 to 1.0), uses current volume if None
            loop: Whether to loop the track
            fade_ms: Fade in duration in milliseconds

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        # Use provided volume or current volume
        if volume is None:
            volume = self.volume

        try:
            # Convert to absolute path
            full_path = Path(path).resolve()
            if not full_path.exists():
                print(f"Music file not found: {full_path}")
                return False

            pygame.mixer.music.load(str(full_path))
            pygame.mixer.music.set_volume(volume)

            loops = -1 if loop else 0
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)

            self.current_track = str(full_path)
            print(
                f"Playing music: {full_path.name} (volume: {volume:.2f}, loop: {loop})"
            )
            return True

        except Exception as e:
            print(f"Failed to play music {path}: {e}")
            return False

    def stop(self, fade_ms: int = 1000) -> None:
        """Stop currently playing music with fade out.

        Args:
            fade_ms: Fade out duration in milliseconds
        """
        if not self.enabled:
            return

        try:
            pygame.mixer.music.fadeout(fade_ms)
            self.current_track = None
            print("Music stopped")
        except Exception as e:
            print(f"Failed to stop music: {e}")

    def set_volume(self, volume: float) -> None:
        """Set the music volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.enabled:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except Exception as e:
                print(f"Failed to set music volume: {e}")

    def is_playing(self) -> bool:
        """Check if music is currently playing.

        Returns:
            True if music is playing, False otherwise
        """
        if not self.enabled:
            return False
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False

    def get_current_track(self) -> Optional[str]:
        """Get the currently playing track path.

        Returns:
            Current track path or None if no track is playing
        """
        return self.current_track
