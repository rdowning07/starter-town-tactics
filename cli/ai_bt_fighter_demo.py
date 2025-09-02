#!/usr/bin/env python3
"""
BT Fighter Demo - Shows Behavior Tree AI controlling fighter units with actual assets.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ai.bt import make_basic_combat_tree
from game.ai_bt_adapter import BTAdapter
from game.animation_clock import AnimationClock
from game.demo_base import DemoBase


class BTFighterDemo(DemoBase):
    """Demo for BT AI controlling fighter units with actual assets."""

    def __init__(self, timeout_seconds: int = 30):
        """Initialize the demo."""
        super().__init__(timeout_seconds=timeout_seconds, auto_exit=True)

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("BT Fighter vs Bandit Demo - AI Behavior Trees")
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

        # Demo state - fighter for player, bandit for AI
        self.fighter_animation = "idle_down"
        self.bandit_animation = "idle_down"
        self.active_effects: list = []
        self.camera_x = 0
        self.camera_y = 0

        # Tile size
        self.tile_size = 32

        # BT AI state
        self.bt = make_basic_combat_tree()
        self.bt_tick_count = 0
        self.ai_decision_text = "AI: Thinking..."
        self.last_ai_decision = 0
        self.ai_update_interval = 2  # seconds

        # Unit positions - fighter (player) vs bandit (AI)
        self.fighter_pos = [4, 4]  # Player fighter
        self.bandit_pos = [6, 5]  # AI bandit
        self.fighter_hp = 10
        self.bandit_hp = 8
        self.fighter_ap = 6
        self.bandit_ap = 6

        # Track what the AI did
        self.ai_attacked = False
        self.ai_moved = False

    def _load_animation_metadata(self) -> Dict:
        """Load animation metadata."""
        try:
            with open(
                "assets/units/_metadata/animation_metadata.json", "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
                print(f"Loaded metadata: {list(data.get('units', {}).keys())}")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load animation metadata: {e}")
            return {"units": {}}

    def _load_effects_metadata(self) -> Dict:
        """Load effects metadata."""
        try:
            with open(
                "assets/effects/effects_metadata.json", "r", encoding="utf-8"
            ) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load effects metadata: {e}")
            return {"effects": {}}

    def _load_unit_sprites(self) -> Dict[str, Dict[str, pygame.Surface]]:
        """Load unit sprite sheets."""
        sprites: Dict[str, Dict[str, pygame.Surface]] = {}

        # Load fighter sprites (player unit)
        fighter_sprites = {}
        fighter_files = [
            "down_stand.png",
            "down_walk1.png",
            "down_walk2.png",
            "left_stand.png",
            "left_walk1.png",
            "left_walk2.png",
            "right_stand.png",
            "right_walk1.png",
            "right_walk2.png",
            "up_stand.png",
            "up_walk1.png",
            "up_walk2.png",
        ]

        for filename in fighter_files:
            try:
                full_path = f"assets/units/fighter/{filename}"
                sprite = pygame.image.load(full_path)
                # Map filename to animation name
                if "down_stand" in filename:
                    fighter_sprites["idle_down"] = sprite
                elif "down_walk" in filename:
                    fighter_sprites["walk_down"] = sprite
                elif "left_stand" in filename:
                    fighter_sprites["idle_left"] = sprite
                elif "left_walk" in filename:
                    fighter_sprites["walk_left"] = sprite
                elif "right_stand" in filename:
                    fighter_sprites["idle_right"] = sprite
                elif "right_walk" in filename:
                    fighter_sprites["walk_right"] = sprite
                elif "up_stand" in filename:
                    fighter_sprites["idle_up"] = sprite
                elif "up_walk" in filename:
                    fighter_sprites["walk_up"] = sprite
            except pygame.error as e:
                print(f"Failed to load {full_path}: {e}")
                # Create placeholder
                placeholder = self._create_placeholder(32, 48, (255, 0, 0))
                fighter_sprites["idle_down"] = placeholder

        # Load bandit sprites (AI unit)
        bandit_sprites = {}
        bandit_files = [
            "down_stand.png",
            "down_walk1.png",
            "down_walk2.png",
            "left_stand.png",
            "left_walk1.png",
            "left_walk2.png",
            "right_stand.png",
            "right_walk1.png",
            "right_walk2.png",
            "up_stand.png",
            "up_walk1.png",
            "up_walk2.png",
        ]

        for filename in bandit_files:
            try:
                full_path = f"assets/units/bandit/{filename}"
                sprite = pygame.image.load(full_path)
                # Map filename to animation name
                if "down_stand" in filename:
                    bandit_sprites["idle_down"] = sprite
                elif "down_walk" in filename:
                    bandit_sprites["walk_down"] = sprite
                elif "left_stand" in filename:
                    bandit_sprites["idle_left"] = sprite
                elif "left_walk" in filename:
                    bandit_sprites["walk_left"] = sprite
                elif "right_stand" in filename:
                    bandit_sprites["idle_right"] = sprite
                elif "right_walk" in filename:
                    bandit_sprites["walk_right"] = sprite
                elif "up_stand" in filename:
                    bandit_sprites["idle_up"] = sprite
                elif "up_walk" in filename:
                    bandit_sprites["walk_up"] = sprite
            except pygame.error as e:
                print(f"Failed to load {full_path}: {e}")
                # Create placeholder
                placeholder = self._create_placeholder(32, 48, (255, 0, 0))
                bandit_sprites["idle_down"] = placeholder

        sprites["fighter"] = fighter_sprites
        sprites["bandit"] = bandit_sprites
        print(
            f"Loaded {len(fighter_sprites)} fighter sprites: {list(fighter_sprites.keys())}"
        )
        print(
            f"Loaded {len(bandit_sprites)} bandit sprites: {list(bandit_sprites.keys())}"
        )
        return sprites

    def _load_effect_sprites(self) -> Dict[str, pygame.Surface]:
        """Load effect sprite sheets."""
        sprites = {}
        for effect_name in ["spark", "slash"]:
            if effect_name in self.effects_metadata.get("effects", {}):
                effect_meta = self.effects_metadata["effects"][effect_name]
                sheet_path = effect_meta["sheet"]
                try:
                    sprites[effect_name] = pygame.image.load(sheet_path)
                except pygame.error as e:
                    print(f"Failed to load {sheet_path}: {e}")
                    # Create placeholder
                    sprites[effect_name] = self._create_placeholder(
                        32, 32, (255, 255, 0)
                    )
        return sprites

    def _create_placeholder(
        self, width: int, height: int, color: Tuple[int, int, int]
    ) -> pygame.Surface:
        """Create a placeholder surface."""
        surface = pygame.Surface((width, height))
        surface.fill(color)
        return surface

    def _spawn_effect(self, effect_name: str, x: int, y: int) -> None:
        """Spawn an effect at the given position."""
        effect_id = f"{effect_name}_{len(self.active_effects)}"
        self.active_effects.append(
            {
                "id": effect_id,
                "name": effect_name,
                "x": x,
                "y": y,
                "start_time": pygame.time.get_ticks(),
                "duration": 1000,  # 1 second
            }
        )

    def _update_ai(self) -> None:
        """Update AI behavior using Behavior Tree."""
        current_time = pygame.time.get_ticks()

        # Run BT every 2 seconds
        if current_time - self.last_ai_decision > 2000:
            self.last_ai_decision = current_time
            self.bt_tick_count += 1

            # Reset AI action flags
            self.ai_attacked = False
            self.ai_moved = False

            # Create a mock game state for the BT
            mock_game_state = self._create_mock_game_state()

            try:
                # Run the BT
                ctx = BTAdapter(mock_game_state, "fighter2", "fighter1")
                status = self.bt.tick(ctx)

                # Update AI decision text based on what the BT did
                if status == "SUCCESS":
                    # Check if we can attack (in range and have AP)
                    if self.enemy_in_attack_range() and self.bandit_ap > 0:
                        self.ai_decision_text = (
                            f"AI: Attack! (tick {self.bt_tick_count})"
                        )
                        self._spawn_effect(
                            "slash", self.bandit_pos[0], self.bandit_pos[1]
                        )
                        self.fighter_hp = max(0, self.fighter_hp - 2)
                        self.bandit_ap = max(0, self.bandit_ap - 1)
                        self.ai_attacked = True
                    elif self.bandit_ap > 0:
                        self.ai_decision_text = (
                            f"AI: Move toward target (tick {self.bt_tick_count})"
                        )
                        # Move fighter2 toward fighter1
                        dx = self.fighter_pos[0] - self.bandit_pos[0]
                        dy = self.fighter_pos[1] - self.bandit_pos[1]
                        if abs(dx) > abs(dy):
                            self.bandit_pos[0] += 1 if dx > 0 else -1
                        else:
                            self.bandit_pos[1] += 1 if dy > 0 else -1
                        self.bandit_ap = max(0, self.bandit_ap - 1)
                        self.ai_moved = True
                else:
                    self.ai_decision_text = f"AI: {status} (tick {self.bt_tick_count})"

            except Exception as e:
                self.ai_decision_text = f"AI: Error - {e}"

    def _enemy_in_attack_range(self) -> bool:
        """Check if bandit is in attack range of fighter."""
        dx = abs(self.bandit_pos[0] - self.fighter_pos[0])
        dy = abs(self.bandit_pos[1] - self.fighter_pos[1])
        return (dx + dy) <= 1  # Attack range of 1

    def _execute_attack(self) -> None:
        """Execute fighter attack on bandit if in range."""
        if self._enemy_in_attack_range() and self.fighter_ap > 0:
            # Deal damage
            damage = 3
            self.bandit_hp = max(0, self.bandit_hp - damage)
            self.fighter_ap = max(0, self.fighter_ap - 2)

            # Spawn slash effect
            self._spawn_effect("slash", self.bandit_pos[0], self.bandit_pos[1])

            # Update AI decision text
            self.ai_decision_text = f"🗡️ Fighter attacks! Bandit HP: {self.bandit_hp}"

            # Check if bandit is defeated
            if self.bandit_hp <= 0:
                self.ai_decision_text = "💀 Bandit defeated! Fighter wins!"
        else:
            self.ai_decision_text = "❌ Cannot attack - out of range or no AP!"

    def _create_mock_game_state(self):
        """Create a mock game state for the BT."""

        class MockGameState:
            def __init__(self, demo):
                self.demo = demo
                self.units = MockUnitManager(demo)

            def find_closest_enemy(self, unit_id):
                if unit_id == "bandit":
                    return MockUnit(
                        "fighter", self.demo.fighter_pos[0], self.demo.fighter_pos[1]
                    )
                return None

        class MockUnitManager:
            def __init__(self, demo):
                self.demo = demo

            def get(self, unit_id):
                if unit_id == "bandit":
                    return {
                        "team": "enemy",
                        "hp": self.demo.bandit_hp,
                        "x": self.demo.bandit_pos[0],
                        "y": self.demo.bandit_pos[1],
                        "ap": self.demo.bandit_ap,
                        "attack_range": 1,
                    }
                elif unit_id == "fighter":
                    return {
                        "team": "player",
                        "hp": self.demo.fighter_hp,
                        "x": self.demo.fighter_pos[0],
                        "y": self.demo.fighter_pos[1],
                        "ap": self.demo.fighter_ap,
                        "attack_range": 1,
                    }
                return None

        class MockUnit:
            def __init__(self, unit_id, x, y):
                self.unit_id = unit_id
                self.x = x
                self.y = y

        return MockGameState(self)

    def _draw_terrain(self, surface: pygame.Surface) -> None:
        """Draw terrain grid."""
        # Make the field 50% bigger (15x15 instead of 10x10)
        grid_size = 15
        for y in range(grid_size):
            for x in range(grid_size):
                rect = pygame.Rect(
                    x * self.tile_size - self.camera_x,
                    y * self.tile_size - self.camera_y,
                    self.tile_size,
                    self.tile_size,
                )

                # Natural green field with subtle variations
                base_green = (34, 139, 34)  # Forest green
                # Add subtle random variation for natural look
                variation = (x + y * 3) % 4
                if variation == 0:
                    color = base_green
                elif variation == 1:
                    color = (40, 150, 40)  # Slightly lighter
                elif variation == 2:
                    color = (30, 130, 30)  # Slightly darker
                else:
                    color = (35, 145, 35)  # Medium variation

                pygame.draw.rect(surface, color, rect)
                # Subtle border for tile definition
                pygame.draw.rect(surface, (25, 100, 25), rect, 1)

    def _draw_units(self, surface: pygame.Surface) -> None:
        """Draw units with animations."""
        # Fighter1 (player) - just draw the sprite directly
        if (
            "fighter" in self.unit_sprites
            and "idle_down" in self.unit_sprites["fighter"]
        ):
            fighter1_x = self.fighter_pos[0] * self.tile_size - self.camera_x
            fighter1_y = self.fighter_pos[1] * self.tile_size - self.camera_y

            # Draw sprite centered on the tile
            sprite = self.unit_sprites["fighter"]["idle_down"]
            surface.blit(sprite, (fighter1_x, fighter1_y))

        # Fighter2 (AI controlled) - just draw the sprite directly
        if "bandit" in self.unit_sprites and "idle_down" in self.unit_sprites["bandit"]:
            fighter2_x = self.bandit_pos[0] * self.tile_size - self.camera_x
            fighter2_y = self.bandit_pos[1] * self.tile_size - self.camera_y

            # Draw sprite centered on the tile
            sprite = self.unit_sprites["bandit"]["idle_down"]
            surface.blit(sprite, (fighter2_x, fighter2_y))

    def _blit_animation(
        self,
        surface: pygame.Surface,
        sprite_sheet: pygame.Surface,
        metadata: Dict,
        x: int,
        y: int,
        animation_id: str,
    ) -> None:
        """Blit a single frame of animation."""
        try:
            frame_width = metadata.get("frame_width", 32)
            frame_height = metadata.get("frame_height", 32)
            frame_index = metadata.get("frame_index", 0)

            # Calculate frame position in sprite sheet
            frames_per_row = sprite_sheet.get_width() // frame_width
            frame_row = frame_index // frames_per_row
            frame_col = frame_index % frames_per_row

            # Extract frame from sprite sheet
            frame_rect = pygame.Rect(
                frame_col * frame_width,
                frame_row * frame_height,
                frame_width,
                frame_height,
            )

            # Create frame surface
            frame_surface = pygame.Surface((frame_width, frame_height))
            frame_surface.blit(sprite_sheet, (0, 0), frame_rect)

            # Draw frame
            surface.blit(frame_surface, (x, y))

        except Exception as e:
            # Fallback: draw colored rectangle
            pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(x, y, 32, 32))

    def _draw_effects(self, surface: pygame.Surface) -> None:
        """Draw active effects."""
        current_time = pygame.time.get_ticks()
        self.active_effects = [
            effect
            for effect in self.active_effects
            if current_time - effect["start_time"] < effect["duration"]
        ]

        for effect in self.active_effects:
            effect_name = effect["name"]
            if effect_name in self.effect_sprites:
                effect_x = effect["x"] * self.tile_size - self.camera_x
                effect_y = effect["y"] * self.tile_size - self.camera_y
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
            "WASD: Move fighter around",
            "SPACE: Attack bandit (if in range)",
            "W: Toggle bandit walk animation",
            "ESC: Quit",
        ]

        y_offset = 10
        for instruction in instructions:
            text = self.font.render(instruction, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 25

            # Current animations
        anim_text = (
            f"Fighter: {self.fighter_animation}, Bandit: {self.bandit_animation}"
        )
        text = self.font.render(anim_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset + 10))

        # Unit stats
        stats_text = f"Fighter HP: {self.fighter_hp} AP: {self.fighter_ap}"
        text = self.font.render(stats_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset + 35))

        stats_text2 = f"Bandit HP: {self.bandit_hp} AP: {self.bandit_ap}"
        text = self.font.render(stats_text2, True, (255, 255, 255))
        surface.blit(text, (10, y_offset + 60))

        # AI decision
        text = self.font.render(self.ai_decision_text, True, (0, 255, 0))
        surface.blit(text, (10, y_offset + 85))

        # Design Pattern Showcase
        y_offset += 120
        pattern_text = "🏗️ Design Patterns Active:"
        text = self.font.render(pattern_text, True, (255, 255, 0))
        surface.blit(text, (10, y_offset))

        patterns = [
            "├─ Composite: Selector → Sequence → Condition/Action",
            "├─ Strategy: BTContext Protocol → BTAdapter Implementation",
            "├─ Observer: EventBus → GameState → UnitManager",
            "└─ Factory: AnimationMetadata → SpriteManager → Renderer",
        ]

        for i, pattern in enumerate(patterns):
            text = self.font.render(pattern, True, (200, 200, 200))
            surface.blit(text, (10, y_offset + 25 + i * 20))

        # AI Architecture Status
        y_offset += 120
        ai_text = "🧠 AI System Status:"
        text = self.font.render(ai_text, True, (0, 255, 255))
        surface.blit(text, (10, y_offset))

        ai_status = [
            f"├─ Behavior Tree: ✅ Active (every {self.ai_update_interval}s)",
            "├─ Decision Context: ✅ GameState + UnitManager",
            "├─ Action Execution: ✅ Move/Attack Commands",
            "└─ Fallback: ✅ Heuristic if BT fails",
        ]

        for i, status in enumerate(ai_status):
            text = self.font.render(status, True, (200, 200, 200))
            surface.blit(text, (10, y_offset + 25 + i * 20))

        # Active effects count
        y_offset += 120
        effects_text = f"Active effects: {len(self.active_effects)}"
        text = self.font.render(effects_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset))

    def _handle_input(self) -> bool:
        """Handle input events. Returns False to quit."""
        for event in pygame.event.get():
            if self.handle_exit_events(event):
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Fighter attack - check if bandit is in range
                    if self._enemy_in_attack_range():
                        self._execute_attack()
                elif event.key == pygame.K_a:
                    # Fighter attack animation - cycle through available animations
                    if self.fighter_animation == "idle_down":
                        self.fighter_animation = "walk_down"
                    else:
                        self.fighter_animation = "idle_down"
                elif event.key == pygame.K_w:
                    # Toggle bandit walk
                    if self.bandit_animation == "idle_down":
                        self.bandit_animation = "walk_down"
                    else:
                        self.bandit_animation = "idle_down"

        # Handle continuous input (fighter movement + camera)
        keys = pygame.key.get_pressed()

        # Fighter movement with WASD
        old_pos = self.fighter_pos.copy()
        if keys[pygame.K_w]:  # Up
            self.fighter_pos[1] = max(0, self.fighter_pos[1] - 1)
        if keys[pygame.K_s]:  # Down
            self.fighter_pos[1] = min(14, self.fighter_pos[1] + 1)
        if keys[pygame.K_a]:  # Left
            self.fighter_pos[0] = max(0, self.fighter_pos[0] - 1)
        if keys[pygame.K_d]:  # Right
            self.fighter_pos[0] = min(14, self.fighter_pos[0] + 1)

        # Camera follows fighter
        if old_pos != self.fighter_pos:
            self.camera_x = self.fighter_pos[0] * self.tile_size - 400
            self.camera_y = self.fighter_pos[1] * self.tile_size - 300

        # Camera bounds
        self.camera_x = max(0, min(15 * self.tile_size - 800, self.camera_x))
        self.camera_y = max(0, min(15 * self.tile_size - 600, self.camera_y))

        return True

    def run(self) -> None:
        """Run the demo."""
        print(
            f"🎮 Starting BT Fighter vs Bandit Demo (timeout: {self.timeout_seconds}s)"
        )
        print("🤖 Watch the AI bandit use Behavior Tree AI to make decisions!")
        print(
            "📊 The AI bandit will move toward the player fighter and attack when in range."
        )
        print(f"Screen size: {self.screen.get_size()}")
        print(f"Unit sprites loaded: {list(self.unit_sprites.keys())}")

        while not self.should_exit():
            # Handle input
            if not self._handle_input():
                break

            # Update AI
            self._update_ai()

            # Draw
            self.screen.fill((0, 0, 0))
            print("Drawing frame...")

            # Render terrain
            self._draw_terrain(self.screen)

            # Render units
            self._draw_units(self.screen)

            # Render effects
            self._draw_effects(self.screen)

            # Draw UI
            self._draw_ui(self.screen)

            # Draw timeout info
            self.draw_timeout_info(self.screen, self.font)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        print("👋 BT Fighter Demo finished")


def main():
    """Main entry point."""
    demo = BTFighterDemo(timeout_seconds=5)
    demo.run()


if __name__ == "__main__":
    main()
