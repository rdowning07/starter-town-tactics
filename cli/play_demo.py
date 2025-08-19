#!/usr/bin/env python3
"""
CLI demo player for the command-event architecture.

This module demonstrates the core game loop with a visual demo.
TODO: load scenario → GameState; wire adapters/pygame for view/input
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_loop import GameLoop
from core.events import EventBus
from core.rng import Rng
from core.state import GameState
from core.command import Move, Attack, EndTurn
from core.events import Event


def load_demo_state() -> GameState:
    """Load a demo game state for testing.
    
    TODO: Replace with actual scenario loading from YAML
    """
    state = GameState()
    
    # Create a simple demo controller that cycles through commands
    class DemoController:
        def __init__(self):
            self.command_index = 0
            self.commands = [
                Move(unit_id="player1", to=(5, 5)),
                Attack(attacker_id="player1", target_id="enemy1"),
                EndTurn(unit_id="player1"),
                Move(unit_id="player1", to=(6, 6)),
                Attack(attacker_id="player1", target_id="enemy1"),
                EndTurn(unit_id="player1"),
            ]
        
        def decide(self, game_state: GameState):
            command = self.commands[self.command_index % len(self.commands)]
            self.command_index += 1
            return command
    
    state.set_controller(DemoController())
    
    # Mock objectives and turn controller for demo
    state.objectives = MockObjectives()
    state.turn_controller = MockTurnController()
    
    return state


class MockObjectives:
    """Mock objectives manager for demo."""
    
    def update_from_events(self, events):
        for event in events:
            print(f"🎯 Objective update: {event.type}")


class MockTurnController:
    """Mock turn controller for demo."""
    
    def maybe_advance(self, game_state):
        print(f"🔄 Turn advanced")


def main():
    """Run the demo game loop."""
    print("🎮 Starting Command-Event Demo...")
    
    rng = Rng(1337)
    bus = EventBus()
    loop = GameLoop(rng, bus)
    s = load_demo_state()
    
    # Subscribe to events for demo output
    def event_logger(event: Event):
        print(f"📡 Event: {event.type} - {event.payload}")
    
    bus.subscribe(event_logger)
    
    print("🔄 Running demo loop (3600 ticks ≈ 60 seconds @ 60fps)...")
    
    for tick in range(3600):
        loop.tick(s)
        
        # Add some visual feedback every 100 ticks
        if tick % 100 == 0:
            print(f"⏱️  Tick {tick}/3600")
        
        # Stop if game is over
        if s.is_over():
            print("🏁 Game over!")
            break
    
    print("✅ Demo completed!")


if __name__ == "__main__":
    main()
