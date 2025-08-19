"""
Asset manager for Pygame integration with the existing game/ architecture.
Loads sprites, sounds, and metadata from the assets folder.
"""

import json
import os
import pygame
from typing import Dict, Optional, Any


class AssetManager:
    """Manages loading and caching of game assets."""
    
    def __init__(self, base_path: str = "assets"):
        self.base_path = base_path
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.animation_metadata: Dict[str, Dict] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
        # Initialize pygame mixer for sound
        try:
            pygame.mixer.init()
        except pygame.error:
            print("⚠️  Sound system not available")
    
    def load_unit_sprites(self, unit_type: str) -> bool:
        """Load sprites for a specific unit type."""
        unit_path = os.path.join(self.base_path, "units", unit_type)
        
        if not os.path.exists(unit_path):
            print(f"⚠️  Unit path not found: {unit_path}")
            return False
        
        # Load animation sprites
        for animation in ["idle", "walk", "attack"]:
            sprite_path = os.path.join(unit_path, f"{animation}.png")
            if os.path.exists(sprite_path):
                try:
                    image = pygame.image.load(sprite_path).convert_alpha()
                    self.images[f"{unit_type}_{animation}"] = image
                except pygame.error as e:
                    print(f"⚠️  Failed to load {sprite_path}: {e}")
        
        # Load team variants
        for team in ["blue", "red", "neutral"]:
            variant_path = os.path.join(unit_path, f"{team}.png")
            if os.path.exists(variant_path):
                try:
                    image = pygame.image.load(variant_path).convert_alpha()
                    self.images[f"{unit_type}_{team}"] = image
                except pygame.error as e:
                    print(f"⚠️  Failed to load {variant_path}: {e}")
        
        # Load animation metadata
        meta_path = os.path.join(unit_path, "animation_metadata.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    self.animation_metadata[unit_type] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Failed to load metadata {meta_path}: {e}")
        
        return True
    
    def load_terrain_sprites(self) -> None:
        """Load terrain tile sprites."""
        terrain_path = os.path.join(self.base_path, "tiles", "terrain")
        
        if not os.path.exists(terrain_path):
            print(f"⚠️  Terrain path not found: {terrain_path}")
            return
        
        # Load terrain tiles
        for terrain_type in ["grass", "forest", "mountain", "road", "wall", "water"]:
            tile_path = os.path.join(terrain_path, f"{terrain_type}.png")
            if os.path.exists(tile_path):
                try:
                    image = pygame.image.load(tile_path).convert_alpha()
                    self.images[f"terrain_{terrain_type}"] = image
                except pygame.error as e:
                    print(f"⚠️  Failed to load {tile_path}: {e}")
    
    def load_sound_effects(self) -> None:
        """Load sound effects."""
        sfx_path = os.path.join(self.base_path, "sfx")
        
        if not os.path.exists(sfx_path):
            print(f"⚠️  SFX path not found: {sfx_path}")
            return
        
        # Load common sound effects
        sound_names = ["move", "attack", "slash", "block", "death", "heal", "menu", "select", "fireball"]
        
        for sound_name in sound_names:
            sound_path = os.path.join(sfx_path, f"{sound_name}.wav")
            if os.path.exists(sound_path):
                try:
                    sound = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name] = sound
                except pygame.error as e:
                    print(f"⚠️  Failed to load {sound_path}: {e}")
    
    def load_ui_elements(self) -> None:
        """Load UI elements."""
        ui_path = os.path.join(self.base_path, "ui")
        
        if not os.path.exists(ui_path):
            print(f"⚠️  UI path not found: {ui_path}")
            return
        
        # Load UI panels
        panels_path = os.path.join(ui_path, "panels")
        if os.path.exists(panels_path):
            for panel in ["button", "healthbar", "menu_bg"]:
                panel_path = os.path.join(panels_path, f"{panel}.png")
                if os.path.exists(panel_path):
                    try:
                        image = pygame.image.load(panel_path).convert_alpha()
                        self.images[f"ui_{panel}"] = image
                    except pygame.error as e:
                        print(f"⚠️  Failed to load {panel_path}: {e}")
        
        # Load UI icons
        icons_path = os.path.join(ui_path, "icons")
        if os.path.exists(icons_path):
            for icon in ["ap", "attack", "health", "move"]:
                icon_path = os.path.join(icons_path, f"{icon}.png")
                if os.path.exists(icon_path):
                    try:
                        image = pygame.image.load(icon_path).convert_alpha()
                        self.images[f"ui_{icon}"] = image
                    except pygame.error as e:
                        print(f"⚠️  Failed to load {icon_path}: {e}")
    
    def get_unit_sprite(self, unit_type: str, animation: str = "idle") -> Optional[pygame.Surface]:
        """Get a unit sprite for the specified type and animation."""
        key = f"{unit_type}_{animation}"
        return self.images.get(key)
    
    def get_unit_sprite_by_team(self, unit_type: str, team: str) -> Optional[pygame.Surface]:
        """Get a unit sprite for the specified type and team."""
        key = f"{unit_type}_{team}"
        return self.images.get(key)
    
    def get_terrain_sprite(self, terrain_type: str) -> Optional[pygame.Surface]:
        """Get a terrain sprite."""
        key = f"terrain_{terrain_type}"
        return self.images.get(key)
    
    def get_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        """Get a sound effect."""
        return self.sounds.get(sound_name)
    
    def get_ui_element(self, element_name: str) -> Optional[pygame.Surface]:
        """Get a UI element."""
        key = f"ui_{element_name}"
        return self.images.get(key)
    
    def get_animation_metadata(self, unit_type: str) -> Optional[Dict]:
        """Get animation metadata for a unit type."""
        return self.animation_metadata.get(unit_type)
    
    def play_sound(self, sound_name: str) -> None:
        """Play a sound effect if available."""
        sound = self.get_sound(sound_name)
        if sound:
            try:
                sound.play()
            except pygame.error:
                pass  # Sound system might not be available
    
    def load_all_common_assets(self) -> None:
        """Load all commonly used assets."""
        print("📦 Loading common assets...")
        
        # Load terrain
        self.load_terrain_sprites()
        
        # Load sound effects
        self.load_sound_effects()
        
        # Load UI elements
        self.load_ui_elements()
        
        # Load common unit types
        common_units = ["knight", "goblin", "mage", "archer"]
        for unit_type in common_units:
            self.load_unit_sprites(unit_type)
        
        print(f"✅ Loaded {len(self.images)} images, {len(self.sounds)} sounds")
