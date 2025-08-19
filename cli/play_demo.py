#!/usr/bin/env python3
"""
CLI demo player for the command-event architecture.

This module demonstrates the core game loop with a visual demo.
Uses pygame adapters for view/input.
"""

import sys
import os
import pygame
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_loop import GameLoop
from core.events import EventBus
from core.rng import Rng
from core.state import GameState
from core.command import Move, Attack, EndTurn
from core.events import Event
from adapters.pygame import Renderer, InputController


def load_demo_state() -> GameState:
    """Load a demo game state for testing.
    
    TODO: Replace with actual scenario loading from YAML
    """
    state = GameState()
    
    # Create units for the demo
    from core.state import Unit, UnitStats
    player_unit = Unit("player1", (1, 1), team="player", stats=UnitStats(hp=20, atk=8, def_=3))
    enemy_unit = Unit("enemy1", (5, 5), team="enemy", stats=UnitStats(hp=15, atk=6, def_=2))
    state.add_unit(player_unit)
    state.add_unit(enemy_unit)
    
    # Create a more interesting demo controller
    class DemoController:
        def __init__(self):
            self.turn_count = 0
        
        def decide(self, game_state: GameState):
            self.turn_count += 1
            
            # Player actions
            if game_state.current_side() == "player":
                if self.turn_count == 1:
                    return Move(unit_id="player1", to=(3, 3))
                elif self.turn_count == 3:
                    return Attack(attacker_id="player1", target_id="enemy1")
                elif self.turn_count == 5:
                    return Move(unit_id="player1", to=(4, 4))
                else:
                    return EndTurn(unit_id="player1")
            
            # Enemy actions (simple AI)
            else:
                if self.turn_count == 2:
                    return Move(unit_id="enemy1", to=(6, 6))
                elif self.turn_count == 4:
                    return Attack(attacker_id="enemy1", target_id="player1")
                else:
                    return EndTurn(unit_id="enemy1")
    
    state.set_controller(DemoController())
    
    # Mock objectives for demo
    state.objectives = MockObjectives()
    
    return state


class MockObjectives:
    """Mock objectives manager for demo."""
    
    def update_from_events(self, events):
        for event in events:
            print(f"🎯 Objective update: {event.type}")
    
    def get_current_objective(self) -> str:
        return "Demo Objective: Survive and defeat enemies"


class MockTurnController:
    """Mock turn controller for demo."""
    
    @property
    def current_unit_id(self):
        return "player1"
    
    def flag_end_of_turn(self):
        pass
    
    def start_if_needed(self, game_state):
        return []
    
    def maybe_advance(self, game_state):
        print(f"🔄 Turn advanced")
        return []


def main():
    """Run the demo game loop."""
    print("🎮 Starting Command-Event Demo...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Starter Town Tactics - Demo")
    clock = pygame.time.Clock()
    
    # Create sprite manager (simple dict for now)
    sprites = {
        "player1": pygame.Surface((32, 32)),
        "enemy1": pygame.Surface((32, 32))
    }
    sprites["player1"].fill((0, 255, 0))  # Green for player
    sprites["enemy1"].fill((255, 0, 0))   # Red for enemy
    
    # Initialize game components
    rng = Rng(1337)  # Fixed seed from scenario config
    bus = EventBus()
    loop = GameLoop(rng, bus)
    s = load_demo_state()
    
    # Set up pygame adapters
    renderer = Renderer(screen, sprites)
    input_controller = InputController()
    s.set_controller(input_controller)
    
    # Subscribe to events for demo output
    def event_logger(event: Event):
        print(f"📡 Event: {event.type} - {event.payload}")
    
    bus.subscribe(event_logger)
    
    print("🔄 Running demo loop (~15 seconds)...")
    
    start_time = time.time()
    max_time = 15  # 15 seconds max
    
    while time.time() - start_time < max_time and not s.is_over():
        # Handle input and update game
        loop.tick(s)
        
        # Render the game state
        renderer.draw(s.snapshot())
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
        
        # Add some visual feedback every 50 ticks
        if s.tick % 50 == 0:
            print(f"⏱️  Tick {s.tick}")
    
    if s.is_over():
        print("🏁 Game over!")
    else:
        print("⏰ Time limit reached!")
    
    pygame.quit()
    print("✅ Demo completed!")


if __name__ == "__main__":
    main()
