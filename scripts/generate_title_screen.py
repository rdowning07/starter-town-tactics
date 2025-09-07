#!/usr/bin/env python3
"""
Generate the title screen image for Starter Town Tactics.

This script creates a title screen that matches the description provided.
"""

import os
import sys
from pathlib import Path

import pygame

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_title_screen():
    """Create the title screen image."""
    # Initialize pygame
    pygame.init()

    # Create surface - use a reasonable size
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    # Create the title screen surface
    title_surface = pygame.Surface((width, height))

    # Fill with parchment-like background
    # Light beige/cream color
    parchment_color = (245, 245, 220)  # Beige
    title_surface.fill(parchment_color)

    # Add subtle map-like lines
    line_color = (200, 180, 160)  # Slightly darker beige
    for i in range(0, width, 40):
        pygame.draw.line(title_surface, line_color, (i, 0), (i, height), 1)
    for i in range(0, height, 40):
        pygame.draw.line(title_surface, line_color, (0, i), (width, i), 1)

    # Create fonts
    try:
        # Try to use a serif font for the main title
        title_font = pygame.font.Font(None, 72)
        subtitle_font = pygame.font.Font(None, 32)
        press_start_font = pygame.font.Font(None, 48)
        copyright_font = pygame.font.Font(None, 24)
    except:
        # Fallback to default font
        title_font = pygame.font.Font(None, 72)
        subtitle_font = pygame.font.Font(None, 32)
        press_start_font = pygame.font.Font(None, 48)
        copyright_font = pygame.font.Font(None, 24)

    # Main title
    title_text = title_font.render("STARTER TOWN TACTICS", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(width // 2, height // 2 - 80))
    title_surface.blit(title_text, title_rect)

    # Japanese subtitle
    subtitle_text = subtitle_font.render(
        "スタータータウン タクティクス", True, (0, 0, 0)
    )
    subtitle_rect = subtitle_text.get_rect(center=(width // 2, height // 2 - 30))
    title_surface.blit(subtitle_text, subtitle_rect)

    # Decorative lines around subtitle
    line_start_x = subtitle_rect.left - 20
    line_end_x = subtitle_rect.right + 20
    line_y = subtitle_rect.centery
    pygame.draw.line(
        title_surface, (0, 0, 0), (line_start_x, line_y), (line_end_x, line_y), 2
    )

    # Press Start text
    press_start_text = press_start_font.render("Press Start", True, (0, 100, 200))
    press_start_rect = press_start_text.get_rect(center=(width // 2, height // 2 + 30))
    title_surface.blit(press_start_text, press_start_rect)

    # Copyright
    copyright_text = copyright_font.render("2025 Rob Downing", True, (0, 0, 0))
    copyright_rect = copyright_text.get_rect(center=(width // 2, height - 40))
    title_surface.blit(copyright_text, copyright_rect)

    # Draw simple character silhouettes behind the title
    # These represent the four characters mentioned in the description
    char_color = (100, 80, 60)  # Brown for silhouettes

    # Character 1 (left)
    char1_x = width // 2 - 150
    char1_y = height // 2 - 20
    pygame.draw.ellipse(title_surface, char_color, (char1_x, char1_y, 40, 60))

    # Character 2 (middle-left)
    char2_x = width // 2 - 80
    char2_y = height // 2 - 20
    pygame.draw.ellipse(title_surface, char_color, (char2_x, char2_y, 35, 55))

    # Character 3 (middle-right)
    char3_x = width // 2 + 45
    char3_y = height // 2 - 20
    pygame.draw.ellipse(title_surface, char_color, (char3_x, char3_y, 35, 55))

    # Character 4 (right)
    char4_x = width // 2 + 110
    char4_y = height // 2 - 20
    pygame.draw.ellipse(title_surface, char_color, (char4_x, char4_y, 40, 60))

    # Draw simple background structures
    # Tent/hut on left
    tent_x = 50
    tent_y = height - 150
    tent_points = [
        (tent_x, tent_y + 50),
        (tent_x + 20, tent_y),
        (tent_x + 40, tent_y + 50),
    ]
    pygame.draw.polygon(title_surface, (120, 100, 80), tent_points)

    # Gate/archway in center
    gate_x = width // 2 - 30
    gate_y = height - 120
    pygame.draw.rect(title_surface, (80, 60, 40), (gate_x, gate_y, 60, 80))
    pygame.draw.rect(title_surface, parchment_color, (gate_x + 10, gate_y + 20, 40, 60))

    # Tent/hut on right
    tent2_x = width - 90
    tent2_y = height - 150
    tent2_points = [
        (tent2_x, tent2_y + 50),
        (tent2_x + 20, tent2_y),
        (tent2_x + 40, tent2_y + 50),
    ]
    pygame.draw.polygon(title_surface, (120, 100, 80), tent2_points)

    # Small star logo in bottom right
    star_x = width - 40
    star_y = height - 30
    star_points = [
        (star_x, star_y - 10),
        (star_x + 3, star_y - 3),
        (star_x + 10, star_y),
        (star_x + 3, star_y + 3),
        (star_x, star_y + 10),
        (star_x - 3, star_y + 3),
        (star_x - 10, star_y),
        (star_x - 3, star_y - 3),
    ]
    pygame.draw.polygon(title_surface, (255, 255, 255), star_points)

    # Save the image
    output_path = (
        Path(__file__).parent.parent / "assets" / "ui" / "title" / "title_screen.png"
    )
    pygame.image.save(title_surface, str(output_path))
    print(f"Title screen saved to: {output_path}")

    # Clean up
    pygame.quit()

    return str(output_path)


if __name__ == "__main__":
    create_title_screen()
