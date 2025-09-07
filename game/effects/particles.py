"""
Particle System for Starter Town Tactics.

Provides confetti and ember particle effects for victory and defeat.
"""

import math
import random
import time
from typing import List, Optional, Tuple

import pygame


class Particle:
    """Individual particle for effects."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        size: int,
        lifetime: float,
    ):
        """Initialize a particle.

        Args:
            x, y: Starting position
            vx, vy: Velocity
            color: RGB color tuple
            size: Particle size in pixels
            lifetime: How long the particle lives in seconds
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.0
        self.fade = True

    def update(self, dt: float) -> bool:
        """Update particle position and lifetime.

        Args:
            dt: Delta time in seconds

        Returns:
            True if particle is still alive, False if it should be removed
        """
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Apply gravity
        self.vy += self.gravity * dt

        # Update lifetime
        self.lifetime -= dt

        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the particle.

        Args:
            screen: The pygame surface to draw on
        """
        if self.lifetime <= 0:
            return

        # Calculate alpha based on lifetime
        alpha = 255
        if self.fade:
            alpha = int(255 * (self.lifetime / self.max_lifetime))

        # Create surface with alpha
        particle_surface = pygame.Surface(
            (self.size * 2, self.size * 2), pygame.SRCALPHA
        )
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(
            particle_surface, color_with_alpha, (self.size, self.size), self.size
        )

        # Draw particle
        screen.blit(particle_surface, (self.x - self.size, self.y - self.size))


class ParticleSystem:
    """Particle system for creating effects."""

    def __init__(self, max_count: int = 200):
        """Initialize the particle system.

        Args:
            max_count: Maximum number of particles
        """
        self.particles: List[Particle] = []
        self.max_count = max_count

    def add_confetti_burst(self, x: float, y: float, count: int = 50) -> None:
        """Add a confetti burst effect.

        Args:
            x, y: Center position for the burst
            count: Number of particles to create
        """
        colors = [
            (255, 215, 0),  # Gold
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 255, 0),  # Yellow
        ]

        for _ in range(min(count, self.max_count - len(self.particles))):
            # Random direction and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(50, 150)  # Upward bias

            # Random properties
            color = random.choice(colors)
            size = random.randint(2, 6)
            lifetime = random.uniform(1.0, 3.0)

            particle = Particle(x, y, vx, vy, color, size, lifetime)
            particle.gravity = 200.0  # Fall down
            self.particles.append(particle)

        print(f"Confetti burst: {count} particles at ({x:.1f}, {y:.1f})")

    def add_ember_burst(self, x: float, y: float, count: int = 30) -> None:
        """Add an ember burst effect.

        Args:
            x, y: Center position for the burst
            count: Number of particles to create
        """
        colors = [
            (139, 0, 0),  # Dark red
            (255, 69, 0),  # Red orange
            (255, 140, 0),  # Dark orange
            (255, 165, 0),  # Orange
            (255, 215, 0),  # Gold
        ]

        for _ in range(min(count, self.max_count - len(self.particles))):
            # Random direction and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed + random.uniform(-50, 50)  # More random

            # Random properties
            color = random.choice(colors)
            size = random.randint(1, 4)
            lifetime = random.uniform(0.5, 2.0)

            particle = Particle(x, y, vx, vy, color, size, lifetime)
            particle.gravity = 100.0  # Lighter gravity than confetti
            self.particles.append(particle)

        print(f"Ember burst: {count} particles at ({x:.1f}, {y:.1f})")

    def update(self, dt: float) -> None:
        """Update all particles.

        Args:
            dt: Delta time in seconds
        """
        # Update particles and remove dead ones
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all particles.

        Args:
            screen: The pygame surface to draw on
        """
        for particle in self.particles:
            particle.draw(screen)

    def clear(self) -> None:
        """Clear all particles."""
        self.particles.clear()

    def get_particle_count(self) -> int:
        """Get the current number of particles.

        Returns:
            Number of active particles
        """
        return len(self.particles)
