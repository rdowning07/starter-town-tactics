#!/usr/bin/env python3
"""
Test Sprite Sheet Integration Script

This script demonstrates how to use the new sprite sheet loading functionality
and proper pygame initialization.
"""

import pygame
import sys
from pathlib import Path

# Add game directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.sprite_manager import SpriteManager
from game.pygame_init import init_pygame, quit_pygame
from game.unit import Unit

def test_sprite_sheet_loading():
    """Test loading animations from sprite sheets."""
    
    print("🎬 Testing sprite sheet integration...")
    
    # Initialize pygame
    if not init_pygame(window_size=(640, 480), window_title="Sprite Sheet Test"):
        print("❌ Failed to initialize pygame")
        return False
    
    try:
        # Create sprite manager
        sprite_manager = SpriteManager()
        
        # Test sprite sheet loading (if sheet exists)
        sheet_path = "assets/units/knight/attack.png"
        if Path(sheet_path).exists():
            print(f"\n📁 Loading sprite sheet: {sheet_path}")
            sprite_manager.load_unit_animation_from_sheet(
                unit_id="knight",
                animation_name="attack",
                sheet_path=sheet_path,
                frame_width=32,
                frame_height=32
            )
        else:
            print(f"\n⚠️  Sprite sheet not found: {sheet_path}")
            print("   Creating test animation with colored rectangles...")
            
            # Create test animation frames
            test_frames = []
            colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]  # Red to orange
            
            for color in colors:
                frame = pygame.Surface((32, 32))
                frame.fill(color)
                test_frames.append(frame)
            
            sprite_manager.load_unit_animation("knight", "attack", test_frames)
        
        # Create a test unit
        unit = Unit("knight", 2, 2, "player", health=10)
        unit.set_animation("attack", duration=30)
        
        # Test animation playback
        print("\n🎭 Testing animation playback...")
        
        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        
        running = True
        frame_count = 0
        
        while running and frame_count < 60:  # Run for 60 frames
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Update unit animation
            unit.update_animation()
            
            # Get current sprite
            current_sprite = unit.get_current_sprite(sprite_manager)
            
            # Draw sprite at center of screen
            sprite_rect = current_sprite.get_rect()
            sprite_rect.center = (320, 240)
            screen.blit(current_sprite, sprite_rect)
            
            # Draw animation info
            font = pygame.font.Font(None, 24)
            info_text = f"Animation: {unit.current_animation} | Timer: {unit.animation_timer}"
            text_surface = font.render(info_text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10))
            
            pygame.display.flip()
            clock.tick(10)  # 10 FPS
            frame_count += 1
        
        print("✅ Animation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        quit_pygame()

def test_pygame_initialization():
    """Test pygame initialization with different configurations."""
    
    print("\n🎮 Testing pygame initialization...")
    
    # Test 1: Basic initialization
    print("\n📋 Test 1: Basic initialization")
    if init_pygame(window_size=(400, 300), enable_sound=False):
        print("✅ Basic initialization successful")
        quit_pygame()
    else:
        print("❌ Basic initialization failed")
        return False
    
    # Test 2: Full initialization with sound
    print("\n📋 Test 2: Full initialization with sound")
    if init_pygame(window_size=(800, 600), enable_sound=True):
        print("✅ Full initialization successful")
        quit_pygame()
    else:
        print("❌ Full initialization failed")
        return False
    
    # Test 3: Large window initialization
    print("\n📋 Test 3: Large window initialization")
    if init_pygame(window_size=(1920, 1080), enable_sound=False):
        print("✅ Large window initialization successful")
        quit_pygame()
    else:
        print("❌ Large window initialization failed")
        return False
    
    return True

def main():
    """Main test function."""
    print("🎬 Sprite Sheet Integration Test Suite")
    print("=" * 50)
    
    try:
        # Test pygame initialization
        if not test_pygame_initialization():
            print("\n❌ Pygame initialization tests failed")
            return 1
        
        # Test sprite sheet loading
        if not test_sprite_sheet_loading():
            print("\n❌ Sprite sheet loading tests failed")
            return 1
        
        print("\n🎉 All tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 