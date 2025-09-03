# Animation Tools Integration

This document describes the integration of CLI and Visual animation testing tools with the sprite manager and pygame initialization system.

## Overview

The animation tools provide comprehensive testing and validation of sprite sheet loading, animation playback, and metadata management for the tactical game engine.

## Tools Overview

### 1. CLI Animation Tester (`devtools/cli_animation_tester.py`)

**Purpose:** Command-line testing of animation metadata and sprite sheet loading

**Features:**
- ✅ **Metadata validation** - Validates JSON metadata structure
- ✅ **Frame count verification** - Compares expected vs actual frames
- ✅ **Batch testing** - Tests multiple units and animations
- ✅ **Error reporting** - Detailed error messages for debugging
- ✅ **Pygame integration** - Proper initialization for sprite loading

**Usage:**
```bash
# Test all units
make test-cli-animations

# Test specific unit
PYTHONPATH=. python devtools/cli_animation_tester.py knight

# Test specific animation
PYTHONPATH=. python devtools/cli_animation_tester.py knight attack
```

### 2. Visual Animation Tester (`devtools/visual_animation_tester.py`)

**Purpose:** Interactive visual testing of animations with real-time preview

**Features:**
- ✅ **Real-time preview** - Live animation playback
- ✅ **Interactive controls** - Keyboard-based animation switching
- ✅ **Auto-play mode** - Automatic frame progression
- ✅ **Unit selection** - Support for multiple units
- ✅ **Error handling** - Graceful degradation for missing assets
- ✅ **Enhanced UI** - Clear information display

**Usage:**
```bash
# Test with default unit
make test-visual-animations

# Test specific unit
PYTHONPATH=. python devtools/visual_animation_tester.py knight
```

**Controls:**
- **SPACE** - Switch between animations
- **LEFT/RIGHT** - Frame-by-frame control
- **A** - Toggle auto-play mode
- **ESC** - Quit

## Metadata Structure

Animation metadata is stored in JSON files at `assets/units/{unit_id}/animation_metadata.json`:

```json
{
  "idle": {
    "frame_width": 32,
    "frame_height": 32,
    "frames": 2,
    "duration": 500,
    "loop": true,
    "fx_at": [],
    "sound_at": []
  },
  "attack": {
    "frame_width": 32,
    "frame_height": 32,
    "frames": 3,
    "duration": 200,
    "loop": false,
    "fx_at": [1],
    "sound_at": [0]
  }
}
```

**Required Fields:**
- `frame_width` - Width of each frame in pixels
- `frame_height` - Height of each frame in pixels
- `frames` - Number of frames in the animation
- `duration` - Duration per frame in milliseconds

**Optional Fields:**
- `loop` - Whether animation should loop (default: true)
- `fx_at` - Frame indices for special effects
- `sound_at` - Frame indices for sound triggers

## Integration Points

### 1. Sprite Manager Integration

The tools integrate with the enhanced `SpriteManager` class:

```python
# Load animation from sprite sheet
sprite_manager.load_unit_animation_from_sheet(
    unit_id="knight",
    animation_name="attack",
    sheet_path="assets/units/knight/attack.png",
    frame_width=32,
    frame_height=32
)

# Retrieve animation frames
frames = sprite_manager.get_unit_animation_frames("knight", animation_name="attack")

# Get specific sprite
sprite = sprite_manager.get_unit_sprite("knight", state="attack", frame_index=0)
```

### 2. Pygame Initialization

Proper pygame initialization with error handling:

```python
from game.pygame_init import init_pygame, quit_pygame

# Initialize with custom settings
init_pygame(
    window_size=(800, 600),
    window_title="Animation Tester",
    enable_sound=True,
    enable_joystick=False
)

# Clean shutdown
quit_pygame()
```

### 3. Unit Animation Integration

Units can now retrieve their current animation sprites:

```python
unit = Unit("knight", 2, 2, "player", health=10)
unit.set_animation("attack", duration=30)

# Get current sprite for rendering
current_sprite = unit.get_current_sprite(sprite_manager)
```

## Makefile Integration

New makefile targets for easy testing:

```bash
# Test all animation tools
make test-animation-tools

# Test CLI animation tester
make test-cli-animations

# Test visual animation tester
make test-visual-animations

# Test sprite sheet integration
make test-sprite-sheet
```

## Error Handling

The tools provide comprehensive error handling:

### Missing Metadata
- ✅ Graceful handling of missing metadata files
- ✅ Clear error messages with expected paths
- ✅ Continues testing other units

### Missing Sprite Sheets
- ✅ Identifies missing sprite sheet files
- ✅ Provides fallback rendering for testing
- ✅ Continues with available assets

### Invalid Metadata
- ✅ Validates JSON structure
- ✅ Checks required fields
- ✅ Reports specific validation errors

### Pygame Errors
- ✅ Proper initialization error handling
- ✅ Graceful degradation for missing features
- ✅ Clean shutdown on errors

## Testing Workflow

### 1. Development Testing
```bash
# Quick validation of metadata
make test-cli-animations knight

# Visual testing of animations
make test-visual-animations knight
```

### 2. Integration Testing
```bash
# Full integration test
make test-animation-tools

# Sprite sheet integration test
make test-sprite-sheet
```

### 3. Batch Testing
```bash
# Test all units
make test-cli-animations
```

## Future Enhancements

### Planned Features:
- 🔄 **Sound integration** - Audio playback during animations
- 🔄 **Effect triggers** - Visual effects at specific frames
- 🔄 **Performance metrics** - Frame rate and loading time analysis
- 🔄 **Export functionality** - Generate animation previews
- 🔄 **Batch processing** - Process multiple sprite sheets

### Metadata Extensions:
- 🔄 **Frame-specific data** - Individual frame properties
- 🔄 **Animation sequences** - Complex multi-animation sequences
- 🔄 **Team variations** - Different sprites per team
- 🔄 **State transitions** - Animation state machine definitions

## Troubleshooting

### Common Issues:

1. **"No metadata found"**
   - Ensure `animation_metadata.json` exists in unit folder
   - Check JSON syntax is valid

2. **"Sprite sheet not found"**
   - Verify sprite sheet PNG files exist
   - Check file paths match metadata

3. **"Pygame initialization failed"**
   - Ensure pygame is installed
   - Check display permissions

4. **"Frame count mismatch"**
   - Verify sprite sheet dimensions match metadata
   - Check frame width/height calculations

### Debug Commands:
```bash
# Validate metadata structure
python -c "import json; json.load(open('assets/units/knight/animation_metadata.json'))"

# Check sprite sheet dimensions
python -c "import pygame; pygame.init(); img=pygame.image.load('assets/units/knight/attack.png'); print(img.get_size())"

# Test specific animation
PYTHONPATH=. python devtools/cli_animation_tester.py knight attack
```

## Conclusion

The animation tools provide a robust foundation for testing and validating sprite sheet animations in the tactical game engine. The integration with the sprite manager and pygame initialization ensures reliable operation across different environments and asset configurations.

The tools are ready for Phase 4 development and provide excellent debugging capabilities for animation-related issues.
