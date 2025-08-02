# Asset Management Guide for Starter Town Tactics

## 🎯 Quick Start - Safe Asset Sources

### **Immediate Recommendations:**

1. **OpenGameArt.org** - Search for:
   - "32x32 tileset"
   - "tactical rpg"
   - "isometric tiles"
   - "rpg character sprites"

2. **Kenney.nl** - Download:
   - "RPG Asset Pack" (free)
   - "UI Pack" (free)
   - "Tiny Characters" (free)

3. **Itch.io** - Search for:
   - "free tactical assets"
   - "rpg tileset free"
   - "32x32 sprites"

## 📁 Asset Organization Structure

```
assets/
├── tiles/
│   ├── castle/           # Castle environments
│   │   └── castle.png
│   ├── desert/           # Desert environments
│   │   └── desert.png
│   ├── dungeon/          # Dungeon environments
│   │   └── dungeon.png
│   ├── house/            # House environments
│   │   └── house.png
│   ├── interior/         # Interior environments
│   │   └── inside.png
│   ├── village/          # Village environments
│   │   └── outside.png
│   ├── terrain/          # General terrain
│   │   └── terrain.png
│   ├── water/            # Water environments
│   │   └── water.png
│   └── worldmap/         # World map tiles
│       └── world.png
├── units/
│   ├── Recruit/          # Tier 1 - Basic units
│   │   ├── blue_0_0.png  # Animation frames 0-11
│   │   ├── blue_0_1.png
│   │   └── ... (12 frames total)
│   ├── PhoenixBinder/    # Tier 3 - Elite units
│   │   ├── blue_1_0.png  # Animation frames 0-11
│   │   └── ... (12 frames total)
│   ├── CrystalArchon/    # Tier 3 - Elite units
│   │   ├── blue_2_0.png  # Animation frames 0-11
│   │   └── ... (12 frames total)
│   └── ... (34 unit types total)
├── ui/
│   ├── cursors/          # Mouse cursors
│   │   ├── normal.png
│   │   ├── select.png
│   │   └── attack.png
│   ├── icons/            # UI icons
│   │   ├── health.png
│   │   ├── ap.png
│   │   ├── move.png
│   │   └── attack.png
│   └── panels/           # UI panels
│       ├── healthbar.png
│       ├── menu_bg.png
│       └── button.png
└── effects/              # Visual effects
    ├── particles/        # Particle effects
    │   ├── attack.png
    │   ├── heal.png
    │   └── death.png
    ├── summoning/        # Summoning effects
    │   ├── portal.png
    │   ├── sparkle.png
    │   └── energy.png
    └── aura/             # Buff/debuff auras
        ├── buff.png
        ├── debuff.png
        └── shield.png
```

## 🎨 Asset Specifications

### **Unit Assets (32x32 pixels with 12 animation frames):**
- **Format**: PNG with transparency
- **Style**: Consistent art style (pixel art recommended)
- **Animation**: 12 frames per unit (0-11)
- **Naming**: `blue_[unit_id]_[frame].png` (e.g., `blue_0_0.png` to `blue_0_11.png`)
- **Team Variations**: Blue team sprites (red team variations planned)

### **Tile Assets (Environment-based, 32x32 pixels):**
- **Format**: PNG with transparency
- **Style**: Consistent art style (pixel art recommended)
- **Environments**: Castle, Desert, Dungeon, House, Interior, Village, Terrain, Water, Worldmap
- **Colors**: 16-32 colors for good performance
- **Naming**: `[environment].png` (e.g., `castle.png`, `desert.png`)

### **UI Assets:**
- **Format**: PNG with transparency
- **Style**: Clean, readable at small sizes
- **Colors**: High contrast for visibility

## 🔧 Integration with SpriteManager

### **Enhanced SpriteManager Implementation:**

```python
class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.animations = {}
        self.unit_mapping = {}
        self.tier_groups = {}
        self._load_sprite_mapping()
    
    def get_unit_sprite(self, unit_type: str, team: str = "blue", frame: int = 0):
        """Get unit sprite with animation frame support."""
        key = f"unit_{unit_type}_{team}_{frame}"
        return self.sprites.get(key)
    
    def get_unit_animation_frames(self, unit_type: str, team: str = "blue"):
        """Get all animation frames for a unit."""
        frames = []
        for frame in range(12):
            sprite = self.get_unit_sprite(unit_type, team, frame)
            if sprite:
                frames.append(sprite)
        return frames
    
    def get_units_by_tier(self, tier: int):
        """Get all units of a specific tier."""
        return self.tier_groups.get(tier, [])
```

## 🎯 Unit Tier System

### **Tier 1 - Basic Units:**
- Recruit, Acolyte, Apprentice, Squire, Scavenger
- **Color Themes**: Blue, Green, Red, Gray
- **Role**: Starting units, easy to use

### **Tier 2 - Intermediate Units:**
- Soulblade, Graveseer, DuskMonk, OutlawSniper, Summoner
- **Color Themes**: Red, Purple, Gray, Brown, Yellow
- **Role**: Specialized abilities, tactical depth

### **Tier 3 - Elite Units:**
- Necroknight, PhoenixBinder, CrystalArchon, SkygraveRider, Soulbreaker
- **Color Themes**: Purple, Orange, White, Green, Red
- **Role**: Powerful abilities, game-changing units

