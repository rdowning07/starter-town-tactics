#!/usr/bin/env python3
"""
Simple UI test to verify placeholder assets and UI system work.
"""

import os
import sys

import pygame

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.ui.placeholder_assets import create_placeholder_button, create_placeholder_panel
from game.ui.ui_renderer import UIRenderer
from game.ui.ui_state import UIState


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Create UI components
    ui_renderer = UIRenderer(screen)
    ui_state = UIState()

    # Test some placeholder assets
    print("Testing placeholder assets...")
    button = create_placeholder_button(100, 30)
    panel = create_placeholder_panel(200, 150)
    print(f"✅ Created placeholder button: {button.get_size()}")
    print(f"✅ Created placeholder panel: {panel.get_size()}")

    # Mock game state for testing
    class MockGameState:
        def get_turn_count(self):
            return 5

        def is_ai_turn(self):
            return False

        class Units:
            def __init__(self):
                self.units = {"player1": {"hp": 10, "team": "player"}, "enemy1": {"hp": 8, "team": "enemy"}}

        def __init__(self):
            self.units = self.Units()

    game_state = MockGameState()

    # Test UI state
    ui_state.select_unit("player1")
    ui_state.action_menu_pos = (300, 200)
    ui_state.set_movement_range([(3, 3), (3, 4), (4, 3), (4, 4)])
    ui_state.show_tooltip_at("Test tooltip", (400, 300))

    print("Starting UI test...")
    print("Click to test button interaction")
    print("Press ESC or Q to exit")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Test button click
                mouse_pos = pygame.mouse.get_pos()
                print(f"Mouse click at: {mouse_pos}")

                # Check if clicking on action menu buttons
                if ui_state.action_menu_pos:
                    x, y = ui_state.action_menu_pos
                    move_rect = pygame.Rect(x + 10, y + 10, 100, 25)
                    attack_rect = pygame.Rect(x + 10, y + 45, 100, 25)

                    if move_rect.collidepoint(mouse_pos):
                        print("Move button clicked!")
                        ui_state.set_movement_range([(3, 3), (3, 4), (4, 3), (4, 4)])
                    elif attack_rect.collidepoint(mouse_pos):
                        print("Attack button clicked!")
                        ui_state.set_attack_targets([(5, 5), (5, 6), (6, 5)])

        # Clear screen
        screen.fill((20, 20, 20))

        # Render UI
        ui_renderer.render_ui(game_state, ui_state)

        # Draw some test elements
        ui_renderer.draw_text("UI Test - Placeholder Assets", (400, 50))
        ui_renderer.draw_text("Click the action menu buttons to test", (400, 80))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("✅ UI test completed successfully!")


if __name__ == "__main__":
    main()
