#!/usr/bin/env python3
"""
New Terrain Demo - Simple colored grid terrain like units_fx_demo.py.
"""

import sys
from pathlib import Path

import pygame

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.demo_base import DemoBase


class NewTerrainDemo(DemoBase):
    """Demo for simple terrain grid."""

    def __init__(self, timeout_seconds: int = 30):
        """Initialize the demo."""
        super().__init__(timeout_seconds=timeout_seconds, auto_exit=True)

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("New Terrain Demo - Simple Grid")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Demo state
        self.camera_x = 0
        self.camera_y = 0
        self.tile_size = 32

    def _handle_input(self) -> bool:
        """Handle input events. Returns False to quit."""
        for event in pygame.event.get():
            if self.handle_exit_events(event):
                return False

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

    def _draw_terrain(self, surface: pygame.Surface) -> None:
        """Draw simple terrain grid like units_fx_demo.py."""
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

    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Draw UI overlay."""
        # Instructions
        instructions = [
            "Arrow keys: Move camera",
            "ESC: Quit",
        ]

        y_offset = 10
        for instruction in instructions:
            text = self.font.render(instruction, True, (255, 255, 255))
            surface.blit(text, (10, y_offset))
            y_offset += 25

    def run(self) -> None:
        """Run the demo."""
        print(f"🎮 Starting New Terrain Demo (timeout: {self.timeout_seconds}s)")

        while not self.should_exit():
            # Handle input
            if not self._handle_input():
                break

            # Draw
            self.screen.fill((0, 0, 0))

            # Render terrain
            self._draw_terrain(self.screen)

            # Draw UI
            self._draw_ui(self.screen)

            # Draw timeout info
            self.draw_timeout_info(self.screen, self.font)

            pygame.display.flip()
            self.clock.tick(60)

        print("👋 New Terrain Demo finished")
        pygame.quit()


def main():
    """Main entry point."""
    demo = NewTerrainDemo()
    demo.run()


if __name__ == "__main__":
    main()
