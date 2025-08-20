#!/usr/bin/env python3
"""
UI Asset Demo - Demonstrates iterative growth of assets in Pygame.
Shows how UI assets progress from stubs to polished visuals.
Based on ChatGPT's recommendations, adapted to our architecture.
"""

import pygame
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.ui.ui_renderer import UIRenderer
from game.ui.health_ui import HealthUI
from game.ui.ap_ui import APUI
from game.ui.turn_ui import TurnUI
from game.ui.status_ui import StatusUI
from game.ui.cursor_manager import CursorManager
from game.ui.ability_icons import AbilityIcons
from game.ui.ui_state import UIState
from game.game_state import GameState

class UIAssetDemo:
    """Demonstrates iterative UI asset growth in Pygame."""
    
    def __init__(self):
        """Initialize the UI asset demo."""
        pygame.init()
        
        # Display setup
        self.SCREEN_WIDTH = 1024
        self.SCREEN_HEIGHT = 768
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Starter Town Tactics - UI Asset Demo")
        
        # Game components
        self.game_state = GameState()
        self.ui_state = UIState()
        self.ui_renderer = UIRenderer(self.screen, 32)
        
        # UI components
        self.health_ui = HealthUI()
        self.ap_ui = APUI()
        self.turn_ui = TurnUI()
        self.status_ui = StatusUI()
        self.cursor_manager = CursorManager()
        self.ability_icons = AbilityIcons()
        
        # Demo state
        self.current_demo_step = 0
        self.demo_steps = [
            "Basic UI Components",
            "Health & AP Bars",
            "Turn Indicators", 
            "Status Effects",
            "Ability Icons",
            "Custom Cursors",
            "Full UI Integration"
        ]
        
        # Demo units
        self._setup_demo_units()
        
        # Timing
        self.clock = pygame.time.Clock()
        self.last_step_change = time.time()
        self.step_duration = 5.0  # 5 seconds per step
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def _setup_demo_units(self):
        """Set up demo units for the UI demonstration."""
        # Create demo units with various states
        self.game_state.units.units = {
            "hero": {
                "x": 5, "y": 3, "hp": 15, "max_hp": 20, "ap": 2, "max_ap": 3, 
                "alive": True, "team": "player", "type": "knight"
            },
            "enemy": {
                "x": 8, "y": 6, "hp": 8, "max_hp": 15, "ap": 1, "max_ap": 2,
                "alive": True, "team": "enemy", "type": "goblin"
            },
            "ally": {
                "x": 3, "y": 7, "hp": 18, "max_hp": 18, "ap": 3, "max_ap": 3,
                "alive": True, "team": "player", "type": "archer"
            }
        }
        
        # Set selected unit
        self.ui_state.selected_unit = "hero"
        
        # Set up turn controller
        if hasattr(self.game_state, 'turn_controller'):
            self.game_state.turn_controller.current_unit = "hero"
        
        # Set up sim runner
        if hasattr(self.game_state, 'sim_runner'):
            self.game_state.sim_runner.turn_count = 3
            self.game_state.sim_runner._ai_turn = False
    
    def draw_demo_info(self):
        """Draw demo information and controls."""
        # Background panel
        info_panel = pygame.Rect(10, 10, 400, 120)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), info_panel)
        pygame.draw.rect(self.screen, (255, 255, 255), info_panel, 2)
        
        # Title
        title_text = self.title_font.render("UI Asset Demo", True, (255, 255, 255))
        self.screen.blit(title_text, (20, 20))
        
        # Current step
        if 0 <= self.current_demo_step < len(self.demo_steps):
            step_text = self.info_font.render(f"Step: {self.demo_steps[self.current_demo_step]}", True, (255, 255, 0))
            self.screen.blit(step_text, (20, 60))
        else:
            step_text = self.info_font.render("Step: Unknown", True, (255, 255, 0))
            self.screen.blit(step_text, (20, 60))
        
        # Progress
        progress = (self.current_demo_step + 1) / len(self.demo_steps) * 100
        progress_text = self.small_font.render(f"Progress: {progress:.0f}%", True, (200, 200, 200))
        self.screen.blit(progress_text, (20, 85))
        
        # Controls
        controls_text = self.small_font.render("SPACE: Next Step | ESC: Exit | R: Reset", True, (150, 150, 150))
        self.screen.blit(controls_text, (20, 110))
    
    def draw_asset_info(self):
        """Draw information about current assets."""
        # Asset info panel
        asset_panel = pygame.Rect(self.SCREEN_WIDTH - 350, 10, 340, 200)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), asset_panel)
        pygame.draw.rect(self.screen, (255, 255, 255), asset_panel, 2)
        
        # Title
        asset_title = self.info_font.render("Asset Status", True, (255, 255, 255))
        self.screen.blit(asset_title, (self.SCREEN_WIDTH - 340, 20))
        
        # Asset counts
        ui_assets = len(self.ui_renderer._ui_assets)
        asset_text = self.small_font.render(f"UI Assets Loaded: {ui_assets}", True, (200, 200, 200))
        self.screen.blit(asset_text, (self.SCREEN_WIDTH - 340, 50))
        
        # Asset types
        asset_types = {
            "Health/AP": ["healthbar", "apbar"],
            "Cursors": ["cursor", "select_cursor", "move_cursor", "attack_cursor", "invalid_cursor"],
            "Icons": ["attack_icon", "move_icon", "heal_icon", "wait_icon", "special_icon", "defend_icon"],
            "Panels": ["status_panel", "turn_panel", "action_panel", "health_panel"]
        }
        
        y_offset = 80
        for category, assets in asset_types.items():
            category_text = self.small_font.render(f"{category}: {len(assets)}", True, (150, 255, 150))
            self.screen.blit(category_text, (self.SCREEN_WIDTH - 340, y_offset))
            y_offset += 20
    
    def draw_step_1_basic_ui(self):
        """Step 1: Basic UI Components."""
        # Draw basic UI elements
        self.draw_demo_info()
        self.draw_asset_info()
        
        # Show basic text
        text = self.info_font.render("Basic UI Components - Foundation", True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - 150, 200))
        
        # Show asset loading status
        status_text = self.small_font.render("Assets loaded with fallback mechanisms", True, (200, 200, 200))
        self.screen.blit(status_text, (self.SCREEN_WIDTH // 2 - 150, 230))
    
    def draw_step_2_health_ap_bars(self):
        """Step 2: Health & AP Bars."""
        self.draw_demo_info()
        self.draw_asset_info()
        
        # Draw health and AP bars for all units
        self.health_ui.draw_all_health_bars(self.screen, self.game_state, self.ui_state, 64)
        self.ap_ui.draw_all_ap_bars(self.screen, self.game_state, self.ui_state, 64)
        
        # Show explanation
        text = self.info_font.render("Health & AP Bars - Unit Status", True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - 150, 200))
        
        # Show unit info
        y_offset = 230
        for unit_id, unit_data in self.game_state.units.units.items():
            unit_text = f"{unit_id.title()}: HP {unit_data['hp']}/{unit_data['max_hp']} | AP {unit_data['ap']}/{unit_data['max_ap']}"
            text_surface = self.small_font.render(unit_text, True, (200, 200, 200))
            self.screen.blit(text_surface, (self.SCREEN_WIDTH // 2 - 150, y_offset))
            y_offset += 20
    
    def draw_step_3_turn_indicators(self):
        """Step 3: Turn Indicators."""
        self.draw_demo_info()
        self.draw_asset_info()
        
        # Draw turn UI
        self.turn_ui.draw_turn_indicator(self.screen, self.game_state, self.ui_state, self.SCREEN_WIDTH, 40)
        self.turn_ui.draw_unit_turn_highlight(self.screen, self.game_state, self.ui_state, 64)
        
        # Show explanation
        text = self.info_font.render("Turn Indicators - Game Flow", True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - 150, 200))
        
        # Show turn info
        turn_text = f"Turn: {getattr(self.game_state.sim_runner, 'turn_count', 0)} | Current: {self.ui_state.selected_unit}"
        text_surface = self.small_font.render(turn_text, True, (200, 200, 200))
        self.screen.blit(text_surface, (self.SCREEN_WIDTH // 2 - 150, 230))
    
    def draw_step_4_status_effects(self):
        """Step 4: Status Effects."""
        self.draw_demo_info()
        self.draw_asset_info()
        
        # Draw status UI
        self.status_ui.draw_all_status_icons(self.screen, self.game_state, self.ui_state, 64)
        
        # Show explanation
        text = self.info_font.render("Status Effects - Buffs & Debuffs", True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - 150, 200))
        
        # Show status info
        status_text = "Status effects display above units (poison, shield, etc.)"
        text_surface = self.small_font.render(status_text, True, (200, 200, 200))
        self.screen.blit(text_surface, (self.SCREEN_WIDTH // 2 - 150, 230))
    
    def draw_step_5_ability_icons(self):
        """Step 5: Ability Icons."""
        self.draw_demo_info()
        self.draw_asset_info()
        
        # Draw ability icons for selected unit
        if self.ui_state.selected_unit:
            unit_data = self.game_state.units.units[self.ui_state.selected_unit]
            abilities = self.ability_icons.get_available_abilities(unit_data)
            self.ability_icons.draw_ability_panel(self.screen, abilities, (50, 400), unit_data["ap"])
        
        # Show explanation
        text = self.info_font.render("Ability Icons - Unit Actions", True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - 150, 200))
        
        # Show ability info
        ability_text = "Ability icons show available actions and AP costs"
        text_surface = self.small_font.render(ability_text, True, (200, 200, 200))
        self.screen.blit(text_surface, (self.SCREEN_WIDTH // 2 - 150, 230))
    
    def draw_step_6_custom_cursors(self):
        """Step 6: Custom Cursors."""
        self.draw_demo_info()
        self.draw_asset_info()
        
        # Update cursor based on UI state
        mouse_pos = pygame.mouse.get_pos()
        self.cursor_manager.update_cursor(self.ui_state, mouse_pos)
        self.cursor_manager.draw_cursor(self.screen, mouse_pos)
        
        # Show explanation
        text = self.info_font.render("Custom Cursors - Context Awareness", True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - 150, 200))
        
        # Show cursor info
        cursor_info = self.cursor_manager.get_cursor_info()
        cursor_text = f"Current Cursor: {cursor_info['current_cursor']}"
        text_surface = self.small_font.render(cursor_text, True, (200, 200, 200))
        self.screen.blit(text_surface, (self.SCREEN_WIDTH // 2 - 150, 230))
    
    def draw_step_7_full_integration(self):
        """Step 7: Full UI Integration."""
        self.draw_demo_info()
        self.draw_asset_info()
        
        # Draw all UI components together
        self.health_ui.draw_all_health_bars(self.screen, self.game_state, self.ui_state, 64)
        self.ap_ui.draw_all_ap_bars(self.screen, self.game_state, self.ui_state, 64)
        self.turn_ui.draw_turn_indicator(self.screen, self.game_state, self.ui_state, self.SCREEN_WIDTH, 40)
        self.turn_ui.draw_unit_turn_highlight(self.screen, self.game_state, self.ui_state, 64)
        self.status_ui.draw_all_status_icons(self.screen, self.game_state, self.ui_state, 64)
        
        # Draw ability icons
        if self.ui_state.selected_unit:
            unit_data = self.game_state.units.units[self.ui_state.selected_unit]
            abilities = self.ability_icons.get_available_abilities(unit_data)
            self.ability_icons.draw_ability_panel(self.screen, abilities, (50, 400), unit_data["ap"])
        
        # Update and draw cursor
        mouse_pos = pygame.mouse.get_pos()
        self.cursor_manager.update_cursor(self.ui_state, mouse_pos)
        self.cursor_manager.draw_cursor(self.screen, mouse_pos)
        
        # Show explanation
        text = self.info_font.render("Full UI Integration - Complete System", True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - 150, 200))
        
        # Show integration info
        integration_text = "All UI components working together seamlessly"
        text_surface = self.small_font.render(integration_text, True, (200, 200, 200))
        self.screen.blit(text_surface, (self.SCREEN_WIDTH // 2 - 150, 230))
    
    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.current_demo_step = (self.current_demo_step + 1) % len(self.demo_steps)
                    self.last_step_change = time.time()
                elif event.key == pygame.K_r:
                    self.current_demo_step = 0
                    self.last_step_change = time.time()
        
        return True
    
    def update(self):
        """Update demo state."""
        # Auto-advance steps
        current_time = time.time()
        if current_time - self.last_step_change > self.step_duration:
            self.current_demo_step = (self.current_demo_step + 1) % len(self.demo_steps)
            self.last_step_change = current_time
    
    def draw(self):
        """Draw the current demo step."""
        # Clear screen
        self.screen.fill((30, 30, 30))
        
        # Draw grid background
        self._draw_grid()
        
        # Draw demo units
        self._draw_demo_units()
        
        # Draw current step
        step_functions = [
            self.draw_step_1_basic_ui,
            self.draw_step_2_health_ap_bars,
            self.draw_step_3_turn_indicators,
            self.draw_step_4_status_effects,
            self.draw_step_5_ability_icons,
            self.draw_step_6_custom_cursors,
            self.draw_step_7_full_integration
        ]
        
        if 0 <= self.current_demo_step < len(step_functions):
            step_functions[self.current_demo_step]()
    
    def _draw_grid(self):
        """Draw a grid background."""
        tile_size = 64
        for x in range(0, self.SCREEN_WIDTH, tile_size):
            pygame.draw.line(self.screen, (50, 50, 50), (x, 0), (x, self.SCREEN_HEIGHT))
        for y in range(0, self.SCREEN_HEIGHT, tile_size):
            pygame.draw.line(self.screen, (50, 50, 50), (0, y), (self.SCREEN_WIDTH, y))
    
    def _draw_demo_units(self):
        """Draw demo units on the grid."""
        tile_size = 64
        for unit_id, unit_data in self.game_state.units.units.items():
            x, y = unit_data["x"], unit_data["y"]
            screen_x = x * tile_size
            screen_y = y * tile_size
            
            # Draw unit representation
            color = (0, 255, 0) if unit_data["team"] == "player" else (255, 0, 0)
            pygame.draw.rect(self.screen, color, (screen_x + 8, screen_y + 8, tile_size - 16, tile_size - 16))
            pygame.draw.rect(self.screen, (255, 255, 255), (screen_x + 8, screen_y + 8, tile_size - 16, tile_size - 16), 2)
            
            # Draw unit name
            name_text = self.small_font.render(unit_id.title(), True, (255, 255, 255))
            self.screen.blit(name_text, (screen_x + 4, screen_y + tile_size + 2))
    
    def run(self):
        """Run the UI asset demo."""
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    """Main entry point."""
    try:
        demo = UIAssetDemo()
        demo.run()
    except Exception as e:
        print(f"Error running UI asset demo: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