### **Tier 4 - Legendary Units:**
- DeathMagister, SaintEidolon, WyrmTemplar, RadiantVirtue, Hellborne
- **Color Themes**: Black, Gold, Yellow, White, Red
- **Role**: Rare, extremely powerful

### **Tier 5 - Mythic Units:**
- Berserker, SoulSinger, Witchblade, CryptSentinel, BloodKnight, etc.
- **Color Themes**: Red, Violet, Purple, Gray, Crimson, Orange, Blue, Black
- **Role**: Ultimate units, campaign rewards

## 🚀 Quick Asset Acquisition Workflow

### **Step 1: Get Basic Assets**
1. Go to **OpenGameArt.org**
2. Search for "32x32 tileset"
3. Download a complete set (look for CC0 or CC-BY licensed)
4. Extract to `assets/tiles/terrain/`

### **Step 2: Get Unit Sprites**
1. Search for "rpg character sprites 32x32"
2. Download character sets
3. Organize by unit type in `assets/units/`

### **Step 3: Get UI Elements**
1. Go to **Kenney.nl**
2. Download "UI Pack"
3. Extract icons to `assets/ui/icons/`

### **Step 4: Test Integration**
```bash
# Test asset loading
python -c "from game.sprite_manager import SpriteManager; sm = SpriteManager(); print('✅ Assets loaded successfully')"
```

## 🎯 Tileset Management System

### **Tileset Mapping (data/tileset_mapping.yaml):**
The game uses a YAML-based tileset mapping system that defines:
- **File paths** for each tileset
- **Layer classification** (background, midground, foreground)
- **Tags** for easy filtering and organization
- **Tile dimensions** (32x32 pixels)

### **Available Tilesets:**
- **Castle** (midground) - Stone, indoors, royalty
- **Desert** (midground) - Sand, outdoors, dry
- **Dungeon** (background) - Underground, stone, spooky
- **House** (foreground) - Walls, roofs, buildings
- **Interior** (midground) - Furniture, rooms, indoors
- **Village** (foreground) - Outdoors, trees, props
- **Terrain** (background) - Grass, paths, rocks
- **Water** (background) - Water, lava, coast
- **Worldmap** (background) - Overworld, icons, strategic

### **SpriteManager Tileset Methods:**
```python
# Get tileset information
sm.get_tileset_info("castle")
sm.get_tileset_file("desert")
sm.get_tileset_tags("dungeon")
sm.get_tileset_layer("house")

# List and filter tilesets
sm.list_available_tilesets()
sm.get_tilesets_by_layer("background")
sm.get_tilesets_by_tag("stone")
```

### **Tileset Validation:**
Run `python scripts/validateassets.py` to validate:
- File existence
- Image dimensions
- Tile grid compatibility
- Proper file structure

## ⚠️ Safety Checklist

### **Before Using Any Asset:**
- [ ] **License**: Check if it's free for commercial use
- [ ] **Attribution**: Note if attribution is required
- [ ] **Format**: Ensure it's PNG with transparency
- [ ] **Size**: Verify it's 32x32 or 64x64 pixels
- [ ] **Style**: Check if it matches your game's art style

### **Safe License Types:**
- ✅ **CC0** - Public domain, no restrictions
- ✅ **CC-BY** - Free with attribution
- ✅ **MIT** - Free with license notice
- ✅ **GPL** - Free but requires source sharing

### **Avoid:**
- ❌ **Commercial licenses** (unless you plan to pay)
- ❌ **Non-commercial only** (if you plan to sell)
- ❌ **Unclear licensing**

## 🎯 Recommended Asset Packs

### **For Immediate Use:**

1. **"RPG Tileset" by Kenney** (Kenney.nl)
   - Complete terrain set
   - 32x32 pixel art
   - CC0 license

2. **"Tiny Characters" by Kenney** (Kenney.nl)
   - Character sprites
   - Multiple variations
   - CC0 license

3. **"UI Pack" by Kenney** (Kenney.nl)
   - Complete UI elements
   - Icons and panels
   - CC0 license

### **For Advanced Features:**

1. **"Battle for Wesnoth" assets** (OpenGameArt.org)
   - Tactical game specific
   - High quality
   - GPL license

2. **"Tuxemon" project assets** (GitHub)
   - Pokemon-style tactical
   - Open source
   - GPL license

## 🔄 Asset Update Workflow

### **When Adding New Assets:**
1. Download and verify license
2. Resize to 32x32 if needed
3. Place in appropriate folder
4. Update SpriteManager if needed
5. Test in game
6. Commit to version control

### **Asset Naming Convention:**
- **Units**: `blue_[unit_id]_[frame].png` (12 frames: 0-11)
- **Tiles**: `[environment].png` (e.g., `castle.png`, `desert.png`)
- **UI**: `ui_[element].png`
- **Effects**: `effect_[type].png`

## 📝 License Tracking

Create a `LICENSES.md` file to track asset licenses:

```markdown
# Asset Licenses

## Unit Assets
- Source: Game Assets
- Artist: [Artist Name]
- License: CC0
- Attribution: Not required

## Terrain Assets
- Source: OpenGameArt.org
- Artist: [Artist Name]
- License: CC-BY 3.0
- Attribution: Required

## UI Assets
- Source: Kenney.nl
- Artist: Kenney
- License: CC0
- Attribution: Not required
```

This ensures you stay compliant with all asset licenses! 