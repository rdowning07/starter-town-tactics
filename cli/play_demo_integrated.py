#!/usr/bin/env python3
"""
Integrated demo player that uses the new demo loader.
Bridges the provided files with our working game/ architecture.
"""

import argparse
import os
import sys
import time

import pygame

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.overlay.overlay_state import OverlayState
from game.renderer import Renderer
from game.sprite_manager import SpriteManager
from loaders.demo_loader import load_assets_after_pygame_init, load_state, load_state_and_assets


def _fallback_draw(screen, game_state, tile_px=32):
    """Fallback drawing function if renderer fails."""
    screen.fill((12, 12, 16))

    # Try to infer grid size from units
    units_dict = getattr(game_state.units, "units", {})
    if units_dict:
        max_x = max((info.get("x", 0) for info in units_dict.values()), default=16)
        max_y = max((info.get("y", 0) for info in units_dict.values()), default=16)
        w, h = max(16, max_x + 4), max(9, max_y + 4)
    else:
        w, h = 16, 9

    # Draw grid
    for y in range(h):
        for x in range(w):
            pygame.draw.rect(
                screen,
                (32, 48, 32),
                (x * tile_px, y * tile_px, tile_px - 1, tile_px - 1),
            )

    # Draw units
    for name, info in units_dict.items():
        x, y = int(info.get("x", 0)), int(info.get("y", 0))
        team = info.get("team", "neutral")
        color = (80, 160, 255) if team == "player" else (200, 80, 80) if team == "enemy" else (180, 180, 80)
        pygame.draw.rect(screen, color, (x * tile_px, y * tile_px, tile_px, tile_px))

    # Draw HUD
    try:
        font = pygame.font.Font(None, 18)
        y_offset = 4
        info_lines = [
            f"Turn: {getattr(game_state.sim_runner, 'turn_count', 0)}",
            f"Phase: {getattr(game_state.sim_runner, 'phase', 'UNKNOWN')}",
            f"Units: {len(units_dict)}",
        ]

        for line in info_lines:
            screen.blit(font.render(str(line), True, (230, 230, 230)), (4, y_offset))
            y_offset += 18
    except Exception:
        pass


def main():
    """Run the integrated demo."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="assets/scenarios/demo.yaml")
    parser.add_argument("--smoke", action="store_true", help="Exit after ~3 seconds (for CI)")
    parser.add_argument("--enhanced", action="store_true", help="Use enhanced renderer with assets")
    parser.add_argument("--w", type=int, default=960)
    parser.add_argument("--h", type=int, default=540)
    args = parser.parse_args()

    print("🎮 Starting Integrated Demo...")

    # Load game state and optionally assets
    if args.enhanced:
        print("📦 Loading with enhanced assets...")
        game_state, asset_manager = load_state_and_assets(args.scenario)
    else:
        print("📋 Loading basic state...")
        game_state = load_state(args.scenario)
        asset_manager = None

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((args.w, args.h))
    pygame.display.set_caption(f"Starter Town Tactics - {game_state.name}")
    clock = pygame.time.Clock()

    # Load assets after pygame initialization if enhanced mode
    if args.enhanced and asset_manager:
        try:
            load_assets_after_pygame_init(asset_manager)
            print("✅ Assets loaded after pygame initialization")
        except Exception as e:
            print(f"⚠️  Asset loading failed: {e}")
            asset_manager = None

    # Create renderer using real game API
    renderer = None
    if args.enhanced and asset_manager:
        try:
            # Use the real renderer with sprite manager
            sprite_manager = getattr(game_state, "sprite_manager", SpriteManager())
            renderer = Renderer(screen, sprite_manager)
            print("✅ Using real game renderer")
        except Exception as e:
            print(f"⚠️  Real renderer failed: {e}")
            renderer = None

    if not renderer:
        print("📋 Using fallback renderer")

    print("🔄 Running demo loop...")

    start_time = time.time()
    running = True

    while running:
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and asset_manager:
                    # Play sound effect for testing
                    asset_manager.play_sound("move")

        # Run one turn if we have a sim runner
        if hasattr(game_state, "sim_runner"):
            game_state.sim_runner.run_turn()

        # Render using real game API
        if renderer:
            try:
                # Use the real renderer API with proper parameters
                overlay_state = getattr(game_state, "overlay_state", OverlayState())
                fx_manager = getattr(game_state, "fx_manager", None)
                renderer.render(game_state, overlay_state, fx_manager)
            except Exception as e:
                print(f"⚠️  Renderer failed: {e}")
                _fallback_draw(screen, game_state)
        else:
            _fallback_draw(screen, game_state)

        pygame.display.flip()
        clock.tick(60)

        # Smoke test: exit after 3 seconds
        if args.smoke and (time.time() - start_time) > 3:
            print("⏰ Smoke test completed")
            break

        # Add some delay for visibility
        time.sleep(0.1)

    pygame.quit()
    print("✅ Integrated demo completed!")
    print(f"📊 Scenario: {game_state.name}")
    print(f"📊 Units loaded: {len(game_state.units.get_all_units())}")
    if asset_manager:
        print(f"📊 Assets loaded: {len(asset_manager.images)} images, {len(asset_manager.sounds)} sounds")


if __name__ == "__main__":
    main()
