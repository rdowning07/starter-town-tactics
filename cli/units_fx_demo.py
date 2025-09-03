#!/usr/bin/env python3
"""
Units & FX Demo - Demonstrates fighter/bandit animations with spark/slash effects.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.animation_clock import AnimationClock
from game.demo_base import DemoBase


class UnitsFXDemo(DemoBase):
    """Demo for units and FX animations."""

    def __init__(self, timeout_seconds: int = 30):
        """Initialize the demo."""
        super().__init__(timeout_seconds=timeout_seconds, auto_exit=True)

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Units & FX Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Animation clock
        self.animation_clock = AnimationClock()

        # Load metadata
        self.animation_metadata = self._load_animation_metadata()
        self.effects_metadata = self._load_effects_metadata()

        # Load assets
        self.unit_sprites = self._load_unit_sprites()
        self.effect_sprites = self._load_effect_sprites()

        # Demo state
        self.fighter_animation = "idle"
        self.bandit_animation = "idle"
        self.active_effects = []
        self.camera_x = 0
        self.camera_y = 0

        # Tile size
        self.tile_size = 32

    def _load_animation_metadata(self) -> Dict:
        """Load animation metadata."""
        try:
            with open("assets/units/_metadata/animation_metadata.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load animation metadata: {e}")
            return {"units": {}}

    def _load_effects_metadata(self) -> Dict:
        """Load effects metadata."""
        try:
            with open("assets/effects/effects_metadata.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load effects metadata: {e}")
            return {"effects": {}}

    def _load_unit_sprites(self) -> Dict[str, Dict[str, pygame.Surface]]:
        """Load unit sprite sheets."""
        sprites = {}
        for unit_name in ["fighter", "bandit"]:
            sprites[unit_name] = {}
            if unit_name in self.animation_metadata.get("units", {}):
                unit_meta = self.animation_metadata["units"][unit_name]
                for anim_name in unit_meta:
                    sheet_path = unit_meta[anim_name]["sheet"]
                    try:
                        sprites[unit_name][anim_name] = pygame.image.load(sheet_path)
                    except pygame.error as e:
                        print(f"Failed to load {sheet_path}: {e}")
                        # Create placeholder
                        sprites[unit_name][anim_name] = self._create_placeholder(32, 32, (255, 0, 0))
        return sprites

    def _load_effect_sprites(self) -> Dict[str, pygame.Surface]:
        """Load effect sprite sheets."""
        sprites = {}
        for effect_name in ["spark", "slash"]:
            if effect_name in self.effects_metadata.get("effects", {}):
                sheet_path = self.effects_metadata["effects"][effect_name]["sheet"]
                try:
                    sprites[effect_name] = pygame.image.load(sheet_path)
                except pygame.error as e:
                    print(f"Failed to load {sheet_path}: {e}")
                    # Create placeholder
                    sprites[effect_name] = self._create_placeholder(32, 32, (0, 255, 0))
        return sprites

    def _create_placeholder(self, width: int, height: int, color: Tuple[int, int, int]) -> pygame.Surface:
        """Create a placeholder surface."""
        surface = pygame.Surface((width, height))
        surface.fill(color)
        return surface

    def _get_frame_index(self, meta: Dict, animation_id: Optional[str] = None) -> int:
        """Get current frame index for animation."""
        return self.animation_clock.get_frame_index(meta, animation_id)

    def _blit_animation(
        self,
        surface: pygame.Surface,
        sheet: pygame.Surface,
        meta: Dict,
        world_x: int,
        world_y: int,
        animation_id: Optional[str] = None,
    ) -> None:
        """Blit an animated sprite."""
        frame_size = meta["frame_size"]
        frame_w, frame_h = frame_size
        origin = meta.get("origin", [frame_w // 2, frame_h])
        origin_x, origin_y = origin

        # Get current frame
        frame_idx = self._get_frame_index(meta, animation_id)

        # Calculate source rectangle
        src_rect = pygame.Rect(frame_idx * frame_w, 0, frame_w, frame_h)

        # Calculate screen position
        screen_x = world_x - self.camera_x - origin_x + self.tile_size // 2
        screen_y = world_y - self.camera_y - origin_y + self.tile_size

        # Blit the frame
        surface.blit(sheet, (screen_x, screen_y), src_rect)

    def _spawn_effect(self, effect_name: str, x: int, y: int) -> None:
        """Spawn an effect at the given position."""
        if effect_name in self.effects_metadata.get("effects", {}):
            effect_id = f"{effect_name}_{len(self.active_effects)}"
            self.active_effects.append(
                {
                    "id": effect_id,
                    "name": effect_name,
                    "x": x,
                    "y": y,
                    "start_time": self.animation_clock.get_elapsed_ms(),
                }
            )
            # Start tracking the animation
            self.animation_clock.start_animation(effect_id, self.effects_metadata["effects"][effect_name])

    def _update_effects(self) -> None:
        """Update active effects."""
        current_time = self.animation_clock.get_elapsed_ms()
        finished_effects = []

        for effect in self.active_effects:
            effect_id = effect["id"]
            self.animation_clock.update_animation(effect_id)

            if self.animation_clock.is_animation_finished(effect_id):
                finished_effects.append(effect)

        # Remove finished effects
        for effect in finished_effects:
            self.active_effects.remove(effect)
            self.animation_clock.clear_animation(effect["id"])

    def _draw_terrain(self, surface: pygame.Surface) -> None:
        """Draw simple terrain grid."""
        for y in range(10):
            for x in range(10):
                rect = pygame.Rect(
                    x * self.tile_size - self.camera_x,
                    y * self.tile_size - self.camera_y,
                    self.tile_size,
                    self.tile_size,
                )
                color = (100, 150, 100) if (x + y) % 2 == 0 else (80, 120, 80)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (50, 50, 50), rect, 1)

    def _draw_units(self, surface: pygame.Surface) -> None:
        """Draw units with animations."""
        # Fighter at (4, 4)
        if "fighter" in self.unit_sprites and self.fighter_animation in self.unit_sprites["fighter"]:
            fighter_x = 4 * self.tile_size
            fighter_y = 4 * self.tile_size
            fighter_meta = self.animation_metadata["units"]["fighter"][self.fighter_animation]
            self._blit_animation(
                surface,
                self.unit_sprites["fighter"][self.fighter_animation],
                fighter_meta,
                fighter_x,
                fighter_y,
                "fighter_idle",
            )

        # Bandit at (6, 5)
        if "bandit" in self.unit_sprites and self.bandit_animation in self.unit_sprites["bandit"]:
            bandit_x = 6 * self.tile_size
            bandit_y = 5 * self.tile_size
            bandit_meta = self.animation_metadata["units"]["bandit"][self.bandit_animation]
            self._blit_animation(
                surface,
                self.unit_sprites["bandit"][self.bandit_animation],
                bandit_meta,
                bandit_x,
                bandit_y,
                "bandit_idle",
            )

    def _draw_effects(self, surface: pygame.Surface) -> None:
        """Draw active effects."""
        for effect in self.active_effects:
            effect_name = effect["name"]
            if effect_name in self.effect_sprites:
                effect_x = effect["x"] * self.tile_size
                effect_y = effect["y"] * self.tile_size
                effect_meta = self.effects_metadata["effects"][effect_name]
                self._blit_animation(
                    surface,
                    self.effect_sprites[effect_name],
                    effect_meta,
                    effect_x,
                    effect_y,
                    effect["id"],
                )

    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Draw UI overlay."""
        # Instructions
        instructions = [
            "SPACE: Spawn spark at fighter",
            "A: Fighter attack animation",
            "W: Toggle bandit walk",
            "Arrow keys: Move camera",
            "ESC: Quit",
        ]

        y_offset = 10
        for instruction in instructions:
            text = self.font.render(instruction, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 25

        # Current animations
        anim_text = f"Fighter: {self.fighter_animation}, Bandit: {self.bandit_animation}"
        text = self.font.render(anim_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset + 10))

        # Active effects count
        effects_text = f"Active effects: {len(self.active_effects)}"
        text = self.font.render(effects_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset + 35))

    def _handle_input(self) -> bool:
        """Handle input events. Returns False to quit."""
        for event in pygame.event.get():
            if self.handle_exit_events(event):
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Spawn spark at fighter
                    self._spawn_effect("spark", 4, 4)
                elif event.key == pygame.K_a:
                    # Fighter attack animation
                    self.fighter_animation = "attack"
                    # Start attack animation
                    self.animation_clock.start_animation(
                        "fighter_attack",
                        self.animation_metadata["units"]["fighter"]["attack"],
                    )
                elif event.key == pygame.K_w:
                    # Toggle bandit walk
                    if self.bandit_animation == "idle":
                        self.bandit_animation = "walk"
                    else:
                        self.bandit_animation = "idle"

        # Handle continuous input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.camera_x -= 5
        if keys[pygame.K_RIGHT]:
            self.camera_x += 5
        if keys[pygame.K_UP]:
            self.camera_y -= 5
        if keys[pygame.K_DOWN]:
            self.camera_y += 5

        return True

    def _update_animations(self) -> None:
        """Update animation states."""
        # Check if knight attack is finished
        if self.fighter_animation == "attack" and self.animation_clock.is_animation_finished("fighter_attack"):
            self.fighter_animation = "idle"
            self.animation_clock.clear_animation("fighter_attack")

    def run(self) -> None:
        """Run the demo."""
        print(f"🎮 Starting Units & FX Demo (timeout: {self.timeout_seconds}s)")

        while not self.should_exit():
            # Handle input
            if not self._handle_input():
                break

            # Update
            self._update_animations()
            self._update_effects()

            # Draw
            self.screen.fill((0, 0, 0))

            # Draw layers in order: terrain → units → fx → ui
            self._draw_terrain(self.screen)
            self._draw_units(self.screen)
            self._draw_effects(self.screen)
            self._draw_ui(self.screen)

            # Draw timeout info
            self.draw_timeout_info(self.screen, self.font)

            pygame.display.flip()
            self.clock.tick(60)

        print("👋 Units & FX Demo finished")
        pygame.quit()


def main():
    """Main entry point."""
    demo = UnitsFXDemo()
    demo.run()


if __name__ == "__main__":
    main()
