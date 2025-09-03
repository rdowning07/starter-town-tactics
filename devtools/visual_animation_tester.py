# devtools/visual_animation_tester.py

import json
import os
import signal
import sys
import time
from pathlib import Path

import pygame

from game.fx_manager import FXManager
from game.pygame_init import init_pygame, quit_pygame
from game.renderer import Renderer
from game.sound_manager import SoundManager
from game.sprite_manager import SpriteManager

FPS = 8
WINDOW_SIZE = (400, 400)
ASSET_PATH = "assets/units"

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global shutdown_requested  # pylint: disable=global-statement
    shutdown_requested = True
    print("\n⏹️  Shutdown requested...")


def load_animation_metadata(unit_id: str):
    """Load animation metadata for a unit."""
    metadata_path = os.path.join(ASSET_PATH, unit_id, "animation_metadata.json")
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    with open(metadata_path, encoding="utf-8") as f:
        return json.load(f)


def get_available_units():
    """Get list of units that have animation metadata."""
    units = []
    units_dir = Path(ASSET_PATH)

    if not units_dir.exists():
        return units

    for unit_dir in units_dir.iterdir():
        if unit_dir.is_dir():
            metadata_path = unit_dir / "animation_metadata.json"
            if metadata_path.exists():
                units.append(unit_dir.name)

    return sorted(units)


def setup_animation_tester(unit_id, enable_sound):
    """Setup animation tester components."""
    # Load metadata
    metadata = load_animation_metadata(unit_id)
    animations = list(metadata.keys())

    if not animations:
        print("❌ No animations found in metadata!")
        return None

    print(f"✅ Loaded {len(animations)} animations: {animations}")

    # Setup display
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    # Initialize managers
    sprite_manager = SpriteManager()
    sound_manager = SoundManager(enable_sound=enable_sound)
    fx_manager = FXManager()
    # Note: renderer is initialized but not used in this demo
    _renderer = Renderer(screen, sprite_manager)

    # Load sounds
    sound_manager.load_sound("slash", "assets/sfx/slash.wav")
    sound_manager.load_sound("death", "assets/sfx/death.wav")
    sound_manager.load_sound("move", "assets/sfx/move.wav")
    sound_manager.load_sound("select", "assets/sfx/select.wav")

    return {
        "metadata": metadata,
        "animations": animations,
        "screen": screen,
        "clock": clock,
        "sprite_manager": sprite_manager,
        "sound_manager": sound_manager,
        "fx_manager": fx_manager,
    }


def handle_animation_events(
    event, current_anim_index, animations, metadata, frame_index, frame_timer, sound_manager, load_func, auto_play
):
    """Handle pygame events for animation control."""
    if event.type == pygame.QUIT:
        return False, current_anim_index, frame_index, frame_timer, auto_play
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return False, current_anim_index, frame_index, frame_timer, auto_play
        if event.key == pygame.K_RIGHT:
            return True, current_anim_index, frame_index + 1, 0, auto_play
        if event.key == pygame.K_LEFT:
            return True, current_anim_index, frame_index - 1, 0, auto_play
        if event.key == pygame.K_SPACE:
            new_anim_index = (current_anim_index + 1) % len(animations)
            sound_manager.play("select")
            if load_func():
                return True, new_anim_index, 0, 0, auto_play
            return True, current_anim_index, frame_index, frame_timer, auto_play
        if event.key == pygame.K_a:
            new_auto_play = not auto_play
            print(f"🔄 Auto-play: {'ON' if new_auto_play else 'OFF'}")
            return True, current_anim_index, frame_index, frame_timer, new_auto_play
    return True, current_anim_index, frame_index, frame_timer, auto_play


