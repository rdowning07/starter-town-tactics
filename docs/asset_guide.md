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
│   ├── terrain/          # Basic terrain types
│   │   ├── grass.png
│   │   ├── forest.png
│   │   ├── mountain.png
│   │   ├── water.png
│   │   ├── road.png
│   │   └── wall.png
│   ├── elevation/        # Height variations
│   │   ├── level_1.png
│   │   ├── level_2.png
│   │   └── level_3.png
│   └── special/          # Special terrain
│       ├── lava.png
│       ├── ice.png
│       └── portal.png
├── units/
│   ├── knight/           # Unit type folders
│   │   ├── blue.png      # Team variations
│   │   ├── red.png
│   │   └── neutral.png
│   ├── archer/
│   │   ├── blue.png
│   │   └── red.png
│   ├── mage/
│   │   ├── blue.png
│   │   └── red.png
│   ├── goblin/           # Enemy units
│   │   └── ai.png
│   └── ai/               # AI-specific units
│       ├── boss.png
│       └── minion.png
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
    └── animations/       # Animation frames
        ├── walk/
        └── attack/
```

## 🎨 Asset Specifications

### **Tile Assets (32x32 pixels):**
- **Format**: PNG with transparency
- **Style**: Consistent art style (pixel art recommended)
- **Colors**: 16-32 colors for good performance
- **Variations**: 3-4 variations per terrain type

### **Unit Assets (32x32 or 64x64 pixels):**
- **Format**: PNG with transparency
- **Style**: Match tile art style
- **Team Colors**: Blue/Red variations
- **Animations**: 2-4 frames for idle/movement

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
        self.tile_sets = {}
    
    def load_assets(self):
        """Load all game assets."""
        self.load_terrain_assets()
        self.load_unit_assets()
        self.load_ui_assets()
        self.load_effect_assets()
    
    def load_terrain_assets(self):
        """Load terrain tile assets."""
        terrain_types = ['grass', 'forest', 'mountain', 'water', 'road', 'wall']
        for terrain in terrain_types:
            path = f"assets/tiles/terrain/{terrain}.png"
            if os.path.exists(path):
                self.sprites[f"terrain_{terrain}"] = pygame.image.load(path)
    
    def load_unit_assets(self):
        """Load unit sprite assets."""
        unit_types = ['knight', 'archer', 'mage', 'goblin']
        teams = ['blue', 'red', 'ai', 'neutral']
        
        for unit_type in unit_types:
            for team in teams:
                path = f"assets/units/{unit_type}/{team}.png"
                if os.path.exists(path):
                    self.sprites[f"unit_{unit_type}_{team}"] = pygame.image.load(path)
    
    def get_terrain_sprite(self, terrain_type: str):
        """Get terrain sprite by type."""
        return self.sprites.get(f"terrain_{terrain_type}")
    
    def get_unit_sprite(self, unit_type: str, team: str = "neutral"):
        """Get unit sprite by type and team."""
        return self.sprites.get(f"unit_{unit_type}_{team}")
```

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
python -c "from game.sprite_manager import SpriteManager; sm = SpriteManager(); sm.load_assets(); print('✅ Assets loaded successfully')"
```

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
- **Tiles**: `terrain_[type].png`
- **Units**: `unit_[type]_[team].png`
- **UI**: `ui_[element].png`
- **Effects**: `effect_[type].png`

## 📝 License Tracking

Create a `LICENSES.md` file to track asset licenses:

```markdown
# Asset Licenses

## Terrain Assets
- Source: OpenGameArt.org
- Artist: [Artist Name]
- License: CC-BY 3.0
- Attribution: Required

## Unit Assets
- Source: Kenney.nl
- Artist: Kenney
- License: CC0
- Attribution: Not required

## UI Assets
- Source: Kenney.nl
- Artist: Kenney
- License: CC0
- Attribution: Not required
```

This ensures you stay compliant with all asset licenses! 