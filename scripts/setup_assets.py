#!/usr/bin/env python3
"""
Asset Setup Script for Starter Town Tactics
Helps organize and validate asset structure
"""

import os
import sys
from pathlib import Path


def create_asset_structure():
    """Create the recommended asset directory structure."""
    
    # Define the asset structure
    asset_structure = {
        "assets/tiles/terrain": [
            "grass.png",
            "forest.png", 
            "mountain.png",
            "water.png",
            "road.png",
            "wall.png"
        ],
        "assets/tiles/elevation": [
            "level_1.png",
            "level_2.png",
            "level_3.png"
        ],
        "assets/tiles/special": [
            "lava.png",
            "ice.png",
            "portal.png"
        ],
        "assets/units/knight": [
            "blue.png",
            "red.png",
            "neutral.png"
        ],
        "assets/units/archer": [
            "blue.png",
            "red.png"
        ],
        "assets/units/mage": [
            "blue.png",
            "red.png"
        ],
        "assets/units/goblin": [
            "ai.png"
        ],
        "assets/units/ai": [
            "boss.png",
            "minion.png"
        ],
        "assets/ui/cursors": [
            "normal.png",
            "select.png",
            "attack.png"
        ],
        "assets/ui/icons": [
            "health.png",
            "ap.png",
            "move.png",
            "attack.png"
        ],
        "assets/ui/panels": [
            "healthbar.png",
            "menu_bg.png",
            "button.png"
        ],
        "assets/effects/particles": [
            "attack.png",
            "heal.png",
            "death.png"
        ],
        "assets/effects/animations/walk": [],
        "assets/effects/animations/attack": []
    }
    
    print("🎨 Setting up asset directory structure...")
    
    for directory, files in asset_structure.items():
        # Create directory
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")
        
        # Create placeholder files (empty PNGs or text files)
        for file in files:
            file_path = Path(directory) / file
            if not file_path.exists():
                # Create a simple placeholder
                with open(file_path, 'w') as f:
                    f.write(f"# Placeholder for {file}\n")
                    f.write(f"# Replace with actual asset from recommended sources\n")
                print(f"    📄 Created placeholder: {file}")
    
    print("\n✅ Asset structure created successfully!")


def print_asset_guide():
    """Print quick asset acquisition guide."""
    
    print("\n" + "="*60)
    print("🎯 QUICK ASSET ACQUISITION GUIDE")
    print("="*60)
    
    print("\n📥 SAFEST SOURCES:")
    print("1. OpenGameArt.org - Search '32x32 tileset', 'tactical rpg'")
    print("2. Kenney.nl - Download 'RPG Asset Pack' (free, CC0)")
    print("3. Itch.io - Search 'free tactical assets'")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Download assets from recommended sources")
    print("2. Replace placeholder files in assets/ directory")
    print("3. Ensure all assets are 32x32 pixels (PNG format)")
    print("4. Test with: python main.py")
    
    print("\n⚠️  SAFETY CHECKLIST:")
    print("- [ ] Check license (CC0, CC-BY, MIT are safe)")
    print("- [ ] Verify format (PNG with transparency)")
    print("- [ ] Confirm size (32x32 or 64x64 pixels)")
    print("- [ ] Test in game")
    
    print("\n📚 DETAILED GUIDE:")
    print("See: docs/asset_guide.md for complete instructions")


def validate_assets():
    """Check if assets are properly organized."""
    
    print("\n🔍 Validating asset structure...")
    
    required_dirs = [
        "assets/tiles/terrain",
        "assets/units/knight", 
        "assets/ui/icons"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for directory in missing_dirs:
            print(f"  - {directory}")
        print("\nRun this script to create the structure.")
        return False
    
    print("✅ Asset structure is valid!")
    return True


def main():
    """Main function."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_assets()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "guide":
        print_asset_guide()
        return
    
    # Default: create structure and show guide
    create_asset_structure()
    print_asset_guide()
    
    print(f"\n🚀 Ready to add assets! Check {os.path.abspath('docs/asset_guide.md')} for detailed instructions.")


if __name__ == "__main__":
    main() 