def main():
    """Main function with improved error handling and unit selection."""

    # Enable mute via CLI flag
    enable_sound = "--mute" not in sys.argv

    # Add timeout for automated testing
    timeout_seconds = 10  # 10 second timeout for testing
    start_time = time.time()

    # Get available units
    available_units = get_available_units()

    if not available_units:
        print("❌ No units with animation metadata found!")
        print(f"   Expected metadata files in: {ASSET_PATH}/*/animation_metadata.json")
        return 1

    # Select unit (use command line argument or default to first)
    unit_id = sys.argv[1] if len(sys.argv) > 1 else available_units[0]

    if unit_id not in available_units:
        print(f"❌ Unit '{unit_id}' not found or has no metadata!")
        print(f"   Available units: {available_units}")
        return 1

    print("🎬 Visual Animation Tester")
    print(f"📁 Unit: {unit_id}")
    print(f"🔊 Sound: {'Enabled' if enable_sound else 'Muted'}")

    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize pygame
    if not init_pygame(window_size=WINDOW_SIZE, window_title=f"Animation Tester - {unit_id}"):
        print("❌ Failed to initialize pygame")
        return 1

    try:
        # Setup components
        components = setup_animation_tester(unit_id, enable_sound)
        if not components:
            return 1

        metadata = components["metadata"]
        animations = components["animations"]
        screen = components["screen"]
        clock = components["clock"]
        sprite_manager = components["sprite_manager"]
        sound_manager = components["sound_manager"]
        fx_manager = components["fx_manager"]

        # Load first animation
        current_anim_index = 0
        frame_index = 0
        current_animation = animations[current_anim_index]
        anim_data = metadata[current_animation]

        def load_current_animation():
            """Load the current animation into sprite manager."""
            sprite_path = os.path.join(ASSET_PATH, unit_id, f"{current_animation}.png")
            if not os.path.exists(sprite_path):
                print(f"⚠️  Sprite sheet not found: {sprite_path}")
                return False

            try:
                # Use default frame dimensions for the new metadata format
                frame_width = 32  # Default frame width
                frame_height = 32  # Default frame height

                sprite_manager.load_unit_animation_from_sheet(
                    unit_id, current_animation, sprite_path, frame_width, frame_height
                )
                print(f"✅ Loaded {current_animation} with {anim_data.get('frame_count', 'unknown')} frames")
                return True
            except (OSError, pygame.error) as e:
                print(f"❌ Failed to load animation: {e}")
                return False

        if not load_current_animation():
            return 1

        # Main loop
        running = True
        auto_play = False
        frame_timer = 0

        print("\n🎮 Controls:")
        print("  SPACE - Switch animation")
        print("  LEFT/RIGHT - Frame by frame")
        print("  A - Toggle auto-play")
        print("  ESC - Quit")
        print(f"  ⏰ Auto-exit after {timeout_seconds} seconds (for testing)")

        while running:
            # Check for shutdown request
            if shutdown_requested:
                print("\n⏹️  Shutdown requested, exiting...")
                break

            # Check timeout for automated testing
            if time.time() - start_time > timeout_seconds:
                print(f"\n⏰ Timeout reached ({timeout_seconds}s), exiting...")
                break

            screen.fill((20, 20, 20))

            # Handle events
            for event in pygame.event.get():
                running, current_anim_index, frame_index, frame_timer, auto_play = handle_animation_events(
                    event,
                    current_anim_index,
                    animations,
                    metadata,
                    frame_index,
                    frame_timer,
                    sound_manager,
                    load_current_animation,
                    auto_play,
                )
                if not running:
                    break

                # Update animation data if animation changed
                if current_animation != animations[current_anim_index]:
                    current_animation = animations[current_anim_index]
                    anim_data = metadata[current_animation]

            if not running:
                break

            # Auto-play logic
            if auto_play:
                frame_timer += 1
                if frame_timer >= FPS:
                    frame_index += 1
                    frame_timer = 0

                    # Play sound effects and trigger visual effects based on animation metadata
                    if frame_index in anim_data.get("sound_at", []):
                        if current_animation == "attack":
                            sound_manager.play("slash")
                            # Trigger flash effect for attack
                            fx_manager.trigger_flash((WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2), (255, 0, 0), 0.2)
                        elif current_animation == "walk":
                            sound_manager.play("move")
                            # Trigger particle effect for movement
                            fx_manager.trigger_particle((WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2), "sparkle", 3, 0.5)

                    # Trigger visual effects based on animation metadata
                    if frame_index in anim_data.get("fx_at", []):
                        print(f"🎬 Triggering FX for {current_animation} frame {frame_index}")
                        unit_position = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
                        if current_animation == "attack":
                            fx_manager.trigger_fx("flash", unit_position)
                            fx_manager.trigger_fx("screen_shake", unit_position)  # Screen shake!
                        elif current_animation == "walk":
                            fx_manager.trigger_particle(unit_position, "sparkle", 5, 0.8)

            # Get current sprite
            try:
                sprite = sprite_manager.get_unit_sprite(unit_id, current_animation, frame_index)
                if sprite:
                    rect = sprite.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
                    screen.blit(sprite, rect)
            except (OSError, pygame.error) as e:
                print(f"⚠️  Error rendering sprite: {e}")

            # Update FX and render with screen shake
            fx_manager.update()
            # Note: In a real game, you would call renderer.render() here
            # For this demo, we just draw FX effects directly
            fx_manager.draw_fx(screen)

            # Draw UI
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Unit: {unit_id}",
                f"Animation: {current_animation}",
                f"Frame: {frame_index + 1}/{anim_data.get('frame_count', 'unknown')}",
                f"Auto-play: {'ON' if auto_play else 'OFF'}",
                f"FX Active: {fx_manager.get_active_effects_count()}",
                "",
                "Controls: SPACE=Switch, A=Auto, ←→=Frame, ESC=Quit",
            ]

            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))

            pygame.display.flip()
            clock.tick(FPS)

        print("✅ Animation tester completed")
        return 0

    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user (Ctrl+C)")
        return 0
    except (OSError, ValueError) as e:
        print(f"❌ Error in animation tester: {e}")
        return 1

    finally:
        if "sound_manager" in locals():
            sound_manager.cleanup()
        if "fx_manager" in locals():
            fx_manager.clear_effects()
        quit_pygame()


if __name__ == "__main__":
    sys.exit(main())
