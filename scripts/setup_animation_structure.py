#!/usr/bin/env python3
"""
Setup Animation Structure Script

This script creates standardized animation folder structure for all units:
units/
└── unit_name/
    ├── idle/
    │   ├── frame_0.png
    │   └── frame_1.png
    └── attack/
        ├── frame_0.png
        ├── frame_1.png
        └── frame_2.png
"""

import os
import shutil
import glob
from pathlib import Path

def create_animation_structure():
    """Create standardized animation structure for all units."""
    
    units_dir = Path("assets/units")
    if not units_dir.exists():
        print("❌ assets/units directory not found!")
        return
    
    # Get all unit directories
    unit_dirs = [d for d in units_dir.iterdir() if d.is_dir()]
    
    print(f"🎯 Found {len(unit_dirs)} unit directories")
    
    for unit_dir in unit_dirs:
        unit_name = unit_dir.name
        print(f"\n📁 Processing: {unit_name}")
        
        # Create animation directories
        idle_dir = unit_dir / "idle"
        attack_dir = unit_dir / "attack"
        walk_dir = unit_dir / "walk"
        
        idle_dir.mkdir(exist_ok=True)
        attack_dir.mkdir(exist_ok=True)
        walk_dir.mkdir(exist_ok=True)
        
        # Get existing sprites
        existing_sprites = list(unit_dir.glob("*.png"))
        
        if not existing_sprites:
            print(f"  ⚠️  No sprites found for {unit_name}")
            continue
        
        print(f"  📄 Found {len(existing_sprites)} existing sprites")
        
        # Organize sprites based on naming pattern
        if _is_numbered_sprite_format(existing_sprites):
            _organize_numbered_sprites(unit_dir, existing_sprites)
        else:
            _organize_simple_sprites(unit_dir, existing_sprites)
        
        print(f"  ✅ Animation structure created for {unit_name}")

def _is_numbered_sprite_format(sprites):
    """Check if sprites use numbered format (e.g., blue_0_0.png)."""
    for sprite in sprites:
        if "_" in sprite.stem and sprite.stem.split("_")[-1].isdigit():
            return True
    return False

def _organize_numbered_sprites(unit_dir, sprites):
    """Organize numbered sprites into animation folders."""
    
    # Group sprites by their sequence number (last number in filename)
    sequences = {}
    
    for sprite in sprites:
        parts = sprite.stem.split("_")
        if len(parts) >= 2 and parts[-1].isdigit():
            sequence_num = int(parts[-1])
            if sequence_num not in sequences:
                sequences[sequence_num] = []
            sequences[sequence_num].append(sprite)
    
    # Create idle animation (first few frames)
    idle_dir = unit_dir / "idle"
    idle_frames = sorted(sequences.keys())[:2]  # First 2 frames for idle
    
    for i, frame_num in enumerate(idle_frames):
        for sprite in sequences[frame_num]:
            new_name = f"frame_{i}.png"
            new_path = idle_dir / new_name
            shutil.copy2(sprite, new_path)
            print(f"    🎬 Created idle frame {i}: {sprite.name} -> {new_name}")
    
    # Create attack animation (middle frames)
    attack_dir = unit_dir / "attack"
    attack_frames = sorted(sequences.keys())[2:5]  # Next 3 frames for attack
    
    for i, frame_num in enumerate(attack_frames):
        for sprite in sequences[frame_num]:
            new_name = f"frame_{i}.png"
            new_path = attack_dir / new_name
            shutil.copy2(sprite, new_path)
            print(f"    ⚔️  Created attack frame {i}: {sprite.name} -> {new_name}")
    
    # Create walk animation (remaining frames)
    walk_dir = unit_dir / "walk"
    walk_frames = sorted(sequences.keys())[5:8]  # Next 3 frames for walk
    
    for i, frame_num in enumerate(walk_frames):
        for sprite in sequences[frame_num]:
            new_name = f"frame_{i}.png"
            new_path = walk_dir / new_name
            shutil.copy2(sprite, new_path)
            print(f"    🚶 Created walk frame {i}: {sprite.name} -> {new_name}")

def _organize_simple_sprites(unit_dir, sprites):
    """Organize simple sprites (e.g., blue.png, red.png) into animation folders."""
    
    idle_dir = unit_dir / "idle"
    attack_dir = unit_dir / "attack"
    
    # For simple sprites, create basic animations
    if len(sprites) >= 1:
        # Use first sprite for idle frame 0
        shutil.copy2(sprites[0], idle_dir / "frame_0.png")
        print(f"    🎬 Created idle frame 0: {sprites[0].name}")
        
        # Use first sprite for idle frame 1 (same sprite, different timing)
        shutil.copy2(sprites[0], idle_dir / "frame_1.png")
        print(f"    🎬 Created idle frame 1: {sprites[0].name}")
    
    if len(sprites) >= 2:
        # Use second sprite for attack frame 0
        shutil.copy2(sprites[1], attack_dir / "frame_0.png")
        print(f"    ⚔️  Created attack frame 0: {sprites[1].name}")
        
        # Use first sprite for attack frame 1 (return to base)
        shutil.copy2(sprites[0], attack_dir / "frame_1.png")
        print(f"    ⚔️  Created attack frame 1: {sprites[0].name}")
        
        # Use second sprite for attack frame 2 (attack pose)
        shutil.copy2(sprites[1], attack_dir / "frame_2.png")
        print(f"    ⚔️  Created attack frame 2: {sprites[1].name}")
    else:
        # If only one sprite, use it for all attack frames
        for i in range(3):
            shutil.copy2(sprites[0], attack_dir / f"frame_{i}.png")
            print(f"    ⚔️  Created attack frame {i}: {sprites[0].name}")

def create_animation_config():
    """Create animation configuration file."""
    
    config_content = """# Animation Configuration
# This file defines animation settings for each unit type

animations:
  idle:
    frame_duration: 500  # milliseconds
    loop: true
    frames: ["frame_0.png", "frame_1.png"]
  
  attack:
    frame_duration: 200  # milliseconds
    loop: false
    frames: ["frame_0.png", "frame_1.png", "frame_2.png"]
  
  walk:
    frame_duration: 300  # milliseconds
    loop: true
    frames: ["frame_0.png", "frame_1.png", "frame_2.png"]

# Unit-specific overrides
unit_overrides:
  knight:
    attack:
      frame_duration: 150  # Faster attack
  mage:
    attack:
      frame_duration: 400  # Slower attack
"""
    
    config_path = Path("data/animation_config.yaml")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"📝 Created animation config: {config_path}")

def main():
    """Main function to set up animation structure."""
    print("🎬 Setting up animation structure for all units...")
    
    try:
        create_animation_structure()
        create_animation_config()
        
        print("\n✅ Animation structure setup complete!")
        print("\n📁 New structure created:")
        print("   units/")
        print("   └── unit_name/")
        print("       ├── idle/")
        print("       │   ├── frame_0.png")
        print("       │   └── frame_1.png")
        print("       ├── attack/")
        print("       │   ├── frame_0.png")
        print("       │   ├── frame_1.png")
        print("       │   └── frame_2.png")
        print("       └── walk/")
        print("           ├── frame_0.png")
        print("           ├── frame_1.png")
        print("           └── frame_2.png")
        
    except Exception as e:
        print(f"❌ Error setting up animation structure: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 