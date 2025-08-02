import os
import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml


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
        self, unit_type: str, team: str = "blue", frame: int = 0
    ) -> Optional[str]:
        """Get unit sprite with animation frame support."""
        key = f"unit_{unit_type}_{team}_{frame}"
        return self.sprites.get(key)

    def get_unit_animation_frames(
        self, unit_type: str, team: str = "blue"
    ) -> List[str]:
        """Get all animation frames for a unit."""
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
