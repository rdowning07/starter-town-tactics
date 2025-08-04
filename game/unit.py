# @api
# game/unit.py

"""Defines the Unit class for game entities."""
from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.grid import Grid


# @api
class Unit:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        team: str,
        symbol: str | None = None,
        move_range: int = 3,
        health: int = 10,
        hp: int | None = None,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.team = team
        self.symbol = symbol or name[0].upper()
        self.move_range = move_range
        self.health = health
        self.hp = hp if hp is not None else health
        self.remaining_moves = move_range
        
        # Animation support
        self.current_animation = "idle"
        self.animation_timer = 0

    # @refactor - fixed movement to properly account for terrain cost only
    def move(self, new_x: int, new_y: int, grid: Grid) -> bool:
        # Disallow diagonal movement and enforce range
        dx = abs(new_x - self.x)
        dy = abs(new_y - self.y)
        if dx + dy == 0:
            return False  # No movement
        if dx > 0 and dy > 0:
            return False  # Diagonal movement not allowed
        if dx + dy > self.remaining_moves:
            return False  # Too far
        if not grid.is_within_bounds(new_x, new_y):
            return False
        dest_tile = grid.get_tile(new_x, new_y)
        if dest_tile.unit:
            return False
        cost = dest_tile.movement_cost
        print(
            f"DEBUG: Trying to move from ({self.x},{self.y}) to "
            f"({new_x},{new_y}), cost={cost}, "
            f"remaining_moves={self.remaining_moves}"
        )
        if cost > self.remaining_moves:
            return False
        # Perform movement
        grid.get_tile(self.x, self.y).unit = None
        dest_tile.unit = self
        self.x, self.y = new_x, new_y
        self.remaining_moves -= cost
        return True

    def move_to(self, x: int, y: int) -> None:
        """Directly sets unit's position (used in tests)."""
        self.x = x
        self.y = y

    def is_alive(self) -> bool:
        """Returns True if unit has HP > 0."""
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        """Reduces HP by amount and sets appropriate animation."""
        self.hp = max(0, self.hp - amount)
        
        # Set animation based on damage
        if self.hp <= 0:
            self.set_animation("die")
        elif amount >= 3:
            self.set_animation("stun")
        else:
            self.set_animation("hurt")

    # Animation support
    def set_animation(self, name: str, duration: int = 10) -> None:
        """Set the current animation state."""
        self.current_animation = name
        self.animation_timer = duration

    def update_animation(self) -> None:
        """Update animation timer and reset to idle when done."""
        if self.animation_timer > 0:
            self.animation_timer -= 1
        if self.animation_timer == 0:
            self.current_animation = "idle"

    def get_current_sprite(self, sprite_manager) -> pygame.Surface:
        """Get the current sprite for this unit based on animation state."""
        if hasattr(sprite_manager, 'get_unit_sprite'):
            # Calculate frame index based on animation timer
            if self.animation_timer > 0:
                # For attack animations, use timer to determine frame
                if self.current_animation == "attack":
                    frame_index = max(0, 30 - self.animation_timer) // 10  # 3 frames over 30 ticks
                else:
                    frame_index = (30 - self.animation_timer) % 2  # 2 frames for idle/walk
            else:
                frame_index = 0
            
            sprite = sprite_manager.get_unit_sprite(self.name, state=self.current_animation, frame_index=frame_index)
            if sprite:
                return sprite
        
        # Fallback: create a colored rectangle based on team
        fallback = pygame.Surface((32, 32))
        if self.team == "player":
            fallback.fill((0, 255, 0))  # Green for player
        elif self.team == "ai":
            fallback.fill((255, 0, 0))  # Red for AI
        else:
            fallback.fill((128, 128, 128))  # Gray for neutral
        
        return fallback
