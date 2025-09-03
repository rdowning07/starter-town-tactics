#!/usr/bin/env python3
"""
Generate UI Stub Assets - Creates placeholder PNG files for UI components.
Aligned with existing UIRenderer architecture and fallback mechanisms.
"""

import os
from pathlib import Path

import pygame


def generate_ui_stubs():
    """Generate UI stub assets for the game."""

    # Initialize pygame for image generation
    pygame.init()

    # Define asset specifications
    stubs = {
        # Health and AP bars
        "healthbar.png": {"size": (64, 8), "color": (255, 0, 0), "description": "Health bar background"},
        "apbar.png": {"size": (64, 8), "color": (0, 0, 255), "description": "AP bar background"},
        # Cursors
        "cursors/cursor.png": {"size": (16, 16), "color": (255, 255, 255), "description": "Default cursor"},
        "cursors/select.png": {"size": (16, 16), "color": (255, 255, 0), "description": "Selection cursor"},
        "cursors/move.png": {"size": (16, 16), "color": (0, 255, 0), "description": "Movement cursor"},
        "cursors/attack.png": {"size": (16, 16), "color": (255, 0, 0), "description": "Attack cursor"},
        "cursors/invalid.png": {"size": (16, 16), "color": (128, 128, 128), "description": "Invalid action cursor"},
        # Icons
        "icons/attack.png": {"size": (32, 32), "color": (139, 0, 0), "description": "Attack ability icon"},
        "icons/move.png": {"size": (32, 32), "color": (0, 100, 0), "description": "Move ability icon"},
        "icons/heal.png": {"size": (32, 32), "color": (0, 255, 0), "description": "Heal ability icon"},
        "icons/wait.png": {"size": (32, 32), "color": (255, 255, 0), "description": "Wait ability icon"},
        "icons/special.png": {"size": (32, 32), "color": (255, 0, 255), "description": "Special ability icon"},
        "icons/defend.png": {"size": (32, 32), "color": (0, 0, 255), "description": "Defend ability icon"},
        "icons/health.png": {"size": (32, 32), "color": (255, 0, 0), "description": "Health icon"},
        "icons/ap.png": {"size": (32, 32), "color": (0, 0, 255), "description": "AP icon"},
        # Panels
        "panels/status_panel.png": {"size": (128, 32), "color": (50, 50, 50), "description": "Status panel background"},
        "panels/turn_panel.png": {"size": (128, 32), "color": (100, 100, 100), "description": "Turn panel background"},
        "panels/action_panel.png": {
            "size": (128, 32),
            "color": (150, 150, 150),
            "description": "Action panel background",
        },
        "panels/health_panel.png": {"size": (128, 32), "color": (75, 75, 75), "description": "Health panel background"},
    }

    # Create assets directory
    assets_dir = Path("assets/ui")
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (assets_dir / "cursors").mkdir(exist_ok=True)
    (assets_dir / "icons").mkdir(exist_ok=True)
    (assets_dir / "panels").mkdir(exist_ok=True)

    generated_count = 0

    print("🎨 Generating UI stub assets...")
    print("=" * 50)

    for path, props in stubs.items():
        full_path = assets_dir / path

        # Create surface with specified size and color
        surface = pygame.Surface(props["size"])
        surface.fill(props["color"])

        # Add a subtle border for better visibility
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 1)

        # Save the image
        pygame.image.save(surface, full_path)

        print(f"✅ Created: {full_path} ({props['size'][0]}x{props['size'][1]}) - {props['description']}")
        generated_count += 1

    # Create asset manifest
    manifest = {"ui_assets": {"version": "1.0", "description": "UI stub assets for Starter Town Tactics", "assets": {}}}

    for path, props in stubs.items():
        manifest["ui_assets"]["assets"][path.replace(".png", "").replace("/", "_")] = {
            "path": f"assets/ui/{path}",
            "size": props["size"],
            "description": props["description"],
            "type": "stub",
        }

    # Save manifest
    import json

    manifest_path = assets_dir / "ui_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print("=" * 50)
    print(f"🎯 Generated {generated_count} UI stub assets")
    print(f"📄 Asset manifest: {manifest_path}")
    print("✅ Ready for integration with UIRenderer system!")

    pygame.quit()
    return generated_count


if __name__ == "__main__":
    try:
        count = generate_ui_stubs()
        print(f"\n🎮 Successfully generated {count} UI stub assets!")
        print("💡 These stubs can be replaced with real artwork as needed.")
        print("🔧 The UIRenderer system will automatically use fallbacks if assets are missing.")
    except Exception as e:
        print(f"❌ Error generating UI stubs: {e}")
        exit(1)
