#!/usr/bin/env python3
"""
CLI demo player for the command-event architecture.

This module demonstrates the core game loop with a visual demo.
Uses pygame adapters for view/input.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import pygame

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.pygame.overlay_state import OverlayState

# Use the real renderer; fall back to rectangles if render() raises
from game.renderer import Renderer as RealRenderer  # type: ignore
from loaders.demo_loader import load_state


def _fallback_draw(screen: pygame.Surface, gs, tile_px: int = 32) -> None:
    screen.fill((12, 12, 16))

    # Derive a safe grid if map is not present
    w = getattr(getattr(gs, "map", None), "width", None)
    h = getattr(getattr(gs, "map", None), "height", None)
    if w is None or h is None:
        units_dict = getattr(getattr(gs, "units", None), "units", {}) or {}
        maxx = max((int(u.get("x", 0)) for u in units_dict.values()), default=16)
        maxy = max((int(u.get("y", 0)) for u in units_dict.values()), default=9)
        w, h = max(16, maxx + 4), max(9, maxy + 4)

    for y in range(h):
        for x in range(w):
            pygame.draw.rect(screen, (32, 48, 32), (x * tile_px, y * tile_px, tile_px - 1, tile_px - 1))

    # Units via UnitManager.units dict
    units_dict = getattr(getattr(gs, "units", None), "units", {}) or {}
    for name, info in units_dict.items():
        x, y = int(info.get("x", 0)), int(info.get("y", 0))
        team = info.get("team") or info.get("side") or "neutral"
        color = (80, 160, 255) if team == "player" else (200, 80, 80) if team == "enemy" else (180, 180, 80)
        pygame.draw.rect(screen, color, (x * tile_px, y * tile_px, tile_px, tile_px))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="assets/scenarios/demo.yaml")
    ap.add_argument("--smoke", action="store_true", help="Exit after ~3 seconds (for CI)")
    ap.add_argument("--w", type=int, default=960)
    ap.add_argument("--h", type=int, default=540)
    args = ap.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((args.w, args.h))
    clock = pygame.time.Clock()

    gs = load_state(args.scenario)

    # Prepare overlay + renderer
    overlay = OverlayState()
    renderer = RealRenderer(screen, getattr(gs, "sprite_manager", None))  # type: ignore[arg-type]

    # Use your existing SimRunner from GameState, else make one
    runner = getattr(gs, "sim_runner", None)
    if runner is None:
        from game.ai_controller import AIController  # type: ignore
        from game.sim_runner import SimRunner  # type: ignore

        runner = SimRunner(gs.turn_controller, AIController([]))
        if hasattr(runner, "set_game_state"):
            runner.set_game_state(gs)

    # If you have a camera, keep it updated
    camera = getattr(gs, "camera", None)

    t0 = time.time()
    running = True
    while running and not gs.is_game_over():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        # Drive one turn per frame; player turns will log and end (per your SimRunner)
        runner.run_turn()

        # Camera update if present
        if camera is not None and hasattr(camera, "update"):
            camera.update()

        # Try real renderer first; fall back if it errors
        try:
            renderer.render(gs, overlay, getattr(gs, "fx_manager", None))  # type: ignore[arg-type]
        except Exception:
            _fallback_draw(screen, gs)
            pygame.display.flip()

        clock.tick(60)

        if args.smoke and (time.time() - t0) > 3.0:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
