#!/usr/bin/env python3
"""
Integrated soak test that uses the new demo loader.
Provides performance testing for the game system.
"""

import json
import os
import sys
import time
from typing import Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loaders.demo_loader import load_state

# Import game modules
from game.action_point_manager import ActionPointManager
from game.tactical_state_machine import TacticalStateMachine
from game.turn_controller import TurnController
from game.sim_runner import SimRunner
from game.ai_controller import AIController


class SoakAI(AIController):
    """Simple AI for soak testing - always passes."""
    
    def __init__(self):
        super().__init__([])
    
    def take_action(self, unit: Any):
        """Take action for the given unit - simple pass for soak testing."""
        # For soak testing, we just pass - no complex AI logic
        unit_name = getattr(unit, 'name', str(unit)) if hasattr(unit, 'name') else str(unit)
        print(f"DEBUG: SoakAI.take_action called for {unit_name}")
        pass
    
    def decide_action(self, ai_unit: Any) -> None:
        """Decide action - simple pass for soak testing."""
        pass
    
    def attack(self, ai_unit: Any, target_unit: Any) -> None:
        """Attack action - no-op for soak testing."""
        pass
    
    def move(self, ai_unit: Any, target_position: Any) -> None:
        """Move action - no-op for soak testing."""
        pass


def main():
    """Run the integrated soak test."""
    print("🧪 Starting Integrated Soak Test...")
    
    # Load game state
    try:
        game_state = load_state("assets/scenarios/demo.yaml")
        print(f"✅ Loaded scenario: {game_state.name}")
    except Exception as e:
        print(f"⚠️  Failed to load scenario: {e}")
        print("📋 Using default demo state...")
        game_state = load_state("nonexistent.yaml")  # Will fall back to default
    
    # The game state is already fully wired with all components
    # We just need to ensure the AI controller is properly set up
    ai = SoakAI()
    ai.set_game_state(game_state)
    
    # Replace the AI controller in the sim runner
    game_state.sim_runner.ai_controller = ai
    
    print(f"📊 Game state loaded with {len(game_state.units.get_all_units())} units")
    print(f"📊 Turn controller has {len(game_state.turn_controller.units)} units")
    
    # Run performance test
    n_ticks = 10000
    print(f"🔄 Running {n_ticks} ticks for performance measurement...")
    
    t0 = time.perf_counter()
    for i in range(n_ticks):
        game_state.sim_runner.run_turn()
        
        # Progress reporting
        if i % 1000 == 0 and i > 0:
            elapsed = time.perf_counter() - t0
            rate = i / elapsed
            print(f"⏱️  {i}/{n_ticks} ticks ({rate:.0f} ticks/sec)")
        
        # Stop if game is over
        if game_state.sim_runner.phase == "GAME_OVER":
            print(f"🏁 Game over at tick {i}")
            break
    
    dt = time.perf_counter() - t0
    tps = (n_ticks / dt) if dt > 0 else 0.0
    ms_per_tick = (dt * 1000) / n_ticks
    
    # Prepare results
    results = {
        "ticks": n_ticks,
        "seconds": round(dt, 3),
        "tps": round(tps, 1),
        "ms_per_tick": round(ms_per_tick, 3),
        "performance_grade": "excellent" if tps > 1000 else "good" if tps > 100 else "needs_optimization"
    }
    
    print("\n📊 Performance Results:")
    print(json.dumps(results, indent=2))
    
    # Write artifact
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/soak.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"📁 Artifact written to: artifacts/soak.json")
    
    # Performance gate
    assert tps >= 3000, f"Perf gate failed: {tps:.1f} tps < 3000 tps"
    
    print("✅ Soak test completed successfully!")
    print(f"🎯 Performance grade: {results['performance_grade']}")


if __name__ == "__main__":
    main()
