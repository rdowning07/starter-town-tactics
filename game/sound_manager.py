"""
Sound Manager for Starter Town Tactics

Handles loading, playing, and managing sound effects and music.
"""

import pygame
import os
from typing import Dict, List
from pathlib import Path

class SoundManager:
    """Manages sound effects and music for the game."""
    
    def __init__(self, enable_sound: bool = True):
        """Initialize the sound manager."""
        self.enabled = enable_sound
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
        # Initialize pygame mixer if sound is enabled
        if self.enabled:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                print("✅ Sound system initialized")
            except pygame.error as e:
                print(f"⚠️  Sound system initialization failed: {e}")
                self.enabled = False
    
    def load_sound(self, name: str, filepath: str) -> bool:
        """Load a sound effect from file."""
        if not self.enabled:
            return False
            
        try:
            if not os.path.exists(filepath):
                print(f"⚠️  Sound file not found: {filepath}")
                return False
                
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(self.sfx_volume)
            self.sounds[name] = sound
            print(f"✅ Loaded sound: {name}")
            return True
            
        except pygame.error as e:
            print(f"❌ Failed to load sound {name}: {e}")
            return False
    
    def load_sounds_from_directory(self, directory: str) -> int:
        """Load all WAV files from a directory."""
        if not self.enabled:
            return 0
            
        loaded_count = 0
        sfx_dir = Path(directory)
        
        if not sfx_dir.exists():
            print(f"⚠️  Sound directory not found: {directory}")
            return 0
        
        for sound_file in sfx_dir.glob("*.wav"):
            sound_name = sound_file.stem  # filename without extension
            if self.load_sound(sound_name, str(sound_file)):
                loaded_count += 1
        
        print(f"🎵 Loaded {loaded_count} sounds from {directory}")
        return loaded_count
    
    def play(self, sound_name: str) -> bool:
        """Play a sound effect."""
        if not self.enabled or sound_name not in self.sounds:
            return False
            
        try:
            self.sounds[sound_name].play()
            return True
        except pygame.error as e:
            print(f"❌ Failed to play sound {sound_name}: {e}")
            return False
    
    def play_music(self, filepath: str, loop: bool = True) -> bool:
        """Play background music."""
        if not self.enabled:
            return False
            
        try:
            if not os.path.exists(filepath):
                print(f"⚠️  Music file not found: {filepath}")
                return False
                
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            print(f"🎵 Playing music: {filepath}")
            return True
            
        except pygame.error as e:
            print(f"❌ Failed to play music: {e}")
            return False
    
    def stop_music(self) -> None:
        """Stop background music."""
        if self.enabled:
            pygame.mixer.music.stop()
    
    def pause_music(self) -> None:
        """Pause background music."""
        if self.enabled:
            pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Unpause background music."""
        if self.enabled:
            pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Update volume for all loaded sounds
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def mute(self) -> None:
        """Mute all sounds."""
        self.enabled = False
        self.stop_music()
        print("🔇 Sound muted")
    
    def unmute(self) -> None:
        """Unmute sounds."""
        self.enabled = True
        print("🔊 Sound unmuted")
    
    def toggle_mute(self) -> None:
        """Toggle mute state."""
        if self.enabled:
            self.mute()
        else:
            self.unmute()
    
    def get_loaded_sounds(self) -> List[str]:
        """Get list of loaded sound names."""
        return list(self.sounds.keys())
    
    def is_sound_loaded(self, sound_name: str) -> bool:
        """Check if a sound is loaded."""
        return sound_name in self.sounds
    
    def cleanup(self) -> None:
        """Clean up sound resources."""
        if self.enabled:
            pygame.mixer.quit()
            print("🔇 Sound system shutdown")
