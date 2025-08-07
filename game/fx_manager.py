"""FX Manager for Starter Town Tactics.

Handles visual effects like flashes, particles, screen shake,
and other visual feedback.
"""

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

    def __init__(self):
        """Initialize the FX manager."""
        self.effects: List[FXEffect] = []
        self.screen_shake_offset = (0, 0)
        self.screen_shake_decay = 0.9
        self.flash_surface: Optional[pygame.Surface] = None
        self.particle_surfaces: Dict[str, pygame.Surface] = {}

    def trigger_fx(
        self, fx_type: str, position: Tuple[int, int],
        duration: float = 0.5, intensity: float = 1.0,
        color: Tuple[int, int, int] = (255, 255, 255),
        size: int = 10, metadata: Optional[Dict[str, Any]] = None
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
            metadata=metadata or {}
        )
        self.effects.append(effect)
        print(f"✨ Triggered {fx_type} at {position}")

    def trigger_flash(
        self, position: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        duration: float = 0.3, intensity: float = 1.0
    ) -> None:
        """Trigger a flash effect."""
        self.trigger_fx(
            "flash", position, duration, intensity, color, size=10
        )

    def trigger_screen_shake(
        self, intensity: float = 5.0, duration: float = 0.5
    ) -> None:
        """Trigger screen shake effect."""
        self.trigger_fx(
            "screen_shake", (0, 0), duration, intensity,
            color=(255, 255, 255), size=10,
            metadata={"shake_intensity": intensity}
        )

    def trigger_particle(
        self, position: Tuple[int, int],
        particle_type: str = "sparkle",
        count: int = 5, duration: float = 1.0
    ) -> None:
        """Trigger particle effect."""
        for i in range(count):
            offset = (i * 2 - count, i * 2 - count)  # Spread particles
            pos = (position[0] + offset[0], position[1] + offset[1])
            self.trigger_fx(
                "particle", pos, duration, intensity=1.0,
                color=(255, 255, 255), size=10,
                metadata={"particle_type": particle_type}
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
                shake_intensity = (
                    effect.metadata.get("shake_intensity", 5.0)
                    if effect.metadata else 5.0
                )
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

    def _draw_flash(
        self, screen: pygame.Surface, effect: FXEffect, progress: float
    ) -> None:
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
                    effect.position[0] - effect.size,
                    effect.position[1] - effect.size,
                    effect.size * 2,
                    effect.size * 2
                )
                screen.blit(flash_surface, flash_rect, flash_rect)

    def _draw_particle(
        self, screen: pygame.Surface, effect: FXEffect, progress: float
    ) -> None:
        """Draw a particle effect."""
        # Simple particle as a colored circle
        if progress < 0.8:  # Particles fade out in last 20%
            alpha = int(255 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                # Create particle surface
                particle_size = max(2, int(effect.size * (1.0 - progress)))
                particle_surface = pygame.Surface(
                    (particle_size * 2, particle_size * 2), pygame.SRCALPHA
                )
                # Draw particle
                pygame.draw.circle(
                    particle_surface,
                    (*effect.color, alpha),
                    (particle_size, particle_size),
                    particle_size
                )
                screen.blit(
                    particle_surface,
                    (effect.position[0] - particle_size,
                     effect.position[1] - particle_size)
                )

    def _draw_glow(
        self, screen: pygame.Surface, effect: FXEffect, progress: float
    ) -> None:
        """Draw a glow effect."""
        # Simple glow as expanding circle
        if progress < 0.8:
            alpha = int(128 * (1.0 - progress) * effect.intensity)
            alpha = max(0, min(255, alpha))
            if alpha > 0:
                glow_size = int(effect.size * (1.0 + progress * 2))
                glow_surface = pygame.Surface(
                    (glow_size * 2, glow_size * 2), pygame.SRCALPHA
                )
                # Draw glow
                pygame.draw.circle(
                    glow_surface,
                    (*effect.color, alpha),
                    (glow_size, glow_size),
                    glow_size
                )
                screen.blit(
                    glow_surface,
                    (effect.position[0] - glow_size,
                     effect.position[1] - glow_size)
                )

    def clear_effects(self) -> None:
        """Clear all active effects."""
        self.effects.clear()
        self.screen_shake_offset = (0, 0)

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

    def get_shake_offset(self) -> Tuple[int, int]:
        """Get current screen shake offset for rendering."""
        return self.screen_shake_offset
