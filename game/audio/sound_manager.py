"""
Sound Manager - plays sounds for game events with full architecture integration.
Integrated with GameState and includes fallback handling and logging.
"""

import pygame
import os
from typing import Optional, Dict, List
from game.ui.ui_state import UIState

# @api
# @refactor
class SoundManager:
    """Plays sounds for game events with full architecture integration."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.sounds = {}
        self.sound_enabled = True
        self.volume = 0.7
        self.missing_sounds = []
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._load_sounds()
        except Exception as e:
            print(f"⚠️  Sound system initialization failed: {e}")
            self.sound_enabled = False
    
    def _load_sounds(self):
        """Load all sound files with fallback handling."""
        sound_files = {
            "move": "assets/sfx/move.wav",
            "attack": "assets/sfx/attack.wav",
            "victory": "assets/sfx/victory.wav",
            "defeat": "assets/sfx/defeat.wav",
            "select": "assets/sfx/select.wav",
            "death": "assets/sfx/death.wav",
            "heal": "assets/sfx/heal.wav",
            "block": "assets/sfx/block.wav"
        }
        
        for sound_name, sound_path in sound_files.items():
            try:
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(self.volume)
                    
                    if self.logger:
                        self.logger.log_event("sound_loaded", {
                            "sound": sound_name,
                            "path": sound_path
                        })
                else:
                    self.missing_sounds.append(sound_name)
                    if self.logger:
                        self.logger.log_event("sound_missing", {
                            "sound": sound_name,
                            "path": sound_path
                        })
            except Exception as e:
                self.missing_sounds.append(sound_name)
                if self.logger:
                    self.logger.log_event("sound_load_error", {
                        "sound": sound_name,
                        "path": sound_path,
                        "error": str(e)
                    })
    
    def play(self, sound_name: str, volume: Optional[float] = None):
        """Play a sound with validation and logging."""
        if not self.sound_enabled:
            return
        
        if sound_name not in self.sounds:
            if sound_name not in self.missing_sounds:
                self.missing_sounds.append(sound_name)
                if self.logger:
                    self.logger.log_event("sound_not_found", {
                        "sound": sound_name
                    })
            return
        
        try:
            # Set volume if specified
            if volume is not None:
                self.sounds[sound_name].set_volume(volume)
            
            # Play the sound
            self.sounds[sound_name].play()
            
            if self.logger:
                self.logger.log_event("sound_played", {
                    "sound": sound_name,
                    "volume": volume or self.volume
                })
        
        except Exception as e:
            if self.logger:
                self.logger.log_event("sound_play_error", {
                    "sound": sound_name,
                    "error": str(e)
                })
    
    def play_game_event(self, event_type: str, game_state=None, **kwargs):
        """Play sound based on game event type."""
        sound_mapping = {
            "unit_moved": "move",
            "unit_attacked": "attack",
            "unit_selected": "select",
            "unit_died": "death",
            "unit_healed": "heal",
            "attack_blocked": "block",
            "game_victory": "victory",
            "game_defeat": "defeat"
        }
        
        sound_name = sound_mapping.get(event_type)
        if sound_name:
            self.play(sound_name)
    
    def set_volume(self, volume: float):
        """Set global volume for all sounds."""
        self.volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
        
        if self.logger:
            self.logger.log_event("volume_changed", {
                "volume": self.volume
            })
    
    def enable_sound(self, enabled: bool):
        """Enable or disable sound system."""
        self.sound_enabled = enabled
        
        if self.logger:
            self.logger.log_event("sound_toggled", {
                "enabled": enabled
            })
    
    def get_missing_sounds(self) -> List[str]:
        """Get list of missing sound files."""
        return self.missing_sounds.copy()
    
    def get_sound_status(self) -> Dict:
        """Get comprehensive sound system status."""
        return {
            "enabled": self.sound_enabled,
            "volume": self.volume,
            "loaded_sounds": list(self.sounds.keys()),
            "missing_sounds": self.missing_sounds,
            "total_sounds": len(self.sounds) + len(self.missing_sounds)
        }
    
    def create_sound_report(self) -> str:
        """Create a detailed sound system report."""
        status = self.get_sound_status()
        
        report = f"""
🔊 Sound System Report
=====================
Status: {'Enabled' if status['enabled'] else 'Disabled'}
Volume: {status['volume']:.1%}
Loaded Sounds: {len(status['loaded_sounds'])}/{status['total_sounds']}

✅ Loaded Sounds:
"""
        
        for sound in status['loaded_sounds']:
            report += f"  - {sound}\n"
        
        if status['missing_sounds']:
            report += f"\n❌ Missing Sounds:\n"
            for sound in status['missing_sounds']:
                report += f"  - {sound}\n"
        
        return report
    
    def cleanup(self):
        """Clean up sound resources."""
        try:
            pygame.mixer.quit()
        except Exception as e:
            if self.logger:
                self.logger.log_event("sound_cleanup_error", {
                    "error": str(e)
                })

# Global sound manager instance
_sound_manager = None

def get_sound_manager(logger=None) -> SoundManager:
    """Get global sound manager instance."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager(logger)
    return _sound_manager

def play_sound(sound_name: str, volume: Optional[float] = None):
    """Global function to play sounds."""
    sound_manager = get_sound_manager()
    sound_manager.play(sound_name, volume)

def play_game_event_sound(event_type: str, game_state=None, **kwargs):
    """Global function to play game event sounds."""
    sound_manager = get_sound_manager()
    sound_manager.play_game_event(event_type, game_state, **kwargs)
