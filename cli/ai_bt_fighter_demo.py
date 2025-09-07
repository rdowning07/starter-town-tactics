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
from game.effects.screen_effects import ScreenEffects
from game.factories.entity_factory import EntityFactory
from game.services.victory_service import GameOutcome, VictoryService
from game.ui.banners import CutInText, TurnBanner, VictoryBanner
from game.ui.control_card import ControlCard
from game.ui.health_and_ko import HealthAndKOOverlay
from game.ui.roster_panel import RosterPanel


class BTFighterDemo(DemoBase):
    """Demo for BT AI controlling fighter units with actual assets."""

    def __init__(self, timeout_seconds: int = 0):
        """Initialize the demo."""
        super().__init__(timeout_seconds=timeout_seconds, auto_exit=False)

        pygame.init()
        # Screen size: (width, height) - change these values to make screen larger
        self.screen = pygame.display.set_mode((1200, 800))  # Larger screen: 1200x800
        pygame.display.set_caption("BT Fighter vs Bandit Demo - AI Behavior Trees")
        print(f"Display initialized: {self.screen.get_size()}")
        print("Window should be visible now!")
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

        # Demo state - fighter for player, multiple bandits for AI, black mage for ranged testing
        self.fighter_animation = "pose1"  # Use available sprite
        self.mage_animation = "pose1"  # Use available sprite
        self.healer_animation = "pose1"  # Use available sprite
        self.ranger_animation = "pose1"  # Use available sprite

        # Multiple bandits using same sprites
        self.bandit_animations = [
            "pose1",
            "pose2",
            "pose3",
            "pose1",
        ]  # Cycle through poses

        # Add mage position and stats
        self.mage_pos = [7, 7]  # Position mage between fighter and bandit
        self.mage_hp = 15
        self.mage_ap = 3
        self.mage_attack_range = 3  # Ranged attacks!

        # Add healer position and stats
        self.healer_pos = [8, 7]  # Position healer next to mage
        self.healer_hp = 12
        self.healer_ap = 4
        self.healer_heal_range = 2  # Healing range

        # Add ranger position and stats
        self.ranger_pos = [9, 7]  # Position ranger next to healer
        self.ranger_hp = 14
        self.ranger_ap = 3
        self.ranger_attack_range = 2  # Medium range attacks
        self.ranger_ap_regen = 1  # Regenerate 1 AP per tick

        # Projectile system for flying fireballs
        self.active_projectiles: list = []

        self.active_effects: list = []
        self.camera_x = 0
        self.camera_y = -2  # Moved up by 2 pixels

        # Tile size
        self.tile_size = 48  # Larger tiles and characters (was 32)

        # NEW: Use the actual systems
        self.entity_factory = EntityFactory()
        self.ai_scheduler = AIScheduler()
        self.victory_service = VictoryService(
            player_team_id=1, enemy_team_ids={2}, alive_by_team={1: 4, 2: 4}
        )

        # Subscribe to victory events
        self.victory_service.subscribe(self._on_battle_outcome)
        self.battle_outcome: Optional[GameOutcome] = None

        # BT AI state
        self.bt = make_basic_combat_tree()
        self.bt_tick_count = 0
        self.ai_decision_text = "AI: Thinking..."
        self.last_ai_decision = 0

        # UI Components
        self.health_overlay = HealthAndKOOverlay()
        self.victory_banner = VictoryBanner()
        self.turn_banner = TurnBanner()
        self.cutin_text = CutInText()
        self.control_card = ControlCard()
        self.roster_panel = RosterPanel()
        self.screen_effects = ScreenEffects()

        # Camera shake offset
        self.camera_shake_x = 0.0
        self.camera_shake_y = 0.0
        self.ai_update_interval = 2  # seconds

        # Unit positions - fighter (player) vs bandit (AI)
        self.fighter_pos = [4, 4]  # Player fighter
        self.fighter_hp = 30  # 3x HP
        self.fighter_ap = 6

        # 4 Bandits (AI opponents) - spread them out
        self.bandit_positions = [
            [6, 5],  # Bandit 1
            [8, 3],  # Bandit 2
            [5, 8],  # Bandit 3
            [9, 6],  # Bandit 4
        ]
        self.bandit_hp = [8, 8, 8, 8]  # HP for each bandit
        self.bandit_ap = [6, 6, 6, 6]  # AP for each bandit

        # Track what the AI did
        self.ai_attacked = False
        self.ai_moved = False

        # Movement timing - prevent multiple moves per key press
        self.last_move_time = 0
        self.move_delay = 200  # milliseconds between moves
        self.last_key_pressed: int = 0

        # AI decision timing
        self.last_ai_decision = 0
        self.last_mage_decision = 0
        self.last_healer_decision = 0
        self.last_bandit_decision = 0
        self.last_ranger_decision = 0
        self.last_ranger_ap_regen = 0
        self.last_fighter_ai_decision = 0  # Separate timer for AP regeneration
        self.bt_tick_count = 0

        # Register AI unit with scheduler (slowed down 3x)
        self.ai_scheduler.register("bandit", self._ai_tick, period_s=6.0, offset_s=1.5)

    def _on_battle_outcome(self, outcome: GameOutcome):
        """Handle battle outcome changes."""
        self.battle_outcome = outcome
        if outcome == GameOutcome.VICTORY:
            self.ai_decision_text = "🎉 VICTORY! All enemies defeated!"
            self.victory_banner.show_victory()
            self.screen_effects.unit_defeated(8.0)  # Strong effect for victory
        elif outcome == GameOutcome.DEFEAT:
            self.ai_decision_text = "💀 DEFEAT! Player team eliminated!"
            self.victory_banner.show_defeat()
            self.screen_effects.unit_defeated(8.0)  # Strong effect for defeat

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

        # Load black mage sprites
        mage_sprites = {}
        mage_path = Path("assets/units/black_mage")
        if mage_path.exists():
            for png_file in mage_path.glob("*.png"):
                try:
                    sprite = pygame.image.load(str(png_file))
                    # Check if sprite is too small (stub file) - lower threshold for mage
                    if sprite.get_width() < 15 or sprite.get_height() < 15:
                        print(
                            f"Skipping stub sprite: {png_file.name} ({sprite.get_width()}x{sprite.get_height()})"
                        )
                        continue

                    # Map filename to animation state
                    anim_state = png_file.stem
                    mage_sprites[anim_state] = sprite
                    print(f"Loaded mage sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        # Load white mage sprites
        healer_sprites = {}
        healer_path = Path("assets/units/white_mage")
        if healer_path.exists():
            for png_file in healer_path.glob("*.png"):
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
                    healer_sprites[anim_state] = sprite
                    print(f"Loaded healer sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        # Load ranger sprites
        ranger_sprites = {}
        ranger_path = Path("assets/units/ranger")
        if ranger_path.exists():
            for png_file in ranger_path.glob("*.png"):
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
                    ranger_sprites[anim_state] = sprite
                    print(f"Loaded ranger sprite: {anim_state}")
                except pygame.error as e:
                    print(f"Failed to load {png_file}: {e}")

        sprites["fighter"] = fighter_sprites
        sprites["bandit"] = bandit_sprites
        sprites["mage"] = mage_sprites
        sprites["healer"] = healer_sprites
        sprites["ranger"] = ranger_sprites

        # Set default animations - use fallback if no real sprites
        if not fighter_sprites:
            print("No real fighter sprites found, using fallback")
        if not bandit_sprites:
            print("No real bandit sprites found, using fallback")

        return sprites

    def _load_effect_sprites(self) -> Dict[str, pygame.Surface]:
        """Load effect sprite sheets and slice them into frames."""
        sprites = {}
        for effect_name in ["spark", "slash"]:
            if effect_name in self.effects_metadata.get("effects", {}):
                effect_meta = self.effects_metadata["effects"][effect_name]
                sheet_path = effect_meta["sheet"]
                try:
                    # Load the sprite sheet with alpha channel preserved
                    sheet = pygame.image.load(sheet_path).convert_alpha()
                    frame_width = effect_meta["frame_size"][0]
                    frame_height = effect_meta["frame_size"][1]
                    frames = effect_meta["frames"]

                    # Extract the first frame with transparency
                    first_frame = pygame.Surface(
                        (frame_width, frame_height), pygame.SRCALPHA
                    )
                    first_frame.blit(sheet, (0, 0), (0, 0, frame_width, frame_height))
                    sprites[effect_name] = first_frame

                    print(
                        f"Loaded {effect_name} effect: {frame_width}x{frame_height}, {frames} frames"
                    )
                except pygame.error as e:
                    print(f"Failed to load {sheet_path}: {e}")
                    # Create placeholder
                    sprites[effect_name] = self._create_placeholder(
                        32, 32, (255, 255, 0, 128)  # Semi-transparent yellow
                    )
        return sprites

    def _create_placeholder(
        self, width: int, height: int, color: Tuple[int, int, int, int]
    ) -> pygame.Surface:
        """Create a placeholder surface with transparency."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)
        return surface

    def _create_fireball_effect(self, size: int = 32) -> pygame.Surface:
        """Create a simple fireball effect for mage attacks."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Create a glowing fireball effect
        center = size // 2
        radius = size // 3

        # Outer glow (orange)
        for r in range(radius + 4, radius - 1, -1):
            alpha = max(0, 255 - (r - radius) * 50)
            color = (255, 165, 0, alpha)  # Orange with fade
            pygame.draw.circle(surface, color, (center, center), r)

        # Core fireball (red-yellow)
        pygame.draw.circle(
            surface, (255, 255, 0, 200), (center, center), radius - 2
        )  # Yellow core
        pygame.draw.circle(
            surface, (255, 100, 0, 255), (center, center), radius - 4
        )  # Red center

        return surface

    def _create_healing_effect(self, size: int = 32) -> pygame.Surface:
        """Create a simple healing effect for healer spells."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Create a glowing ethereal healing effect
        center = size // 2
        radius = size // 3

        # Outer glow (soft white-blue)
        for r in range(radius + 6, radius - 1, -1):
            alpha = max(0, 180 - (r - radius) * 30)
            color = (200, 220, 255, alpha)  # Soft white-blue with fade
            pygame.draw.circle(surface, color, (center, center), r)

        # Middle glow (pure white)
        pygame.draw.circle(
            surface, (255, 255, 255, 150), (center, center), radius
        )  # White glow

        # Core healing (bright white)
        pygame.draw.circle(
            surface, (255, 255, 255, 255), (center, center), radius - 3
        )  # Bright white core

        # Inner sparkle (cyan accent)
        pygame.draw.circle(
            surface, (100, 255, 255, 200), (center, center), radius - 6
        )  # Cyan sparkle

        return surface

    def _create_arrow_projectile(self, size: int = 16) -> pygame.Surface:
        """Create a simple arrow projectile for ranger attacks."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        # Draw arrow shaft (brown)
        pygame.draw.rect(surface, (139, 69, 19, 255), (center - 1, center - 4, 2, 8))

        # Draw arrowhead (gray)
        points = [
            (center, center - 6),  # Tip
            (center - 2, center - 4),  # Left
            (center + 2, center - 4),  # Right
        ]
        pygame.draw.polygon(surface, (128, 128, 128, 255), points)

        # Draw fletching (red)
        pygame.draw.rect(surface, (255, 0, 0, 255), (center - 2, center + 2, 4, 2))

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
                        # Spawn slash effect at BANDIT's position (attacker), not fighter's
                        self._spawn_effect(
                            "slash", self.bandit_pos[0], self.bandit_pos[1]
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
        """Check if any enemy is in attack range."""
        for bandit_pos in self.bandit_positions:
            dx = abs(bandit_pos[0] - self.fighter_pos[0])
            dy = abs(bandit_pos[1] - self.fighter_pos[1])
            if (dx + dy) <= 1:  # Range of 1 for melee
                return True
        return False

    def _execute_attack(self) -> None:
        """Execute fighter attack on bandit if in range."""
        if self._enemy_in_attack_range() and self.fighter_ap > 0:
            # Find the closest bandit in range
            closest_bandit = None
            closest_distance = float("inf")
            for i, bandit_pos in enumerate(self.bandit_positions):
                if self.bandit_hp[i] > 0:  # Only consider living bandits
                    dx = abs(bandit_pos[0] - self.fighter_pos[0])
                    dy = abs(bandit_pos[1] - self.fighter_pos[1])
                    distance = dx + dy
                    if (
                        distance <= 1 and distance < closest_distance
                    ):  # In range and closest
                        closest_distance = distance
                        closest_bandit = i

            if closest_bandit is not None:
                # Deal damage
                damage = 3
                self.bandit_hp[closest_bandit] = max(
                    0, self.bandit_hp[closest_bandit] - damage
                )
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
                bandit_pos = self.bandit_positions[closest_bandit]
                self._spawn_effect("slash", bandit_pos[0], bandit_pos[1])

                # Screen effects for attack
                self.screen_effects.hit_impact(4.0)

                # Update AI decision text
                self.ai_decision_text = f"🗡️ Fighter attacks Bandit {closest_bandit+1}! Bandit HP: {self.bandit_hp[closest_bandit]}"

                # Check if bandit is defeated
                if self.bandit_hp[closest_bandit] <= 0:
                    self.screen_effects.unit_defeated(6.0)
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
                    # Return the first bandit for now (we'll update this for multiple bandits)
                    return {
                        "team": 2,  # Enemy team
                        "hp": self.demo.bandit_hp[0],
                        "x": self.demo.bandit_positions[0][0],
                        "y": self.demo.bandit_positions[0][1],
                        "ap": self.demo.bandit_ap[0],
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
                elif unit_id == "mage":
                    return {
                        "team": 1,  # Player team
                        "hp": self.demo.mage_hp,
                        "x": self.demo.mage_pos[0],
                        "y": self.demo.mage_pos[1],
                        "ap": self.demo.mage_ap,
                        "attack_range": 3,  # Ranged attacks!
                    }
                elif unit_id == "healer":
                    return {
                        "team": 1,  # Player team
                        "hp": self.demo.healer_hp,
                        "x": self.demo.healer_pos[0],
                        "y": self.demo.healer_pos[1],
                        "ap": self.demo.healer_ap,
                        "attack_range": 2,  # Healing range
                    }
                elif unit_id == "ranger":
                    return {
                        "team": 1,  # Player team
                        "hp": self.demo.ranger_hp,
                        "x": self.demo.ranger_pos[0],
                        "y": self.demo.ranger_pos[1],
                        "ap": self.demo.ranger_ap,
                        "attack_range": 2,  # Medium range attacks
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
                    return self.demo.bandit_ap[0]  # Return first bandit's AP for now
                elif unit_id == "fighter":
                    return self.demo.fighter_ap
                elif unit_id == "mage":
                    return self.demo.mage_ap
                elif unit_id == "healer":
                    return self.demo.healer_ap
                elif unit_id == "ranger":
                    return self.demo.ranger_ap
                return 0

            def can_spend(self, unit_id, amount):
                return self.get_ap(unit_id) >= amount

            def spend(self, unit_id, amount):
                if unit_id == "bandit":
                    self.demo.bandit_ap[0] = max(
                        0, self.demo.bandit_ap[0] - amount
                    )  # Update first bandit for now
                elif unit_id == "fighter":
                    self.demo.fighter_ap = max(0, self.demo.fighter_ap - amount)
                elif unit_id == "mage":
                    self.demo.mage_ap = max(0, self.demo.mage_ap - amount)
                elif unit_id == "healer":
                    self.demo.healer_ap = max(0, self.demo.healer_ap - amount)
                elif unit_id == "ranger":
                    self.demo.ranger_ap = max(0, self.demo.ranger_ap - amount)

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
                - self.camera_x
                - self.camera_shake_x,
                self.fighter_pos[1] * self.tile_size
                + self.tile_size // 2
                - self.camera_y
                - self.camera_shake_y,
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
                    - self.camera_x
                    - self.camera_shake_x,
                    self.fighter_pos[1] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_y
                    - self.camera_shake_y,
                ),
                self.tile_size // 3,
            )

        # 4 Bandits (AI) - draw each bandit
        for i, bandit_pos in enumerate(self.bandit_positions):
            if self.bandit_hp[i] <= 0:  # Skip dead bandits
                continue

            animation = self.bandit_animations[i % len(self.bandit_animations)]
            if (
                "bandit" in self.unit_sprites
                and animation in self.unit_sprites["bandit"]
            ):
                sprite = self.unit_sprites["bandit"][animation]
                sprite_rect = sprite.get_rect()
                sprite_rect.center = (
                    bandit_pos[0] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_x,
                    bandit_pos[1] * self.tile_size
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
                        bandit_pos[0] * self.tile_size
                        + self.tile_size // 2
                        - self.camera_x,
                        bandit_pos[1] * self.tile_size
                        + self.tile_size // 2
                        - self.camera_y,
                    ),
                    self.tile_size // 3,
                )

        # Mage (Ranged) - draw the sprite directly
        if (
            "mage" in self.unit_sprites
            and self.mage_animation in self.unit_sprites["mage"]
        ):
            sprite = self.unit_sprites["mage"][self.mage_animation]
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (
                self.mage_pos[0] * self.tile_size + self.tile_size // 2 - self.camera_x,
                self.mage_pos[1] * self.tile_size + self.tile_size // 2 - self.camera_y,
            )
            surface.blit(sprite, sprite_rect)
        else:
            # Fallback: draw a colored circle
            pygame.draw.circle(
                surface,
                (0, 255, 255),  # Cyan for mage
                (
                    self.mage_pos[0] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_x,
                    self.mage_pos[1] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_y,
                ),
                self.tile_size // 3,
            )

        # Healer (Support) - draw the sprite directly
        if (
            "healer" in self.unit_sprites
            and self.healer_animation in self.unit_sprites["healer"]
        ):
            sprite = self.unit_sprites["healer"][self.healer_animation]
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (
                self.healer_pos[0] * self.tile_size
                + self.tile_size // 2
                - self.camera_x,
                self.healer_pos[1] * self.tile_size
                + self.tile_size // 2
                - self.camera_y,
            )
            surface.blit(sprite, sprite_rect)
        else:
            # Fallback: draw a colored circle
            pygame.draw.circle(
                surface,
                (255, 255, 255),  # White for healer
                (
                    self.healer_pos[0] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_x,
                    self.healer_pos[1] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_y,
                ),
                self.tile_size // 3,
            )

        # Ranger (Ranged) - draw the sprite directly
        if (
            "ranger" in self.unit_sprites
            and self.ranger_animation in self.unit_sprites["ranger"]
        ):
            sprite = self.unit_sprites["ranger"][self.ranger_animation]
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (
                self.ranger_pos[0] * self.tile_size
                + self.tile_size // 2
                - self.camera_x,
                self.ranger_pos[1] * self.tile_size
                + self.tile_size // 2
                - self.camera_y,
            )
            surface.blit(sprite, sprite_rect)
        else:
            # Fallback: draw a colored circle
            pygame.draw.circle(
                surface,
                (0, 255, 0),  # Green for ranger
                (
                    self.ranger_pos[0] * self.tile_size
                    + self.tile_size // 2
                    - self.camera_x,
                    self.ranger_pos[1] * self.tile_size
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
                elif effect_name == "fireball":
                    # Draw fireball effect
                    sprite = self._create_fireball_effect()
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
                elif effect_name == "healing":
                    # Draw healing effect
                    sprite = self._create_healing_effect()
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

    def _draw_projectiles(self, surface: pygame.Surface) -> None:
        """Draw active fireball projectiles."""
        current_time = pygame.time.get_ticks()
        projectiles_to_remove = []

        for projectile in self.active_projectiles:
            # Check if projectile has expired
            if current_time - projectile["start_time"] > projectile["duration"]:
                projectiles_to_remove.append(projectile)
                continue

            # Calculate current position
            current_x = projectile["x"] + projectile["dx"] * (
                current_time - projectile["start_time"]
            )
            current_y = projectile["y"] + projectile["dy"] * (
                current_time - projectile["start_time"]
            )

            # Draw projectile based on type
            if projectile["id"].startswith("fireball"):
                sprite = self._create_fireball_effect(
                    16
                )  # Smaller fireball for projectile
            elif projectile["id"].startswith("arrow"):
                sprite = self._create_arrow_projectile(16)  # Arrow projectile
            else:
                sprite = self._create_fireball_effect(16)  # Default fallback

            sprite_rect = sprite.get_rect()
            sprite_rect.center = (
                current_x - self.camera_x,
                current_y - self.camera_y,
            )
            surface.blit(sprite, sprite_rect)

        # Remove expired/hit projectiles
        for projectile in projectiles_to_remove:
            self.active_projectiles.remove(projectile)

    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Draw UI elements."""
        y_offset = 10

        # Title
        title_text = "Starter Town Tactics Demo"
        text = self.font.render(title_text, True, (255, 255, 255))
        surface.blit(text, (10, y_offset))

        # Add spacing line
        y_offset += 30

        # Instructions removed - now shown in control card on the right

        # Battle outcome
        if self.battle_outcome:
            y_offset += 30
            outcome_text = f"Battle: {self.battle_outcome.value.upper()}"
            color = (
                (0, 255, 0)
                if self.battle_outcome == GameOutcome.VICTORY
                else (255, 0, 0)
            )
            text = self.font.render(outcome_text, True, color)
            surface.blit(text, (10, y_offset))

        # All text moved to right side info panel

        # All system/pattern/architecture info moved to right side info panel

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
                    # Cycle through bandit animations (not used in current system)
                    pass
                elif event.key == pygame.K_h:  # H key to damage mage
                    # Damage mage to demonstrate healing
                    self.mage_hp = max(0, self.mage_hp - 5)
                    print(f"💥 Mage damaged! Mage HP: {self.mage_hp}")

                    # Restore healer AP for demonstration
                    self.healer_ap = min(4, self.healer_ap + 2)
                    print(f"✨ Healer AP restored! Healer AP: {self.healer_ap}")

                    # Spawn damage effect at mage's position
                    self._spawn_effect("spark", self.mage_pos[0], self.mage_pos[1])

        # Handle movement - ONE TILE AT A TIME with proper timing
        keys = pygame.key.get_pressed()
        moved = False

        # Only allow movement if enough time has passed AND key was just pressed
        if current_time - self.last_move_time > self.move_delay:
            # Check for key press (not continuous hold)
            if keys[pygame.K_w] and self.last_key_pressed != pygame.K_w:  # Up
                new_pos = [self.fighter_pos[0], max(0, self.fighter_pos[1] - 1)]
                if (
                    not self._position_overlaps_any_bandit(new_pos)
                    and not self._positions_overlap(new_pos, self.mage_pos)
                    and not self._positions_overlap(new_pos, self.healer_pos)
                    and not self._positions_overlap(new_pos, self.ranger_pos)
                ):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_w
            elif keys[pygame.K_s] and self.last_key_pressed != pygame.K_s:  # Down
                new_pos = [self.fighter_pos[0], min(14, self.fighter_pos[1] + 1)]
                if (
                    not self._position_overlaps_any_bandit(new_pos)
                    and not self._positions_overlap(new_pos, self.mage_pos)
                    and not self._positions_overlap(new_pos, self.healer_pos)
                    and not self._positions_overlap(new_pos, self.ranger_pos)
                ):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_s
            elif keys[pygame.K_a] and self.last_key_pressed != pygame.K_a:  # Left
                new_pos = [max(0, self.fighter_pos[0] - 1), self.fighter_pos[1]]
                if (
                    not self._position_overlaps_any_bandit(new_pos)
                    and not self._positions_overlap(new_pos, self.mage_pos)
                    and not self._positions_overlap(new_pos, self.healer_pos)
                    and not self._positions_overlap(new_pos, self.ranger_pos)
                ):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_a
            elif keys[pygame.K_d] and self.last_key_pressed != pygame.K_d:  # Right
                new_pos = [min(14, self.fighter_pos[0] + 1), self.fighter_pos[1]]
                if (
                    not self._position_overlaps_any_bandit(new_pos)
                    and not self._positions_overlap(new_pos, self.mage_pos)
                    and not self._positions_overlap(new_pos, self.healer_pos)
                    and not self._positions_overlap(new_pos, self.ranger_pos)
                ):
                    self.fighter_pos = new_pos
                    self.fighter_animation = "pose2"  # Use available sprite
                    moved = True
                    self.last_key_pressed = pygame.K_d
            else:
                # No movement keys pressed, return to idle
                self.fighter_animation = "pose1"
                self.last_key_pressed = 0

        # Reset key tracking when no keys are pressed
        if not any(
            [keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]]
        ):
            self.last_key_pressed = 0

        # Camera follows fighter
        if moved:
            self.last_move_time = current_time
            # Camera follows fighter - adjust offsets for new screen size
            self.camera_x = (
                self.fighter_pos[0] * self.tile_size - 600
            )  # Half of new width (1200/2)
            self.camera_y = (
                self.fighter_pos[1] * self.tile_size - 400
            )  # Half of new height (800/2)

        # Camera bounds - updated for new screen size (1200x800) and tile size (48)
        self.camera_x = max(0, min(15 * self.tile_size - 1200, self.camera_x))
        self.camera_y = max(0, min(15 * self.tile_size - 800, self.camera_y))

        return True

    def _positions_overlap(self, pos1: list, pos2: list) -> bool:
        """Check if two positions overlap."""
        return pos1[0] == pos2[0] and pos1[1] == pos2[1]

    def _position_overlaps_any_bandit(self, pos: list) -> bool:
        """Check if a position overlaps with any living bandit."""
        for i, bandit_pos in enumerate(self.bandit_positions):
            if self.bandit_hp[i] > 0 and self._positions_overlap(pos, bandit_pos):
                return True
        return False

    def _update_mage_ai(self) -> None:
        """Update mage AI behavior - ranged attacks."""
        current_time = pygame.time.get_ticks()

        # Run mage AI every 4.5 seconds (slowed down 3x)
        if current_time - self.last_mage_decision > 4500:
            self.last_mage_decision = current_time

            # Find the closest living bandit
            closest_bandit = None
            closest_distance = float("inf")
            for i, bandit_pos in enumerate(self.bandit_positions):
                if self.bandit_hp[i] > 0:  # Only consider living bandits
                    distance = abs(self.mage_pos[0] - bandit_pos[0]) + abs(
                        self.mage_pos[1] - bandit_pos[1]
                    )
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_bandit = i

            if closest_bandit is not None:
                bandit_pos = self.bandit_positions[closest_bandit]
                # Debug: show current positions and distance
                print(
                    f"🧙‍♂️ Mage at ({self.mage_pos[0]}, {self.mage_pos[1]}), Bandit {closest_bandit+1} at ({bandit_pos[0]}, {bandit_pos[1]}), Distance: {closest_distance}, Range: {self.mage_attack_range}"
                )

                # Check if mage can attack bandit (ranged attack)
                if self._mage_can_attack_bandit(closest_bandit) and self.mage_ap > 0:
                    # Mage attacks bandit from range!
                    damage = 2  # Less damage than melee but from range
                    self.bandit_hp[closest_bandit] = max(
                        0, self.bandit_hp[closest_bandit] - damage
                    )
                    self.mage_ap = max(0, self.mage_ap - 1)

                    # Spawn flying fireball projectile from mage to bandit
                    self._spawn_fireball_projectile(
                        self.mage_pos[0],
                        self.mage_pos[1],
                        bandit_pos[0],
                        bandit_pos[1],
                    )

                    # Screen effects for mage attack
                    self.screen_effects.hit_impact(3.0)

                    print(
                        f"🔥 Mage casts fireball! Bandit {closest_bandit+1} HP: {self.bandit_hp[closest_bandit]}"
                    )

                    # Check if bandit is defeated
                    if self.bandit_hp[closest_bandit] <= 0:
                        self.screen_effects.unit_defeated(5.0)
                        self.victory_service.on_unit_defeated(2)

                # If mage can't attack, move toward closest bandit
                elif self.mage_ap > 0 and not self._mage_can_attack_bandit(
                    closest_bandit
                ):
                    # Move mage toward bandit to get in range
                    dx = bandit_pos[0] - self.mage_pos[0]
                    dy = bandit_pos[1] - self.mage_pos[1]

                    # Move in the direction with larger distance
                    if abs(dx) > abs(dy):
                        # Move horizontally
                        new_x = self.mage_pos[0] + (1 if dx > 0 else -1)
                        new_pos = [new_x, self.mage_pos[1]]
                        if (
                            not self._position_overlaps_any_bandit(new_pos)
                            and not self._positions_overlap(new_pos, self.fighter_pos)
                            and not self._positions_overlap(new_pos, self.healer_pos)
                            and not self._positions_overlap(new_pos, self.ranger_pos)
                        ):
                            self.mage_pos[0] = new_x
                            self.mage_ap = max(0, self.mage_ap - 1)
                            print(
                                f"🧙‍♂️ Mage moves toward bandit: ({self.mage_pos[0]}, {self.mage_pos[1]})"
                            )
                    else:
                        # Move vertically
                        new_y = self.mage_pos[1] + (1 if dy > 0 else -1)
                        new_pos = [self.mage_pos[0], new_y]
                        if (
                            not self._position_overlaps_any_bandit(new_pos)
                            and not self._positions_overlap(new_pos, self.fighter_pos)
                            and not self._positions_overlap(new_pos, self.healer_pos)
                            and not self._positions_overlap(new_pos, self.ranger_pos)
                        ):
                            self.mage_pos[1] = new_y
                            self.mage_ap = max(0, self.mage_ap - 1)
                            print(
                                f"🧙‍♂️ Mage moves toward bandit: ({self.mage_pos[0]}, {self.mage_pos[1]})"
                            )

    def _mage_can_attack_bandit(self, bandit_index: int) -> bool:
        """Check if mage can attack bandit from range."""
        bandit_pos = self.bandit_positions[bandit_index]
        dx = abs(self.mage_pos[0] - bandit_pos[0])
        dy = abs(self.mage_pos[1] - bandit_pos[1])
        return (dx + dy) <= self.mage_attack_range  # Range 3!

    def _spawn_fireball_projectile(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> None:
        """Spawn a fireball projectile from start to end."""
        # Calculate trajectory
        dx = end_x - start_x
        dy = end_y - start_y
        distance = max(1, abs(dx) + abs(dy))  # Manhattan distance

        # Normalize direction for smooth movement
        if distance > 0:
            dx_norm = dx / distance
            dy_norm = dy / distance
        else:
            dx_norm = dy_norm = 0

        # Create projectile data
        projectile = {
            "id": f"fireball_{len(self.active_projectiles)}",
            "x": start_x * self.tile_size + self.tile_size // 2,  # Pixel position
            "y": start_y * self.tile_size + self.tile_size // 2,
            "target_x": end_x * self.tile_size + self.tile_size // 2,
            "target_y": end_y * self.tile_size + self.tile_size // 2,
            "dx": dx_norm * 4,  # Speed: 4 pixels per frame
            "dy": dy_norm * 4,
            "start_time": pygame.time.get_ticks(),
            "duration": 2000,  # 2 seconds max flight time
            "hit_target": False,
        }

        self.active_projectiles.append(projectile)
        print(f"🔥 Fireball launched from ({start_x}, {start_y}) to ({end_x}, {end_y})")

    def _spawn_arrow_projectile(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> None:
        """Spawn an arrow projectile from start to end."""
        # Calculate trajectory
        dx = end_x - start_x
        dy = end_y - start_y
        distance = max(1, abs(dx) + abs(dy))  # Manhattan distance

        # Normalize direction for smooth movement
        if distance > 0:
            dx_norm = dx / distance
            dy_norm = dy / distance
        else:
            dx_norm = dy_norm = 0

        # Create projectile data
        projectile = {
            "id": f"arrow_{len(self.active_projectiles)}",
            "x": start_x * self.tile_size + self.tile_size // 2,  # Pixel position
            "y": start_y * self.tile_size + self.tile_size // 2,
            "target_x": end_x * self.tile_size + self.tile_size // 2,
            "target_y": end_y * self.tile_size + self.tile_size // 2,
            "dx": dx_norm * 5,  # Speed: 5 pixels per frame (faster than fireball)
            "dy": dy_norm * 5,
            "start_time": pygame.time.get_ticks(),
            "duration": 1500,  # 1.5 seconds max flight time
            "hit_target": False,
        }

        self.active_projectiles.append(projectile)
        print(f"🏹 Arrow launched from ({start_x}, {start_y}) to ({end_x}, {end_y})")

    def _update_projectiles(self) -> None:
        """Update projectile positions and check for hits."""
        current_time = pygame.time.get_ticks()
        projectiles_to_remove = []

        for projectile in self.active_projectiles:
            # Check if projectile has expired
            if current_time - projectile["start_time"] > projectile["duration"]:
                projectiles_to_remove.append(projectile)
                continue

            # Move projectile
            old_x, old_y = projectile["x"], projectile["y"]
            projectile["x"] += projectile["dx"]
            projectile["y"] += projectile["dy"]

            # Check if projectile hit target or passed it
            start_x = projectile["x"] - projectile["dx"]  # Previous position
            start_y = projectile["y"] - projectile["dy"]
            target_x = projectile["target_x"]
            target_y = projectile["target_y"]

            # Check if we've crossed the target line (prevents overshooting)
            if not projectile["hit_target"]:
                # Check if we've moved past the target in either direction
                crossed_x = (start_x <= target_x <= projectile["x"]) or (
                    projectile["x"] <= target_x <= start_x
                )
                crossed_y = (start_y <= target_y <= projectile["y"]) or (
                    projectile["y"] <= target_y <= start_y
                )

                # Hit if we're close to target AND we've crossed it
                target_distance = abs(projectile["x"] - target_x) + abs(
                    projectile["y"] - target_y
                )
                if target_distance < 15 and (
                    crossed_x or crossed_y
                ):  # 15 pixel hit radius
                    projectile["hit_target"] = True
                    # Spawn explosion effect at target
                    target_tile_x = int(target_x // self.tile_size)
                    target_tile_y = int(target_y // self.tile_size)
                    self._spawn_effect("fireball", target_tile_x, target_tile_y)
                    print(
                        f"💥 Fireball hit target at ({target_tile_x}, {target_tile_y})!"
                    )
                    projectiles_to_remove.append(projectile)

        # Remove expired/hit projectiles
        for projectile in projectiles_to_remove:
            self.active_projectiles.remove(projectile)

    def _update_healer_ai(self) -> None:
        """Update healer AI behavior - healing allies."""
        current_time = pygame.time.get_ticks()

        # Run healer AI every 6 seconds (slowed down 3x)
        if (
            current_time - self.last_healer_decision > 6000
        ):  # Reusing last_mage_decision for healer
            self.last_healer_decision = current_time  # Update last_mage_decision

            # Find the ally with lowest HP
            allies = [
                ("fighter", self.fighter_hp, self.fighter_pos),
                ("mage", self.mage_hp, self.mage_pos),
                ("ranger", self.ranger_hp, self.ranger_pos),
            ]

            # Sort by HP (lowest first)
            allies.sort(key=lambda x: x[1])
            target_name, target_hp, target_pos = allies[0]

            # Debug: show current positions and distance
            distance = abs(self.healer_pos[0] - target_pos[0]) + abs(
                self.healer_pos[1] - target_pos[1]
            )
            print(
                f"🧙‍♂️ Healer at ({self.healer_pos[0]}, {self.healer_pos[1]}), {target_name.title()} at ({target_pos[0]}, {target_pos[1]}), Distance: {distance}, Range: {self.healer_heal_range}"
            )

            # Check if healer can heal the lowest HP ally
            if self._healer_can_heal_target(target_pos) and self.healer_ap > 0:
                # Healer heals the target!
                heal_amount = 3  # Increased healing
                if target_name == "fighter":
                    self.fighter_hp = min(
                        self.fighter_hp + heal_amount, 10
                    )  # Max HP 10
                elif target_name == "mage":
                    self.mage_hp = min(self.mage_hp + heal_amount, 15)  # Max HP 15
                else:  # ranger
                    self.ranger_hp = min(self.ranger_hp + heal_amount, 14)  # Max HP 14

                self.healer_ap = max(0, self.healer_ap - 1)

                # Spawn healing effect at healer's position
                self._spawn_effect("healing", self.healer_pos[0], self.healer_pos[1])

                current_hp = (
                    self.fighter_hp
                    if target_name == "fighter"
                    else (self.mage_hp if target_name == "mage" else self.ranger_hp)
                )

                # Screen effects for healing
                self.screen_effects.heal_effect()
                print(f"💚 Healer heals {target_name}! {target_name} HP: {current_hp}")
                print(
                    f"💚 Healer heals {target_name.title()}! {target_name.title()} HP: {current_hp}"
                )

                # Don't trigger victory on full heal - that's not a win condition!

            # If healer can't heal, move toward the target
            elif self.healer_ap > 0 and not self._healer_can_heal_target(target_pos):
                # Move healer toward the target to get in range
                dx = target_pos[0] - self.healer_pos[0]
                dy = target_pos[1] - self.healer_pos[1]

                # Move in the direction with larger distance
                if abs(dx) > abs(dy):
                    # Move horizontally
                    new_x = self.healer_pos[0] + (1 if dx > 0 else -1)
                    if (
                        not self._positions_overlap(
                            [new_x, self.healer_pos[1]], self.fighter_pos
                        )
                        and not self._positions_overlap(
                            [new_x, self.healer_pos[1]], self.mage_pos
                        )
                        and not self._positions_overlap(
                            [new_x, self.healer_pos[1]], self.ranger_pos
                        )
                    ):
                        self.healer_pos[0] = new_x
                        self.healer_ap = max(0, self.healer_ap - 1)
                        print(
                            f"🧙‍♂️ Healer moves toward {target_name}: ({self.healer_pos[0]}, {self.healer_pos[1]})"
                        )
                else:
                    # Move vertically
                    new_y = self.healer_pos[1] + (1 if dy > 0 else -1)
                    if (
                        not self._positions_overlap(
                            [self.healer_pos[0], new_y], self.fighter_pos
                        )
                        and not self._positions_overlap(
                            [self.healer_pos[0], new_y], self.mage_pos
                        )
                        and not self._positions_overlap(
                            [self.healer_pos[0], new_y], self.ranger_pos
                        )
                    ):
                        self.healer_pos[1] = new_y
                        self.healer_ap = max(0, self.healer_ap - 1)
                        print(
                            f"🧙‍♂️ Healer moves toward {target_name}: ({self.healer_pos[0]}, {self.healer_pos[1]})"
                        )

    def _healer_can_heal_target(self, target_pos: list) -> bool:
        """Check if healer can heal target from range."""
        dx = abs(self.healer_pos[0] - target_pos[0])
        dy = abs(self.healer_pos[1] - target_pos[1])
        return (dx + dy) <= self.healer_heal_range  # Range 2!

    def _update_bandit_ai(self) -> None:
        """Update bandit AI behavior - move and attack."""
        current_time = pygame.time.get_ticks()

        # Run bandit AI every 2 seconds (different from mage)
        if current_time - self.last_bandit_decision > 2000:
            self.last_bandit_decision = current_time

            # Update each living bandit
            for i, bandit_pos in enumerate(self.bandit_positions):
                if self.bandit_hp[i] <= 0:  # Skip dead bandits
                    continue

                # Debug: show current positions and distance
                distance = abs(bandit_pos[0] - self.fighter_pos[0]) + abs(
                    bandit_pos[1] - self.fighter_pos[1]
                )
                print(
                    f"👹 Bandit {i+1} at ({bandit_pos[0]}, {bandit_pos[1]}), Fighter at ({self.fighter_pos[0]}, {self.fighter_pos[1]}), Distance: {distance}"
                )

                # Check if bandit can attack fighter (melee attack)
                if self._bandit_can_attack_fighter(i) and self.bandit_ap[i] > 0:
                    # Bandit attacks fighter!
                    damage = 2  # Less damage than ranged but melee
                    self.fighter_hp = max(0, self.fighter_hp - damage)
                    self.bandit_ap[i] = max(0, self.bandit_ap[i] - 1)

                    # Spawn slash effect at bandit's position (attacker)
                    self._spawn_effect("slash", bandit_pos[0], bandit_pos[1])

                    print(f"🗡️ Bandit {i+1} attacks! Fighter HP: {self.fighter_hp}")

                    # Check if fighter is defeated
                    if self.fighter_hp <= 0:
                        self.victory_service.on_unit_defeated(1)
                        print("💀 FIGHTER DEFEATED! Bandits win!")

                # If bandit can't attack, move toward fighter
                elif self.bandit_ap[i] > 0 and not self._bandit_can_attack_fighter(i):
                    # Move bandit toward fighter to get in range
                    dx = self.fighter_pos[0] - bandit_pos[0]
                    dy = self.fighter_pos[1] - bandit_pos[1]

                    # Move in the direction with larger distance
                    if abs(dx) > abs(dy):
                        # Move horizontally
                        new_x = bandit_pos[0] + (1 if dx > 0 else -1)
                        new_pos = [new_x, bandit_pos[1]]
                        if (
                            not self._position_overlaps_any_bandit(new_pos)
                            and not self._positions_overlap(new_pos, self.mage_pos)
                            and not self._positions_overlap(new_pos, self.healer_pos)
                            and not self._positions_overlap(new_pos, self.ranger_pos)
                        ):
                            self.bandit_positions[i][0] = new_x
                            self.bandit_ap[i] = max(0, self.bandit_ap[i] - 1)
                            print(
                                f"👹 Bandit {i+1} moves toward fighter: ({bandit_pos[0]}, {bandit_pos[1]})"
                            )
                    else:
                        # Move vertically
                        new_y = bandit_pos[1] + (1 if dy > 0 else -1)
                        new_pos = [bandit_pos[0], new_y]
                        if (
                            not self._position_overlaps_any_bandit(new_pos)
                            and not self._positions_overlap(new_pos, self.mage_pos)
                            and not self._positions_overlap(new_pos, self.healer_pos)
                            and not self._positions_overlap(new_pos, self.ranger_pos)
                        ):
                            self.bandit_positions[i][1] = new_y
                            self.bandit_ap[i] = max(0, self.bandit_ap[i] - 1)
                            print(
                                f"👹 Bandit {i+1} moves toward fighter: ({bandit_pos[0]}, {bandit_pos[1]})"
                            )

    def _bandit_can_attack_fighter(self, bandit_index: int) -> bool:
        """Check if bandit can attack fighter from melee range."""
        bandit_pos = self.bandit_positions[bandit_index]
        dx = abs(bandit_pos[0] - self.fighter_pos[0])
        dy = abs(bandit_pos[1] - self.fighter_pos[1])
        return (dx + dy) <= 1  # Range of 1 for melee

    def _update_ranger_ai(self) -> None:
        """Update ranger AI behavior - ranged attacks with AP regeneration."""
        current_time = pygame.time.get_ticks()

        # Regenerate AP every tick (ranger special ability) - slowed down 3x
        if current_time - self.last_ranger_ap_regen > 3000:  # Every 3 seconds
            self.last_ranger_ap_regen = current_time
            self.ranger_ap = min(
                5, self.ranger_ap + self.ranger_ap_regen
            )  # Cap at 5 AP
            print(f"🏹 Ranger AP regenerated! Ranger AP: {self.ranger_ap}")

        # Run ranger AI every 7.5 seconds (slowed down 3x)
        if current_time - self.last_ranger_decision > 7500:
            self.last_ranger_decision = current_time

            # Find the closest living bandit
            closest_bandit = None
            closest_distance = float("inf")
            for i, bandit_pos in enumerate(self.bandit_positions):
                if self.bandit_hp[i] > 0:  # Only consider living bandits
                    distance = abs(self.ranger_pos[0] - bandit_pos[0]) + abs(
                        self.ranger_pos[1] - bandit_pos[1]
                    )
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_bandit = i

            if closest_bandit is not None:
                bandit_pos = self.bandit_positions[closest_bandit]
                # Debug: show current positions and distance
                print(
                    f"🏹 Ranger at ({self.ranger_pos[0]}, {self.ranger_pos[1]}), Bandit {closest_bandit+1} at ({bandit_pos[0]}, {bandit_pos[1]}), Distance: {closest_distance}, Range: {self.ranger_attack_range}"
                )

                # Check if ranger can attack bandit (ranged attack)
                if (
                    self._ranger_can_attack_bandit(closest_bandit)
                    and self.ranger_ap > 0
                ):
                    # Ranger attacks bandit!
                    damage = 2  # Medium damage between fighter (3) and mage (2)
                    self.bandit_hp[closest_bandit] = max(
                        0, self.bandit_hp[closest_bandit] - damage
                    )
                    self.ranger_ap = max(0, self.ranger_ap - 1)

                    # Spawn arrow projectile from ranger to bandit
                    self._spawn_arrow_projectile(
                        self.ranger_pos[0],
                        self.ranger_pos[1],
                        bandit_pos[0],
                        bandit_pos[1],
                    )

                    print(
                        f"🏹 Ranger shoots bandit {closest_bandit+1}! Bandit HP: {self.bandit_hp[closest_bandit]}"
                    )

                    # Check if bandit is defeated
                    if self.bandit_hp[closest_bandit] <= 0:
                        self.victory_service.on_unit_defeated(2)

            # If ranger can't attack, move toward bandit
            elif self.ranger_ap > 0 and not self._ranger_can_attack_bandit():
                # Move ranger toward bandit to get in range
                dx = self.bandit_pos[0] - self.ranger_pos[0]
                dy = self.bandit_pos[1] - self.ranger_pos[1]

                # Move in the direction with larger distance
                if abs(dx) > abs(dy):
                    # Move horizontally
                    new_x = self.ranger_pos[0] + (1 if dx > 0 else -1)
                    if (
                        not self._positions_overlap(
                            [new_x, self.ranger_pos[1]], self.fighter_pos
                        )
                        and not self._positions_overlap(
                            [new_x, self.ranger_pos[1]], self.mage_pos
                        )
                        and not self._positions_overlap(
                            [new_x, self.ranger_pos[1]], self.healer_pos
                        )
                    ):
                        self.ranger_pos[0] = new_x
                        self.ranger_ap = max(0, self.ranger_ap - 1)
                        print(
                            f"🏹 Ranger moves toward bandit: ({self.ranger_pos[0]}, {self.ranger_pos[1]})"
                        )
                else:
                    # Move vertically
                    new_y = self.ranger_pos[1] + (1 if dy > 0 else -1)
                    if (
                        not self._positions_overlap(
                            [self.ranger_pos[0], new_y], self.fighter_pos
                        )
                        and not self._positions_overlap(
                            [self.ranger_pos[0], new_y], self.mage_pos
                        )
                        and not self._positions_overlap(
                            [self.ranger_pos[0], new_y], self.healer_pos
                        )
                    ):
                        self.ranger_pos[1] = new_y
                        self.ranger_ap = max(0, self.ranger_ap - 1)
                        print(
                            f"🏹 Ranger moves toward bandit: ({self.ranger_pos[0]}, {self.ranger_pos[1]})"
                        )

    def _ranger_can_attack_bandit(self, bandit_index: int) -> bool:
        """Check if ranger can attack bandit from range."""
        bandit_pos = self.bandit_positions[bandit_index]
        dx = abs(self.ranger_pos[0] - bandit_pos[0])
        dy = abs(self.ranger_pos[1] - bandit_pos[1])
        return (dx + dy) <= self.ranger_attack_range  # Range 2!

    def _update_fighter_ai(self) -> None:
        """Update fighter AI - gets overridden by player input."""
        current_time = pygame.time.get_ticks()

        # Only run AI if no recent player input (within last 2 seconds)
        if current_time - self.last_key_pressed < 2000:
            return  # Player recently gave input, skip AI
        else:
            # Show that fighter AI is active
            if (
                current_time - self.last_fighter_ai_decision > 2500
            ):  # Show message 0.5s before action
                print("🤖 Fighter AI is active (no player input)")

        # Run fighter AI every 3 seconds (slowed down 3x)
        if current_time - self.last_fighter_ai_decision > 3000:
            self.last_fighter_ai_decision = current_time

            # Find closest bandit
            closest_bandit = None
            closest_distance = float("inf")
            for i, bandit_pos in enumerate(self.bandit_positions):
                if self.bandit_hp[i] > 0:  # Only consider living bandits
                    distance = abs(self.fighter_pos[0] - bandit_pos[0]) + abs(
                        self.fighter_pos[1] - bandit_pos[1]
                    )
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_bandit = i

            if closest_bandit is not None:
                bandit_pos = self.bandit_positions[closest_bandit]

                # Check if fighter can attack bandit
                if (
                    self._fighter_can_attack_bandit(closest_bandit)
                    and self.fighter_ap > 0
                ):
                    # Fighter attacks bandit!
                    damage = 3
                    self.bandit_hp[closest_bandit] = max(
                        0, self.bandit_hp[closest_bandit] - damage
                    )
                    self.fighter_ap = max(0, self.fighter_ap - 2)

                    # Spawn slash effect at bandit's position
                    self._spawn_effect("slash", bandit_pos[0], bandit_pos[1])

                    # Update AI decision text
                    self.ai_decision_text = f"🤖 Fighter AI attacks Bandit {closest_bandit+1}! Bandit HP: {self.bandit_hp[closest_bandit]}"
                    print(
                        f"🤖 Fighter AI attacks Bandit {closest_bandit+1}! Bandit HP: {self.bandit_hp[closest_bandit]}"
                    )

                    # Check if bandit is defeated
                    if self.bandit_hp[closest_bandit] <= 0:
                        self.victory_service.on_unit_defeated(2)
                        self.ai_decision_text = (
                            f"🤖 Fighter AI defeats Bandit {closest_bandit+1}!"
                        )

                elif self.fighter_ap > 0:
                    # Move fighter toward bandit
                    dx = bandit_pos[0] - self.fighter_pos[0]
                    dy = bandit_pos[1] - self.fighter_pos[1]

                    if abs(dx) > abs(dy):
                        # Move horizontally
                        new_x = self.fighter_pos[0] + (1 if dx > 0 else -1)
                        if 0 <= new_x < 20:  # Stay in bounds
                            self.fighter_pos[0] = new_x
                            self.fighter_ap = max(0, self.fighter_ap - 1)
                            self.ai_decision_text = f"🤖 Fighter AI moves toward bandit: ({self.fighter_pos[0]}, {self.fighter_pos[1]})"
                            print(
                                f"🤖 Fighter AI moves toward bandit: ({self.fighter_pos[0]}, {self.fighter_pos[1]})"
                            )
                    else:
                        # Move vertically
                        new_y = self.fighter_pos[1] + (1 if dy > 0 else -1)
                        if 0 <= new_y < 15:  # Stay in bounds
                            self.fighter_pos[1] = new_y
                            self.fighter_ap = max(0, self.fighter_ap - 1)
                            self.ai_decision_text = f"🤖 Fighter AI moves toward bandit: ({self.fighter_pos[0]}, {self.fighter_pos[1]})"
                            print(
                                f"🤖 Fighter AI moves toward bandit: ({self.fighter_pos[0]}, {self.fighter_pos[1]})"
                            )

    def _fighter_can_attack_bandit(self, bandit_index: int) -> bool:
        """Check if fighter can attack the specified bandit."""
        if bandit_index >= len(self.bandit_positions):
            return False

        bandit_pos = self.bandit_positions[bandit_index]
        dx = abs(self.fighter_pos[0] - bandit_pos[0])
        dy = abs(self.fighter_pos[1] - bandit_pos[1])
        return (dx + dy) <= 1  # Melee range

    def run(self) -> None:
        """Run the demo."""
        print("Starting BT Fighter Demo...")
        print("Controls: WASD to move, SPACE to attack")
        print("AI bandit uses Behavior Tree for decisions")
        print("")
        print("Design Patterns in Use:")
        print("├─ Factory Method: EntityFactory for unit creation")
        print("├─ Composite Pattern: Behavior Tree structure")
        print("├─ Strategy Pattern: BTContext for AI decisions")
        print("├─ Observer Pattern: VictoryService for game events")
        print("├─ State Pattern: GameState management")
        print("└─ Command Pattern: Action Point system")
        print("")

        running = True
        while running:
            # Handle input
            running = self._handle_input()

            # Update AI scheduler
            self.ai_scheduler.update(0.016)  # ~60 FPS

            # Update fighter AI (gets overridden by player input)
            self._update_fighter_ai()

            # Simple mage AI - attack bandit if in range
            self._update_mage_ai()

            # Simple healer AI - heal allies if in range
            self._update_healer_ai()

            # Simple bandit AI - move and attack
            self._update_bandit_ai()

            # Simple ranger AI - ranged attacks with AP regeneration
            self._update_ranger_ai()

            # Update projectiles
            self._update_projectiles()

            # Update screen effects and get camera shake
            shake_offset = self.screen_effects.update(0.016)
            self.camera_shake_x = shake_offset[0]
            self.camera_shake_y = shake_offset[1]

            # Update UI components
            self.victory_banner.update(0.016)
            self.turn_banner.update(0.016)
            self.cutin_text.update(0.016)

            # Clear screen
            self.screen.fill((0, 0, 0))

            # Draw everything with camera shake
            self._draw_terrain(self.screen)
            self._draw_units(self.screen)
            self._draw_effects(self.screen)
            self._draw_projectiles(self.screen)

            # Draw health bars and KO markers
            self._draw_health_overlay(self.screen)

            # Draw UI components
            self._draw_ui(self.screen)
            self._draw_controls_text(self.screen)
            self._draw_roster_panel(self.screen)
            self._draw_info_panel(self.screen)
            self._draw_architecture_panel(self.screen)
            self._draw_methods_panel(self.screen)

            # Draw banners and cut-in text
            self.turn_banner.draw(self.screen)
            self.cutin_text.draw(self.screen)
            self.victory_banner.draw(self.screen)

            # Draw screen effects (flash, etc.)
            self.screen_effects.draw(self.screen)

            # Update display
            pygame.display.flip()

            # Cap frame rate
            self.clock.tick(60)

        print("Demo finished.")
        pygame.quit()

    def _draw_health_overlay(self, surface: pygame.Surface) -> None:
        """Draw health bars and KO markers for all units."""
        # Create unit data for health overlay
        units_data = {}

        # Fighter
        units_data["fighter"] = {
            "x": self.fighter_pos[0],
            "y": self.fighter_pos[1],
            "hp": self.fighter_hp,
            "max_hp": 10,
            "alive": self.fighter_hp > 0,
        }

        # Bandits
        for i, (pos, hp) in enumerate(zip(self.bandit_positions, self.bandit_hp)):
            units_data[f"bandit_{i}"] = {
                "x": pos[0],
                "y": pos[1],
                "hp": hp,
                "max_hp": 8,
                "alive": hp > 0,
            }

        # Mage
        units_data["mage"] = {
            "x": self.mage_pos[0],
            "y": self.mage_pos[1],
            "hp": self.mage_hp,
            "max_hp": 15,
            "alive": self.mage_hp > 0,
        }

        # Healer
        units_data["healer"] = {
            "x": self.healer_pos[0],
            "y": self.healer_pos[1],
            "hp": self.healer_hp,
            "max_hp": 12,
            "alive": self.healer_hp > 0,
        }

        # Ranger
        units_data["ranger"] = {
            "x": self.ranger_pos[0],
            "y": self.ranger_pos[1],
            "hp": self.ranger_hp,
            "max_hp": 14,
            "alive": self.ranger_hp > 0,
        }

        # Draw health overlay with camera shake
        camera_x = self.camera_x + self.camera_shake_x
        camera_y = self.camera_y + self.camera_shake_y
        self.health_overlay.draw_all_units(
            surface, units_data, camera_x, camera_y, self.tile_size
        )

    def _draw_roster_panel(self, surface: pygame.Surface) -> None:
        """Draw the roster panel showing team status."""
        # Create team data
        teams = {
            1: {  # Player team
                "name": "Allies",
                "units": [
                    {
                        "name": "Fighter",
                        "hp": self.fighter_hp,
                        "max_hp": 10,
                        "alive": self.fighter_hp > 0,
                    },
                    {
                        "name": "Mage",
                        "hp": self.mage_hp,
                        "max_hp": 15,
                        "alive": self.mage_hp > 0,
                    },
                    {
                        "name": "Healer",
                        "hp": self.healer_hp,
                        "max_hp": 12,
                        "alive": self.healer_hp > 0,
                    },
                    {
                        "name": "Ranger",
                        "hp": self.ranger_hp,
                        "max_hp": 14,
                        "alive": self.ranger_hp > 0,
                    },
                ],
            },
            2: {  # Enemy team
                "name": "Bandits",
                "units": [
                    {"name": f"Bandit {i+1}", "hp": hp, "max_hp": 8, "alive": hp > 0}
                    for i, hp in enumerate(self.bandit_hp)
                ],
            },
        }

        self.roster_panel.draw(surface, teams)

    def _draw_info_panel(self, surface: pygame.Surface) -> None:
        """Draw info panel with animation and AI decision info."""
        # Position info panel to avoid overlapping with game area (720px wide)
        panel_x = 750  # Right side of screen
        panel_y = 10  # Same vertical level as Allies panel

        # Create info data
        alive_bandits = [h for h in self.bandit_hp if h > 0]
        bandit_hp_text = f"Bandits: {len(alive_bandits)} alive"
        if alive_bandits:
            bandit_hp_text += f" (HP: {', '.join(map(str, alive_bandits))})"

        info_items = [
            f"Animation: {self.fighter_animation} (HP: {self.fighter_hp})",
            bandit_hp_text,
            f"AI Decision: {self.bt_tick_count}",
            f"Active Effects: {len(self.active_effects)}",
            f"AI Tasks: {self.ai_scheduler.get_task_count()}",
        ]

        # Draw background
        panel_width = 350  # Expanded for longer text
        panel_height = len(info_items) * 25 + 30  # Reduced line height from 30 to 25
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black

        # Draw border
        pygame.draw.rect(
            panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2
        )

        # Draw title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("GAME INFO", True, (255, 255, 255))
        panel_surface.blit(title_surface, (10, 10))

        # Draw info items
        y_offset = 35
        for item in info_items:
            text_surface = font.render(item, True, (255, 255, 255))
            panel_surface.blit(text_surface, (10, y_offset))
            y_offset += 25  # Reduced from 30 to 25 to match panel height calculation

        # Blit to main surface
        surface.blit(panel_surface, (panel_x, panel_y))

    def _draw_controls_text(self, surface: pygame.Surface) -> None:
        """Draw controls text under the game tiles."""
        font = pygame.font.Font(None, 24)

        # Controls text
        controls = ["WASD - Move Fighter", "SPACE - Attack", "ESC - Exit"]

        # Position under the game area (720px wide, 48px tiles = 15 tiles)
        # Center the text under the game area
        start_x = 50  # Start position under tiles
        y_pos = 750  # Below the game area

        # Draw each control with spacing
        x_offset = 0
        for control in controls:
            text_surface = font.render(control, True, (255, 255, 255))
            surface.blit(text_surface, (start_x + x_offset, y_pos))
            x_offset += 200  # Space controls horizontally

    def _draw_architecture_panel(self, surface: pygame.Surface) -> None:
        """Draw architecture & patterns panel."""
        panel_x = 750  # Right side of screen
        panel_y = 192  # Moved up one tile (48px) from 240

        arch_items = [
            "Architecture & Patterns:",
            "├─ Composite: BT Structure",
            "├─ Strategy: BTContext",
            "├─ Observer: VictoryService",
            "├─ Factory: EntityFactory",
            "├─ Scheduler: AIScheduler",
            "└─ State: GameState",
        ]

        # Draw background
        panel_width = 350
        panel_height = len(arch_items) * 25 + 30
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))

        # Draw border
        pygame.draw.rect(
            panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2
        )

        # Draw title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("ARCHITECTURE", True, (255, 255, 255))
        panel_surface.blit(title_surface, (10, 10))

        # Draw items
        y_offset = 35
        for item in arch_items:
            text_surface = font.render(item, True, (255, 255, 255))
            panel_surface.blit(text_surface, (10, y_offset))
            y_offset += 25

        surface.blit(panel_surface, (panel_x, panel_y))

    def _draw_methods_panel(self, surface: pygame.Surface) -> None:
        """Draw methods active panel."""
        panel_x = 750  # Right side of screen

        methods_items = [
            "Methods Active:",
            "├─ _handle_input() - Player controls",
            "├─ _update_effects() - Visual effects",
            "├─ _draw_terrain() - Map rendering",
            "├─ _draw_units() - Character sprites",
            "├─ _draw_ui() - Interface panels",
            "└─ _update_ai() - AI decision making",
        ]

        # Calculate panel height and position so bottom aligns with controls text at y=750
        panel_width = 350
        panel_height = len(methods_items) * 25 + 30
        panel_y = (
            750 - panel_height - 24
        )  # Position so bottom aligns with controls text, moved up half tile (24px)

        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))

        # Draw border
        pygame.draw.rect(
            panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2
        )

        # Draw title
        font = pygame.font.Font(None, 20)
        title_surface = font.render("METHODS", True, (255, 255, 255))
        panel_surface.blit(title_surface, (10, 10))

        # Draw items
        y_offset = 35
        for item in methods_items:
            text_surface = font.render(item, True, (255, 255, 255))
            panel_surface.blit(text_surface, (10, y_offset))
            y_offset += 25

        surface.blit(panel_surface, (panel_x, panel_y))


def main():
    """Main entry point."""
    demo = BTFighterDemo(timeout_seconds=0)
    demo.run()


if __name__ == "__main__":
    main()
