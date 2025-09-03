#!/usr/bin/env python3
"""
Test Animation System Script

This script tests the new standardized animation system with the folder structure:
units/
└── unit_name/
    ├── idle/
    │   ├── frame_0.png
    │   └── frame_1.png
    └── attack/
        ├── frame_0.png
        ├── frame_1.png
        └── frame_2.png
"""

import sys
from pathlib import Path

import pygame

# Add game directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.sprite_manager import SpriteManager


def test_animation_loading():
    """Test loading animations from the new folder structure."""

    print("🎬 Testing animation system...")

    # Initialize pygame
    pygame.init()

    # Create sprite manager
    sprite_manager = SpriteManager()

    # Load all unit animations
    print("\n📁 Loading all unit animations...")
    sprite_manager.load_all_unit_animations()

    # Test specific units
    test_units = ["knight", "Recruit", "archer", "mage"]

    print("\n🧪 Testing animation retrieval...")

    for unit_name in test_units:
        print(f"\n📋 Testing {unit_name}:")

        # Test idle animation
        idle_frames = sprite_manager.get_unit_animation_frames(unit_name, animation_name="idle")
        print(f"  🎬 Idle frames: {len(idle_frames)}")

        # Test attack animation
        attack_frames = sprite_manager.get_unit_animation_frames(unit_name, animation_name="attack")
        print(f"  ⚔️  Attack frames: {len(attack_frames)}")

        # Test walk animation
        walk_frames = sprite_manager.get_unit_animation_frames(unit_name, animation_name="walk")
        print(f"  🚶 Walk frames: {len(walk_frames)}")

        # Test individual sprite retrieval
        idle_sprite = sprite_manager.get_unit_sprite(unit_name, state="idle", frame_index=0)
        if idle_sprite:
            print(f"  ✅ Idle sprite loaded successfully")
        else:
            print(f"  ❌ Failed to load idle sprite")

    print("\n✅ Animation system test complete!")

    # Test animation playback simulation
    print("\n🎭 Testing animation playback...")

    unit_name = "knight"
    idle_frames = sprite_manager.get_unit_animation_frames(unit_name, animation_name="idle")

    if idle_frames:
        print(f"  🎬 {unit_name} idle animation has {len(idle_frames)} frames")

        # Simulate animation cycle
        for i, frame in enumerate(idle_frames):
            print(f"    Frame {i}: {'pygame.Surface' if hasattr(frame, 'get_size') else 'file path'}")
    else:
        print(f"  ❌ No idle frames found for {unit_name}")

    pygame.quit()


def test_animation_structure():
    """Test that the animation folder structure is correct."""

    print("\n📁 Testing animation folder structure...")

    units_dir = Path("assets/units")
    if not units_dir.exists():
        print("❌ assets/units directory not found!")
        return

    unit_dirs = [d for d in units_dir.iterdir() if d.is_dir()]

    structure_issues = []

    for unit_dir in unit_dirs:
        unit_name = unit_dir.name
        print(f"\n📋 Checking {unit_name}:")

        # Check for animation folders
        animation_folders = ["idle", "attack", "walk"]

        for anim_folder in animation_folders:
            anim_path = unit_dir / anim_folder

            if anim_path.exists():
                frame_files = list(anim_path.glob("frame_*.png"))
                print(f"  ✅ {anim_folder}: {len(frame_files)} frames")

                if not frame_files:
                    structure_issues.append(f"{unit_name}/{anim_folder}: No frame files")
            else:
                print(f"  ❌ {anim_folder}: Missing folder")
                structure_issues.append(f"{unit_name}/{anim_folder}: Missing folder")

    if structure_issues:
        print(f"\n⚠️  Found {len(structure_issues)} structure issues:")
        for issue in structure_issues:
            print(f"  - {issue}")
    else:
        print("\n✅ All animation folders have correct structure!")


def main():
    """Main test function."""
    print("🎬 Animation System Test Suite")
    print("=" * 40)

    try:
        test_animation_structure()
        test_animation_loading()

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
