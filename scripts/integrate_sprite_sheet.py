#!/usr/bin/env python3
"""
Sprite Sheet Integration Script

This script takes a sprite sheet and automatically slices it into individual
animation frames and organizes them into our unit structure.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pygame

# Add game directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.pygame_init import init_pygame, quit_pygame

# Configuration
SPRITE_SIZE = 32
FRAMES_PER_ANIMATION = 4  # Assuming 4 frames per animation type
ANIMATION_TYPES = ["idle", "walk", "attack"]

# Character mappings (based on the sprite sheet analysis)
CHARACTER_MAPPINGS = {
    0: {"name": "Knight", "team": "player", "colors": ["green", "grey"]},
    1: {"name": "Shadow", "team": "ai", "colors": ["grey", "black"]},
    2: {"name": "Berserker", "team": "ai", "colors": ["pink", "red"]},
    3: {"name": "Paladin", "team": "player", "colors": ["red", "white"]},
    4: {"name": "Mage", "team": "player", "colors": ["blue", "grey"]},
    5: {"name": "Ranger", "team": "ai", "colors": ["brown", "green"]},
}


def slice_sprite_sheet(sheet_path: str) -> Dict[str, Dict[str, Any]]:
    """Slice the sprite sheet into individual frames."""

    if not init_pygame(window_size=(100, 100), enable_sound=False):
        print("❌ Failed to initialize pygame")
        return {}

    try:
        # Load the sprite sheet
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()

        print(f"📊 Sprite sheet loaded: {sheet_width}x{sheet_height}")
        print(f"🎯 Sprite size: {SPRITE_SIZE}x{SPRITE_SIZE}")

        # Calculate grid dimensions
        cols = sheet_width // SPRITE_SIZE
        rows = sheet_height // SPRITE_SIZE

        print(f"📐 Grid: {cols} columns x {rows} rows")

        # Extract frames for each character
        characters = {}

        for row in range(rows):
            if row in CHARACTER_MAPPINGS:
                char_info = CHARACTER_MAPPINGS[row]
                char_name = char_info["name"]
                characters[char_name] = {"frames": [], "info": char_info}

                # Extract frames for this character
                for col in range(cols):
                    x = col * SPRITE_SIZE
                    y = row * SPRITE_SIZE

                    frame = sheet.subsurface(pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)).copy()
                    characters[char_name]["frames"].append(frame)

                print(f"✅ {char_name}: {len(characters[char_name]['frames'])} frames")

        return characters

    except Exception as e:
        print(f"❌ Error loading sprite sheet: {e}")
        return {}
    finally:
        quit_pygame()


def organize_animations(characters: Dict[str, Dict]) -> None:
    """Organize frames into animation types and save to unit folders."""

    for char_name, char_data in characters.items():
        frames = char_data["frames"]
        char_info = char_data["info"]

        # Create unit directory
        unit_dir = Path(f"assets/units/{char_name.lower()}")
        unit_dir.mkdir(exist_ok=True)

        print(f"\n📁 Processing {char_name}...")

        # Organize frames into animations
        animations = {}
        frames_per_anim = len(frames) // len(ANIMATION_TYPES)

        for i, anim_type in enumerate(ANIMATION_TYPES):
            start_frame = i * frames_per_anim
            end_frame = start_frame + frames_per_anim

            anim_frames = frames[start_frame:end_frame]
            animations[anim_type] = anim_frames

            # Create animation subdirectory
            anim_dir = unit_dir / anim_type
            anim_dir.mkdir(exist_ok=True)

            # Save individual frames
            for j, frame in enumerate(anim_frames):
                frame_path = anim_dir / f"frame_{j}.png"
                pygame.image.save(frame, str(frame_path))

            print(f"  ✅ {anim_type}: {len(anim_frames)} frames")

        # Create metadata
        create_animation_metadata(char_name, animations, unit_dir)

        # Create sprite sheet for each animation
        create_animation_sprite_sheets(char_name, animations, unit_dir)


def create_animation_metadata(char_name: str, animations: Dict[str, List[pygame.Surface]], unit_dir: Path) -> None:
    """Create animation metadata JSON file."""

    metadata = {}

    for anim_type, frames in animations.items():
        metadata[anim_type] = {
            "frame_width": SPRITE_SIZE,
            "frame_height": SPRITE_SIZE,
            "frames": len(frames),
            "duration": 200 if anim_type == "attack" else 300,
            "loop": anim_type != "attack",
            "fx_at": [1] if anim_type == "attack" else [],
            "sound_at": [0] if anim_type == "attack" else [],
        }

    metadata_path = unit_dir / "animation_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"  📄 Metadata created: {metadata_path}")


def create_animation_sprite_sheets(char_name: str, animations: Dict[str, List[pygame.Surface]], unit_dir: Path) -> None:
    """Create sprite sheets for each animation type."""

    for anim_type, frames in animations.items():
        if not frames:
            continue

        # Create horizontal sprite sheet
        sheet_width = len(frames) * SPRITE_SIZE
        sheet_height = SPRITE_SIZE

        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)

        for i, frame in enumerate(frames):
            x = i * SPRITE_SIZE
            sheet.blit(frame, (x, 0))

        # Save sprite sheet
        sheet_path = unit_dir / f"{anim_type}.png"
        pygame.image.save(sheet, str(sheet_path))

        print(f"  🖼️  Sprite sheet created: {sheet_path}")


def create_unit_mapping(characters: Dict[str, Dict]) -> None:
    """Create or update unit mapping in sprite_manager."""

    mapping = {}

    for char_name, char_data in characters.items():
        char_info = char_data["info"]

        mapping[char_name.lower()] = {
            "name": char_name,
            "team": char_info["team"],
            "tier": 1,
            "color": char_info["colors"][0],
            "sprite": f"assets/units/{char_name.lower()}/idle/frame_0.png",
        }

    # Save to a new mapping file
    mapping_path = Path("data/unit_mapping_new.json")
    mapping_path.parent.mkdir(exist_ok=True)

    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=2)

    print(f"\n📋 Unit mapping created: {mapping_path}")


def main():
    """Main integration function."""

    print("🎬 Sprite Sheet Integration Tool")
    print("=" * 40)

    # Check if sprite sheet exists
    sheet_path = "future1.png"
    if not os.path.exists(sheet_path):
        print(f"❌ Sprite sheet not found: {sheet_path}")
        print("   Please place the sprite sheet in the project root as 'future1.png'")
        return 1

    print(f"📁 Found sprite sheet: {sheet_path}")

    # Slice the sprite sheet
    print("\n🔪 Slicing sprite sheet...")
    characters = slice_sprite_sheet(sheet_path)

    if not characters:
        print("❌ Failed to slice sprite sheet")
        return 1

    # Organize animations
    print("\n📂 Organizing animations...")
    organize_animations(characters)

    # Create unit mapping
    print("\n🗺️ Creating unit mapping...")
    create_unit_mapping(characters)

    print(f"\n🎉 Integration complete!")
    print(f"✅ Created {len(characters)} character units")
    print(f"✅ Each unit has {len(ANIMATION_TYPES)} animation types")
    print(f"✅ Ready for testing with: make test-cli-animations")

    return 0


if __name__ == "__main__":
    exit(main())
