"""
Outcome Orchestrator for Starter Town Tactics.

Coordinates all cinematic effects for victory and defeat outcomes.
"""

import time
from typing import Optional

from game.effects.particles import ParticleSystem
from game.services.music_manager import MusicManager
from game.services.slowmo import SlowMo
from game.ui.banners import VictoryBanner
from game.ui.gradient_sweep import GradientSweep


class OutcomeOrchestrator:
    """Orchestrates all outcome effects for dramatic presentation."""

    def __init__(
        self,
        slowmo: SlowMo,
        gradient: GradientSweep,
        particles: ParticleSystem,
        banners: VictoryBanner,
        music: MusicManager,
    ):
        """Initialize the outcome orchestrator.

        Args:
            slowmo: Slow motion system
            gradient: Gradient sweep overlay
            particles: Particle system
            banners: Victory/defeat banners
            music: Music manager
        """
        self.slowmo = slowmo
        self.gradient = gradient
        self.particles = particles
        self.banners = banners
        self.music = music

        self.active = False
        self.outcome: Optional[str] = None
        self.start_time: Optional[float] = None

    def trigger_victory(self, center_x: float = 600, center_y: float = 400) -> None:
        """Trigger all victory effects.

        Args:
            center_x, center_y: Center position for particle effects
        """
        self.active = True
        self.outcome = "victory"
        self.start_time = time.time()

        print("🎉 VICTORY ORCHESTRATION STARTED")

        # 1. Slow motion for dramatic effect
        self.slowmo.trigger(slow_factor=0.3, duration=1.5)

        # 2. Victory banner
        self.banners.show_victory()

        # 3. Victory fanfare music
        self.music.play("assets/music/Victory.mp3", volume=0.7, loop=False)

        # 4. Gold gradient sweep
        self.gradient.trigger("victory", duration=2.0)

        # 5. Confetti burst
        self.particles.add_confetti_burst(center_x, center_y, count=60)

    def trigger_defeat(self, center_x: float = 600, center_y: float = 400) -> None:
        """Trigger all defeat effects.

        Args:
            center_x, center_y: Center position for particle effects
        """
        self.active = True
        self.outcome = "defeat"
        self.start_time = time.time()

        print("💀 DEFEAT ORCHESTRATION STARTED")

        # 1. Slow motion for dramatic effect
        self.slowmo.trigger(slow_factor=0.2, duration=2.0)

        # 2. Defeat banner
        self.banners.show_defeat()

        # 3. Red gradient sweep
        self.gradient.trigger("defeat", duration=2.5)

        # 4. Ember burst
        self.particles.add_ember_burst(center_x, center_y, count=40)

    def update(self, dt: float) -> None:
        """Update all orchestrated effects.

        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return

        # Update all systems
        self.particles.update(dt)
        # Gradient update is handled in draw method

        # Check if effects should end
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            if elapsed > 3.0:  # End orchestration after 3 seconds
                self.active = False
                self.outcome = None
                self.start_time = None
                print("Outcome orchestration completed")

    def draw(self, screen) -> None:
        """Draw all orchestrated effects.

        Args:
            screen: The pygame surface to draw on
        """
        if not self.active:
            return

        # Draw particles first (behind other effects)
        self.particles.draw(screen)

        # Draw gradient overlay
        self.gradient.draw(screen)

        # Banner is drawn separately by the main game loop

    def is_active(self) -> bool:
        """Check if orchestration is currently active.

        Returns:
            True if orchestration is active, False otherwise
        """
        return self.active

    def get_outcome(self) -> Optional[str]:
        """Get the current outcome being orchestrated.

        Returns:
            Current outcome ("victory", "defeat", or None)
        """
        return self.outcome
