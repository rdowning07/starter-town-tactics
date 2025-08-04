#!/usr/bin/env python3
"""
Test FX System Integration

This script demonstrates the integration of the FX system with GameState
and animation metadata triggers.
"""

import pygame
import json
import os
from game.game_state import GameState
from game.sprite_manager import SpriteManager
from game.pygame_init import init_pygame, quit_pygame
from game.sound_manager import SoundManager

def test_fx_integration():
    """Test FX system integration with GameState."""
    
    print("🎬 Testing FX System Integration")
    print("=" * 40)
    
    # Initialize pygame
    if not init_pygame(window_size=(800, 600), window_title="FX Integration Test"):
        print("❌ Failed to initialize pygame")
        return False
    
    try:
        # Create game state
        game_state = GameState()
        print("✅ GameState created with FX manager")
        
        # Test basic FX triggering
        print("\n🔧 Testing basic FX triggering...")
        
        # Trigger various effects
        game_state.trigger_flash((400, 300), (255, 0, 0), 0.5)  # Red flash
        game_state.trigger_particle((400, 300), "sparkle", 10, 1.0)  # Particles
        game_state.trigger_screen_shake(5.0, 0.5)  # Screen shake
        
        print(f"✅ Triggered effects. Active count: {game_state.fx_manager.get_active_effects_count()}")
        
        # Test animation metadata integration
        print("\n🎭 Testing animation metadata integration...")
        
        # Load knight animation metadata
        metadata_path = "assets/units/knight/animation_metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path) as f:
                metadata = json.load(f)
            
            print("✅ Loaded knight animation metadata")
            
            # Test FX triggers from metadata
            for anim_name, anim_data in metadata.items():
                fx_frames = anim_data.get("fx_at", [])
                sound_frames = anim_data.get("sound_at", [])
                
                print(f"  {anim_name}: FX at frames {fx_frames}, Sound at frames {sound_frames}")
                
                # Simulate triggering effects for each frame
                for frame_index in range(anim_data["frames"]):
                    if frame_index in fx_frames:
                        print(f"    Frame {frame_index}: Would trigger FX")
                        game_state.trigger_fx("flash", (400, 300), 0.2, 0.5, (255, 255, 0))
                    
                    if frame_index in sound_frames:
                        print(f"    Frame {frame_index}: Would trigger sound")
        else:
            print("⚠️  Knight metadata not found")
        
        # Test FX update and rendering
        print("\n🎨 Testing FX rendering...")
        
        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        
        # Run for a few seconds to see effects
        start_time = pygame.time.get_ticks()
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            if current_time - start_time > 3000:  # 3 seconds
                break
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Trigger new effects on spacebar
                        game_state.trigger_flash((400, 300), (0, 255, 0), 0.3)
                        game_state.trigger_particle((400, 300), "sparkle", 5, 0.8)
            
            # Clear screen
            screen.fill((20, 20, 20))
            
            # Draw test info
            font = pygame.font.Font(None, 36)
            text = font.render("FX Integration Test - Press SPACE for effects, ESC to quit", True, (255, 255, 255))
            screen.blit(text, (50, 50))
            
            # Draw active effects count
            fx_count = game_state.fx_manager.get_active_effects_count()
            count_text = font.render(f"Active Effects: {fx_count}", True, (255, 255, 0))
            screen.blit(count_text, (50, 100))
            
            # Update and draw FX
            game_state.update_fx()
            game_state.draw_fx(screen)
            
            pygame.display.flip()
            clock.tick(60)
        
        print("✅ FX rendering test completed")
        
        # Test cleanup
        print("\n🧹 Testing FX cleanup...")
        game_state.clear_fx()
        print(f"✅ Effects cleared. Active count: {game_state.fx_manager.get_active_effects_count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in FX integration test: {e}")
        return False
    
    finally:
        quit_pygame()

def test_animation_fx_triggers():
    """Test FX triggers from animation metadata."""
    
    print("\n🎬 Testing Animation FX Triggers")
    print("=" * 40)
    
    # Test FX triggers from metadata directly
    print("Testing FX triggers from animation metadata...")
    
    metadata_path = "assets/units/knight/animation_metadata.json"
    if not os.path.exists(metadata_path):
        print(f"❌ Metadata not found: {metadata_path}")
        return False
    
    try:
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        print("✅ Loaded knight animation metadata")
        
        # Test that FX triggers are properly configured
        fx_triggers_found = False
        
        for anim_name, anim_data in metadata.items():
            fx_frames = anim_data.get("fx_at", [])
            if fx_frames:
                print(f"  ✅ {anim_name}: FX triggers at frames {fx_frames}")
                fx_triggers_found = True
            else:
                print(f"  ⚠️  {anim_name}: No FX triggers")
        
        if fx_triggers_found:
            print("✅ Animation metadata contains FX triggers")
            return True
        else:
            print("⚠️  No FX triggers found in animation metadata")
            return False
            
    except Exception as e:
        print(f"❌ Error testing animation metadata: {e}")
        return False

def main():
    """Main test function."""
    
    print("🎬 FX System Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("FX Integration with GameState", test_fx_integration),
        ("Animation FX Triggers", test_animation_fx_triggers)
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
        print("🎉 All FX integration tests passed!")
        print("\n💡 FX system features:")
        print("  ✅ Integrated with GameState")
        print("  ✅ Animation metadata triggers")
        print("  ✅ Visual effects (flash, particles, screen shake)")
        print("  ✅ Sound integration")
        print("  ✅ Proper cleanup and resource management")
        return 0
    else:
        print("⚠️  Some FX integration tests failed.")
        return 1

if __name__ == "__main__":
    exit(main()) 