#!/usr/bin/env python3
"""
UI Multi-Unit Demo - Demonstrates multiple units with hoverable health bars and status icons.
Based on ChatGPT's recommendations, adapted to our existing architecture.
"""

import pygame
import sys
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

def main():
    """Main entry point for multi-unit UI demo."""
    
    # ---------------------------
    # Step 1: Initialize Pygame
    # ---------------------------
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Starter Town Tactics Multi-Unit UI Demo")
    clock = pygame.time.Clock()
    
    # ---------------------------
    # Step 2: Initialize Game Systems (Our Architecture)
    # ---------------------------
    game_state = GameState()
    ui_state = UIState()
    ui_renderer = UIRenderer(screen, 32)
    
    # ---------------------------
    # Step 3: Instantiate UI Components (Our Pattern)
    # ---------------------------
    health_ui = HealthUI()
    ap_ui = APUI()
    turn_ui = TurnUI()
    status_ui = StatusUI()
    cursor_manager = CursorManager()
    ability_icons = AbilityIcons()
    
    # ---------------------------
    # Step 4: Set Up Demo Units (Multiple Units)
    # ---------------------------
    game_state.units.units = {
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
        },
        "mage": {
            "x": 7, "y": 4, "hp": 12, "max_hp": 16, "ap": 4, "max_ap": 4,
            "alive": True, "team": "player", "type": "mage"
        },
        "boss": {
            "x": 10, "y": 8, "hp": 25, "max_hp": 30, "ap": 2, "max_ap": 3,
            "alive": True, "team": "enemy", "type": "boss"
        }
    }
    
    # Set initial selected unit
    ui_state.selected_unit = "hero"
    
    # Set up turn controller
    if hasattr(game_state, 'turn_controller'):
        game_state.turn_controller.current_unit = "hero"
    
    # Set up sim runner
    if hasattr(game_state, 'sim_runner'):
        game_state.sim_runner.turn_count = 3
        game_state.sim_runner._ai_turn = False
    
    # ---------------------------
    # Step 5: Demo Loop
    # ---------------------------
    running = True
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    ui_state.selected_unit = "hero"
                elif event.key == pygame.K_2:
                    ui_state.selected_unit = "enemy"
                elif event.key == pygame.K_3:
                    ui_state.selected_unit = "ally"
                elif event.key == pygame.K_4:
                    ui_state.selected_unit = "mage"
                elif event.key == pygame.K_5:
                    ui_state.selected_unit = "boss"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Simple unit selection by clicking
                mouse_pos = pygame.mouse.get_pos()
                tile_x = mouse_pos[0] // 64
                tile_y = mouse_pos[1] // 64
                
                # Find unit at clicked position
                for unit_id, unit_data in game_state.units.units.items():
                    if unit_data["x"] == tile_x and unit_data["y"] == tile_y:
                        ui_state.selected_unit = unit_id
                        break
        
        # Clear screen
        screen.fill((30, 30, 30))
        
        # Draw grid
        tile_size = 64
        for x in range(0, SCREEN_WIDTH, tile_size):
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, tile_size):
            pygame.draw.line(screen, (50, 50, 50), (0, y), (SCREEN_WIDTH, y))
        
        # Draw units
        for unit_id, unit_data in game_state.units.units.items():
            x, y = unit_data["x"], unit_data["y"]
            screen_x = x * tile_size
            screen_y = y * tile_size
            
            # Determine unit color
            if unit_data["team"] == "player":
                color = (0, 255, 0)  # Green for player
            else:
                color = (255, 0, 0)  # Red for enemy
            
            # Highlight selected unit
            if unit_id == ui_state.selected_unit:
                pygame.draw.rect(screen, (255, 255, 0), (screen_x, screen_y, tile_size, tile_size), 3)
            
            # Draw unit
            pygame.draw.rect(screen, color, (screen_x + 8, screen_y + 8, tile_size - 16, tile_size - 16))
            pygame.draw.rect(screen, (255, 255, 255), (screen_x + 8, screen_y + 8, tile_size - 16, tile_size - 16), 2)
            
            # Draw unit name
            name_text = small_font.render(unit_id.title(), True, (255, 255, 255))
            screen.blit(name_text, (screen_x + 4, screen_y + tile_size + 2))
        
        # ---------------------------
        # Step 6: Render UI Components (Our Architecture)
        # ---------------------------
        
        # Draw health bars for all units
        health_ui.draw_all_health_bars(screen, game_state, ui_state, 64)
        
        # Draw AP bars for all units
        ap_ui.draw_all_ap_bars(screen, game_state, ui_state, 64)
        
        # Draw turn indicator
        turn_ui.draw_turn_indicator(screen, game_state, ui_state, SCREEN_WIDTH, 40)
        
        # Draw turn highlight
        turn_ui.draw_unit_turn_highlight(screen, game_state, ui_state, 64)
        
        # Draw status icons
        status_ui.draw_all_status_icons(screen, game_state, ui_state, 64)
        
        # Draw ability icons for selected unit
        if ui_state.selected_unit and ui_state.selected_unit in game_state.units.units:
            unit_data = game_state.units.units[ui_state.selected_unit]
            abilities = ability_icons.get_available_abilities(unit_data)
            ability_icons.draw_ability_panel(screen, abilities, (50, 600), unit_data["ap"])
        
        # Update and draw cursor
        mouse_pos = pygame.mouse.get_pos()
        cursor_manager.update_cursor(ui_state, mouse_pos)
        cursor_manager.draw_cursor(screen, mouse_pos)
        
        # ---------------------------
        # Step 7: Draw UI Information
        # ---------------------------
        
        # Info panel
        info_panel = pygame.Rect(10, 10, 400, 200)
        pygame.draw.rect(screen, (0, 0, 0, 180), info_panel)
        pygame.draw.rect(screen, (255, 255, 255), info_panel, 2)
        
        # Title
        title_text = font.render("Multi-Unit UI Demo", True, (255, 255, 255))
        screen.blit(title_text, (20, 20))
        
        # Selected unit info
        if ui_state.selected_unit and ui_state.selected_unit in game_state.units.units:
            unit_data = game_state.units.units[ui_state.selected_unit]
            unit_info = f"Selected: {ui_state.selected_unit.title()}"
            unit_text = font.render(unit_info, True, (255, 255, 0))
            screen.blit(unit_text, (20, 50))
            
            hp_info = f"HP: {unit_data['hp']}/{unit_data['max_hp']}"
            hp_text = small_font.render(hp_info, True, (200, 200, 200))
            screen.blit(hp_text, (20, 75))
            
            ap_info = f"AP: {unit_data['ap']}/{unit_data['max_ap']}"
            ap_text = small_font.render(ap_info, True, (200, 200, 200))
            screen.blit(ap_text, (20, 95))
            
            team_info = f"Team: {unit_data['team'].title()}"
            team_text = small_font.render(team_info, True, (200, 200, 200))
            screen.blit(team_text, (20, 115))
        
        # Controls
        controls = [
            "Controls:",
            "1-5: Select units",
            "Mouse: Click to select",
            "ESC: Exit"
        ]
        
        for i, control in enumerate(controls):
            control_text = small_font.render(control, True, (150, 150, 150))
            screen.blit(control_text, (20, 140 + i * 15))
        
        # Asset info
        asset_panel = pygame.Rect(SCREEN_WIDTH - 350, 10, 340, 150)
        pygame.draw.rect(screen, (0, 0, 0, 180), asset_panel)
        pygame.draw.rect(screen, (255, 255, 255), asset_panel, 2)
        
        asset_title = font.render("Asset Status", True, (255, 255, 255))
        screen.blit(asset_title, (SCREEN_WIDTH - 340, 20))
        
        ui_assets = len(ui_renderer._ui_assets)
        asset_text = small_font.render(f"UI Assets Loaded: {ui_assets}", True, (200, 200, 200))
        screen.blit(asset_text, (SCREEN_WIDTH - 340, 50))
        
        # Show asset categories
        asset_categories = {
            "Health/AP": ["healthbar", "apbar"],
            "Cursors": ["cursor", "select_cursor", "move_cursor", "attack_cursor", "invalid_cursor"],
            "Icons": ["attack_icon", "move_icon", "heal_icon", "wait_icon", "special_icon", "defend_icon"],
            "Panels": ["status_panel", "turn_panel", "action_panel", "health_panel"]
        }
        
        y_offset = 80
        for category, assets in asset_categories.items():
            category_text = small_font.render(f"{category}: {len(assets)}", True, (150, 255, 150))
            screen.blit(category_text, (SCREEN_WIDTH - 340, y_offset))
            y_offset += 20
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error running multi-unit UI demo: {e}")
        pygame.quit()
        sys.exit(1)
