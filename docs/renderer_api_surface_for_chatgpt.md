# Renderer API Surface for ChatGPT - AnimationClock & UnitRenderer Integration

## Current Architecture Overview

### Core Components
- **Renderer**: Main rendering orchestrator (`game/renderer.py`)
- **SpriteManager**: Asset loading and management (`game/sprite_manager.py`)
- **FXManager**: Visual effects and particles (`game/fx_manager.py`)
- **AnimationManager**: Animation playback and validation (`game/animation_manager.py`)

### Key Constraints & Patterns

## 1. Renderer API Surface

### Main Render Method
```python
def render(self, game_state: "GameState", overlay_state: OverlayState, fx_manager: Optional[FXManager] = None) -> None:
    """Main render entrypoint per frame."""
    # Clear screen
    # Apply screen shake offset from FX manager
    # Render layers in order: terrain -> units -> overlays -> FX
```

### Current Draw Function Names & Signatures

#### Terrain Rendering
```python
def render_grid(self, grid: Grid, offset_x: int = 0, offset_y: int = 0) -> None:
    """Render the terrain grid."""
    # Iterates grid.tiles[y][x] for each tile
    # Calls sprite_manager.get_terrain_sprite(tile.terrain)
    # Handles both file paths and pygame.Surface objects
    # Falls back to colored rectangles if sprites fail
```

#### Unit Rendering
```python
def render_units(self, unit_manager: UnitManager, grid: Grid, offset_x: int = 0, offset_y: int = 0) -> None:
    """Render all living units."""
    # Scans grid for placed units (tile.unit)
    # Calls _render_single_unit for each unit

def _render_single_unit(self, unit_manager: UnitManager, unit, x: int, y: int, offset_x: int, offset_y: int) -> None:
    """Render a single unit."""
    # Calls sprite_manager.get_unit_sprite(unit.name)
    # Handles both file paths and pygame.Surface objects
    # Falls back to colored circles if sprites fail
    # Calls _render_unit_indicators for HP/AP bars
```

#### Overlay Rendering
```python
def render_overlays(self, grid: Grid, overlay_state: OverlayState, offset_x: int = 0, offset_y: int = 0) -> None:
    """Render movement and threat overlays."""
    # Renders movement tiles (blue rectangles)
    # Renders threat tiles (red rectangles)
```

### Coordinate System
- **Tile-based**: All positions use tile coordinates (x, y) multiplied by `TILE_SIZE = 32`
- **Screen shake**: Applied via `offset_x, offset_y` parameters
- **Position calculation**: `(x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)`

## 2. SpriteManager API Surface

### Key Methods for AnimationClock Integration
```python
def get_unit_sprite(self, unit_name: str) -> Optional[str | pygame.Surface]:
    """Get unit sprite - returns file path or pygame.Surface"""

def get_terrain_sprite(self, terrain_char: str) -> Optional[str | pygame.Surface]:
    """Get terrain sprite - returns file path or pygame.Surface"""

def get_animation_metadata(self, unit_name: str) -> Dict:
    """Get animation metadata for a unit"""

def load_unit_animations_from_folder(self, unit_id: str, unit_folder: str) -> None:
    """Load animations from standardized folder structure"""

def load_unit_animation_from_sheet(self, unit_id: str, animation_name: str, sheet_path: str, frame_width: int, frame_height: int) -> None:
    """Load animation from sprite sheet"""
```

### Animation Metadata Structure
```python
{
    "idle": {
        "frame_count": 4, 
        "frame_duration": 4, 
        "loop": True
    },
    "attack": {
        "frame_count": 5, 
        "frame_duration": 2, 
        "loop": False,
        "fx_type": "spark", 
        "fx_at": [2], 
        "sound_at": [1]
    },
    "hurt": {
        "frame_count": 2, 
        "frame_duration": 3, 
        "loop": False,
        "fx_type": "flash", 
        "fx_at": [0], 
        "sound_at": [0]
    }
}
```

## 3. FXManager API Surface

### Key Methods for FX Integration
```python
def trigger_fx(self, fx_type: str, position: Tuple[int, int], duration: float = 0.5, intensity: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255), size: int = 10, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Trigger a visual effect"""

def get_shake_offset(self) -> Tuple[float, float]:
    """Get current screen shake offset"""

def update(self, dt: float) -> None:
    """Update all active effects"""

def draw(self, screen: pygame.Surface) -> None:
    """Draw all active effects"""
```

### Available FX Types
```python
FXType.FLASH = "flash"
FXType.SCREEN_SHAKE = "screen_shake"
FXType.PARTICLE = "particle"
FXType.DAMAGE = "damage"
FXType.HEAL = "heal"
FXType.CRITICAL = "critical"
FXType.SPARK = "spark"
FXType.FIRE = "fire"
FXType.ICE = "ice"
FXType.COMBO = "combo"
FXType.EXPLOSION = "explosion"
FXType.MAGIC = "magic"
```

## 4. AnimationManager API Surface

### Key Methods for AnimationClock Integration
```python
class Animation:
    def __init__(self, frames: List[pygame.Surface], frame_time: int = 100, name: str = "unknown"):
        # frames: List of pygame.Surface objects
        # frame_time: Milliseconds per frame
        # name: Animation name for identification

    def update(self, dt: int) -> None:
        """Update animation frame based on delta time"""

    def get_current_frame(self) -> pygame.Surface:
        """Get current animation frame"""

    def reset(self) -> None:
        """Reset animation to first frame"""

    def is_finished(self) -> bool:
        """Check if non-looping animation is complete"""
```

