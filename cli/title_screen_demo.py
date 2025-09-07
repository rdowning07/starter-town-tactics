#!/usr/bin/env python3
"""
Title Screen Demo - Shows the title screen for 20 seconds before starting the main demo.

This demo demonstrates the title screen integration with the game flow.
"""

import sys
from pathlib import Path

import pygame

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.ui.title_screen import TitleScreen


class TitleScreenDemo:
    """Demo that shows title screen followed by main game."""

    def __init__(self):
        """Initialize the demo."""
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Starter Town Tactics - Title Screen Demo")
        self.clock = pygame.time.Clock()

        # Initialize title screen
        self.title_screen = TitleScreen(duration_seconds=7.0)

        # Demo state
        self.running = True
        self.showing_title = True

        # Start the title screen
        self.title_screen.start()

        print("Title Screen Demo initialized")
        print("The title screen will display for 20 seconds")
        print("Press ESC or close the window to exit")

    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.showing_title:
                    # Allow skipping the title screen with space
                    self.title_screen.skip()
                    self.showing_title = False
                    print("Title screen skipped - starting main demo")

    def update(self, dt: float) -> None:
        """Update the demo state."""
        if self.showing_title:
            # Update title screen
            still_showing = self.title_screen.update(dt)
            if not still_showing:
                self.showing_title = False
                print("Title screen completed - starting main demo")
        else:
            # Here you would normally update the main game
            # For this demo, we'll just show a simple message
            pass

    def draw(self) -> None:
        """Draw the current state."""
        self.screen.fill((0, 0, 0))  # Black background

        if self.showing_title:
            # Draw title screen
            self.title_screen.draw(self.screen)

            # Show instructions
            font = pygame.font.Font(None, 24)
            instruction_text = font.render(
                "Press SPACE to skip title screen", True, (255, 255, 255)
            )
            self.screen.blit(instruction_text, (10, 10))

            # Show remaining time
            remaining_time = self.title_screen.get_remaining_time()
            time_text = font.render(
                f"Time remaining: {remaining_time:.1f}s", True, (255, 255, 255)
            )
            self.screen.blit(time_text, (10, 40))
        else:
            # Draw main demo content
            font = pygame.font.Font(None, 48)
            title_text = font.render("Main Demo Started!", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(450, 200))
            self.screen.blit(title_text, title_rect)

            # Show some demo content
            demo_font = pygame.font.Font(None, 32)
            demo_text = demo_font.render(
                "Title screen demo completed successfully!", True, (200, 200, 200)
            )
            demo_rect = demo_text.get_rect(center=(450, 300))
            self.screen.blit(demo_text, demo_rect)

            # Show instructions
            instruction_font = pygame.font.Font(None, 24)
            instruction_text = instruction_font.render(
                "Press ESC to exit", True, (150, 150, 150)
            )
            instruction_rect = instruction_text.get_rect(center=(450, 400))
            self.screen.blit(instruction_text, instruction_rect)

    def run(self) -> None:
        """Run the demo."""
        print("Starting Title Screen Demo...")

        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds

            self.handle_events()
            self.update(dt)
            self.draw()

            pygame.display.flip()

        print("Title Screen Demo finished")
        pygame.quit()


def main():
    """Main entry point."""
    demo = TitleScreenDemo()
    demo.run()


if __name__ == "__main__":
    main()
