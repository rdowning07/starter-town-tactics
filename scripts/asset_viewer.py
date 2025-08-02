#!/usr/bin/env python3
"""
Modern Asset Viewer for Starter Town Tactics
Integrates with SpriteManager and current asset structure.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# Add game directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from game.sprite_manager import SpriteManager


class AssetViewer:
    """Modern asset viewer with SpriteManager integration."""

    def __init__(self, screen_width: int = 1024, screen_height: int = 768):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sprite_manager = SpriteManager()

        # Asset categories and current selection
        self.categories = ["units", "tiles", "effects", "ui"]
        self.current_category = 0
        self.current_asset_index = 0

        # Asset lists by category
        self.assets = {
            "units": self._get_unit_assets(),
            "tiles": self._get_tile_assets(),
            "effects": self._get_effect_assets(),
            "ui": self._get_ui_assets(),
        }

        # UI state
        self.font = None
        self.small_font = None
        self.colors = {
            "background": (30, 30, 30),
            "text": (255, 255, 255),
            "highlight": (100, 150, 255),
            "error": (255, 100, 100),
            "success": (100, 255, 100),
        }

        # Pygame objects (initialized later)
        self.screen = None
        self.clock = None

    def _get_unit_assets(self) -> List[Tuple[str, str, str]]:
        """Get list of unit assets (name, team, path)."""
        assets = []
        units_dir = Path("assets/units")

        if units_dir.exists():
            for unit_dir in units_dir.iterdir():
                if unit_dir.is_dir():
                    unit_name = unit_dir.name
                    for sprite_file in unit_dir.glob("*.png"):
                        # Extract team and frame info from filename
                        filename = sprite_file.stem
                        parts = filename.split("_")
                        if len(parts) >= 2:
                            team = parts[0]
                            assets.append((unit_name, team, str(sprite_file)))

        return assets

    def _get_tile_assets(self) -> List[Tuple[str, str, str]]:
        """Get list of tile assets (environment, name, path)."""
        assets = []
        tiles_dir = Path("assets/tiles")

        if tiles_dir.exists():
            for env_dir in tiles_dir.iterdir():
                if env_dir.is_dir():
                    env_name = env_dir.name
                    for tile_file in env_dir.glob("*.png"):
                        tile_name = tile_file.stem
                        assets.append((env_name, tile_name, str(tile_file)))

        return assets

    def _get_effect_assets(self) -> List[Tuple[str, str, str]]:
        """Get list of effect assets (type, name, path)."""
        assets = []
        effects_dir = Path("assets/effects")

        if effects_dir.exists():
            for effect_type_dir in effects_dir.iterdir():
                if effect_type_dir.is_dir():
                    effect_type = effect_type_dir.name
                    for effect_file in effect_type_dir.glob("*.png"):
                        effect_name = effect_file.stem
                        assets.append((effect_type, effect_name, str(effect_file)))

        return assets

    def _get_ui_assets(self) -> List[Tuple[str, str, str]]:
        """Get list of UI assets (type, name, path)."""
        assets = []
        ui_dir = Path("assets/ui")

        if ui_dir.exists():
            for ui_type_dir in ui_dir.iterdir():
                if ui_type_dir.is_dir():
                    ui_type = ui_type_dir.name
                    for ui_file in ui_type_dir.glob("*.png"):
                        ui_name = ui_file.stem
                        assets.append((ui_type, ui_name, str(ui_file)))

        return assets

    def init_pygame(self):
        """Initialize Pygame and fonts."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Starter Town Tactics - Asset Viewer")
        self.clock = pygame.time.Clock()

        # Initialize fonts
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)

    def load_current_asset(self) -> Optional[pygame.Surface]:
        """Load the currently selected asset."""
        category = self.categories[self.current_category]
        assets = self.assets[category]

        if not assets:
            return None

        if self.current_asset_index >= len(assets):
            self.current_asset_index = 0

        try:
            _, _, asset_path = assets[self.current_asset_index]
            return pygame.image.load(asset_path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    def draw_ui(self):
        """Draw the user interface."""
        self.screen.fill(self.colors["background"])

        # Draw category selector
        self._draw_category_selector()

        # Draw asset info
        self._draw_asset_info()

        # Draw navigation help
        self._draw_navigation_help()

        # Draw current asset
        self._draw_current_asset()

    def _draw_category_selector(self):
        """Draw the category selection bar."""
        y_offset = 10
        x_offset = 10

        for i, category in enumerate(self.categories):
            color = (
                self.colors["highlight"]
                if i == self.current_category
                else self.colors["text"]
            )
            text = self.font.render(category.upper(), True, color)
            self.screen.blit(text, (x_offset, y_offset))
            x_offset += text.get_width() + 20

        # Draw asset count
        category = self.categories[self.current_category]
        assets = self.assets[category]
        count_text = self.small_font.render(
            f"Assets: {len(assets)}", True, self.colors["text"]
        )
        self.screen.blit(count_text, (x_offset, y_offset + 5))

    def _draw_asset_info(self):
        """Draw information about the current asset."""
        category = self.categories[self.current_category]
        assets = self.assets[category]

        if not assets:
            text = self.font.render("No assets found", True, self.colors["error"])
            self.screen.blit(text, (10, 60))
            return

        if self.current_asset_index >= len(assets):
            return

        asset_name, asset_subtype, asset_path = assets[self.current_asset_index]

        # Asset details
        details = [
            f"Category: {category}",
            f"Name: {asset_name}",
            f"Type: {asset_subtype}",
            f"Path: {asset_path}",
            f"Index: {self.current_asset_index + 1}/{len(assets)}",
        ]

        y_offset = 60
        for detail in details:
            text = self.small_font.render(detail, True, self.colors["text"])
            self.screen.blit(text, (10, y_offset))
            y_offset += 20

    def _draw_navigation_help(self):
        """Draw navigation instructions."""
        help_texts = [
            "Navigation:",
            "← → Arrow Keys: Navigate assets",
            "↑ ↓ Arrow Keys: Change category",
            "ESC: Exit viewer",
            "SPACE: Toggle fullscreen",
        ]

        y_offset = self.screen_height - 120
        for help_text in help_texts:
            text = self.small_font.render(help_text, True, self.colors["text"])
            self.screen.blit(text, (10, y_offset))
            y_offset += 18

    def _draw_current_asset(self):
        """Draw the current asset image."""
        asset_surface = self.load_current_asset()

        if asset_surface is None:
            text = self.font.render("Failed to load asset", True, self.colors["error"])
            text_rect = text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            self.screen.blit(text, text_rect)
            return

        # Calculate position to center the image
        img_width, img_height = asset_surface.get_size()
        x = (self.screen_width - img_width) // 2
        y = (self.screen_height - img_height) // 2

        # Ensure image doesn't go off screen
        x = max(x, 200)  # Leave space for UI
        y = max(y, 150)  # Leave space for UI

        self.screen.blit(asset_surface, (x, y))

        # Draw image dimensions
        dim_text = self.small_font.render(
            f"{img_width}x{img_height}", True, self.colors["text"]
        )
        self.screen.blit(dim_text, (x, y - 20))

    def handle_events(self) -> bool:
        """Handle Pygame events. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_LEFT:
                    self._previous_asset()
                if event.key == pygame.K_RIGHT:
                    self._next_asset()
                if event.key == pygame.K_UP:
                    self._previous_category()
                if event.key == pygame.K_DOWN:
                    self._next_category()
                if event.key == pygame.K_SPACE:
                    self._toggle_fullscreen()

        return True

    def _previous_asset(self):
        """Go to previous asset."""
        category = self.categories[self.current_category]
        assets = self.assets[category]
        if assets:
            self.current_asset_index = (self.current_asset_index - 1) % len(assets)

    def _next_asset(self):
        """Go to next asset."""
        category = self.categories[self.current_category]
        assets = self.assets[category]
        if assets:
            self.current_asset_index = (self.current_asset_index + 1) % len(assets)

    def _previous_category(self):
        """Go to previous category."""
        self.current_category = (self.current_category - 1) % len(self.categories)
        self.current_asset_index = 0

    def _next_category(self):
        """Go to next category."""
        self.current_category = (self.current_category + 1) % len(self.categories)
        self.current_asset_index = 0

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode((self.screen_width, self.screen_height))
        else:
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def run(self):
        """Main viewer loop."""
        self.init_pygame()

        running = True
        while running:
            running = self.handle_events()

            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def main():
    """Main function."""
    print("🎨 Starting Asset Viewer...")
    print("Loading assets from current project structure...")

    viewer = AssetViewer()
    viewer.run()


if __name__ == "__main__":
    main()
