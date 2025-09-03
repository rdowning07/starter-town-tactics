"""FX Manager for Starter Town Tactics.

Handles visual effects like flashes, particles, screen shake,
and other visual feedback.
"""

import math
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import pygame


class FXType(Enum):
    """Types of visual effects."""

    FLASH = "flash"
    SCREEN_SHAKE = "screen_shake"
    PARTICLE = "particle"
    FADE = "fade"
    GLOW = "glow"
    # Week 4 additions
    DAMAGE = "damage"
    HEAL = "heal"
    CRITICAL = "critical"
    STATUS_APPLY = "status_apply"
    STATUS_REMOVE = "status_remove"
    BUFF = "buff"
    DEBUFF = "debuff"
    # Week 5 additions
    SPARK = "spark"
    FIRE = "fire"
    ICE = "ice"
    COMBO = "combo"
    EXPLOSION = "explosion"
    MAGIC = "magic"


@dataclass
class FXEffect:
    """Represents a single visual effect."""

    fx_type: FXType
    position: Tuple[int, int]
    duration: float
    start_time: float
    intensity: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    size: int = 10
    active: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FXManager:
    """Manages visual effects for the game."""

    def __init__(self) -> None:
        """Initialize the FX manager."""
        self.effects: List[FXEffect] = []
        self.screen_shake_offset: Tuple[float, float] = (0.0, 0.0)
        self.screen_shake_decay = 0.9
        self.flash_surface: Optional[pygame.Surface] = None
        self.particle_surfaces: Dict[str, pygame.Surface] = {}

    def trigger_fx(
        self,
        fx_type: str,
        position: Tuple[int, int],
        duration: float = 0.5,
        intensity: float = 1.0,
        color: Tuple[int, int, int] = (255, 255, 255),
        size: int = 10,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Trigger a visual effect."""
        try:
            fx_enum = FXType(fx_type.lower())
        except ValueError:
            print(f"⚠️  Unknown FX type: {fx_type}")
            return
        effect = FXEffect(
            fx_type=fx_enum,
            position=position,
            duration=duration,
            start_time=time.time(),
            intensity=intensity,
            color=color,
            size=size,
            metadata=metadata or {},
        )
        self.effects.append(effect)
        print(f"✨ Triggered {fx_type} at {position}")

    def trigger_flash(
        self,
        position: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        duration: float = 0.3,
        intensity: float = 1.0,
    ) -> None:
        """Trigger a flash effect."""
        self.trigger_fx("flash", position, duration, intensity, color, size=10)

    def trigger_screen_shake(self, intensity: float = 5.0, duration: float = 0.5) -> None:
        """Trigger screen shake effect."""
        self.trigger_fx(
            "screen_shake",
            (0, 0),
            duration,
            intensity,
            color=(255, 255, 255),
            size=10,
            metadata={"shake_intensity": intensity},
        )

    def trigger_particle(
        self, position: Tuple[int, int], particle_type: str = "sparkle", count: int = 5, duration: float = 1.0
    ) -> None:
        """Trigger particle effect."""
        for i in range(count):
            offset = (i * 2 - count, i * 2 - count)  # Spread particles
            pos = (position[0] + offset[0], position[1] + offset[1])
            self.trigger_fx(
                "particle",
                pos,
                duration,
                intensity=1.0,
                color=(255, 255, 255),
                size=10,
                metadata={"particle_type": particle_type},
            )

    # Week 4 FX Methods
    def trigger_damage_fx(self, position: Tuple[int, int], damage: int) -> None:
        """Trigger damage visual effect."""
        self.trigger_fx(
            "damage",
            position,
            duration=1.0,
            intensity=1.0,
            color=(255, 0, 0),
            size=15,
            metadata={"damage_amount": damage},
        )

    def trigger_heal_fx(self, position: Tuple[int, int], healing: int) -> None:
        """Trigger healing visual effect."""
        self.trigger_fx(
            "heal", position, duration=1.0, intensity=1.0, color=(0, 255, 0), size=15, metadata={"heal_amount": healing}
        )

    def trigger_critical_fx(self, position: Tuple[int, int]) -> None:
        """Trigger critical hit visual effect."""
        self.trigger_fx("critical", position, duration=1.5, intensity=1.5, color=(255, 255, 0), size=20)
        # Add screen shake for critical hits
        self.trigger_screen_shake(intensity=3.0, duration=0.3)

    def trigger_status_apply_fx(self, position: Tuple[int, int], effect_type: str = "buff") -> None:
        """Trigger status effect application visual."""
        color = (0, 255, 0) if effect_type == "buff" else (255, 0, 0)
        self.trigger_fx(
            "status_apply",
            position,
            duration=0.8,
            intensity=1.0,
            color=color,
            size=12,
            metadata={"status_type": effect_type},
        )

    def trigger_status_remove_fx(self, position: Tuple[int, int]) -> None:
        """Trigger status effect removal visual."""
        self.trigger_fx("status_remove", position, duration=0.5, intensity=1.0, color=(255, 255, 255), size=8)

    # Week 5 Advanced Particle FX Methods
    def trigger_spark_fx(self, position: Tuple[int, int], count: int = 8) -> None:
        """Trigger spark particle effect."""
        for i in range(count):
            offset = (i * 3 - count * 1.5, i * 2 - count)
            pos = (position[0] + offset[0], position[1] + offset[1])
            self.trigger_fx(
                "spark",
                pos,
                duration=0.8,
                intensity=1.0,
                color=(255, 255, 0),
                size=4,
                metadata={"particle_type": "spark", "index": i},
            )

    def trigger_fire_fx(self, position: Tuple[int, int], intensity: float = 1.0) -> None:
        """Trigger fire particle effect."""
        self.trigger_fx(
            "fire",
            position,
            duration=1.2,
            intensity=intensity,
            color=(255, 100, 0),
            size=15,
            metadata={"particle_type": "fire", "flicker": True},
        )

    def trigger_ice_fx(self, position: Tuple[int, int], intensity: float = 1.0) -> None:
        """Trigger ice particle effect."""
        self.trigger_fx(
            "ice",
            position,
            duration=1.0,
            intensity=intensity,
            color=(100, 200, 255),
            size=12,
            metadata={"particle_type": "ice", "crystal": True},
        )

    def trigger_combo_fx(self, position: Tuple[int, int], combo_level: int = 1) -> None:
        """Trigger combo visual effect."""
        self.trigger_fx(
            "combo",
            position,
            duration=1.0,
            intensity=1.0 + combo_level * 0.2,
            color=(255, 255, 255),
            size=10 + combo_level * 2,
            metadata={"particle_type": "combo", "level": combo_level},
        )

    def trigger_explosion_fx(self, position: Tuple[int, int], radius: int = 20) -> None:
        """Trigger explosion effect with particles."""
        # Main explosion
        self.trigger_fx(
            "explosion",
            position,
            duration=1.5,
            intensity=1.5,
            color=(255, 200, 0),
            size=radius,
            metadata={"particle_type": "explosion", "radius": radius},
        )

        # Add screen shake
        self.trigger_screen_shake(intensity=5.0, duration=0.5)

        # Spark particles
        self.trigger_spark_fx(position, count=12)

    def trigger_magic_fx(self, position: Tuple[int, int], magic_type: str = "arcane") -> None:
        """Trigger magic visual effect."""
        colors = {"arcane": (200, 100, 255), "fire": (255, 100, 0), "ice": (100, 200, 255), "lightning": (255, 255, 0)}
        color = colors.get(magic_type, (200, 100, 255))

        self.trigger_fx(
            "magic",
            position,
            duration=1.2,
            intensity=1.0,
            color=color,
            size=18,
            metadata={"particle_type": "magic", "type": magic_type},
        )

    def update(self) -> None:
        """Update all active effects."""
        current_time = time.time()
        # Update screen shake
        self.screen_shake_offset = (0, 0)
        # Process effects
        active_effects = []
        for effect in self.effects:
            elapsed = current_time - effect.start_time
            if elapsed >= effect.duration:
                # Effect expired
                if effect.fx_type == FXType.SCREEN_SHAKE:
                    self.screen_shake_offset = (0, 0)
                continue
            # Effect still active
            active_effects.append(effect)
            # Update effect-specific logic
            if effect.fx_type == FXType.SCREEN_SHAKE:
                progress = elapsed / effect.duration
                intensity = effect.intensity * (1.0 - progress)
                shake_intensity = effect.metadata.get("shake_intensity", 5.0) if effect.metadata else 5.0
                shake_x = intensity * shake_intensity
                shake_y = intensity * shake_intensity
                self.screen_shake_offset = (shake_x, shake_y)
        self.effects = active_effects

    def draw_fx(self, screen: pygame.Surface) -> None:
        """Draw all active effects."""
        if not self.effects:
            return
        # Apply screen shake offset
        if self.screen_shake_offset != (0, 0):
            # Create a temporary surface for screen shake
            shake_surface = screen.copy()
            screen.fill((0, 0, 0))  # Clear screen
            screen.blit(shake_surface, self.screen_shake_offset)
        # Draw individual effects
        for effect in self.effects:
            self._draw_effect(screen, effect)

    def _draw_effect(self, screen: pygame.Surface, effect: FXEffect) -> None:
        """Draw a single effect."""
        current_time = time.time()
        elapsed = current_time - effect.start_time
        progress = elapsed / effect.duration
        if effect.fx_type == FXType.FLASH:
            self._draw_flash(screen, effect, progress)
        elif effect.fx_type == FXType.PARTICLE:
            self._draw_particle(screen, effect, progress)
        elif effect.fx_type == FXType.GLOW:
            self._draw_glow(screen, effect, progress)
        elif effect.fx_type == FXType.DAMAGE:
            self._draw_damage(screen, effect, progress)
        elif effect.fx_type == FXType.HEAL:
            self._draw_heal(screen, effect, progress)
        elif effect.fx_type == FXType.CRITICAL:
            self._draw_critical(screen, effect, progress)
        elif effect.fx_type == FXType.STATUS_APPLY:
            self._draw_status_apply(screen, effect, progress)
        elif effect.fx_type == FXType.STATUS_REMOVE:
            self._draw_status_remove(screen, effect, progress)
        elif effect.fx_type == FXType.SPARK:
            self._draw_spark(screen, effect, progress)
        elif effect.fx_type == FXType.FIRE:
            self._draw_fire(screen, effect, progress)
        elif effect.fx_type == FXType.ICE:
            self._draw_ice(screen, effect, progress)
        elif effect.fx_type == FXType.COMBO:
            self._draw_combo(screen, effect, progress)
        elif effect.fx_type == FXType.EXPLOSION:
            self._draw_explosion(screen, effect, progress)
        elif effect.fx_type == FXType.MAGIC:
            self._draw_magic(screen, effect, progress)

    def _draw_flash(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw a flash effect."""
        # Create flash surface if needed
        if self.flash_surface is None:
            self.flash_surface = pygame.Surface(screen.get_size())
            self.flash_surface.set_alpha(128)
        # Calculate alpha based on progress (fade out)
        alpha = int(255 * (1.0 - progress) * effect.intensity)
        alpha = max(0, min(255, alpha))
        if alpha > 0:
            flash_surface = self.flash_surface.copy()
            flash_surface.fill(effect.color)
            flash_surface.set_alpha(alpha)
            # Draw flash at position or full screen
            if effect.position == (0, 0):
                screen.blit(flash_surface, (0, 0))
            else:
                # Local flash around position
                flash_rect = pygame.Rect(
                    effect.position[0] - effect.size, effect.position[1] - effect.size, effect.size * 2, effect.size * 2
                )
                screen.blit(flash_surface, flash_rect, flash_rect)

    def _draw_particle(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw a particle effect."""
        # Simple particle as a colored circle
        if progress < 0.8:  # Particles fade out in last 20%
            alpha = int(255 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Create particle surface
                particle_size = max(2, int(effect.size * (1.0 - progress)))
                particle_surface = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                # Draw particle
                pygame.draw.circle(
                    particle_surface, (*effect.color, alpha), (particle_size, particle_size), particle_size
                )
                screen.blit(particle_surface, (effect.position[0] - particle_size, effect.position[1] - particle_size))

    def _draw_glow(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw a glow effect."""
        # Simple glow as expanding circle
        if progress < 0.8:
            alpha = int(128 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                glow_size = int(effect.size * (1.0 + progress * 2))
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                # Draw glow
                pygame.draw.circle(glow_surface, (*effect.color, alpha), (glow_size, glow_size), glow_size)
                screen.blit(glow_surface, (effect.position[0] - glow_size, effect.position[1] - glow_size))

    def clear_effects(self) -> None:
        """Clear all active effects."""
        self.effects.clear()
        self.screen_shake_offset = (0.0, 0.0)

    def get_active_effects_count(self) -> int:
        """Get the number of active effects."""
        return len(self.effects)

    def is_effect_active(self, fx_type: str) -> bool:
        """Check if any effect of the given type is active."""
        try:
            fx_enum = FXType(fx_type.lower())
            return any(effect.fx_type == fx_enum for effect in self.effects)
        except ValueError:
            return False

    def get_shake_offset(self) -> Tuple[float, float]:
        """Get current screen shake offset for rendering."""
        return self.screen_shake_offset

    # Week 4 Drawing Methods
    def _draw_damage(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw damage effect with floating text."""
        if progress < 1.0:
            # Floating damage text
            damage = effect.metadata.get("damage_amount", 0) if effect.metadata else 0
            text = f"-{damage}"

            # Create font for damage text
            font = pygame.font.Font(None, 24)

            # Calculate position (float upward)
            float_offset = int(progress * 30)  # Float up 30 pixels
            text_pos = (effect.position[0], effect.position[1] - float_offset)

            # Calculate alpha (fade out)
            alpha = int(255 * (1.0 - progress))

            # Render text
            text_surface = font.render(text, True, effect.color)
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, text_pos)

    def _draw_heal(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw heal effect with floating text and glow."""
        if progress < 1.0:
            # Floating heal text
            healing = effect.metadata.get("heal_amount", 0) if effect.metadata else 0
            text = f"+{healing}"

            # Create font for heal text
            font = pygame.font.Font(None, 24)

            # Calculate position (float upward)
            float_offset = int(progress * 30)  # Float up 30 pixels
            text_pos = (effect.position[0], effect.position[1] - float_offset)

            # Calculate alpha (fade out)
            alpha = int(255 * (1.0 - progress))

            # Render text
            text_surface = font.render(text, True, effect.color)
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, text_pos)

            # Add glow effect
            glow_size = int(effect.size * (1.0 + progress))
            glow_alpha = int(64 * (1.0 - progress))
            if glow_alpha > 0:
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*effect.color, glow_alpha), (glow_size, glow_size), glow_size)
                screen.blit(glow_surface, (effect.position[0] - glow_size, effect.position[1] - glow_size))

    def _draw_critical(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw critical hit effect with burst and text."""
        if progress < 1.0:
            # Critical text
            text = "CRITICAL!"
            font = pygame.font.Font(None, 32)

            # Scale effect
            scale = 1.0 + (1.0 - progress) * 0.5  # Start big, shrink

            # Calculate alpha
            alpha = int(255 * (1.0 - progress))

            # Render text with scale effect
            text_surface = font.render(text, True, effect.color)
            text_surface.set_alpha(alpha)

            # Scale the text surface
            scaled_width = int(text_surface.get_width() * scale)
            scaled_height = int(text_surface.get_height() * scale)
            if scaled_width > 0 and scaled_height > 0:
                scaled_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))
                text_rect = scaled_surface.get_rect(center=effect.position)
                screen.blit(scaled_surface, text_rect)

            # Add burst particles
            particle_count = 8
            for i in range(particle_count):
                angle = (i / particle_count) * 2 * 3.14159  # Full circle
                distance = progress * 40  # Expand outward
                particle_x = effect.position[0] + int(distance * math.cos(angle))
                particle_y = effect.position[1] + int(distance * math.sin(angle))

                particle_alpha = int(128 * (1.0 - progress))
                if particle_alpha > 0:
                    particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, (*effect.color, particle_alpha), (3, 3), 3)
                    screen.blit(particle_surface, (particle_x - 3, particle_y - 3))

    def _draw_status_apply(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw status effect application."""
        if progress < 1.0:
            # Pulsing circle effect
            pulse = 1.0 + 0.3 * math.sin(progress * 6.28)  # Sine wave pulse
            size = int(effect.size * pulse)
            alpha = int(128 * (1.0 - progress))

            if alpha > 0:
                circle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (*effect.color, alpha), (size, size), size, 2)
                screen.blit(circle_surface, (effect.position[0] - size, effect.position[1] - size))

    def _draw_status_remove(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw status effect removal."""
        if progress < 1.0:
            # Shrinking circle effect
            size = int(effect.size * (1.0 - progress))
            alpha = int(255 * (1.0 - progress))

            if alpha > 0 and size > 0:
                circle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (*effect.color, alpha), (size, size), size)
                screen.blit(circle_surface, (effect.position[0] - size, effect.position[1] - size))

    # Week 5 Advanced Particle Drawing Methods
    def _draw_spark(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw spark particle effect."""
        if progress < 0.8:
            alpha = int(255 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Spark as small bright circle
                spark_size = max(1, int(effect.size * (1.0 - progress * 0.5)))
                spark_surface = pygame.Surface((spark_size * 2, spark_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(spark_surface, (*effect.color, alpha), (spark_size, spark_size), spark_size)
                screen.blit(spark_surface, (effect.position[0] - spark_size, effect.position[1] - spark_size))

    def _draw_fire(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw fire particle effect."""
        if progress < 1.0:
            alpha = int(128 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Fire as flickering flame
                fire_size = int(effect.size * (1.0 + progress * 0.3))
                fire_surface = pygame.Surface((fire_size * 2, fire_size * 2), pygame.SRCALPHA)

                # Flicker effect
                flicker = 1.0 + 0.2 * math.sin(progress * 20)
                flicker_alpha = int(alpha * flicker)

                pygame.draw.circle(fire_surface, (*effect.color, flicker_alpha), (fire_size, fire_size), fire_size)
                screen.blit(fire_surface, (effect.position[0] - fire_size, effect.position[1] - fire_size))

    def _draw_ice(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw ice particle effect."""
        if progress < 1.0:
            alpha = int(150 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Ice as crystalline shape
                ice_size = int(effect.size * (1.0 - progress * 0.2))
                ice_surface = pygame.Surface((ice_size * 2, ice_size * 2), pygame.SRCALPHA)

                # Draw diamond shape
                points = [
                    (ice_size, ice_size - ice_size // 2),
                    (ice_size + ice_size // 2, ice_size),
                    (ice_size, ice_size + ice_size // 2),
                    (ice_size - ice_size // 2, ice_size),
                ]
                pygame.draw.polygon(ice_surface, (*effect.color, alpha), points)
                screen.blit(ice_surface, (effect.position[0] - ice_size, effect.position[1] - ice_size))

    def _draw_combo(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw combo visual effect."""
        if progress < 1.0:
            alpha = int(255 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Combo as expanding ring
                combo_size = int(effect.size * (1.0 + progress * 2))
                combo_surface = pygame.Surface((combo_size * 2, combo_size * 2), pygame.SRCALPHA)

                # Draw ring
                pygame.draw.circle(combo_surface, (*effect.color, alpha), (combo_size, combo_size), combo_size, 3)
                screen.blit(combo_surface, (effect.position[0] - combo_size, effect.position[1] - combo_size))

    def _draw_explosion(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw explosion effect."""
        if progress < 1.0:
            alpha = int(200 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Explosion as expanding circle with particles
                explosion_size = int(effect.size * (1.0 + progress * 3))
                explosion_surface = pygame.Surface((explosion_size * 2, explosion_size * 2), pygame.SRCALPHA)

                # Main explosion
                pygame.draw.circle(
                    explosion_surface, (*effect.color, alpha), (explosion_size, explosion_size), explosion_size
                )

                # Inner glow
                inner_alpha = int(alpha * 0.5)
                inner_size = explosion_size // 2
                pygame.draw.circle(
                    explosion_surface, (*effect.color, inner_alpha), (explosion_size, explosion_size), inner_size
                )

                screen.blit(
                    explosion_surface, (effect.position[0] - explosion_size, effect.position[1] - explosion_size)
                )

    def _draw_magic(self, screen: pygame.Surface, effect: FXEffect, progress: float) -> None:
        """Draw magic visual effect."""
        if progress < 1.0:
            alpha = int(180 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Magic as pulsing star
                magic_size = int(effect.size * (1.0 + 0.3 * math.sin(progress * 10)))
                magic_surface = pygame.Surface((magic_size * 2, magic_size * 2), pygame.SRCALPHA)

                # Draw star shape
                center = (magic_size, magic_size)
                points = []
                for i in range(8):
                    angle = i * math.pi / 4
                    radius = magic_size if i % 2 == 0 else magic_size // 2
                    x = center[0] + radius * math.cos(angle)
                    y = center[1] + radius * math.sin(angle)
                    points.append((x, y))

                pygame.draw.polygon(magic_surface, (*effect.color, alpha), points)
                screen.blit(magic_surface, (effect.position[0] - magic_size, effect.position[1] - magic_size))