## 5. Recommended AnimationClock Integration

### Architecture Constraints
1. **No Singleton Pattern**: Don't use `get_instance()` - pass instances to constructors
2. **Coordinate System**: Use tile-based coordinates with `TILE_SIZE = 32`
3. **Fallback Handling**: Always provide fallbacks for missing assets
4. **Screen Shake**: Integrate with existing `offset_x, offset_y` system
5. **Layered Rendering**: Maintain order: terrain → units → FX → UI

### AnimationClock Component Design
```python
class AnimationClock:
    """Manages animation timing and frame updates."""
    
    def __init__(self, sprite_manager: SpriteManager, fx_manager: Optional[FXManager] = None):
        self.sprite_manager = sprite_manager
        self.fx_manager = fx_manager
        self.animations: Dict[str, Animation] = {}
        self.unit_animations: Dict[str, Dict[str, Animation]] = {}
        
    def update(self, dt: int) -> None:
        """Update all active animations."""
        
    def get_unit_animation(self, unit_id: str, animation_name: str) -> Optional[Animation]:
        """Get animation for specific unit and animation type."""
        
    def trigger_unit_animation(self, unit_id: str, animation_name: str, position: Tuple[int, int]) -> None:
        """Trigger animation and associated FX."""
```

### UnitRenderer Component Design
```python
class UnitRenderer:
    """Enhanced unit rendering with animation support."""
    
    def __init__(self, sprite_manager: SpriteManager, animation_clock: AnimationClock):
        self.sprite_manager = sprite_manager
        self.animation_clock = animation_clock
        
    def render_unit(self, screen: pygame.Surface, unit, x: int, y: int, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render unit with current animation frame."""
        
    def render_all_units(self, screen: pygame.Surface, unit_manager: UnitManager, grid: Grid, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render all units with animations."""
```

## 6. FX Test Preferences

### Recommended FX Test Approach
**Preference: Spark on keypress** (not auto-fire on start)

**Rationale:**
1. **Interactive Testing**: Allows user control over when FX trigger
2. **Performance**: Avoids overwhelming the screen with auto-firing effects
3. **Debugging**: Easier to isolate and test specific FX types
4. **User Experience**: More predictable and less distracting

### Suggested FX Test Implementation
```python
def handle_fx_test_input(self, event: pygame.event.Event) -> None:
    """Handle FX test keypresses."""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_1:
            self.fx_manager.trigger_fx("spark", (100, 100))
        elif event.key == pygame.K_2:
            self.fx_manager.trigger_fx("fire", (200, 100))
        elif event.key == pygame.K_3:
            self.fx_manager.trigger_fx("ice", (300, 100))
        elif event.key == pygame.K_4:
            self.fx_manager.trigger_fx("explosion", (400, 100))
        elif event.key == pygame.K_5:
            self.fx_manager.trigger_fx("magic", (500, 100))
        elif event.key == pygame.K_SPACE:
            # Screen shake test
            self.fx_manager.trigger_fx("screen_shake", (0, 0), duration=1.0, intensity=2.0)
```

## 7. Integration Points

### Renderer Integration
```python
# In Renderer.render() method, replace:
self.render_units(game_state.units, grid, offset_x, offset_y)

# With:
self.unit_renderer.render_all_units(self.screen, game_state.units, grid, offset_x, offset_y)
```

### AnimationClock Integration
```python
# In main game loop:
def update(self, dt: int):
    self.animation_clock.update(dt)
    self.fx_manager.update(dt)
```

### FX Integration
```python
# In render loop, after unit rendering:
if self.fx_manager:
    self.fx_manager.draw(self.screen)
```

## 8. Asset Structure Expectations

### Unit Animation Folders
```
assets/units/{unit_name}/
├── idle/
│   ├── frame_0.png
│   ├── frame_1.png
│   └── ...
├── attack/
│   ├── frame_0.png
│   ├── frame_1.png
│   └── ...
├── walk/
│   ├── frame_0.png
│   ├── frame_1.png
│   └── ...
└── animation_metadata.json (optional)
```

### Sprite Sheet Format
- Horizontal frame layout
- Consistent frame dimensions
- Alpha channel support
- Standard naming: `{unit_name}_{animation}.png`

## 9. Testing & Validation

### AnimationClock Tests
- Frame timing accuracy
- Animation state transitions
- FX trigger integration
- Performance with multiple animations

### UnitRenderer Tests
- Animation frame display
- Coordinate system accuracy
- Fallback rendering
- Performance with multiple units

### FX Integration Tests
- Keypress responsiveness
- Visual effect rendering
- Screen shake integration
- Performance impact

## 10. Success Criteria

### AnimationClock
- ✅ Smooth frame transitions
- ✅ Accurate timing
- ✅ FX trigger integration
- ✅ Memory efficient

### UnitRenderer
- ✅ Correct animation display
- ✅ Proper positioning
- ✅ Fallback handling
- ✅ Performance optimization

### Overall Integration
- ✅ No breaking changes to existing renderer
- ✅ Maintains layered rendering order
- ✅ Preserves coordinate system
- ✅ Integrates with existing FX system
