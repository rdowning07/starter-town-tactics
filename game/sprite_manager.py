import os
import re
from typing import Dict, List, Optional

import yaml
import pygame


class SpriteManager:
    """
    Enhanced sprite manager with animation frame support and tier-based unit loading.
    Supports the sprite_mapping_master.yaml configuration.
    """

    def __init__(self):
        self.sprites = {}
        self.animations = {}
        self.unit_mapping = {}
        self.tier_groups = {}
        self.tilesets = {}
        self.unit_sprites = {}  # Add missing attribute for animation support
        self._load_sprite_mapping()
        self._load_tileset_mapping()

    def _load_sprite_mapping(self):
        """Load sprite mapping from YAML configuration."""
        mapping_path = "sprite_mapping_master.yaml"

        if os.path.exists(mapping_path):
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.unit_mapping = yaml.safe_load(f)

            # Group units by tier
            for unit_name, unit_data in self.unit_mapping.items():
                tier = unit_data.get("tier", 1)
                if tier not in self.tier_groups:
                    self.tier_groups[tier] = []
                self.tier_groups[tier].append(unit_name)

    def _load_tileset_mapping(self):
        """Load tileset mapping from YAML configuration."""
        mapping_path = "data/tileset_mapping.yaml"

        if os.path.exists(mapping_path):
            with open(mapping_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.tilesets = {
                    tileset["name"]: tileset for tileset in data.get("tilesets", [])
                }

    def load_assets(self):
        """Load all game assets including animation frames."""
        self.load_terrain_assets()
        self.load_unit_assets()
        self.load_ui_assets()
        self.load_effect_assets()

    def load_terrain_assets(self):
        """Load terrain tile assets."""
        terrain_mapping = {
            "castle": "castle.png",
            "desert": "desert.png",
            "dungeon": "dungeon.png",
            "house": "house.png",
            "interior": "inside.png",
            "village": "outside.png",
            "terrain": "terrain.png",
            "water": "water.png",
            "worldmap": "world.png",
        }

        for terrain_type, filename in terrain_mapping.items():
            path = f"assets/tiles/{terrain_type}/{filename}"
            if os.path.exists(path):
                self.sprites[f"terrain_{terrain_type}"] = path

    def load_unit_assets(self):
        """Load unit sprite assets with animation frame support."""
        # Load from sprite mapping
        for unit_name, unit_data in self.unit_mapping.items():
            base_sprite = unit_data["sprite"]
            unit_dir = os.path.dirname(base_sprite)

            # Extract unit ID from the base sprite path (e.g., "blue_1_0.png" -> ID 1)
            match = re.search(r"blue_(\d+)_0\.png", base_sprite)
            if match:
                unit_id = match.group(1)

                if os.path.exists(unit_dir):
                    # Load all animation frames for this unit
                    for frame in range(12):  # 0-11 frames
                        # Use the correct unit ID: blue_{unit_id}_{frame}.png
                        frame_path = f"{unit_dir}/blue_{unit_id}_{frame}.png"
                        if os.path.exists(frame_path):
                            key = f"unit_{unit_name}_blue_{frame}"
                            self.sprites[key] = frame_path
                            self.animations[key] = frame

    def load_ui_assets(self):
        """Load UI element assets."""
        ui_elements = ["health", "ap", "move", "attack"]
        for element in ui_elements:
            path = f"assets/ui/icons/{element}.png"
            if os.path.exists(path):
                self.sprites[f"ui_{element}"] = path

    def load_effect_assets(self):
        """Load effect assets."""
        effect_types = ["summoning", "particle", "aura"]
        for effect_type in effect_types:
            effect_dir = f"assets/effects/{effect_type}"
            if os.path.exists(effect_dir):
                for file in os.listdir(effect_dir):
                    if file.endswith(".png"):
                        path = f"{effect_dir}/{file}"
                        key = f"effect_{effect_type}_{file[:-4]}"
                        self.sprites[key] = path

    def get_terrain_sprite(self, terrain_type: str) -> Optional[str]:
        """Get terrain sprite by type."""
        return self.sprites.get(f"terrain_{terrain_type}")

    def get_unit_sprite(
        self, unit_type: str, team: str = "blue", frame: int = 0, state: str = "idle", frame_index: int = 0
    ) -> Optional[str | pygame.Surface]:
        """Get unit sprite with animation frame support and backward compatibility."""
        # First try the new animation system
        if unit_type in self.unit_sprites:
            animation = self.unit_sprites[unit_type].get(state)
            if animation and isinstance(animation, list):
                return animation[frame_index % len(animation)]
            elif animation:
                return animation
        
        # Fall back to the old system
        key = f"unit_{unit_type}_{team}_{frame}"
        return self.sprites.get(key)

    def get_unit_animation_frames(
        self, unit_type: str, team: str = "blue", animation_name: str = "idle"
    ) -> List[str | pygame.Surface]:
        """Get all animation frames for a unit from the new animation structure."""
        # Try new animation structure first
        if unit_type in self.unit_sprites and animation_name in self.unit_sprites[unit_type]:
            return self.unit_sprites[unit_type][animation_name]
        
        # Fallback to old method
        frames = []
        for frame in range(12):
            sprite = self.get_unit_sprite(unit_type, team, frame)
            if sprite:
                frames.append(sprite)
        return frames

    def get_units_by_tier(self, tier: int) -> List[str]:
        """Get all units of a specific tier."""
        return self.tier_groups.get(tier, [])

    def get_unit_info(self, unit_type: str) -> Optional[Dict]:
        """Get unit information from mapping."""
        return self.unit_mapping.get(unit_type)

    def get_unit_color(self, unit_type: str) -> Optional[str]:
        """Get unit's color theme."""
        unit_info = self.get_unit_info(unit_type)
        return unit_info.get("color") if unit_info else None

    def get_unit_tier(self, unit_type: str) -> int:
        """Get unit's tier level."""
        unit_info = self.get_unit_info(unit_type)
        return unit_info.get("tier", 1) if unit_info else 1

    def get_cursor_sprite(self) -> Optional[str]:
        """Returns the cursor sprite."""
        return self.sprites.get("ui_cursor")

    def get_sprite(self, name: str) -> Optional[str]:
        """Get sprite by name."""
        return self.sprites.get(name)

    def add_sprite(self, name: str, sprite_path: str):
        """Add a sprite to the manager."""
        self.sprites[name] = sprite_path

    def list_available_units(self) -> List[str]:
        """List all available unit types."""
        return list(self.unit_mapping.keys())

    def validate_assets(self) -> Dict[str, List[str]]:
        """Validate that all mapped assets exist."""
        missing = []
        found = []

        for unit_name, unit_data in self.unit_mapping.items():
            base_sprite = unit_data["sprite"]
            if os.path.exists(base_sprite):
                found.append(unit_name)
            else:
                missing.append(unit_name)

        return {"found": found, "missing": missing}

    def get_tileset_info(self, tileset_name: str) -> Optional[Dict]:
        """Get tileset information from mapping."""
        return self.tilesets.get(tileset_name)

    def get_tileset_file(self, tileset_name: str) -> Optional[str]:
        """Get tileset file path."""
        tileset_info = self.get_tileset_info(tileset_name)
        return tileset_info.get("file") if tileset_info else None

    def get_tileset_tags(self, tileset_name: str) -> List[str]:
        """Get tileset tags."""
        tileset_info = self.get_tileset_info(tileset_name)
        return tileset_info.get("tags", []) if tileset_info else []

    def get_tileset_layer(self, tileset_name: str) -> Optional[str]:
        """Get tileset layer (background, midground, foreground)."""
        tileset_info = self.get_tileset_info(tileset_name)
        return tileset_info.get("layer") if tileset_info else None

    def list_available_tilesets(self) -> List[str]:
        """List all available tileset names."""
        return list(self.tilesets.keys())

    def get_tilesets_by_layer(self, layer: str) -> List[str]:
        """Get all tilesets for a specific layer."""
        return [
            name for name, info in self.tilesets.items() if info.get("layer") == layer
        ]

    def get_tilesets_by_tag(self, tag: str) -> List[str]:
        """Get all tilesets with a specific tag."""
        return [
            name for name, info in self.tilesets.items() if tag in info.get("tags", [])
        ]

    def get_animation_metadata(self, unit_name: str) -> Dict:
        """Get animation metadata for a unit."""
        # Try to load from unit-specific metadata file
        metadata_path = f"assets/units/{unit_name}/animation_metadata.json"
        if os.path.exists(metadata_path):
            try:
                import json
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load metadata for {unit_name}: {e}")
        
        # Return default metadata if unit-specific file doesn't exist
        return {
            "idle": {"frame_count": 4, "frame_duration": 4, "loop": True},
            "attack": {"frame_count": 5, "frame_duration": 2, "loop": False, "fx_type": "spark", "fx_at": [2], "sound_at": [1]},
            "hurt": {"frame_count": 2, "frame_duration": 3, "loop": False, "fx_type": "flash", "fx_at": [0], "sound_at": [0]},
            "die": {"frame_count": 6, "frame_duration": 3, "loop": False, "fx_type": "shake", "fx_at": [2], "sound_at": [3]},
            "stun": {"frame_count": 3, "frame_duration": 3, "loop": False, "fx_type": "flash", "fx_at": [1], "sound_at": [1]}
        }

    # Additional methods for visual debugger and tests
    def load_terrain_sprite(self, terrain_type: str, surface: pygame.Surface) -> None:
        """Load a terrain sprite surface directly."""
        self.sprites[f"terrain_{terrain_type}"] = surface

    def load_unit_sprite(self, unit_id: str, animation_state: str, surface: pygame.Surface) -> None:
        """Load a unit sprite surface directly."""
        key = f"unit_{unit_id}_{animation_state}"
        self.sprites[key] = surface

    def load_unit_animation(self, unit_id: str, animation_name: str, frame_list: list[pygame.Surface]) -> None:
        """Load a unit animation with multiple frames."""
        if unit_id not in self.unit_sprites:
            self.unit_sprites[unit_id] = {}
        self.unit_sprites[unit_id][animation_name] = frame_list

    def load_unit_animation_from_sheet(
        self,
        unit_id: str,
        animation_name: str,
        sheet_path: str,
        frame_width: int,
        frame_height: int
    ) -> None:
        """Load a unit animation from a sprite sheet."""
        try:
            sheet = pygame.image.load(sheet_path).convert_alpha()
            sheet_width, _ = sheet.get_size()
            frames = []

            for x in range(0, sheet_width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, 0, frame_width, frame_height)).copy()
                frames.append(frame)

            if unit_id not in self.unit_sprites:
                self.unit_sprites[unit_id] = {}

            self.unit_sprites[unit_id][animation_name] = frames
            print(f"✅ Loaded {len(frames)} frames from sheet for {unit_id} {animation_name}")
            
        except pygame.error as e:
            print(f"⚠️  Failed to load sprite sheet {sheet_path}: {e}")
        except Exception as e:
            print(f"❌ Error loading sprite sheet {sheet_path}: {e}")

    def load_unit_animations_from_folder(self, unit_id: str, unit_folder: str) -> None:
        """Load all animations for a unit from the standardized folder structure."""
        from pathlib import Path
        
        unit_path = Path(unit_folder)
        if not unit_path.exists():
            print(f"⚠️  Unit folder not found: {unit_folder}")
            return
        
        # Initialize unit in sprite dictionary
        if unit_id not in self.unit_sprites:
            self.unit_sprites[unit_id] = {}
        
        # Load animations from subfolders
        animation_types = ["idle", "attack", "walk"]
        
        for anim_type in animation_types:
            anim_folder = unit_path / anim_type
            if anim_folder.exists():
                frames = []
                frame_files = sorted(anim_folder.glob("frame_*.png"))
                
                for frame_file in frame_files:
                    try:
                        frame_surface = pygame.image.load(str(frame_file))
                        frames.append(frame_surface)
                    except pygame.error as e:
                        print(f"⚠️  Failed to load frame {frame_file}: {e}")
                
                if frames:
                    self.unit_sprites[unit_id][anim_type] = frames
                    print(f"✅ Loaded {len(frames)} frames for {unit_id} {anim_type}")
                else:
                    print(f"⚠️  No frames found for {unit_id} {anim_type}")

    def load_all_unit_animations(self, units_base_path: str = "assets/units") -> None:
        """Load animations for all units from the standardized folder structure."""
        from pathlib import Path
        
        units_path = Path(units_base_path)
        if not units_path.exists():
            print(f"⚠️  Units base path not found: {units_base_path}")
            return
        
        unit_folders = [d for d in units_path.iterdir() if d.is_dir()]
        print(f"🎬 Loading animations for {len(unit_folders)} units...")
        
        for unit_folder in unit_folders:
            unit_id = unit_folder.name
            self.load_unit_animations_from_folder(unit_id, str(unit_folder))
        
        print("✅ Animation loading complete!")
