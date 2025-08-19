#!/usr/bin/env python3
"""
Performance soak test for the command-event architecture.

This module runs the game loop at high frequency to measure performance
and identify bottlenecks in the command-event system.
"""

import sys
import os
import time
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_loop import GameLoop
from core.events import EventBus
from core.rng import Rng
from core.state import GameState
from core.command import Move, Attack, EndTurn


def headless_demo_state() -> GameState:
    """Create a headless demo state for performance testing.
    
    This state is optimized for performance testing without visual output.
    """
    state = GameState()
    
    # Create a simple controller that generates commands rapidly
    class SoakController:
        def __init__(self):
            self.tick_count = 0
            self.commands = [
                Move(unit_id="player1", to=(1, 1)),
                Attack(attacker_id="player1", target_id="enemy1"),
                EndTurn(unit_id="player1"),
                Move(unit_id="player1", to=(2, 2)),
                Attack(attacker_id="player1", target_id="enemy2"),
                EndTurn(unit_id="player1"),
            ]
        
        def decide(self, game_state: GameState):
            command = self.commands[self.tick_count % len(self.commands)]
            self.tick_count += 1
            return command
    
    state.set_controller(SoakController())
    
    # Minimal mock components for performance testing
    state.objectives = MinimalObjectives()
    state.turn_controller = MinimalTurnController()
    
    return state


class MinimalObjectives:
    """Minimal objectives manager for performance testing."""
    
    def update_from_events(self, events):
        # Do nothing for performance testing
        pass


class MinimalTurnController:
    """Minimal turn controller for performance testing."""
    
    def maybe_advance(self, game_state):
        # Do nothing for performance testing
        pass


def main():
    """Run performance soak test."""
    print("🧪 Starting Command-Event Performance Soak Test...")
    
    s = headless_demo_state()
    loop = GameLoop(Rng(1337), EventBus())
    n = 10000
    
    print(f"🔄 Running {n} ticks for performance measurement...")
    
    t0 = time.perf_counter()
    for i in range(n):
        loop.tick(s)
        
        # Progress indicator every 1000 ticks
        if i % 1000 == 0 and i > 0:
            elapsed = time.perf_counter() - t0
            rate = i / elapsed
            print(f"⏱️  {i}/{n} ticks ({rate:.0f} ticks/sec)")
    
    dt = time.perf_counter() - t0
    
    # Calculate performance metrics
    ticks_per_sec = n / dt
    ms_per_tick = (dt * 1000) / n
    
    results = {
        "ticks": n,
        "seconds": round(dt, 3),
        "ticks_per_sec": round(ticks_per_sec, 1),
        "ms_per_tick": round(ms_per_tick, 3),
        "performance_grade": "excellent" if ticks_per_sec > 1000 else "good" if ticks_per_sec > 100 else "needs_optimization"
    }
    
    print("\n📊 Performance Results:")
    print(json.dumps(results, indent=2))
    
    # Performance recommendations
    if results["performance_grade"] == "excellent":
        print("🎉 Excellent performance! System can handle high-frequency updates.")
    elif results["performance_grade"] == "good":
        print("✅ Good performance. Suitable for most game scenarios.")
    else:
        print("⚠️  Performance needs optimization for real-time gameplay.")
    
    print("✅ Soak test completed!")


if __name__ == "__main__":
    main()
