#!/usr/bin/env python3
"""
Integrated Fighter Demo - Shows fighter units in the main game architecture.
"""

import sys
from pathlib import Path

import pygame

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.ai_controller import AIController
from game.demo_base import DemoBase
from game.game_state import GameState
from game.grid import Grid
from game.overlay.overlay_state import OverlayState
from game.renderer import Renderer
from game.sim_runner import SimRunner
from game.sprite_manager import SpriteManager
from game.tile import Tile
from game.turn_controller import TurnController
from game.unit_manager import UnitManager


class FighterIntegratedDemo(DemoBase):
    """Demo showing fighter units integrated into the main game architecture."""

    def __init__(self, timeout_seconds: int = 30):
        super().__init__(timeout_seconds=timeout_seconds, auto_exit=True)

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Fighter Integrated Demo - Main Game Architecture")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Initialize game systems
        self.sprite_manager = SpriteManager()
        self.sprite_manager.load_assets()

        self.unit_manager = UnitManager()
        self.turn_controller = TurnController()

        # Create game state
        self.game_state = GameState()
        self.game_state.units = self.unit_manager
        self.game_state.turn_controller = self.turn_controller
        self.game_state.sprite_manager = self.sprite_manager

        # Create renderer
        self.renderer = Renderer(self.screen, self.sprite_manager)

        # Create overlay state
        self.overlay_state = OverlayState()

        # Setup the scenario
        self._setup_fighter_scenario()

        # Create AI controller and sim runner
        self.ai_controller = AIController([])
        self.sim_runner = SimRunner(self.turn_controller, self.ai_controller)
        self.sim_runner.set_game_state(self.game_state)

        # Animation timing
        self.start_time = pygame.time.get_ticks()

    def _setup_fighter_scenario(self):
        """Setup a simple scenario with fighter units and terrain."""
        # Create a grid with proper terrain types
        self.grid = Grid(10, 8)

        # Set terrain types for each tile (grass, forest, etc.)
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.get_tile(x, y)
                # Alternate between grass and forest for visual variety
                if (x + y) % 3 == 0:
                    tile.terrain = "forest"
                elif (x + y) % 2 == 0:
                    tile.terrain = "grass"
                else:
                    tile.terrain = "dirt"

        # Register fighter units with positions
        self.unit_manager.register_unit("fighter_1", "player", hp=10, x=3, y=3)
        self.unit_manager.register_unit("fighter_2", "enemy", hp=8, x=6, y=4)

        # Place units on the grid
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                tile = self.grid.get_tile(x, y)
                if x == 3 and y == 3:
                    # Place player fighter
                    from game.unit import Unit

                    tile.unit = Unit("fighter_1", "player", x, y)
                elif x == 6 and y == 4:
                    # Place enemy fighter
                    from game.unit import Unit

                    tile.unit = Unit("fighter_2", "enemy", x, y)

        # Set the grid in game state
        self.game_state.terrain_grid = self.grid

    def _handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_demo()
                return
            elif event.key == pygame.K_SPACE:
                # Advance one turn
                self.sim_runner.run_turn()

    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Draw UI information."""
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = f"Time: {elapsed}s"
        turn_text = f"Turn: {self.turn_controller.current_turn}"

        # Unit info
        player_units = [
            uid for uid, unit in self.unit_manager.units.items() if unit["team"] == "player" and unit["alive"]
        ]
        enemy_units = [
            uid for uid, unit in self.unit_manager.units.items() if unit["team"] == "enemy" and unit["alive"]
        ]

        units_text = f"Player: {len(player_units)} | Enemy: {len(enemy_units)}"

        time_surface = self.font.render(time_text, True, (255, 255, 255))
        turn_surface = self.font.render(turn_text, True, (255, 255, 255))
        units_surface = self.font.render(units_text, True, (255, 255, 255))

        surface.blit(time_surface, (10, 10))
        surface.blit(turn_surface, (10, 35))
        surface.blit(units_surface, (10, 60))

        # Instructions
        instructions = ["Controls:", "Space - Advance turn", "ESC - Quit"]

        for i, instruction in enumerate(instructions):
            text_surface = self.font.render(instruction, True, (200, 200, 200))
            surface.blit(text_surface, (10, 500 + i * 25))

    def run(self) -> None:
        """Run the integrated fighter demo."""
        print("🎮 Fighter Integrated Demo")
        print("This demo shows fighter units integrated into the main game architecture.")
        print("The fighters should render with animations in the main game renderer.")
        print()

        while not self.should_exit():
            # Handle events
            for event in pygame.event.get():
                self._handle_input(event)

            # Clear screen
            self.screen.fill((0, 0, 0))

            # Render the game using the main renderer
            try:
                self.renderer.render(self.game_state, self.overlay_state)
            except Exception as e:
                print(f"Renderer error: {e}")
                # Fallback rendering
                self._fallback_render()

            # Draw UI
            self._draw_ui(self.screen)

            # Draw timeout info
            self.draw_timeout_info(self.screen, self.font)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        print("✅ Fighter integrated demo completed!")

    def _fallback_render(self):
        """Fallback rendering if main renderer fails."""
        # Draw simple grid
        tile_size = 32
        for y in range(8):
            for x in range(10):
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                color = (100, 150, 100) if (x + y) % 2 == 0 else (80, 120, 80)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

        # Draw units as circles
        for y in range(8):
            for x in range(10):
                tile = self.grid.get_tile(x, y)
                if tile.unit:
                    color = (255, 255, 0) if tile.unit.team == "player" else (255, 0, 0)
                    center = (
                        x * tile_size + tile_size // 2,
                        y * tile_size + tile_size // 2,
                    )
                    pygame.draw.circle(self.screen, color, center, tile_size // 3)


def main():
    """Main entry point."""
    demo = FighterIntegratedDemo(timeout_seconds=30)
    demo.run()


if __name__ == "__main__":
    main()
