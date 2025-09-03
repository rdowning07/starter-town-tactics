"""
Placeholder asset generator for UI development.
Creates simple colored shapes when real assets are missing.
"""

from typing import Optional, Tuple

import pygame


def create_placeholder_rect(
    width: int, height: int, color: Tuple[int, int, int], border_color: Optional[Tuple[int, int, int]] = None
) -> pygame.Surface:
    """Create a colored rectangle placeholder."""
    surf = pygame.Surface((width, height))
    surf.fill(color)

    if border_color:
        pygame.draw.rect(surf, border_color, surf.get_rect(), 2)

    return surf


def create_placeholder_circle(
    radius: int, color: Tuple[int, int, int], border_color: Optional[Tuple[int, int, int]] = None
) -> pygame.Surface:
    """Create a colored circle placeholder."""
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius, radius), radius)

    if border_color:
        pygame.draw.circle(surf, border_color, (radius, radius), radius, 2)

    return surf


def create_placeholder_button(width: int = 100, height: int = 30) -> pygame.Surface:
    """Create a button placeholder."""
    return create_placeholder_rect(width, height, (100, 100, 200), (150, 150, 255))


def create_placeholder_panel(width: int = 200, height: int = 150) -> pygame.Surface:
    """Create a panel placeholder."""
    return create_placeholder_rect(width, height, (50, 50, 50), (100, 100, 100))


def create_placeholder_icon(size: int = 16, color: Tuple[int, int, int] = (255, 255, 255)) -> pygame.Surface:
    """Create an icon placeholder."""
    return create_placeholder_rect(size, size, color, (200, 200, 200))


def create_placeholder_unit_sprite(size: int = 32, team: str = "player") -> pygame.Surface:
    """Create a unit sprite placeholder."""
    if team == "player":
        color = (0, 255, 0)  # Green for player
    elif team == "enemy":
        color = (255, 0, 0)  # Red for enemy
    else:
        color = (255, 255, 0)  # Yellow for neutral

    return create_placeholder_circle(size // 2, color, (255, 255, 255))


def create_placeholder_terrain_tile(size: int = 32, terrain_type: str = "grass") -> pygame.Surface:
    """Create a terrain tile placeholder."""
    colors = {
        "grass": (34, 139, 34),
        "water": (0, 191, 255),
        "mountain": (139, 69, 19),
        "forest": (0, 100, 0),
        "road": (160, 82, 45),
        "wall": (128, 128, 128),
    }

    color = colors.get(terrain_type, (128, 128, 128))
    return create_placeholder_rect(size, size, color)


def create_placeholder_effect(size: int = 32, effect_type: str = "particle") -> pygame.Surface:
    """Create an effect placeholder."""
    colors = {"particle": (255, 255, 0), "aura": (255, 0, 255), "summoning": (0, 255, 255)}

    color = colors.get(effect_type, (255, 255, 255))
    return create_placeholder_circle(size // 2, color)


def create_placeholder_sound(duration: float = 0.1) -> bytes:
    """Create a silent WAV file placeholder."""
    # Generate a minimal silent WAV file
    sample_rate = 44100
    num_samples = int(duration * sample_rate)

    # WAV header (44 bytes)
    header = bytearray(44)

    # RIFF header
    header[0:4] = b"RIFF"
    header[4:8] = (36 + num_samples * 2).to_bytes(4, "little")  # File size
    header[8:12] = b"WAVE"

    # fmt chunk
    header[12:16] = b"fmt "
    header[16:20] = (16).to_bytes(4, "little")  # fmt chunk size
    header[20:22] = (1).to_bytes(2, "little")  # PCM format
    header[22:24] = (1).to_bytes(2, "little")  # Mono
    header[24:28] = sample_rate.to_bytes(4, "little")  # Sample rate
    header[28:32] = (sample_rate * 2).to_bytes(4, "little")  # Byte rate
    header[32:34] = (2).to_bytes(2, "little")  # Block align
    header[34:36] = (16).to_bytes(2, "little")  # Bits per sample

    # data chunk
    header[36:40] = b"data"
    header[40:44] = (num_samples * 2).to_bytes(4, "little")  # Data size

    # Silent audio data
    audio_data = b"\x00\x00" * num_samples

    return bytes(header) + audio_data
