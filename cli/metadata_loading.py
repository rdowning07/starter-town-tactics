"""
Metadata loading methods for the BT Fighter Demo.

This module contains the metadata loading methods extracted from the main demo
to improve code organization and maintainability.
"""

import json
from pathlib import Path
from typing import Dict

import pygame


class MetadataLoading:
    """Metadata loading methods for the demo."""

    def __init__(self, effect_creation):
        """Initialize metadata loading with effect creation reference."""
        self.effect_creation = effect_creation

    def load_animation_metadata(self) -> Dict:
        """Load animation metadata."""
        try:
            with open(
                "assets/units/_metadata/animation_metadata.json", "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
                print(f"Loaded metadata: {list(data.get('units', {}).keys())}")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load animation metadata: {e}")
            return {"units": {}}

    def load_effects_metadata(self) -> Dict:
        """Load effects metadata."""
        try:
            with open(
                "assets/effects/effects_metadata.json", "r", encoding="utf-8"
            ) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load effects metadata: {e}")
            return {"effects": {}}

    def load_unit_sprites(self) -> Dict[str, Dict[str, pygame.Surface]]:
        """Load unit sprites from individual PNG files."""
        sprites = {}

        # Load fighter sprites
        fighter_sprites = {}
        fighter_path = Path("assets/units/fighter")
        if fighter_path.exists():
            for png_file in fighter_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file)
                    if sprite.get_width() < 20 or sprite.get_height() < 20:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem  # filename without extension
                    fighter_sprites[anim_state] = sprite
                    print(f"Loaded fighter sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        # Load bandit sprites
        bandit_sprites = {}
        bandit_path = Path("assets/units/bandit")
        if bandit_path.exists():
            for png_file in bandit_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file)
                    if sprite.get_width() < 20 or sprite.get_height() < 20:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem
                    bandit_sprites[anim_state] = sprite
                    print(f"Loaded bandit sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        # Load black mage sprites
        mage_sprites = {}
        mage_path = Path("assets/units/black_mage")
        if mage_path.exists():
            for png_file in mage_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file) - lower threshold for mage
                    if sprite.get_width() < 15 or sprite.get_height() < 15:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem
                    mage_sprites[anim_state] = sprite
                    print(f"Loaded mage sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        # Load white mage sprites
        healer_sprites = {}
        healer_path = Path("assets/units/white_mage")
        if healer_path.exists():
            for png_file in healer_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file)
                    if sprite.get_width() < 20 or sprite.get_height() < 20:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem
                    healer_sprites[anim_state] = sprite
                    print(f"Loaded healer sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        # Load ranger sprites
        ranger_sprites = {}
        ranger_path = Path("assets/units/ranger")
        if ranger_path.exists():
            for png_file in ranger_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file)
                    if sprite.get_width() < 20 or sprite.get_height() < 20:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem
                    ranger_sprites[anim_state] = sprite
                    print(f"Loaded ranger sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        sprites["fighter"] = fighter_sprites
        sprites["bandit"] = bandit_sprites
        sprites["mage"] = mage_sprites
        sprites["healer"] = healer_sprites
        sprites["ranger"] = ranger_sprites

        # Set default animations - use fallback if no real sprites
        if not fighter_sprites:
            print("No real fighter sprites found, using fallback")
        if not bandit_sprites:
            print("No real bandit sprites found, using fallback")

        return sprites

    def load_effect_sprites(self, effects_metadata: Dict) -> Dict[str, pygame.Surface]:
        """Load effect sprite sheets and slice them into frames."""
        sprites = {}
        for effect_name in ["spark", "slash"]:
            if effect_name in effects_metadata.get("effects", {}):
                effect_meta = effects_metadata["effects"][effect_name]
                sheet_path = effect_meta["sheet"]
                try:
                    # Load the sprite sheet with alpha channel preserved
                    sheet = pygame.image.load(sheet_path).convert_alpha()
                    frame_width = effect_meta["frame_size"][0]
                    frame_height = effect_meta["frame_size"][1]
                    frames = effect_meta["frames"]

                    # Extract the first frame with transparency
                    first_frame = pygame.Surface(
                        (frame_width, frame_height), pygame.SRCALPHA
                    )
                    first_frame.blit(sheet, (0, 0), (0, 0, frame_width, frame_height))
                    sprites[effect_name] = first_frame

                    print(
                        f"Loaded {effect_name} effect: {frame_width}x{frame_height}, {frames} frames"
                    )
                except pygame.error as e:
                    print(f"Failed to load {sheet_path}: {e}")
                    # Create placeholder
                    sprites[effect_name] = self.effect_creation.create_placeholder(
                        32, 32, (255, 255, 0, 128)  # Semi-transparent yellow
                    )
        return sprites
