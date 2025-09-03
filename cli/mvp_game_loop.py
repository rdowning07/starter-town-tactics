"""
MVP Game Loop - Integrates Week 7 asset validation with existing game systems.
Creates a fully playable MVP using validated assets and comprehensive game state.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pygame

# Import our MVP demo scene
from cli.mvp_demo_scene import MVPDemoScene
from game.ai.enemy_ai import AIBehaviorType, EnemyAI
from game.animation_manager import AnimationManager, get_animation_manager
from game.asset_validator import AssetValidator
from game.audio.sound_manager import get_sound_manager
from game.combo_system import ComboManager
from game.event_triggers import EventManager
from game.fx_manager import FXManager

# Import our existing game systems
from game.game_state import GameState
from game.game_win_loss import GameWinLoss
from game.scenario_manager import ScenarioManager
from game.sprite_validator import SpriteValidator
from game.status_effects import StatusEffectManager

# Import Week 7 asset validation systems
from game.terrain_validator import TerrainValidator
from game.ui.game_actions import GameActions
from game.ui.health_ui import HealthUI
from game.ui.input_handler import handle_keyboard_input, handle_mouse_input
from game.ui.status_ui import StatusUI
from game.ui.turn_ui import TurnUI
from game.ui.ui_renderer import UIRenderer
from game.ui.ui_state import UIState


class Camera:
    """Simple camera system for the MVP game loop."""

    def __init__(self, screen_size: Tuple[int, int], tile_size: int = 32):
        self.screen_width, self.screen_height = screen_size
        self.tile_size = tile_size
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.smooth_factor = 0.1

    def update(self):
        """Smooth camera movement towards target."""
        self.x += (self.target_x - self.x) * self.smooth_factor
        self.y += (self.target_y - self.y) * self.smooth_factor

    def set_target(self, x: float, y: float):
        """Set camera target position."""
        self.target_x = x
        self.target_y = y

    def center_on_tile(self, tile_x: int, tile_y: int):
        """Center camera on a specific tile."""
        world_x = tile_x * self.tile_size
        world_y = tile_y * self.tile_size
        target_x = world_x - self.screen_width // 2
        target_y = world_y - self.screen_height // 2
        self.set_target(target_x, target_y)

    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        return int(world_pos[0] - self.x), int(world_pos[1] - self.y)

    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        return screen_pos[0] + self.x, screen_pos[1] + self.y

    def get_visible_tiles(self) -> Tuple[int, int, int, int]:
        """Get the range of tiles visible on screen."""
        start_x = max(0, int(self.x // self.tile_size))
        start_y = max(0, int(self.y // self.tile_size))
        end_x = int((self.x + self.screen_width) // self.tile_size) + 1
        end_y = int((self.y + self.screen_height) // self.tile_size) + 1
        return start_x, start_y, end_x, end_y


class MVPGameLoop:
    """
    MVP Game Loop that integrates validated assets with existing game systems.
    Provides a fully playable experience with camera, input, and visual feedback.
    """

    def __init__(self, screen_size: Tuple[int, int] = (800, 600)):
        self.screen_size = screen_size
        self.tile_size = 32
        self.running = False

        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("MVP Game Loop - Starter Town Tactics")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Camera system
        self.camera = Camera(screen_size, self.tile_size)

        # Game systems (existing)
        self.game_state = GameState()
        self.ui_state = UIState()
        self.ui_renderer = UIRenderer(self.screen, self.tile_size)
        self.game_actions = GameActions()
        self.turn_ui = TurnUI()
        self.health_ui = HealthUI()
        self.status_ui = StatusUI()
        self.win_loss = GameWinLoss()

        # Managers
        self.status_manager = StatusEffectManager()
        self.fx_manager = FXManager()
        self.combo_manager = ComboManager(self.status_manager)
        self.event_manager = EventManager(self.fx_manager)
        self.sound_manager = get_sound_manager()

        # Week 7 asset validation systems
        self.terrain_validator = TerrainValidator()
        self.sprite_validator = SpriteValidator()
        self.asset_validator = AssetValidator()
        self.animation_manager = get_animation_manager()

        # MVP demo scene for asset loading
        self.demo_scene = MVPDemoScene(screen_size)

        # Game state
        self.grid_width = screen_size[0] // self.tile_size
        self.grid_height = screen_size[1] // self.tile_size
        self.terrain_map: Dict[Tuple[int, int], str] = {}
        self.units: Dict[str, Any] = {}

        # Input tracking
        self.keys_pressed: Set[int] = set()
        self.mouse_pos = (0, 0)

    def initialize(self) -> bool:
        """Initialize the MVP game loop with asset validation."""
        print("🎮 Initializing MVP Game Loop...")

        # Step 1: Run asset validation (Week 7 integration)
        print("📋 Running asset validation...")
        try:
            terrain_results = self.terrain_validator.validate_all_terrain()
            sprite_results = self.sprite_validator.validate_all_sprites()
            asset_results = self.asset_validator.validate_all_assets()

            print(f"✅ Asset validation complete:")
            print(f"   - Terrain types validated: {len(terrain_results)}")
            print(f"   - Unit types validated: {len(sprite_results)}")
            print(f"   - Total assets validated: {len(asset_results)}")

        except Exception as e:
            print(f"❌ Asset validation failed: {e}")
            return False

        # Step 2: Initialize demo scene for asset loading
        print("🎬 Initializing demo scene...")
        if not self.demo_scene.initialize():
            print("❌ Failed to initialize demo scene")
            return False

        # Step 3: Create demo game state
        print("🎲 Creating demo game state...")
        self._create_demo_scenario()

        # Step 4: Initialize game systems
        print("⚙️ Initializing game systems...")
        # Note: GameState integration would need additional attributes
        # For now, managers are handled by the MVP loop directly

        print("✅ MVP Game Loop initialized successfully!")
        return True

    def _create_demo_scenario(self):
        """Create a demo scenario with units and terrain."""
        # Set up game state metadata
        self.game_state.name = "MVP Demo - Week 8"
        self.game_state.description = "Playable MVP with validated assets"

        # Add demo units with proper positioning
        self.game_state.units.register_unit("player_hero", "player", hp=25)
        self.game_state.units.register_unit("player_mage", "player", hp=20)
        self.game_state.units.register_unit("enemy_orc", "enemy", hp=22)
        self.game_state.units.register_unit("enemy_goblin", "enemy", hp=15)

        # Add to turn controller
        self.game_state.turn_controller.add_unit("player_hero")
        self.game_state.turn_controller.add_unit("player_mage")
        self.game_state.turn_controller.add_unit("enemy_orc")
        self.game_state.turn_controller.add_unit("enemy_goblin")

        # Initialize terrain (simple grass field with some variety)
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                # Create varied terrain
                if (x + y) % 4 == 0:
                    terrain_type = "stone"
                elif (x * y) % 7 == 0:
                    terrain_type = "water"
                else:
                    terrain_type = "grass"

                self.terrain_map[(x, y)] = terrain_type

        # Center camera on player units
        self.camera.center_on_tile(3, 3)

    def run(self) -> bool:
        """Run the MVP game loop."""
        if not self.initialize():
            return False

        self.running = True
        print("🚀 Starting MVP game loop...")

        try:
            while self.running:
                dt = self.clock.tick(60)  # 60 FPS

                # Handle events
                self._handle_events()

                # Update game systems
                self._update(dt)

                # Render everything
                self._render()

        except KeyboardInterrupt:
            print("\n⏹️ Game loop interrupted by user")
        except Exception as e:
            print(f"❌ Game loop error: {e}")
            return False
        finally:
            self._cleanup()

        return True

    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)

                # Handle special keys
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # End turn
                    self.game_state.turn_controller.end_turn()
                elif event.key == pygame.K_r:
                    # Reset game
                    self._create_demo_scenario()

                # Camera controls
                elif event.key == pygame.K_w:
                    self.camera.set_target(self.camera.target_x, self.camera.target_y - 64)
                elif event.key == pygame.K_s:
                    self.camera.set_target(self.camera.target_x, self.camera.target_y + 64)
                elif event.key == pygame.K_a:
                    self.camera.set_target(self.camera.target_x - 64, self.camera.target_y)
                elif event.key == pygame.K_d:
                    self.camera.set_target(self.camera.target_x + 64, self.camera.target_y)

                # Handle UI input
                handle_keyboard_input(event, self.ui_state)

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = pygame.mouse.get_pos()
                # Convert screen to world coordinates
                world_pos = self.camera.screen_to_world(self.mouse_pos)
                tile_x = int(world_pos[0] // self.tile_size)
                tile_y = int(world_pos[1] // self.tile_size)

                # Handle mouse input through existing system
                handle_mouse_input(self.mouse_pos, self.game_state, self.ui_state, self.game_actions, tile_x, tile_y)

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = pygame.mouse.get_pos()

    def _update(self, dt: int):
        """Update game systems."""
        # Update camera
        self.camera.update()

        # Update managers
        self.status_manager.tick_effects(self.game_state)
        # Note: FXManager and other systems would need update methods
        # For now, focusing on core camera and input functionality

        # Update win/loss conditions
        game_status = self.win_loss.check_victory_conditions(self.game_state)
        if game_status != "ongoing":
            print(f"🎯 Game Status: {game_status}")

    def _render(self):
        """Render the game."""
        # Clear screen
        self.screen.fill((32, 32, 32))  # Dark gray background

        # Render terrain
        self._render_terrain()

        # Render units
        self._render_units()

        # Render UI overlays
        self._render_ui()

        # Render HUD
        self._render_hud()

        # Update display
        pygame.display.flip()

    def _render_terrain(self):
        """Render terrain tiles."""
        start_x, start_y, end_x, end_y = self.camera.get_visible_tiles()

        for x in range(start_x, min(end_x, self.grid_width)):
            for y in range(start_y, min(end_y, self.grid_height)):
                terrain_type = self.terrain_map.get((x, y), "grass")

                # Get terrain color
                color = self._get_terrain_color(terrain_type)

                # Calculate screen position
                world_x = x * self.tile_size
                world_y = y * self.tile_size
                screen_x, screen_y = self.camera.world_to_screen((world_x, world_y))

                # Draw tile
                pygame.draw.rect(self.screen, color, (screen_x, screen_y, self.tile_size, self.tile_size))

                # Draw grid lines
                pygame.draw.rect(self.screen, (64, 64, 64), (screen_x, screen_y, self.tile_size, self.tile_size), 1)

    def _render_units(self):
        """Render units on the map."""
        for unit_id in self.game_state.units.get_all_units():
            if not self.game_state.units.is_alive(unit_id):
                continue

            # Get unit info (we'd normally get this from unit manager)
            # For now, use placeholder positions
            unit_data = self._get_unit_display_data(unit_id)
            if not unit_data:
                continue

            x, y = unit_data["position"]
            team = unit_data["team"]

            # Calculate screen position
            world_x = x * self.tile_size + self.tile_size // 4
            world_y = y * self.tile_size + self.tile_size // 4
            screen_x, screen_y = self.camera.world_to_screen((world_x, world_y))

            # Get unit color
            color = (0, 255, 0) if team == "player" else (255, 0, 0)

            # Draw unit
            pygame.draw.circle(
                self.screen,
                color,
                (screen_x + self.tile_size // 4, screen_y + self.tile_size // 4),
                self.tile_size // 3,
            )

            # Draw unit ID
            text = self.font.render(unit_id.split("_")[1][:3], True, (255, 255, 255))
            self.screen.blit(text, (screen_x, screen_y - 20))

    def _render_ui(self):
        """Render UI overlays using existing system."""
        # Use existing UI renderer for overlays
        if self.ui_state.selected_unit:
            # Highlight selected unit
            unit_data = self._get_unit_display_data(self.ui_state.selected_unit)
            if unit_data:
                x, y = unit_data["position"]
                world_x = x * self.tile_size
                world_y = y * self.tile_size
                screen_x, screen_y = self.camera.world_to_screen((world_x, world_y))

                # Draw selection highlight
                pygame.draw.rect(self.screen, (255, 255, 0), (screen_x, screen_y, self.tile_size, self.tile_size), 3)

        # Draw movement range if showing
        if self.ui_state.show_movement_range and self.ui_state.movement_tiles:
            for tile_x, tile_y in self.ui_state.movement_tiles:
                world_x = tile_x * self.tile_size
                world_y = tile_y * self.tile_size
                screen_x, screen_y = self.camera.world_to_screen((world_x, world_y))

                # Draw movement highlight
                s = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                s.fill((0, 255, 0, 100))
                self.screen.blit(s, (screen_x, screen_y))

    def _render_hud(self):
        """Render heads-up display."""
        # Current turn info
        current_unit = self.game_state.turn_controller.get_current_unit()
        turn_text = f"Turn: {current_unit or 'None'}"
        text_surface = self.font.render(turn_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

        # Controls help
        controls = [
            "Controls:",
            "WASD - Move camera",
            "Mouse - Select/Move units",
            "Space - End turn",
            "R - Reset game",
            "ESC - Quit",
        ]

        for i, control in enumerate(controls):
            text_surface = self.font.render(control, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, 40 + i * 20))

        # Game status
        status_text = f"Units: P={len(self.game_state.units.get_unit_ids_by_team('player'))} E={len(self.game_state.units.get_unit_ids_by_team('enemy'))}"
        text_surface = self.font.render(status_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (self.screen_size[0] - 200, 10))

    def _get_terrain_color(self, terrain_type: str) -> Tuple[int, int, int]:
        """Get color for terrain type."""
        colors = {
            "grass": (50, 150, 50),
            "stone": (100, 100, 100),
            "water": (50, 50, 200),
            "forest": (30, 100, 30),
            "mountain": (80, 60, 40),
            "desert": (200, 180, 100),
            "dungeon": (40, 40, 40),
            "castle": (120, 120, 120),
        }
        return colors.get(terrain_type, (80, 80, 80))

    def _get_unit_display_data(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """Get unit display data for rendering."""
        if not self.game_state.units.is_alive(unit_id):
            return None

        team = self.game_state.units.get_team(unit_id)

        # For demo purposes, use hardcoded positions
        # In a real game, this would come from the unit manager
        positions = {"player_hero": (3, 3), "player_mage": (4, 3), "enemy_orc": (8, 6), "enemy_goblin": (9, 7)}

        position = positions.get(unit_id, (0, 0))

        return {
            "position": position,
            "team": team,
            "hp": self.game_state.units.get_hp(unit_id),
            "max_hp": 25,  # Placeholder
        }

    def _cleanup(self):
        """Clean up resources."""
        if self.sound_manager:
            self.sound_manager.cleanup()
        pygame.quit()
        print("🧹 MVP Game Loop cleaned up")


def main():
    """Main entry point for MVP game loop."""
    print("🎮 Starting MVP Game Loop - Starter Town Tactics")

    game_loop = MVPGameLoop()
    success = game_loop.run()

    if success:
        print("✅ MVP Game Loop completed successfully")
        return 0
    else:
        print("❌ MVP Game Loop failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
