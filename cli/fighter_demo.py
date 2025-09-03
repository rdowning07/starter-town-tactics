#!/usr/bin/env python3
"""
Fighter Demo - Shows a fighter unit on green terrain with directional controls.
"""

from pathlib import Path

import pygame

from game.AnimationCatalog import AnimationCatalog
from game.demo_base import DemoBase
from game.UnitRenderer import UnitRenderer


class FighterDemo(DemoBase):
    """Demo showing a fighter unit with directional controls."""

    def __init__(self, timeout_seconds: int = 30):
        super().__init__(timeout_seconds=timeout_seconds, auto_exit=True)

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Fighter Demo - Arrow keys to move, ESC to quit")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Initialize unit system
        self.anim_catalog = AnimationCatalog(Path("assets/units/_metadata/animation_metadata.json"))
        self.unit_renderer = UnitRenderer(self.anim_catalog, tile_size=(32, 32))

        # Fighter state
        self.fighter_pos = [5, 5]  # Grid position
        self.fighter_direction = "down"  # Current facing
        self.fighter_state = "idle"  # idle or walk
        self.camera_x = 0
        self.camera_y = 0

        # Animation timing
        self.start_time = pygame.time.get_ticks()

    def _handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_demo()
                return

    def _draw_terrain(self, surface: pygame.Surface) -> None:
        """Draw simple green terrain grid."""
        tile_size = 32
        for y in range(20):
            for x in range(25):
                rect = pygame.Rect(
                    x * tile_size - self.camera_x,
                    y * tile_size - self.camera_y,
                    tile_size,
                    tile_size,
                )
                color = (100, 150, 100) if (x + y) % 2 == 0 else (80, 120, 80)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (50, 50, 50), rect, 1)

    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Draw UI information."""
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = f"Time: {elapsed}s"
        pos_text = f"Fighter: ({self.fighter_pos[0]:.1f}, {self.fighter_pos[1]:.1f})"
        state_text = f"State: {self.fighter_state}_{self.fighter_direction}"

        time_surface = self.font.render(time_text, True, (255, 255, 255))
        pos_surface = self.font.render(pos_text, True, (255, 255, 255))
        state_surface = self.font.render(state_text, True, (255, 255, 255))

        surface.blit(time_surface, (10, 10))
        surface.blit(pos_surface, (10, 35))
        surface.blit(state_surface, (10, 60))

        # Instructions
        instructions = ["Controls:", "WASD or Arrow Keys - Move fighter", "ESC - Quit"]

        for i, instruction in enumerate(instructions):
            text_surface = self.font.render(instruction, True, (200, 200, 200))
            surface.blit(text_surface, (10, 500 + i * 25))

    def run(self) -> None:
        """Run the fighter demo."""
        while not self.should_exit():
            # Handle events
            for event in pygame.event.get():
                self._handle_input(event)

            # Handle continuous input (key states)
            keys = pygame.key.get_pressed()
            speed = 8

            # Camera movement (Arrow keys only)
            self.camera_x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * speed
            self.camera_y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed

            # Fighter movement and animation (WASD only)
            if keys[pygame.K_w]:
                self.fighter_direction = "up"
                self.fighter_state = "walk"
            elif keys[pygame.K_s]:
                self.fighter_direction = "down"
                self.fighter_state = "walk"
            elif keys[pygame.K_a]:
                self.fighter_direction = "left"
                self.fighter_state = "walk"
            elif keys[pygame.K_d]:
                self.fighter_direction = "right"
                self.fighter_state = "walk"
            else:
                self.fighter_state = "idle"

            # Update fighter position based on movement
            if self.fighter_state == "walk":
                if self.fighter_direction == "up":
                    self.fighter_pos[1] -= 0.1
                elif self.fighter_direction == "down":
                    self.fighter_pos[1] += 0.1
                elif self.fighter_direction == "left":
                    self.fighter_pos[0] -= 0.1
                elif self.fighter_direction == "right":
                    self.fighter_pos[0] += 0.1

            # Clear screen
            self.screen.fill((0, 0, 0))

            # Draw terrain
            self._draw_terrain(self.screen)

            # Draw fighter
            elapsed_ms = pygame.time.get_ticks() - self.start_time
            fighter_state = f"{self.fighter_state}_{self.fighter_direction}"

            self.unit_renderer.draw_unit(
                surface=self.screen,
                unit_sprite="fighter",
                state=fighter_state,
                grid_xy=(int(self.fighter_pos[0]), int(self.fighter_pos[1])),
                camera_px=(self.camera_x, self.camera_y),
                elapsed_ms=elapsed_ms,
            )

            # Draw UI
            self._draw_ui(self.screen)

            # Draw timeout info
            self.draw_timeout_info(self.screen, self.font)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def main():
    """Main entry point."""
    demo = FighterDemo(timeout_seconds=30)
    demo.run()


if __name__ == "__main__":
    main()
