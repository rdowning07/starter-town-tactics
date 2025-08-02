#!/usr/bin/env python3
"""
Test script to verify sprite loading and display
"""

import pygame
import sys
from game.sprite_manager import SpriteManager

def test_sprite_loading():
    """Test that sprites can be loaded correctly."""
    print("🧪 Testing Sprite Loading System")
    print("=" * 50)
    
    # Initialize sprite manager
    sprites = SpriteManager()
    sprites.load_assets()
    
    # Test tileset loading
    print("\n📋 Tileset Information:")
    print(f"Available tilesets: {sprites.list_available_tilesets()}")
    
    for tileset_name in sprites.list_available_tilesets():
        info = sprites.get_tileset_info(tileset_name)
        file_path = sprites.get_tileset_file(tileset_name)
        tags = sprites.get_tileset_tags(tileset_name)
        layer = sprites.get_tileset_layer(tileset_name)
        
        print(f"  {tileset_name}:")
        print(f"    File: {file_path}")
        print(f"    Layer: {layer}")
        print(f"    Tags: {tags}")
    
    # Test unit loading
    print("\n👥 Unit Information:")
    print(f"Available units: {sprites.list_available_units()}")
    
    # Test a few specific units
    test_units = ["Recruit", "PhoenixBinder", "CrystalArchon"]
    for unit_name in test_units:
        sprite_path = sprites.get_unit_sprite(unit_name, "blue", 0)
        color = sprites.get_unit_color(unit_name)
        tier = sprites.get_unit_tier(unit_name)
        
        print(f"  {unit_name}:")
        print(f"    Sprite: {sprite_path}")
        print(f"    Color: {color}")
        print(f"    Tier: {tier}")
    
    # Test tier grouping
    print("\n🏆 Tier Information:")
    for tier in range(1, 6):
        units = sprites.get_units_by_tier(tier)
        if units:
            print(f"  Tier {tier}: {units}")
    
    print("\n✅ Sprite loading test completed!")

def test_pygame_display():
    """Test that sprites can be displayed in Pygame."""
    print("\n🎮 Testing Pygame Display")
    print("=" * 50)
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sprite Test")
    clock = pygame.time.Clock()
    
    sprites = SpriteManager()
    sprites.load_assets()
    
    # Load some test images
    test_images = {}
    
    # Try to load terrain
    terrain_path = sprites.get_terrain_sprite("terrain")
    if terrain_path:
        try:
            test_images['terrain'] = pygame.image.load(terrain_path)
            print(f"✅ Loaded terrain: {terrain_path}")
        except Exception as e:
            print(f"❌ Failed to load terrain: {e}")
    
    # Try to load unit sprites
    for unit_name in ["Recruit", "PhoenixBinder", "CrystalArchon"]:
        sprite_path = sprites.get_unit_sprite(unit_name, "blue", 0)
        if sprite_path:
            try:
                test_images[unit_name] = pygame.image.load(sprite_path)
                print(f"✅ Loaded {unit_name}: {sprite_path}")
            except Exception as e:
                print(f"❌ Failed to load {unit_name}: {e}")
    
    # Display loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((50, 50, 50))
        
        # Display loaded images
        y_offset = 50
        for name, image in test_images.items():
            # Scale image to 64x64 for display
            scaled = pygame.transform.scale(image, (64, 64))
            screen.blit(scaled, (50, y_offset))
            
            # Draw label
            font = pygame.font.Font(None, 24)
            text = font.render(name, True, (255, 255, 255))
            screen.blit(text, (120, y_offset + 20))
            
            y_offset += 80
        
        # Draw instructions
        font = pygame.font.Font(None, 20)
        instructions = [
            "Sprite Test - Press ESC to exit",
            f"Loaded {len(test_images)} images successfully"
        ]
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 500 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ Pygame display test completed!")

if __name__ == "__main__":
    test_sprite_loading()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--display":
        test_pygame_display()
    else:
        print("\n💡 Run with --display to test Pygame rendering:")
        print("   python test_sprites.py --display") 