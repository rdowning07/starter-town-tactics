#!/usr/bin/env python3
"""
Enhanced CLI demo player with asset integration and rich visuals.
"""

import argparse
import os
import sys
import time

import pygame

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.pygame.asset_manager import AssetManager
from adapters.pygame.enhanced_renderer import EnhancedRenderer
from devtools.scenario_manager import create_scenario_manager
from game.ai_controller import AIController
from game.fx_manager import FXManager
from game.game_state import GameState
from game.sim_runner import SimRunner
from game.sound_manager import SoundManager
from game.sprite_manager import SpriteManager
from game.unit import Unit


def load_demo_state() -> GameState:
    """Load a demo game state using the existing game/ architecture."""
    # Create game state using existing architecture
    game_state = GameState()

    # Set up demo metadata
    game_state.name = "Enhanced Demo Battle"
    game_state.description = "A demonstration battle with rich visuals and assets"
    game_state.max_turns = 20

    # Create units using existing Unit class
    player_unit = Unit("player1", 1, 1, "player", health=20)
    enemy_unit = Unit("enemy1", 5, 5, "enemy", health=15)

    # Add units to game state
    game_state.units.register_unit("player1", "player", hp=20)
    game_state.units.register_unit("enemy1", "enemy", hp=15)

    # Set unit positions
    game_state.units.units["player1"]["x"] = 1
    game_state.units.units["player1"]["y"] = 1
    game_state.units.units["enemy1"]["x"] = 5
    game_state.units.units["enemy1"]["y"] = 5

    # Add units to turn controller
    game_state.turn_controller.add_unit("player1")
    game_state.turn_controller.add_unit("enemy1")

    return game_state


def main():
    """Run the enhanced demo."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Run 3-second CI smoke test")
    parser.add_argument("--no-assets", action="store_true", help="Skip asset loading for faster startup")
    args = parser.parse_args()

    print("🎮 Starting Enhanced Demo with Asset Integration...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Starter Town Tactics - Enhanced Demo")
    clock = pygame.time.Clock()

    # Load game state
    game_state = load_demo_state()

    # Create asset manager and load assets
    asset_manager = AssetManager()
    if not args.no_assets:
        print("📦 Loading assets...")
        asset_manager.load_all_common_assets()
    else:
        print("⚠️  Skipping asset loading")

    # Create managers
    sprite_manager = SpriteManager()
    fx_manager = FXManager()
    sound_manager = SoundManager()

    # Create enhanced renderer
    renderer = EnhancedRenderer(screen, asset_manager, tile_size=48)  # Larger tiles for better visibility

    # Create AI controller
    ai_controller = AIController([])

    # Create scenario manager (for compatibility)
    camera = None  # No camera for simple demo
    player_unit = None  # No player unit for simple demo
    scenario_manager = create_scenario_manager(camera, ai_controller, player_unit, game_state)
    scenario_manager.set_managers(sprite_manager, fx_manager, sound_manager)

    print("🔄 Running enhanced demo loop...")

    start_time = time.time()
    running = True

    while running and game_state.sim_runner.phase != "GAME_OVER":
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Play a sound effect for testing
                    asset_manager.play_sound("move")

        # Run one turn
        game_state.sim_runner.run_turn()

        # Render with enhanced visuals
        renderer.draw(game_state)
        pygame.display.flip()

        # Cap at 60 FPS
        clock.tick(60)

        # Smoke test: exit after 3 seconds
        if args.smoke and (time.time() - start_time) > 3:
            print("⏰ Smoke test completed")
            break

        # Add some delay for visibility
        time.sleep(0.1)

    pygame.quit()
    print("✅ Enhanced demo completed!")
    print(f"📊 Final state: {game_state.sim_runner.phase}")
    print(f"📊 Turns completed: {game_state.sim_runner.turn_count}")
    print(f"📊 Assets loaded: {len(asset_manager.images)} images, {len(asset_manager.sounds)} sounds")


if __name__ == "__main__":
    main()
