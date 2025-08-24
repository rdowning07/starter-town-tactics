#!/usr/bin/env python3
"""
UI Multi-Unit Demo - Demonstrates multiple units with hoverable health bars and status icons.
Based on ChatGPT's recommendations, adapted to our existing architecture.
"""

import sys
from pathlib import Path

import pygame

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.demo_base import DemoBase
from game.game_state import GameState
from game.ui.ability_icons import AbilityIcons
from game.ui.ap_ui import APUI
from game.ui.cursor_manager import CursorManager
from game.ui.health_ui import HealthUI
from game.ui.status_ui import StatusUI
from game.ui.turn_ui import TurnUI
from game.ui.ui_renderer import UIRenderer
from game.ui.ui_state import UIState


class UIMultiDemo(DemoBase):
    """Multi-unit UI demo with timeout functionality."""

    def __init__(self, timeout_seconds: int = 30):
        """Initialize the demo."""
        super().__init__(timeout_seconds=timeout_seconds, auto_exit=True)

        # Initialize Pygame
        pygame.init()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1024, 768
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Starter Town Tactics Multi-Unit UI Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Initialize game systems
        self.game_state = GameState()
        self.ui_state = UIState()
        self.ui_renderer = UIRenderer(self.screen, 32)

        # Initialize UI components
        self.health_ui = HealthUI()
        self.ap_ui = APUI()
        self.turn_ui = TurnUI()
        self.status_ui = StatusUI()
        self.cursor_manager = CursorManager()
        self.ability_icons = AbilityIcons()

        # Set up demo units
        self._setup_demo_units()

    def _setup_demo_units(self):
        """Set up demo units."""
        self.game_state.units.units = {
            "hero": {
                "x": 5,
                "y": 3,
                "hp": 15,
                "max_hp": 20,
                "ap": 2,
                "max_ap": 3,
                "alive": True,
                "team": "player",
                "type": "knight",
            },
            "enemy": {
                "x": 8,
                "y": 6,
                "hp": 8,
                "max_hp": 15,
                "ap": 1,
                "max_ap": 2,
                "alive": True,
                "team": "enemy",
                "type": "goblin",
            },
            "ally": {
                "x": 3,
                "y": 7,
                "hp": 18,
                "max_hp": 18,
                "ap": 3,
                "max_ap": 3,
                "alive": True,
                "team": "player",
                "type": "archer",
            },
            "mage": {
                "x": 7,
                "y": 4,
                "hp": 12,
                "max_hp": 16,
                "ap": 4,
                "max_ap": 4,
                "alive": True,
                "team": "player",
                "type": "mage",
            },
            "boss": {
                "x": 10,
                "y": 8,
                "hp": 25,
                "max_hp": 30,
                "ap": 2,
                "max_ap": 3,
                "alive": True,
                "team": "enemy",
                "type": "boss",
            },
        }

        # Set initial selected unit
        self.ui_state.selected_unit = "hero"

        # Set up turn controller
        if hasattr(self.game_state, "turn_controller"):
            self.game_state.turn_controller.current_unit = "hero"

        # Set up sim runner
        if hasattr(self.game_state, "sim_runner"):
            self.game_state.sim_runner.turn_count = 3
            self.game_state.sim_runner._ai_turn = False

    def _handle_input(self) -> bool:
        """Handle input events. Returns False to quit."""
        for event in pygame.event.get():
            if self.handle_exit_events(event):
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.ui_state.selected_unit = "hero"
                elif event.key == pygame.K_2:
                    self.ui_state.selected_unit = "enemy"
                elif event.key == pygame.K_3:
                    self.ui_state.selected_unit = "ally"
                elif event.key == pygame.K_4:
                    self.ui_state.selected_unit = "mage"
                elif event.key == pygame.K_5:
                    self.ui_state.selected_unit = "boss"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Simple unit selection by clicking
                mouse_pos = pygame.mouse.get_pos()
                tile_x = mouse_pos[0] // 64
                tile_y = mouse_pos[1] // 64

                # Find unit at clicked position
                for unit_id, unit_data in self.game_state.units.units.items():
                    if unit_data["x"] == tile_x and unit_data["y"] == tile_y:
                        self.ui_state.selected_unit = unit_id
                        break
        return True

    def _draw_scene(self):
        """Draw the demo scene."""
        # Clear screen
        self.screen.fill((30, 30, 30))

        # Draw grid
        tile_size = 64
        for x in range(0, self.SCREEN_WIDTH, tile_size):
            pygame.draw.line(self.screen, (50, 50, 50), (x, 0), (x, self.SCREEN_HEIGHT))
        for y in range(0, self.SCREEN_HEIGHT, tile_size):
            pygame.draw.line(self.screen, (50, 50, 50), (0, y), (self.SCREEN_WIDTH, y))

        # Draw units
        for unit_id, unit_data in self.game_state.units.units.items():
            x, y = unit_data["x"], unit_data["y"]
            screen_x = x * tile_size
            screen_y = y * tile_size

            # Determine unit color
            if unit_data["team"] == "player":
                color = (0, 255, 0)  # Green for player
            else:
                color = (255, 0, 0)  # Red for enemy

            # Highlight selected unit
            if unit_id == self.ui_state.selected_unit:
                pygame.draw.rect(
                    self.screen,
                    (255, 255, 0),
                    (screen_x, screen_y, tile_size, tile_size),
                    3,
                )

            # Draw unit
            pygame.draw.rect(
                self.screen,
                color,
                (screen_x + 8, screen_y + 8, tile_size - 16, tile_size - 16),
            )
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                (screen_x + 8, screen_y + 8, tile_size - 16, tile_size - 16),
                2,
            )

            # Draw unit name
            name_text = self.small_font.render(unit_id.title(), True, (255, 255, 255))
            self.screen.blit(name_text, (screen_x + 4, screen_y + tile_size + 2))

        # Draw UI Components
        # Draw health bars for all units
        for unit_id, unit_data in self.game_state.units.units.items():
            self.health_ui.draw_health_bar(self.screen, unit_id, unit_data, 64)

        # Draw AP bars for all units
        for unit_id, unit_data in self.game_state.units.units.items():
            self.ap_ui.draw_ap_bar(self.screen, unit_id, unit_data, 64)

        # Draw status icons for all units (simplified for demo)
        # In a real implementation, you would need a status manager
        pass

        # Draw turn info (simplified for demo)
        turn_text = self.font.render("Turn: 1", True, (255, 255, 255))
        self.screen.blit(turn_text, (self.SCREEN_WIDTH - 100, 10))

        # Draw ability icons for selected unit (simplified for demo)
        if self.ui_state.selected_unit:
            ability_text = self.font.render(f"Selected: {self.ui_state.selected_unit}", True, (255, 255, 0))
            self.screen.blit(ability_text, (50, 600))

        # Draw custom cursor (simplified for demo)
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(self.screen, (255, 255, 255), mouse_pos, 3)

        # Draw Instructions
        title_text = self.font.render("Multi-Unit UI Demo", True, (255, 255, 255))
        self.screen.blit(title_text, (10, 10))

        instructions = [
            "1-5: Select unit",
            "Click: Select unit by position",
            "ESC: Quit",
            f"Selected: {self.ui_state.selected_unit or 'None'}",
        ]

        y_offset = 40
        for instruction in instructions:
            text = self.font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (10, y_offset))
            y_offset += 25

    def run(self):
        """Run the demo."""
        print(f"🎮 Starting Multi-Unit UI Demo (timeout: {self.timeout_seconds}s)")

        while not self.should_exit():
            # Handle input
            if not self._handle_input():
                break

            # Draw scene
            self._draw_scene()

            # Draw timeout info
            self.draw_timeout_info(self.screen, self.font)

            pygame.display.flip()
            self.clock.tick(60)

        print("👋 Multi-Unit UI Demo finished")
        pygame.quit()


def main():
    """Main entry point."""
    try:
        demo = UIMultiDemo()
        demo.run()
    except Exception as e:
        print(f"Error running multi-unit UI demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
