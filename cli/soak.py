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
    
    # Create units for the demo
    from core.state import Unit, UnitStats
    player_unit = Unit("player1", (1, 1), team="player", stats=UnitStats(hp=20, atk=8, def_=3))
    enemy1_unit = Unit("enemy1", (5, 5), team="enemy", stats=UnitStats(hp=15, atk=6, def_=2))
    enemy2_unit = Unit("enemy2", (6, 6), team="enemy", stats=UnitStats(hp=15, atk=6, def_=2))
    state.add_unit(player_unit)
    state.add_unit(enemy1_unit)
    state.add_unit(enemy2_unit)
    
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
    # Use type ignore for performance testing mock
    state.turn_controller = MinimalTurnController()  # type: ignore
    
    return state


class MinimalObjectives:
    """Minimal objectives manager for performance testing."""
    
    def update_from_events(self, events):
        # Do nothing for performance testing
        pass


class MinimalTurnController:
    """Minimal turn controller for performance testing."""
    
    @property
    def current_unit_id(self):
        return "player1"
    
    def flag_end_of_turn(self):
        pass
    
    def start_if_needed(self, game_state):
        return []
    
    def maybe_advance(self, game_state):
        # Do nothing for performance testing
        return []
        pass


def main():
    """Run performance soak test."""
    print("🧪 Starting Command-Event Performance Soak Test...")
    
    # Create artifacts directory
    os.makedirs("artifacts", exist_ok=True)
    
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
        "tps": round(ticks_per_sec, 1),
        "ms_per_tick": round(ms_per_tick, 3),
        "performance_grade": "excellent" if ticks_per_sec > 1000 else "good" if ticks_per_sec > 100 else "needs_optimization"
    }
    
    print("\n📊 Performance Results:")
    print(json.dumps(results, indent=2))
    
    # Write artifact to artifacts/soak.json
    with open("artifacts/soak.json", "w") as f:
        json.dump({"ticks": n, "seconds": dt, "tps": n/dt}, f, indent=2)
    
    # Performance gate: must achieve >= 3000 tps
    assert (n/dt) >= 3000, f"Perf gate failed: {n/dt:.1f} tps < 3000 tps"
    
    # Performance recommendations
    if results["performance_grade"] == "excellent":
        print("🎉 Excellent performance! System can handle high-frequency updates.")
    elif results["performance_grade"] == "good":
        print("✅ Good performance. Suitable for most game scenarios.")
    else:
        print("⚠️  Performance needs optimization for real-time gameplay.")
    
    print("✅ Soak test completed!")
    print(f"📁 Artifact written to: artifacts/soak.json")


if __name__ == "__main__":
    main()
