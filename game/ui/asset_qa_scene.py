"""
Asset QA Scene - automatically detects missing or misaligned art assets.
Integrated with existing asset system and provides comprehensive validation.
"""

import os
import time
from typing import Dict, List, Optional

import pygame

from game.sprite_manager import SpriteManager


# @api
# @refactor
class AssetQAScene:
    """Automatically displays all assets and logs missing ones with architecture integration."""

    def __init__(self, screen: pygame.Surface, logger=None):
        self.screen = screen
        self.logger = logger
        self.sprite_manager = SpriteManager()
        self.missing_assets = []
        self.placeholder_assets = []
        self.valid_assets = []

        # Load assets
        self.sprite_manager.load_assets()

    def run_asset_qa(self, auto_cycle: bool = True, delay: float = 0.5):
        """Run comprehensive asset QA with visual feedback."""
        print("🔍 Starting Asset QA Scene...")

        # Test terrain tiles
        self._test_terrain_assets()

        # Test unit sprites
        self._test_unit_assets()

        # Test UI assets
        self._test_ui_assets()

        # Generate report
        self._generate_qa_report()

        if auto_cycle:
            self._cycle_through_assets(delay)

        return {"missing": self.missing_assets, "placeholders": self.placeholder_assets, "valid": self.valid_assets}

    def _test_terrain_assets(self):
        """Test terrain tile assets."""
        terrain_types = ["grass", "forest", "mountain", "water", "desert", "dungeon"]

        for terrain_type in terrain_types:
            sprite_path = self.sprite_manager.get_terrain_sprite(terrain_type)
            if sprite_path and os.path.exists(sprite_path):
                try:
                    img = pygame.image.load(sprite_path)
                    self.valid_assets.append(f"terrain_{terrain_type}")
                    if self.logger:
                        self.logger.log_event(
                            "asset_valid", {"type": "terrain", "name": terrain_type, "path": sprite_path}
                        )
                except Exception as e:
                    self.missing_assets.append(f"terrain_{terrain_type} (load error: {e})")
            else:
                self.missing_assets.append(f"terrain_{terrain_type}")

    def _test_unit_assets(self):
        """Test unit sprite assets."""
        unit_types = ["knight", "mage", "archer", "paladin", "shadow", "berserker"]
        teams = ["blue", "red"]
        animation_frames = [0, 1, 2]  # Test first few frames

        for unit_type in unit_types:
            for team in teams:
                for frame in animation_frames:
                    sprite_path = self.sprite_manager.get_unit_sprite(unit_type, team, frame)
                    if sprite_path and os.path.exists(sprite_path):
                        try:
                            img = pygame.image.load(sprite_path)
                            self.valid_assets.append(f"unit_{unit_type}_{team}_{frame}")
                            if self.logger:
                                self.logger.log_event(
                                    "asset_valid",
                                    {"type": "unit", "name": f"{unit_type}_{team}_{frame}", "path": sprite_path},
                                )
                        except Exception as e:
                            self.missing_assets.append(f"unit_{unit_type}_{team}_{frame} (load error: {e})")
                    else:
                        self.missing_assets.append(f"unit_{unit_type}_{team}_{frame}")

    def _test_ui_assets(self):
        """Test UI asset placeholders."""
        # Test placeholder generation
        try:
            # Test button placeholder
            button_surface = pygame.Surface((100, 30))
            button_surface.fill((100, 100, 100))
            self.placeholder_assets.append("ui_button_placeholder")

            # Test panel placeholder
            panel_surface = pygame.Surface((200, 150))
            panel_surface.fill((50, 50, 50))
            self.placeholder_assets.append("ui_panel_placeholder")

            if self.logger:
                self.logger.log_event("placeholder_created", {"type": "ui", "assets": ["button", "panel"]})
        except Exception as e:
            self.missing_assets.append(f"ui_placeholder_generation (error: {e})")

    def _generate_qa_report(self):
        """Generate comprehensive QA report."""
        print("\n" + "=" * 50)
        print("🎨 ASSET QA REPORT")
        print("=" * 50)

        total_assets = len(self.valid_assets) + len(self.placeholder_assets) + len(self.missing_assets)
        valid_percentage = (len(self.valid_assets) / total_assets * 100) if total_assets > 0 else 0

        print(f"📊 Summary:")
        print(f"  ✅ Valid Assets: {len(self.valid_assets)}")
        print(f"  🔧 Placeholder Assets: {len(self.placeholder_assets)}")
        print(f"  ❌ Missing Assets: {len(self.missing_assets)}")
        print(f"  📈 Coverage: {valid_percentage:.1f}%")

        if self.missing_assets:
            print(f"\n❌ Missing Assets:")
            for asset in self.missing_assets:
                print(f"  - {asset}")

        if self.placeholder_assets:
            print(f"\n🔧 Placeholder Assets:")
            for asset in self.placeholder_assets:
                print(f"  - {asset}")

        print("\n" + "=" * 50)

        # Log report
        if self.logger:
            self.logger.log_event(
                "asset_qa_report",
                {
                    "valid_count": len(self.valid_assets),
                    "placeholder_count": len(self.placeholder_assets),
                    "missing_count": len(self.missing_assets),
                    "coverage_percentage": valid_percentage,
                    "missing_assets": self.missing_assets,
                },
            )

    def _cycle_through_assets(self, delay: float):
        """Cycle through all valid assets for visual review."""
        print(f"\n🔄 Cycling through {len(self.valid_assets)} valid assets...")
        print("Press any key to stop cycling...")

        font = pygame.font.Font(None, 24)
        clock = pygame.time.Clock()

        for i, asset_name in enumerate(self.valid_assets):
            # Clear screen
            self.screen.fill((0, 0, 0))

            # Display asset info
            text_surf = font.render(f"Asset {i+1}/{len(self.valid_assets)}: {asset_name}", True, (255, 255, 255))
            self.screen.blit(text_surf, (10, 10))

            # Try to display the asset
            try:
                if asset_name.startswith("terrain_"):
                    terrain_type = asset_name.split("_", 1)[1]
                    sprite_path = self.sprite_manager.get_terrain_sprite(terrain_type)
                    if sprite_path and os.path.exists(sprite_path):
                        img = pygame.image.load(sprite_path)
                        # Scale if needed
                        if img.get_width() > 200 or img.get_height() > 200:
                            img = pygame.transform.scale(img, (200, 200))
                        self.screen.blit(img, (300, 100))

                elif asset_name.startswith("unit_"):
                    parts = asset_name.split("_")
                    if len(parts) >= 4:
                        unit_type, team, frame = parts[1], parts[2], int(parts[3])
                        sprite_path = self.sprite_manager.get_unit_sprite(unit_type, team, frame)
                        if sprite_path and os.path.exists(sprite_path):
                            img = pygame.image.load(sprite_path)
                            # Scale if needed
                            if img.get_width() > 200 or img.get_height() > 200:
                                img = pygame.transform.scale(img, (200, 200))
                            self.screen.blit(img, (300, 100))

                elif asset_name.startswith("ui_"):
                    # Display placeholder
                    placeholder = pygame.Surface((200, 100))
                    placeholder.fill((100, 100, 100))
                    pygame.draw.rect(placeholder, (200, 200, 200), placeholder.get_rect(), 2)
                    self.screen.blit(placeholder, (300, 100))

            except Exception as e:
                error_text = font.render(f"Error loading: {e}", True, (255, 0, 0))
                self.screen.blit(error_text, (300, 100))

            pygame.display.flip()

            # Check for user input to stop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    return

            time.sleep(delay)
            clock.tick(60)

        print("✅ Asset cycling complete!")
        input("Press Enter to exit Asset QA Scene...")


def run_asset_qa_standalone(screen: pygame.Surface, auto_cycle: bool = True):
    """Standalone function to run asset QA (for backward compatibility)."""
    qa_scene = AssetQAScene(screen)
    return qa_scene.run_asset_qa(auto_cycle)
