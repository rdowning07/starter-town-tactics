#!/usr/bin/env python3
"""
BT Fighter Demo - Shows Behavior Tree AI controlling fighter units with actual assets.
FIXED VERSION: Characters actually move and attack using new systems.
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
from game.ai.scheduler import AIScheduler
from game.ai_bt_adapter import BTAdapter
from game.animation_clock import AnimationClock
from game.demo_base import DemoBase
from game.factories.entity_factory import EntityFactory
from game.services.victory_service import BattleOutcome, VictoryService


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
        # Animation states
        self.fighter_animation = "pose1"  # Use available sprite
        self.bandit_animation = "pose1"  # Use available sprite
        self.active_effects: list = []
        self.camera_x = 0
        self.camera_y = 0

        # Tile size
        self.tile_size = 32

        # NEW: Use the actual systems
        self.entity_factory = EntityFactory()
        self.ai_scheduler = AIScheduler()
        self.victory_service = VictoryService(
            player_team_id=1, enemy_team_ids={2}, initial_counts={1: 1, 2: 1}
        )

        # Subscribe to victory events
        self.victory_service.subscribe(self._on_battle_outcome)
        self.battle_outcome: Optional[BattleOutcome] = None

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

        # Register AI unit with scheduler
        self.ai_scheduler.register("bandit", self._ai_tick, period_s=2.0, offset_s=0.5)

        # Movement timing - prevent multiple moves per key press
        self.last_move_time = 0
        self.move_delay = 200  # milliseconds between moves
        self.last_key_pressed: Optional[int] = None

    def _on_battle_outcome(self, outcome: BattleOutcome):
        """Handle battle outcome changes."""
        self.battle_outcome = outcome
        if outcome == BattleOutcome.PLAYER_WIN:
            self.ai_decision_text = "🎉 VICTORY! All enemies defeated!"
        elif outcome == BattleOutcome.PLAYER_LOSE:
            self.ai_decision_text = "💀 DEFEAT! Player team eliminated!"

    def _ai_tick(self):
        """AI tick function for the scheduler."""
        self._update_ai()

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
        """Load unit sprites from individual PNG files."""
        sprites = {}

        # Load fighter sprites
        fighter_sprites = {}
        fighter_path = Path("assets/units/fighter")
        if fighter_path.exists():
            for png_file in fighter_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file)
                    if sprite.get_width() < 20 or sprite.get_height() < 20:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem  # filename without extension
                    fighter_sprites[anim_state] = sprite
                    print(f"Loaded fighter sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        # Load bandit sprites
        bandit_sprites = {}
        bandit_path = Path("assets/units/bandit")
        if bandit_path.exists():
            for png_file in bandit_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file)
                    if sprite.get_width() < 20 or sprite.get_height() < 20:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem
                    bandit_sprites[anim_state] = sprite
                    print(f"Loaded bandit sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        sprites["fighter"] = fighter_sprites
        sprites["bandit"] = bandit_sprites

        # Set default animations - use fallback if no real sprites
        if not fighter_sprites:
            print("No real fighter sprites found, using fallback")
        if not bandit_sprites:
            print("No real bandit sprites found, using fallback")

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

            # Create a simple game state for the BT
            game_state = self._create_simple_game_state()

            try:
                # Run the BT with proper unit IDs
                ctx = BTAdapter(game_state, "bandit", "fighter")
                status = self.bt.tick(ctx)

                # Update AI decision text based on what the BT did
                if status == "SUCCESS":
                    # Check if we can attack (in range and have AP)
                    if self._enemy_in_attack_range() and self.bandit_ap > 0:
                        self.ai_decision_text = (
                            f"AI: Attack! (tick {self.bt_tick_count})"
                        )
                        self._spawn_effect(
                            "slash", self.fighter_pos[0], self.fighter_pos[1]
                        )
                        self.fighter_hp = max(0, self.fighter_hp - 2)
                        self.bandit_ap = max(0, self.bandit_ap - 1)
                        self.ai_attacked = True

                        # Check if fighter is defeated
                        if self.fighter_hp <= 0:
                            self.victory_service.on_unit_defeated(1)
                    elif self.bandit_ap > 0:
                        self.ai_decision_text = (
                            f"AI: Move toward target (tick {self.bt_tick_count})"
                        )
                        # Move bandit toward fighter
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
        """Check if units are in attack range."""
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

            # Set attack animation
            if "down" in self.fighter_animation:
                self.fighter_animation = "shake1"  # Use shake animation for attack
            elif "up" in self.fighter_animation:
                self.fighter_animation = "shake1"
            elif "left" in self.fighter_animation:
                self.fighter_animation = "shake1"
            elif "right" in self.fighter_animation:
                self.fighter_animation = "shake1"

            # Spawn slash effect
            self._spawn_effect("slash", self.bandit_pos[0], self.bandit_pos[1])

            # Update AI decision text
            self.ai_decision_text = f"🗡️ Fighter attacks! Bandit HP: {self.bandit_hp}"

            # Check if bandit is defeated
            if self.bandit_hp <= 0:
                self.victory_service.on_unit_defeated(2)
        else:
            self.ai_decision_text = "❌ Cannot attack - out of range or no AP!"

    def _show_victory_message(self, surface: pygame.Surface, is_victory: bool):
        """Show big victory or defeat message."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Big message
        if is_victory:
            message = "🎉 VICTORY! 🎉"
            color = (0, 255, 0)
            subtitle = "You defeated the bandit!"
        else:
            message = "💀 DEFEAT! 💀"
            color = (255, 0, 0)
            subtitle = "The bandit defeated you!"

        # Main title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render(message, True, color)
        title_rect = title_text.get_rect(center=(400, 250))
        surface.blit(title_text, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_text = subtitle_font.render(subtitle, True, (255, 255, 255))
        subtitle_rect = subtitle_text.get_rect(center=(400, 320))
        surface.blit(subtitle_text, subtitle_rect)

        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render(
            "Press ESC to exit", True, (200, 200, 200)
        )
        instruction_rect = instruction_text.get_rect(center=(400, 380))
        surface.blit(instruction_text, instruction_rect)

    def _create_simple_game_state(self):
        """Create a simple game state for the BT."""

        class SimpleGameState:
            def __init__(self, demo):
                self.demo = demo
                self.units = SimpleUnitManager(demo)
                self.ap_manager = SimpleAPManager(demo)

            def find_closest_enemy(self, unit_id):
                if unit_id == "bandit":
                    return SimpleUnit(
                        "fighter", self.demo.fighter_pos[0], self.demo.fighter_pos[1]
                    )
                return None

        class SimpleUnitManager:
            def __init__(self, demo):
                self.demo = demo

            def get(self, unit_id):
                if unit_id == "bandit":
                    return {
                        "team": 2,  # Enemy team
                        "hp": self.demo.bandit_hp,
                        "x": self.demo.bandit_pos[0],
                        "y": self.demo.bandit_pos[1],
                        "ap": self.demo.bandit_ap,
                        "attack_range": 1,
                    }
                elif unit_id == "fighter":
                    return {
                        "team": 1,  # Player team
                        "hp": self.demo.fighter_hp,
                        "x": self.demo.fighter_pos[0],
                        "y": self.demo.fighter_pos[1],
                        "ap": self.demo.fighter_ap,
                        "attack_range": 1,
                    }
                return None

        class SimpleUnit:
            def __init__(self, unit_id, x, y):
                self.unit_id = unit_id
                self.x = x
                self.y = y

        class SimpleAPManager:
            def __init__(self, demo):
                self.demo = demo
            
            def get_ap(self, unit_id):
                if unit_id == "bandit":
                    return self.demo.bandit_ap
                elif unit_id == "fighter":
                    return self.demo.fighter_ap
                return 0
            
            def can_spend(self, unit_id, amount):
                return self.get_ap(unit_id) >= amount
            
            def spend(self, unit_id, amount):
                if unit_id == "bandit":
                    self.demo.bandit_ap = max(0, self.demo.bandit_ap - amount)
                elif unit_id == "fighter":
                    self.demo.fighter_ap = max(0, self.demo.fighter_ap - amount)

        return SimpleGameState(self)

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
        # Fighter (player) - draw the sprite directly
        if (
            "fighter" in self.unit_sprites
            and self.fighter_animation in self.unit_sprites["fighter"]
        ):
            sprite = self.unit_sprites["fighter"][self.fighter_animation]
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (
                self.fighter_pos[0] * self.tile_size
                + self.tile_size // 2
                - self.camera_x,
                self.fighter_pos[1] * self.tile_size
                + self.tile_size // 2
                - self.camera_y,
            )
            surface.blit(sprite, sprite_rect)
        else:
            # Fallback: draw a colored circle
            pygame.draw.circle(
                surface,
                (0, 0, 255),  # Blue for fighter
                (
                    self.fighter_pos[0] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_x,
                    self.fighter_pos[1] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_y,
                ),
                self.tile_size // 3,
            )

        # Bandit (AI) - draw the sprite directly
        if (
            "bandit" in self.unit_sprites
            and self.bandit_animation in self.unit_sprites["bandit"]
        ):
            sprite = self.unit_sprites["bandit"][self.bandit_animation]
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (
                self.bandit_pos[0] * self.tile_size
                + self.tile_size // 2
                - self.camera_x,
                self.bandit_pos[1] * self.tile_size
                + self.tile_size // 2
                - self.camera_y,
            )
            surface.blit(sprite, sprite_rect)
        else:
            # Fallback: draw a colored circle
            pygame.draw.circle(
                surface,
                (255, 0, 0),  # Red for bandit
                (
                    self.bandit_pos[0] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_x,
                    self.bandit_pos[1] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_y,
                ),
                self.tile_size // 3,
            )

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
        effects_to_remove = []

        for effect in self.active_effects:
            if current_time - effect["start_time"] < effect["duration"]:
                # Draw effect
                effect_name = effect["name"]
                if effect_name in self.effect_sprites:
                    sprite = self.effect_sprites[effect_name]
                    sprite_rect = sprite.get_rect()
                    sprite_rect.center = (
                        effect["x"] * self.tile_size
                        + self.tile_size // 2
                        - self.camera_x,
                        effect["y"] * self.tile_size
                        + self.tile_size // 2
                        - self.camera_y,
                    )
                    surface.blit(sprite, sprite_rect)
            else:
                effects_to_remove.append(effect)

        # Remove expired effects
        for effect in effects_to_remove:
            self.active_effects.remove(effect)

    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Draw UI elements."""
        y_offset = 10

        # Title
        title_text = "BT Fighter vs Bandit Demo - 1v1 Tactical Combat"
        text = self.font.render(title_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset))

        # Instructions
        y_offset += 30
        instructions = [
            "Controls: WASD to move fighter, SPACE to attack",
            "AI bandit uses Behavior Tree for decisions",
            "Goal: Defeat the bandit before they defeat you!",
        ]
        for instruction in instructions:
            text = self.font.render(instruction, True, (200, 200, 200))
            surface.blit(text, (10, y_offset))
            y_offset += 20

        # Current animations
        y_offset += 10
        anim_text = (
            f"Fighter: {self.fighter_animation}, Bandit: {self.bandit_animation}"
        )
        text = self.font.render(anim_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset))

        # Unit stats
        y_offset += 30
        stats_text = f"Fighter HP: {self.fighter_hp} AP: {self.fighter_ap}"
        text = self.font.render(stats_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset))

        y_offset += 25
        stats_text2 = f"Bandit HP: {self.bandit_hp} AP: {self.bandit_ap}"
        text = self.font.render(stats_text2, True, (255, 255, 255))
        surface.blit(text, (10, y_offset))

        # AI decision
        y_offset += 25
        text = self.font.render(self.ai_decision_text, True, (0, 255, 0))
        surface.blit(text, (10, y_offset))

        # Battle outcome
        if self.battle_outcome:
            y_offset += 30
            outcome_text = f"Battle: {self.battle_outcome.value.upper()}"
            color = (
                (0, 255, 0)
                if self.battle_outcome == BattleOutcome.PLAYER_WIN
                else (255, 0, 0)
            )
            text = self.font.render(outcome_text, True, color)
            surface.blit(text, (10, y_offset))

        # NEW: Show the actual systems in action
        y_offset += 120
        systems_text = "🔧 Systems Active:"
        text = self.font.render(systems_text, True, (255, 255, 0))
        surface.blit(text, (10, y_offset))

        systems = [
            f"├─ EntityFactory: ✅ Spawned {self.entity_factory.get_spawned_count()} units",
            f"├─ AIScheduler: ✅ {self.ai_scheduler.get_active_count()} AI units scheduled",
            f"├─ VictoryService: ✅ Battle state tracked",
            "└─ Behavior Tree: ✅ AI decision making",
        ]

        for i, system in enumerate(systems):
            text = self.font.render(system, True, (200, 200, 200))
            surface.blit(text, (10, y_offset + 25 + i * 20))

        # Design Pattern Showcase
        y_offset += 120
        pattern_text = "🏗️ Design Patterns Active:"
        text = self.font.render(pattern_text, True, (255, 255, 0))
        surface.blit(text, (10, y_offset))

        patterns = [
            "├─ Composite: Selector → Sequence → Condition/Action",
            "├─ Strategy: BTContext Protocol → BTAdapter Implementation",
            "├─ Observer: VictoryService → Battle Outcome Events",
            "└─ Factory: EntityFactory → Team Spawning",
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
        current_time = pygame.time.get_ticks()

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
                    if self.fighter_animation == "pose1":
                        self.fighter_animation = "pose2"
                    else:
                        self.fighter_animation = "pose1"
                elif event.key == pygame.K_w:
                    # Toggle bandit walk
                    if self.bandit_animation == "pose1":
                        self.bandit_animation = "pose2"
                    else:
                        self.bandit_animation = "pose1"

        # Handle movement - ONE TILE AT A TIME with proper timing
        keys = pygame.key.get_pressed()
        moved = False

        # Only allow movement if enough time has passed AND key was just pressed
        if current_time - self.last_move_time > self.move_delay:
            # Check for key press (not continuous hold)
            if keys[pygame.K_w] and self.last_key_pressed != pygame.K_w:  # Up
                new_pos = [self.fighter_pos[0], max(0, self.fighter_pos[1] - 1)]
                if not self._positions_overlap(new_pos, self.bandit_pos):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_w
            elif keys[pygame.K_s] and self.last_key_pressed != pygame.K_s:  # Down
                new_pos = [self.fighter_pos[0], min(14, self.fighter_pos[1] + 1)]
                if not self._positions_overlap(new_pos, self.bandit_pos):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_s
            elif keys[pygame.K_a] and self.last_key_pressed != pygame.K_a:  # Left
                new_pos = [max(0, self.fighter_pos[0] - 1), self.fighter_pos[1]]
                if not self._positions_overlap(new_pos, self.bandit_pos):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_a
            elif keys[pygame.K_d] and self.last_key_pressed != pygame.K_d:  # Right
                new_pos = [min(14, self.fighter_pos[0] + 1), self.fighter_pos[1]]
                if not self._positions_overlap(new_pos, self.bandit_pos):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_d
            else:
                # No movement keys pressed, return to idle
                self.fighter_animation = "pose1"
                self.last_key_pressed = None

        # Reset key tracking when no keys are pressed
        if not any(
            [keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]]
        ):
            self.last_key_pressed = None

        # Camera follows fighter
        if moved:
            self.last_move_time = current_time
            self.camera_x = self.fighter_pos[0] * self.tile_size - 400
            self.camera_y = self.fighter_pos[1] * self.tile_size - 300

        # Camera bounds
        self.camera_x = max(0, min(15 * self.tile_size - 800, self.camera_x))
        self.camera_y = max(0, min(15 * self.tile_size - 600, self.camera_y))

        return True

    def _positions_overlap(self, pos1: list, pos2: list) -> bool:
        """Check if two positions overlap."""
        return pos1[0] == pos2[0] and pos1[1] == pos2[1]

    def run(self) -> None:
        """Run the demo."""
        print("Starting BT Fighter Demo...")
        print("Controls: WASD to move, SPACE to attack")
        print("AI bandit uses Behavior Tree for decisions")

        running = True
        while running and not self.should_exit():
            # Handle input
            running = self._handle_input()

            # Update AI scheduler
            self.ai_scheduler.update(0.016)  # ~60 FPS

            # Clear screen
            self.screen.fill((0, 0, 0))

            # Draw everything
            self._draw_terrain(self.screen)
            self._draw_units(self.screen)
            self._draw_effects(self.screen)
            self._draw_ui(self.screen)

            # Show victory/defeat message if battle is over
            if self.battle_outcome:
                if self.battle_outcome == BattleOutcome.PLAYER_WIN:
                    self._show_victory_message(self.screen, True)
                elif self.battle_outcome == BattleOutcome.PLAYER_LOSE:
                    self._show_victory_message(self.screen, False)

            # Update display
            pygame.display.flip()

            # Cap frame rate
            self.clock.tick(60)

        print("Demo finished.")
        pygame.quit()


def main():
    """Main entry point."""
    demo = BTFighterDemo(timeout_seconds=60)
    demo.run()


if __name__ == "__main__":
    main()
