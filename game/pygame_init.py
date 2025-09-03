"""
Pygame Initialization Utility

Provides centralized pygame initialization with proper error handling
and configuration for the tactical game engine.
"""

from typing import Optional, Tuple

import pygame


def init_pygame(
    window_size: Tuple[int, int] = (800, 600),
    window_title: str = "Starter Town Tactics",
    enable_sound: bool = True,
    enable_joystick: bool = False,
) -> bool:
    """
    Initialize pygame with proper configuration.

    Args:
        window_size: Tuple of (width, height) for the game window
        window_title: Title for the game window
        enable_sound: Whether to initialize the sound system
        enable_joystick: Whether to initialize joystick support

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        # Initialize pygame core
        pygame.init()
        print("✅ Pygame core initialized")

        # Set up display
        pygame.display.set_mode(window_size)
        pygame.display.set_caption(window_title)
        print(f"✅ Display initialized: {window_size[0]}x{window_size[1]}")

        # Initialize sound system
        if enable_sound:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                print("✅ Sound system initialized")
            except pygame.error as e:
                print(f"⚠️  Sound system initialization failed: {e}")
                print("   Game will continue without sound support")

        # Initialize joystick support
        if enable_joystick:
            try:
                pygame.joystick.init()
                joystick_count = pygame.joystick.get_count()
                if joystick_count > 0:
                    print(f"✅ Joystick support initialized: {joystick_count} device(s) found")
                else:
                    print("ℹ️  No joystick devices found")
            except pygame.error as e:
                print(f"⚠️  Joystick initialization failed: {e}")

        # Set up event handling
        pygame.event.set_allowed(
            [
                pygame.QUIT,
                pygame.KEYDOWN,
                pygame.KEYUP,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION,
            ]
        )
        print("✅ Event handling configured")

        return True

    except pygame.error as e:
        print(f"❌ Pygame initialization failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during pygame initialization: {e}")
        return False


def quit_pygame():
    """Safely quit pygame and clean up resources."""
    try:
        pygame.mixer.quit()
        pygame.joystick.quit()
        pygame.quit()
        print("✅ Pygame shutdown complete")
    except Exception as e:
        print(f"⚠️  Error during pygame shutdown: {e}")


def get_display_info() -> Optional[object]:
    """Get display information for debugging."""
    try:
        return pygame.display.Info()
    except pygame.error:
        return None


def set_window_icon(icon_path: str) -> bool:
    """Set the window icon."""
    try:
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
        print(f"✅ Window icon set: {icon_path}")
        return True
    except (pygame.error, FileNotFoundError) as e:
        print(f"⚠️  Failed to set window icon: {e}")
        return False


# Convenience function for quick initialization
def quick_init() -> bool:
    """Quick initialization with default settings."""
    return init_pygame(
        window_size=(1024, 768), window_title="Starter Town Tactics", enable_sound=True, enable_joystick=False
    )
