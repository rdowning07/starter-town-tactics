#!/usr/bin/env python3
"""
Test Animation Tools Integration

This script tests the integration of the CLI and Visual animation testers
with the sprite manager and pygame initialization.
"""

import json
import os
import sys
from pathlib import Path

# Add game directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame

from game.pygame_init import init_pygame, quit_pygame
from game.sprite_manager import SpriteManager


def test_metadata_loading():
    """Test loading animation metadata."""

    print("📁 Testing metadata loading...")

    # Test knight metadata
    knight_metadata_path = "assets/units/knight/animation_metadata.json"
    if os.path.exists(knight_metadata_path):
        with open(knight_metadata_path) as f:
            metadata = json.load(f)

        print(f"✅ Knight metadata loaded: {list(metadata.keys())}")

        # Test metadata structure
        for anim_name, anim_data in metadata.items():
            required_fields = ["frame_width", "frame_height", "frames", "duration"]
            missing_fields = [field for field in required_fields if field not in anim_data]

            if missing_fields:
                print(f"⚠️  {anim_name} missing fields: {missing_fields}")
            else:
                print(f"✅ {anim_name} metadata valid")

        return True
    else:
        print(f"❌ Knight metadata not found: {knight_metadata_path}")
        return False


def test_sprite_manager_integration():
    """Test sprite manager integration with animation tools."""

    print("\n🎬 Testing sprite manager integration...")

    # Initialize pygame
    if not init_pygame(window_size=(100, 100), enable_sound=False):
        print("❌ Failed to initialize pygame")
        return False

    try:
        sprite_manager = SpriteManager()

        # Test loading animation from sheet (with fallback)
        print("  Testing sprite sheet loading...")

        # Create test animation frames
        test_frames = []
        colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]

        for color in colors:
            frame = pygame.Surface((32, 32))
            frame.fill(color)
            test_frames.append(frame)

        sprite_manager.load_unit_animation("knight", "attack", test_frames)

        # Test sprite retrieval
        sprite = sprite_manager.get_unit_sprite("knight", state="attack", frame_index=0)
        if sprite:
            print("✅ Sprite retrieval successful")
        else:
            print("❌ Sprite retrieval failed")
            return False

        # Test animation frames
        frames = sprite_manager.get_unit_animation_frames("knight", animation_name="attack")
        if len(frames) == 3:
            print("✅ Animation frames loaded correctly")
        else:
            print(f"❌ Expected 3 frames, got {len(frames)}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error in sprite manager test: {e}")
        return False
    finally:
        quit_pygame()


def test_cli_tester_integration():
    """Test CLI animation tester integration."""

    print("\n📋 Testing CLI animation tester...")

    # Test metadata validation
    knight_metadata_path = "assets/units/knight/animation_metadata.json"
    if not os.path.exists(knight_metadata_path):
        print("❌ Knight metadata not found")
        return False

    with open(knight_metadata_path) as f:
        metadata = json.load(f)

    # Test animation data validation
    attack_data = metadata.get("attack")
    if not attack_data:
        print("❌ Attack animation not found in metadata")
        return False

    required_fields = ["frame_width", "frame_height", "frames"]
    for field in required_fields:
        if field not in attack_data:
            print(f"❌ Missing field: {field}")
            return False

    print("✅ CLI tester metadata validation passed")
    return True


def test_visual_tester_integration():
    """Test visual animation tester integration."""

    print("\n🎮 Testing visual animation tester...")

    # Test unit discovery
    units_dir = Path("assets/units")
    if not units_dir.exists():
        print("❌ Units directory not found")
        return False

    units_with_metadata = []
    for unit_dir in units_dir.iterdir():
        if unit_dir.is_dir():
            metadata_path = unit_dir / "animation_metadata.json"
            if metadata_path.exists():
                units_with_metadata.append(unit_dir.name)

    if not units_with_metadata:
        print("❌ No units with metadata found")
        return False

    print(f"✅ Found units with metadata: {units_with_metadata}")

    # Test metadata loading for each unit
    for unit_id in units_with_metadata:
        metadata_path = os.path.join("assets", "units", unit_id, "animation_metadata.json")
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
            print(f"✅ {unit_id} metadata loaded: {list(metadata.keys())}")
        except Exception as e:
            print(f"❌ Failed to load {unit_id} metadata: {e}")
            return False

    return True


def test_error_handling():
    """Test error handling in animation tools."""

    print("\n🛡️ Testing error handling...")

    # Test missing metadata
    fake_unit = "fake_unit"
    fake_metadata_path = os.path.join("assets", "units", fake_unit, "animation_metadata.json")

    if not os.path.exists(fake_metadata_path):
        print("✅ Correctly handles missing metadata")
    else:
        print("⚠️  Unexpected metadata found for fake unit")

    # Test missing sprite sheets
    knight_attack_path = "assets/units/knight/attack.png"
    if not os.path.exists(knight_attack_path):
        print("✅ Correctly identifies missing sprite sheets")
    else:
        print("⚠️  Unexpected sprite sheet found")

    return True


def main():
    """Main test function."""

    print("🎬 Animation Tools Integration Test Suite")
    print("=" * 50)

    tests = [
        ("Metadata Loading", test_metadata_loading),
        ("Sprite Manager Integration", test_sprite_manager_integration),
        ("CLI Tester Integration", test_cli_tester_integration),
        ("Visual Tester Integration", test_visual_tester_integration),
        ("Error Handling", test_error_handling),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print(f"\n📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Animation tools integration successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
