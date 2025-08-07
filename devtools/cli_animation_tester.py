# devtools/cli_animation_tester.py

import os
import sys
import json
from pathlib import Path
from game.sprite_manager import SpriteManager
from game.pygame_init import init_pygame, quit_pygame

ASSET_DIR = "assets/units"
METADATA_DIR = "assets/units"


def test_animation_slicing(unit_id: str, animation_name: str):
    """Test animation slicing for a specific unit and animation."""

    # Initialize pygame for sprite loading
    if not init_pygame(window_size=(100, 100), enable_sound=False):
        print("❌ Failed to initialize pygame")
        return False

    try:
        unit_dir = os.path.join(METADATA_DIR, unit_id)
        metadata_path = os.path.join(unit_dir, "animation_metadata.json")
        if not os.path.exists(metadata_path):
            print(f"❌ Metadata not found for unit '{unit_id}'")
            print(f"   Expected: {metadata_path}")
            return False

        with open(metadata_path, encoding='utf-8') as f:
            metadata = json.load(f)

        anim_data = metadata.get(animation_name)
        if not anim_data:
            print(f"❌ Animation '{animation_name}' not defined in metadata")
            print(f"   Available animations: {list(metadata.keys())}")
            return False

        frame_width = anim_data["frame_width"]
        frame_height = anim_data["frame_height"]
        expected_frames = anim_data["frames"]
        sprite_path = os.path.join(ASSET_DIR, unit_id, f"{animation_name}.png")

        # Check if sprite sheet exists
        if not os.path.exists(sprite_path):
            print(f"❌ Sprite sheet not found: {sprite_path}")
            return False

        sm = SpriteManager()
        sm.load_unit_animation_from_sheet(
            unit_id,
            animation_name,
            sprite_path,
            frame_width,
            frame_height
        )

        actual_frames = len(sm.unit_sprites[unit_id][animation_name])

        print(f"\n✅ Loaded animation: {unit_id}/{animation_name}")
        print(f"→ Frames sliced: {actual_frames}")
        print(f"→ Frame dimensions: {frame_width}x{frame_height}")
        print(f"→ Frame triggers (metadata): "
              f"{anim_data.get('fx_at', [])}, {anim_data.get('sound_at', [])}")

        if actual_frames != expected_frames:
            print(f"⚠️ Warning: Expected {expected_frames} frames, "
                  f"got {actual_frames}")
            return False

        print("✅ Frame count matches metadata.")
        return True

    except (OSError, ValueError) as e:
        print(f"❌ Error testing animation: {e}")
        return False
    finally:
        quit_pygame()


def test_all_unit_animations():
    """Test all animations for all units that have metadata."""

    print("🎬 Testing all unit animations...")

    units_dir = Path(ASSET_DIR)
    if not units_dir.exists():
        print(f"❌ Units directory not found: {ASSET_DIR}")
        return False

    total_tests = 0
    passed_tests = 0

    for unit_dir in units_dir.iterdir():
        if not unit_dir.is_dir():
            continue

        unit_id = unit_dir.name
        metadata_path = unit_dir / "animation_metadata.json"

        if not metadata_path.exists():
            print(f"⚠️  No metadata for {unit_id}")
            continue

        print(f"\n📁 Testing unit: {unit_id}")

        try:
            with open(metadata_path, encoding='utf-8') as f:
                metadata = json.load(f)

            for animation_name in metadata.keys():
                total_tests += 1
                print(f"  🎬 Testing {animation_name}...", end=" ")

                if test_animation_slicing(unit_id, animation_name):
                    passed_tests += 1
                    print("✅ PASS")
                else:
                    print("❌ FAIL")

        except (OSError, ValueError) as e:
            print(f"❌ Error loading metadata for {unit_id}: {e}")

    print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


def main():
    """Main function with command line argument support."""

    if len(sys.argv) > 2:
        # Test specific unit and animation
        unit_id = sys.argv[1]
        animation_name = sys.argv[2]
        print(f"🎬 Testing specific animation: {unit_id}/{animation_name}")
        success = test_animation_slicing(unit_id, animation_name)
    elif len(sys.argv) > 1:
        # Test all animations for specific unit
        unit_id = sys.argv[1]
        print(f"🎬 Testing all animations for unit: {unit_id}")

        unit_dir = os.path.join(METADATA_DIR, unit_id)
        metadata_path = os.path.join(unit_dir, "animation_metadata.json")
        if not os.path.exists(metadata_path):
            print(f"❌ No metadata found for unit: {unit_id}")
            return 1

        with open(metadata_path, encoding='utf-8') as f:
            metadata = json.load(f)

        total_tests = len(metadata)
        passed_tests = 0

        for animation_name in metadata.keys():
            if test_animation_slicing(unit_id, animation_name):
                passed_tests += 1

        print(f"\n📊 Results for {unit_id}: "
              f"{passed_tests}/{total_tests} passed")
        success = passed_tests == total_tests
    else:
        # Test all units
        success = test_all_unit_animations()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
