#!/usr/bin/env python3
"""
Fixed CLI demo player that uses the existing game/ architecture.
"""

import argparse
import os
import sys
import time

import pygame

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    game_state.name = "Demo Battle"
    game_state.description = "A demonstration battle with player and enemy units"
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


class SimpleRenderer:
    """Simple renderer that works with the existing game state."""

    def __init__(self, screen, tile_size=32):
        self.screen = screen
        self.tile_size = tile_size
        self.font = pygame.font.Font(None, 24)

    def draw(self, game_state: GameState):
        """Draw the game state."""
        # Clear screen
        self.screen.fill((12, 12, 16))

        # Draw grid
        grid_width, grid_height = 10, 10
        for y in range(grid_height):
            for x in range(grid_width):
                color = (32, 48, 32)
                pygame.draw.rect(
                    self.screen, color, (x * self.tile_size, y * self.tile_size, self.tile_size - 1, self.tile_size - 1)
                )

        # Draw units
        for unit_id, unit_data in game_state.units.get_all_units().items():
            x = unit_data.get("x", 0)
            y = unit_data.get("y", 0)
            team = unit_data.get("team", "player")

            # Color based on team
            color = (80, 160, 255) if team == "player" else (200, 80, 80)

            # Draw unit
            pygame.draw.rect(
                self.screen, color, (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
            )

            # Draw unit ID
            text = self.font.render(unit_id, True, (255, 255, 255))
            self.screen.blit(text, (x * self.tile_size + 2, y * self.tile_size + 2))

        # Draw UI info
        y_offset = 10
        info_lines = [
            f"Turn: {game_state.sim_runner.turn_count}",
            f"Phase: {game_state.sim_runner.phase}",
            f"Current Unit: {game_state.turn_controller.get_current_unit()}",
            f"Game Over: {game_state.sim_runner.phase == 'GAME_OVER'}",
        ]

        for line in info_lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (10, y_offset))
            y_offset += 25


def main():
    """Run the fixed demo."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="Run 3-second CI smoke test")
    args = parser.parse_args()

    print("🎮 Starting Fixed Demo (using game/ architecture)...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Starter Town Tactics - Fixed Demo")
    clock = pygame.time.Clock()

    # Load game state
    game_state = load_demo_state()

    # Create managers
    sprite_manager = SpriteManager()
    fx_manager = FXManager()
    sound_manager = SoundManager()

    # Create renderer
    renderer = SimpleRenderer(screen)

    # Create AI controller
    ai_controller = AIController([])

    # Create scenario manager (for compatibility)
    camera = None  # No camera for simple demo
    player_unit = None  # No player unit for simple demo
    scenario_manager = create_scenario_manager(camera, ai_controller, player_unit, game_state)
    scenario_manager.set_managers(sprite_manager, fx_manager, sound_manager)

    print("🔄 Running demo loop...")

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

        # Run one turn
        game_state.sim_runner.run_turn()

        # Render
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
    print("✅ Fixed demo completed!")
    print(f"📊 Final state: {game_state.sim_runner.phase}")
    print(f"📊 Turns completed: {game_state.sim_runner.turn_count}")


if __name__ == "__main__":
    main()
