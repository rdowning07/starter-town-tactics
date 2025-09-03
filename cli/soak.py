#!/usr/bin/env python3
"""
Performance soak test for the command-event architecture.

This module runs the game loop at high frequency to measure performance
and identify bottlenecks in the command-event system.
"""

from __future__ import annotations

import json
import os
import sys
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loaders.demo_loader import load_state


def main():
    gs = load_state("assets/scenarios/demo.yaml")

    # Prefer the SimRunner your GameState already owns
    runner = getattr(gs, "sim_runner", None)
    if runner is None:
        from game.ai_controller import AIController  # type: ignore
        from game.sim_runner import SimRunner  # type: ignore

        runner = SimRunner(gs.turn_controller, AIController([]))
        if hasattr(runner, "set_game_state"):
            runner.set_game_state(gs)

    n = 10000
    t0 = time.perf_counter()
    for _ in range(n):
        if getattr(runner, "phase", None) == "GAME_OVER" or gs.is_game_over():
            break
        runner.run_turn()
    dt = time.perf_counter() - t0
    tps = n / dt if dt > 0 else 0.0

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/soak.json", "w") as f:
        json.dump({"ticks": n, "seconds": dt, "tps": tps}, f, indent=2)

    assert tps >= 3000, f"Perf gate failed: {tps:.0f} < 3000"


if __name__ == "__main__":
    main()
