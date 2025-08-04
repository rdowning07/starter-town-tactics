#!/usr/bin/env python3
"""
Sprite Sheet Usage Demo

This script demonstrates how to use the sprite sheet loading functionality
with the new animation system.
"""

import pygame
import sys
from pathlib import Path

# Add game directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.sprite_manager import SpriteManager
from game.pygame_init import init_pygame, quit_pygame
from game.unit import Unit

def demo_sprite_sheet_usage():
    """Demonstrate sprite sheet loading and usage."""
    
    print("🎬 Sprite Sheet Usage Demo")
    print("=" * 40)
    
    # Initialize pygame
    if not init_pygame(window_size=(800, 600), window_title="Sprite Sheet Demo"):
        print("❌ Failed to initialize pygame")
        return
    
    try:
        # Create sprite manager
        sprite_manager = SpriteManager()
        
        print("\n📁 Loading animations...")
        
        # Method 1: Load from sprite sheet (if available)
        sheet_path = "assets/units/knight/attack.png"
        if Path(sheet_path).exists():
            print(f"✅ Loading from sprite sheet: {sheet_path}")
            sprite_manager.load_unit_animation_from_sheet(
                unit_id="knight",
                animation_name="attack",
                sheet_path=sheet_path,
                frame_width=32,
                frame_height=32
            )
        else:
            print(f"⚠️  Sprite sheet not found: {sheet_path}")
            print("   Using fallback animation...")
            
            # Create fallback animation
            frames = []
            colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]
            for color in colors:
                frame = pygame.Surface((32, 32))
                frame.fill(color)
                frames.append(frame)
            
            sprite_manager.load_unit_animation("knight", "attack", frames)
        
        # Method 2: Load from folder structure (if available)
        knight_folder = "assets/units/knight"
        if Path(knight_folder).exists():
            print(f"✅ Loading from folder structure: {knight_folder}")
            sprite_manager.load_unit_animations_from_folder("knight", knight_folder)
        
        # Create test units
        knight = Unit("knight", 2, 2, "player", health=10)
        knight.set_animation("attack", duration=30)
        
        # Demo loop
        print("\n🎭 Running animation demo...")
        print("Press any key to cycle animations, ESC to quit")
        
        screen = pygame.display.get_surface()
        clock = pygame.time.Clock()
        
        animations = ["idle", "attack", "walk"]
        current_anim = 0
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # Cycle through animations
                        current_anim = (current_anim + 1) % len(animations)
                        knight.set_animation(animations[current_anim], duration=30)
                        print(f"🎬 Switched to: {animations[current_anim]}")
            
            # Clear screen
            screen.fill((50, 50, 50))
            
            # Update unit animation
            knight.update_animation()
            
            # Get current sprite
            current_sprite = knight.get_current_sprite(sprite_manager)
            
            # Draw sprite at center
            sprite_rect = current_sprite.get_rect()
            sprite_rect.center = (400, 300)
            screen.blit(current_sprite, sprite_rect)
            
            # Draw info
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Animation: {knight.current_animation}",
                f"Timer: {knight.animation_timer}",
                f"Team: {knight.team}",
                f"HP: {knight.hp}",
                "",
                "Controls:",
                "SPACE - Cycle animations",
                "ESC - Quit"
            ]
            
            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
            
            pygame.display.flip()
            clock.tick(10)  # 10 FPS
        
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
    
    finally:
        quit_pygame()

def show_integration_examples():
    """Show code examples for integration."""
    
    print("\n📝 Integration Examples:")
    print("=" * 40)
    
    print("\n1. Basic Sprite Sheet Loading:")
    print("""
sprite_manager = SpriteManager()

# Load from sprite sheet
sprite_manager.load_unit_animation_from_sheet(
    unit_id="knight",
    animation_name="attack",
    sheet_path="assets/units/knight/attack.png",
    frame_width=32,
    frame_height=32
)
""")
    
    print("\n2. Folder Structure Loading:")
    print("""
# Load all animations for a unit
sprite_manager.load_unit_animations_from_folder(
    unit_id="knight",
    unit_folder="assets/units/knight"
)

# Load all units at once
sprite_manager.load_all_unit_animations()
""")
    
    print("\n3. Unit Animation Integration:")
    print("""
# Create unit with animation
unit = Unit("knight", 2, 2, "player", health=10)
unit.set_animation("attack", duration=30)

# Get current sprite for rendering
current_sprite = unit.get_current_sprite(sprite_manager)
screen.blit(current_sprite, position)
""")
    
    print("\n4. Pygame Initialization:")
    print("""
from game.pygame_init import init_pygame, quit_pygame

# Initialize with custom settings
init_pygame(
    window_size=(1024, 768),
    window_title="My Game",
    enable_sound=True,
    enable_joystick=False
)

# Clean shutdown
quit_pygame()
""")

if __name__ == "__main__":
    show_integration_examples()
    demo_sprite_sheet_usage() 