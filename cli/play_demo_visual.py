#!/usr/bin/env python3
"""
Visual demo player for the command-event architecture using Pygame.
This module demonstrates the core game loop with actual visual rendering.
"""

import sys
import os
import pygame
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_loop import GameLoop
from core.events import EventBus
from core.rng import Rng
from core.state import GameState, Unit, UnitStats
from core.command import Move, Attack, EndTurn
from core.events import Event

# Pygame setup
pygame.init()
WINDOW_SIZE = (800, 600)
GRID_SIZE = 40
GRID_OFFSET = (50, 50)
GRID_WIDTH = 15
GRID_HEIGHT = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class VisualDemo:
    def __init__(self):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Starter Town Tactics - Command-Event Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Game state
        self.rng = Rng(1337)
        self.bus = EventBus()
        self.loop = GameLoop(self.rng, self.bus)
        self.state = self.load_demo_state()
        
        # Subscribe to events
        self.bus.subscribe(self.handle_event)
        
        # Demo state
        self.tick_count = 0
        self.max_ticks = 3600
        self.events_log = []
        self.running = True

    def load_demo_state(self) -> GameState:
        """Load a demo game state with visual units."""
        state = GameState()
        
        # Create units with positions for visual display
        player_stats = UnitStats(hp=20, atk=8, def_=3, h=1)
        player = Unit("player1", (3, 3), "E", player_stats)
        state.add_unit(player)
        
        enemy_stats = UnitStats(hp=15, atk=6, def_=2, h=0)
        enemy = Unit("enemy1", (8, 5), "W", enemy_stats)
        state.add_unit(enemy)
        
        # Create a simple demo controller
        class VisualDemoController:
            def __init__(self, demo):
                self.demo = demo
                self.command_index = 0
                self.commands = [
                    Move(unit_id="player1", to=(4, 3)),
                    Attack(attacker_id="player1", target_id="enemy1"),
                    EndTurn(unit_id="player1"),
                    Move(unit_id="player1", to=(5, 4)),
                    Attack(attacker_id="player1", target_id="enemy1"),
                    EndTurn(unit_id="player1"),
                    Move(unit_id="player1", to=(6, 5)),
                    Attack(attacker_id="player1", target_id="enemy1"),
                    EndTurn(unit_id="player1"),
                ]
            
            def decide(self, game_state: GameState):
                command = self.commands[self.command_index % len(self.commands)]
                self.command_index += 1
                return command
        
        state.set_controller(VisualDemoController(self))
        
        # Mock objectives and turn controller
        state.objectives = MockObjectives(self)
        state.turn_controller = MockTurnController(self)  # type: ignore
        
        return state

    def handle_event(self, event: Event):
        """Handle game events for visual feedback."""
        self.events_log.append(f"{event.type}: {event.payload}")
        if len(self.events_log) > 10:  # Keep only last 10 events
            self.events_log.pop(0)

    def draw_grid(self):
        """Draw the game grid."""
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (GRID_OFFSET[0] + x * GRID_SIZE, GRID_OFFSET[1]),
                           (GRID_OFFSET[0] + x * GRID_SIZE, GRID_OFFSET[1] + GRID_HEIGHT * GRID_SIZE))
        
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GRID_OFFSET[0], GRID_OFFSET[1] + y * GRID_SIZE),
                           (GRID_OFFSET[0] + GRID_WIDTH * GRID_SIZE, GRID_OFFSET[1] + y * GRID_SIZE))

    def draw_units(self):
        """Draw all units on the grid."""
        for unit in self.state.get_all_units():
            x, y = unit.pos
            screen_x = GRID_OFFSET[0] + x * GRID_SIZE + GRID_SIZE // 2
            screen_y = GRID_OFFSET[1] + y * GRID_SIZE + GRID_SIZE // 2
            
            # Choose color based on unit type
            if unit.id == "player1":
                color = BLUE
            else:
                color = RED
            
            # Draw unit circle
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), GRID_SIZE // 3)
            
            # Draw unit info
            info_text = f"{unit.id}\nHP:{unit.stats.hp}"
            text_surface = self.small_font.render(info_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            self.screen.blit(text_surface, text_rect)

    def draw_ui(self):
        """Draw UI elements."""
        # Draw title
        title = self.font.render("Starter Town Tactics - Command-Event Demo", True, WHITE)
        self.screen.blit(title, (10, 10))
        
        # Draw tick counter
        tick_text = self.font.render(f"Tick: {self.tick_count}/{self.max_ticks}", True, WHITE)
        self.screen.blit(tick_text, (10, 40))
        
        # Draw recent events
        events_text = self.font.render("Recent Events:", True, WHITE)
        self.screen.blit(events_text, (10, 70))
        
        for i, event in enumerate(self.events_log[-5:]):  # Show last 5 events
            event_text = self.small_font.render(event, True, YELLOW)
            self.screen.blit(event_text, (10, 95 + i * 20))
        
        # Draw instructions
        instructions = [
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Reset Demo",
            "ESC - Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, GRAY)
            self.screen.blit(inst_text, (WINDOW_SIZE[0] - 200, 10 + i * 20))

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle pause (not implemented yet)
                    pass
                elif event.key == pygame.K_r:
                    # Reset demo
                    self.state = self.load_demo_state()
                    self.tick_count = 0
                    self.events_log.clear()

    def run(self):
        """Main game loop."""
        print("🎮 Starting Visual Command-Event Demo...")
        print("Controls: SPACE=Pause, R=Reset, ESC=Quit")
        
        while self.running and self.tick_count < self.max_ticks:
            # Handle input
            self.handle_input()
            
            # Update game state
            self.loop.tick(self.state)
            self.tick_count += 1
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_units()
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            
            # Cap at 60 FPS
            self.clock.tick(60)
            
            # Add a small delay to make the demo visible
            time.sleep(0.1)
        
        print("✅ Visual demo completed!")
        pygame.quit()

class MockObjectives:
    def __init__(self, demo):
        self.demo = demo
    
    def update_from_events(self, events):
        pass

class MockTurnController:
    def __init__(self, demo):
        self.demo = demo
    
    def maybe_advance(self, game_state):
        pass

def main():
    """Run the visual demo."""
    demo = VisualDemo()
    demo.run()

if __name__ == "__main__":
    main()
