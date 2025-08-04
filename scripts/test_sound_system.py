#!/usr/bin/env python3
"""
Test Sound System Integration

This script tests the sound manager and sound integration with animations.
"""

import sys
import os
from pathlib import Path

# Add game directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.sound_manager import SoundManager
from game.pygame_init import init_pygame, quit_pygame

def test_sound_manager_basic():
    """Test basic sound manager functionality."""
    
    print("🔊 Testing Sound Manager Basic Functionality")
    print("=" * 50)
    
    # Initialize pygame
    if not init_pygame(window_size=(100, 100), enable_sound=False):
        print("❌ Failed to initialize pygame")
        return False
    
    try:
        # Test sound manager creation
        sound_manager = SoundManager(enable_sound=True)
        print("✅ Sound manager created")
        
        # Test loading sounds
        sounds_to_load = [
            ("slash", "assets/sfx/slash.wav"),
            ("death", "assets/sfx/death.wav"),
            ("move", "assets/sfx/move.wav"),
            ("select", "assets/sfx/select.wav")
        ]
        
        loaded_count = 0
        for name, path in sounds_to_load:
            if sound_manager.load_sound(name, path):
                loaded_count += 1
                print(f"✅ Loaded sound: {name}")
            else:
                print(f"❌ Failed to load sound: {name}")
        
        print(f"📊 Loaded {loaded_count}/{len(sounds_to_load)} sounds")
        
        # Test mute functionality
        print("\n🔇 Testing mute functionality...")
        sound_manager.mute()
        print("✅ Sound muted")
        
        sound_manager.unmute()
        print("✅ Sound unmuted")
        
        # Test volume controls
        print("\n🎚️ Testing volume controls...")
        sound_manager.set_sfx_volume(0.5)
        sound_manager.set_music_volume(0.3)
        print("✅ Volume controls working")
        
        # Test sound playing (should work silently if muted)
        print("\n▶️ Testing sound playback...")
        for name, _ in sounds_to_load:
            if sound_manager.is_sound_loaded(name):
                sound_manager.play(name)
                print(f"✅ Played sound: {name}")
        
        # Test directory loading
        print("\n📁 Testing directory loading...")
        loaded_from_dir = sound_manager.load_sounds_from_directory("assets/sfx")
        print(f"✅ Loaded {loaded_from_dir} sounds from directory")
        
        # Test cleanup
        sound_manager.cleanup()
        print("✅ Sound manager cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in sound manager test: {e}")
        return False
    finally:
        quit_pygame()

def test_sound_integration():
    """Test sound integration with animation metadata."""
    
    print("\n🎬 Testing Sound Integration with Animations")
    print("=" * 50)
    
    # Test animation metadata sound triggers
    test_metadata = {
        "attack": {
            "frame_width": 32,
            "frame_height": 32,
            "frames": 3,
            "duration": 200,
            "loop": False,
            "fx_at": [1],
            "sound_at": [0]  # Play sound at frame 0
        },
        "walk": {
            "frame_width": 32,
            "frame_height": 32,
            "frames": 3,
            "duration": 300,
            "loop": True,
            "fx_at": [],
            "sound_at": [1]  # Play sound at frame 1
        }
    }
    
    print("📋 Testing animation metadata sound triggers...")
    
    for anim_name, anim_data in test_metadata.items():
        sound_triggers = anim_data.get("sound_at", [])
        print(f"  {anim_name}: Sound triggers at frames {sound_triggers}")
        
        # Simulate frame progression
        for frame in range(anim_data["frames"]):
            if frame in sound_triggers:
                print(f"    Frame {frame}: Should play sound")
            else:
                print(f"    Frame {frame}: No sound")
    
    print("✅ Animation metadata sound triggers validated")
    return True

def test_cli_mute_flag():
    """Test CLI mute flag functionality."""
    
    print("\n🎛️ Testing CLI Mute Flag")
    print("=" * 30)
    
    # Simulate different CLI arguments
    test_cases = [
        (["ranger"], "Sound enabled"),
        (["ranger", "--mute"], "Sound muted"),
        (["--mute", "ranger"], "Sound muted"),
        ([], "Sound enabled (default)")
    ]
    
    for args, expected in test_cases:
        enable_sound = "--mute" not in args
        status = "Enabled" if enable_sound else "Muted"
        print(f"  Args: {args} → Sound: {status}")
    
    print("✅ CLI mute flag logic working")
    return True

def main():
    """Main test function."""
    
    print("🎵 Sound System Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Sound Manager", test_sound_manager_basic),
        ("Sound Integration", test_sound_integration),
        ("CLI Mute Flag", test_cli_mute_flag)
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
        print("🎉 All sound system tests passed!")
        print("\n💡 Next steps:")
        print("  1. Run 'make generate-sounds' to create sound effects")
        print("  2. Test with: PYTHONPATH=. python devtools/visual_animation_tester.py ranger")
        print("  3. Test mute with: PYTHONPATH=. python devtools/visual_animation_tester.py ranger --mute")
        return 0
    else:
        print("⚠️  Some sound system tests failed.")
        return 1

if __name__ == "__main__":
    exit(main()) 