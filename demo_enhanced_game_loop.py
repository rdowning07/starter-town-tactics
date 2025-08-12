#!/usr/bin/env python3
"""Demo script for the enhanced game loop implementation."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState
from game.game_loop import game_loop


def demo_enhanced_game_loop():
    """Demonstrate the enhanced game loop with a simple scenario."""
    print("🎮 Enhanced Game Loop Demo")
    print("=" * 50)
    
    # Create a game state
    game_state = GameState()
    
    # Add some units to make it interesting
    print("📦 Setting up initial game state...")
    game_state.add_unit("player1", "player", ap=3, hp=10)
    game_state.add_unit("player2", "player", ap=3, hp=8)
    game_state.add_unit("enemy1", "enemy", ap=3, hp=12)
    game_state.add_unit("enemy2", "enemy", ap=3, hp=6)
    
    print(f"✅ Added {len(game_state.units.get_all_units())} units")
    print(f"🎯 Initial objective: {game_state.get_current_objective()}")
    print()
    
    # Run the game loop for a few turns
    print("🔄 Starting game loop...")
    game_loop(game_state, max_turns=5)
    
    print("\n" + "=" * 50)
    print("🏁 Demo completed!")


def demo_with_events():
    """Demonstrate the enhanced game loop with events."""
    print("🎮 Enhanced Game Loop with Events Demo")
    print("=" * 50)
    
    # Create a game state
    game_state = GameState()
    
    # Add some units
    print("📦 Setting up initial game state...")
    game_state.add_unit("player1", "player", ap=3, hp=10)
    game_state.add_unit("enemy1", "enemy", ap=3, hp=15)
    
    print(f"✅ Added {len(game_state.units.get_all_units())} units")
    print(f"🎯 Initial objective: {game_state.get_current_objective()}")
    print()
    
    # Run the game loop for more turns to trigger events
    print("🔄 Starting game loop with events...")
    game_loop(game_state, max_turns=8)
    
    print("\n" + "=" * 50)
    print("🏁 Events demo completed!")


if __name__ == "__main__":
    print("🎮 Enhanced Game Loop Demonstrations")
    print("=" * 60)
    
    # Run basic demo
    demo_enhanced_game_loop()
    
    print("\n" + "=" * 60)
    
    # Run events demo
    demo_with_events()
    
    print("\n🎉 All demonstrations completed successfully!")
