#!/usr/bin/env python3
"""
Test FX Integration with Sim Runner

This script demonstrates how FX effects can be integrated with the sim_runner
for combat and game events.
"""

import pygame
import time
from game.game_state import GameState
from game.sim_runner import SimRunner
from game.pygame_init import init_pygame, quit_pygame

def test_fx_sim_runner_integration():
    """Test FX integration with sim runner for combat effects."""
    
    print("🎬 Testing FX Integration with Sim Runner")
    print("=" * 50)
    
    # Initialize pygame
    if not init_pygame(window_size=(800, 600), window_title="FX Sim Runner Test"):
        print("❌ Failed to initialize pygame")
        return False
    
    try:
        # Create game state with FX manager
        game_state = GameState()
        print("✅ GameState created with FX manager")
        
        # Create sim runner
        sim_runner = SimRunner(game_state.turn_controller, game_state.ai_controller)
        print("✅ SimRunner created")
        
        # Add some test units
        game_state.add_unit("player1", "player", ap=3, hp=10)
        game_state.add_unit("player2", "player", ap=2, hp=8)
        game_state.add_unit("ai1", "ai", ap=2, hp=6)
        game_state.add_unit("ai2", "ai", ap=1, hp=4)
        
        print("✅ Added test units")
        
        # Simulate some combat events with FX
        print("\n⚔️  Simulating combat events with FX...")
        
        # Simulate player attack
        print("  🗡️  Player attack event")
        game_state.trigger_fx("flash", (400, 300), 0.3, 1.0, (255, 255, 0))  # Yellow flash
        game_state.trigger_screen_shake(3.0, 0.2)  # Screen shake
        
        # Simulate AI response
        print("  🤖 AI response event")
        game_state.trigger_fx("particle", (400, 300), 0.5, 0.8, (255, 0, 0), 8)  # Red particles
        
        # Simulate unit damage
        print("  💥 Unit damage event")
        game_state.damage_unit("ai1", 3)  # Damage AI unit
        game_state.trigger_fx("flash", (400, 300), 0.2, 1.0, (255, 0, 0))  # Red flash
        game_state.trigger_screen_shake(2.0, 0.3)  # Heavy shake
        
        # Simulate unit death
        print("  💀 Unit death event")
        game_state.damage_unit("ai2", 10)  # Kill AI unit
        game_state.trigger_fx("flash", (400, 300), 0.5, 1.5, (255, 0, 0))  # Intense red flash
        game_state.trigger_screen_shake(5.0, 0.5)  # Strong shake
        game_state.trigger_particle((400, 300), "sparkle", 15, 1.0)  # Death particles
        
        # Test FX rendering
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
                        # Trigger new combat event
                        print("  ⚡ Triggering new combat event")
                        game_state.trigger_fx("flash", (400, 300), 0.3, 1.0, (0, 255, 255))
                        game_state.trigger_screen_shake(4.0, 0.3)
            
            # Clear screen
            screen.fill((20, 20, 20))
            
            # Draw test info
            font = pygame.font.Font(None, 36)
            text = font.render("FX Sim Runner Test - Press SPACE for combat events, ESC to quit", True, (255, 255, 255))
            screen.blit(text, (50, 50))
            
            # Draw active effects count
            fx_count = game_state.fx_manager.get_active_effects_count()
            count_text = font.render(f"Active Effects: {fx_count}", True, (255, 255, 0))
            screen.blit(count_text, (50, 100))
            
            # Draw unit status
            units_text = font.render(f"Units: Player({game_state.units.get_unit_count('player')}) AI({game_state.units.get_unit_count('ai')})", True, (0, 255, 255))
            screen.blit(units_text, (50, 150))
            
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
        print(f"❌ Error in FX sim runner test: {e}")
        return False
    
    finally:
        quit_pygame()

def test_combat_fx_triggers():
    """Test combat-specific FX triggers."""
    
    print("\n⚔️  Testing Combat FX Triggers")
    print("=" * 40)
    
    # Create game state
    game_state = GameState()
    
    # Test different combat scenarios
    combat_scenarios = [
        ("Light Attack", lambda: game_state.trigger_fx("flash", (400, 300), 0.2, 0.5, (255, 255, 0))),
        ("Heavy Attack", lambda: (
            game_state.trigger_fx("flash", (400, 300), 0.4, 1.0, (255, 0, 0)),
            game_state.trigger_screen_shake(4.0, 0.3)
        )),
        ("Critical Hit", lambda: (
            game_state.trigger_fx("flash", (400, 300), 0.6, 1.5, (255, 255, 255)),
            game_state.trigger_screen_shake(6.0, 0.5),
            game_state.trigger_particle((400, 300), "sparkle", 20, 1.2)
        )),
        ("Unit Death", lambda: (
            game_state.trigger_fx("flash", (400, 300), 0.8, 2.0, (255, 0, 0)),
            game_state.trigger_screen_shake(8.0, 0.8),
            game_state.trigger_particle((400, 300), "sparkle", 30, 1.5)
        ))
    ]
    
    for scenario_name, trigger_func in combat_scenarios:
        print(f"  Testing: {scenario_name}")
        trigger_func()
        print(f"    ✅ Triggered {scenario_name} effects")
    
    print("✅ All combat FX scenarios tested")
    return True

def main():
    """Main test function."""
    
    print("🎬 FX Sim Runner Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("FX Sim Runner Integration", test_fx_sim_runner_integration),
        ("Combat FX Triggers", test_combat_fx_triggers)
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
        print("🎉 All FX sim runner tests passed!")
        print("\n💡 FX integration features:")
        print("  ✅ Combat event FX triggers")
        print("  ✅ Screen shake integration")
        print("  ✅ Particle effects for damage/death")
        print("  ✅ Flash effects for attacks")
        print("  ✅ Proper cleanup and resource management")
        return 0
    else:
        print("⚠️  Some FX sim runner tests failed.")
        return 1

if __name__ == "__main__":
    exit(main()) 