# Sound System Integration

## 🎵 **Overview**

The sound system provides comprehensive audio support for Starter Town Tactics, including sound effects, music, and animation-triggered audio.

---

## 📁 **File Structure**

```
assets/sfx/
├── slash.wav      # Sword attack sound
├── death.wav      # Unit death sound
├── fireball.wav   # Magic attack sound
├── heal.wav       # Healing spell sound
├── block.wav      # Shield block sound
├── move.wav       # Unit movement sound
├── select.wav     # Unit selection sound
└── menu.wav       # Menu navigation sound
```

---

## 🛠 **Components**

### **1. Sound Manager (`game/sound_manager.py`)**

**Features:**
- ✅ **Sound loading** - Individual and directory loading
- ✅ **Volume control** - Separate SFX and music volumes
- ✅ **Mute functionality** - Global mute/unmute
- ✅ **Error handling** - Graceful degradation
- ✅ **Resource management** - Proper cleanup

**Usage:**
```python
from game.sound_manager import SoundManager

# Initialize with sound enabled/disabled
sound_manager = SoundManager(enable_sound=True)

# Load individual sounds
sound_manager.load_sound("slash", "assets/sfx/slash.wav")
sound_manager.load_sound("death", "assets/sfx/death.wav")

# Load all sounds from directory
sound_manager.load_sounds_from_directory("assets/sfx")

# Play sounds
sound_manager.play("slash")
sound_manager.play("death")

# Volume control
sound_manager.set_sfx_volume(0.8)
sound_manager.set_music_volume(0.7)

# Mute control
sound_manager.mute()
sound_manager.unmute()
sound_manager.toggle_mute()
```

### **2. Placeholder Generator (`devtools/gen_placeholder_wavs.py`)**

**Features:**
- ✅ **Automatic generation** - Creates 8 placeholder sounds
- ✅ **Numpy fallback** - Works without numpy dependency
- ✅ **Configurable tones** - Different frequencies for different effects
- ✅ **Error handling** - Creates silent fallbacks if needed

**Usage:**
```bash
# Generate placeholder sounds
make generate-sounds

# Or run directly
python devtools/gen_placeholder_wavs.py
```

### **3. Visual Animation Tester Integration**

**Features:**
- ✅ **CLI mute flag** - `--mute` argument support
- ✅ **Animation triggers** - Sound plays at specific frames
- ✅ **Selection sounds** - Audio feedback for controls
- ✅ **Auto-play integration** - Sounds during animation playback

**Usage:**
```bash
# Test with sound
PYTHONPATH=. python devtools/visual_animation_tester.py ranger

# Test with sound muted
PYTHONPATH=. python devtools/visual_animation_tester.py ranger --mute
```

---

## 🎬 **Animation Integration**

### **Metadata-Driven Sound Triggers**

Animation metadata includes sound trigger points:

```json
{
  "attack": {
    "frame_width": 32,
    "frame_height": 32,
    "frames": 3,
    "duration": 200,
    "loop": false,
    "fx_at": [1],
    "sound_at": [0]  // Play sound at frame 0
  },
  "walk": {
    "frame_width": 32,
    "frame_height": 32,
    "frames": 3,
    "duration": 300,
    "loop": true,
    "fx_at": [],
    "sound_at": [1]  // Play sound at frame 1
  }
}
```

### **In-Game Integration**

```python
# Inside main Pygame loop
if frame_index in anim_data.get("sound_at", []):
    if current_animation == "attack":
        sound_manager.play("slash")
    elif current_animation == "walk":
        sound_manager.play("move")
```

---

## 🎛️ **CLI Integration**

### **Mute Flag Support**

All tools support the `--mute` flag:

```python
# Enable mute via CLI flag
if "--mute" in sys.argv:
    sound_manager.mute()
```

**Examples:**
```bash
# Sound enabled (default)
PYTHONPATH=. python devtools/visual_animation_tester.py ranger

# Sound muted
PYTHONPATH=. python devtools/visual_animation_tester.py ranger --mute

# Mute flag anywhere in arguments
PYTHONPATH=. python devtools/visual_animation_tester.py --mute ranger
```

---

## 🧪 **Testing**

### **Sound System Test Suite**

```bash
# Run comprehensive sound tests
make test-sound-system
```

**Test Coverage:**
- ✅ **Basic functionality** - Loading, playing, volume control
- ✅ **Mute functionality** - Global mute/unmute
- ✅ **Animation integration** - Metadata sound triggers
- ✅ **CLI integration** - Mute flag handling
- ✅ **Error handling** - Graceful degradation
- ✅ **Resource cleanup** - Proper shutdown

### **Manual Testing**

```bash
# Generate sounds
make generate-sounds

# Test visual animation with sound
PYTHONPATH=. python devtools/visual_animation_tester.py ranger

# Test visual animation muted
PYTHONPATH=. python devtools/visual_animation_tester.py ranger --mute
```

---

## 🎯 **Integration Points**

### **1. Main Game Loop**

```python
# Initialize sound manager
sound_manager = SoundManager(enable_sound=True)

# Load sounds
sound_manager.load_sound("slash", "assets/sfx/slash.wav")
sound_manager.load_sound("death", "assets/sfx/death.wav")

# In game loop
if unit.is_attacking():
    sound_manager.play("slash")
elif unit.is_dying():
    sound_manager.play("death")
```

### **2. Unit Actions**

```python
# Unit movement
def move_unit(unit, new_position):
    # ... movement logic ...
    sound_manager.play("move")

# Unit selection
def select_unit(unit):
    # ... selection logic ...
    sound_manager.play("select")
```

### **3. UI Interactions**

```python
# Menu navigation
def navigate_menu(direction):
    # ... navigation logic ...
    sound_manager.play("menu")

# Button clicks
def handle_button_click(button):
    # ... click logic ...
    sound_manager.play("select")
```

---

## 🔧 **Configuration**

### **Volume Settings**

```python
# Default volumes
sound_manager.set_sfx_volume(0.8)    # Sound effects
sound_manager.set_music_volume(0.7)  # Background music
```

### **Sound File Requirements**

- **Format:** WAV (recommended for compatibility)
- **Channels:** Mono or Stereo
- **Sample Rate:** 44100 Hz (standard)
- **Bit Depth:** 16-bit (recommended)

### **File Naming Convention**

```
assets/sfx/
├── {action}.wav     # e.g., slash.wav, death.wav
├── {effect}.wav     # e.g., fireball.wav, heal.wav
└── {ui}.wav         # e.g., select.wav, menu.wav
```

---

## 🚀 **Future Enhancements**

### **Planned Features:**
- 🔄 **Music system** - Background music with transitions
- 🔄 **3D audio** - Positional sound effects
- 🔄 **Audio streaming** - Large music files
- 🔄 **Sound categories** - Organized sound management
- 🔄 **Audio presets** - Pre-configured sound settings

### **Advanced Integration:**
- 🔄 **Animation sequences** - Complex sound timing
- 🔄 **Environmental audio** - Terrain-based sounds
- 🔄 **Team-specific sounds** - Different audio per faction
- 🔄 **Dynamic mixing** - Adaptive volume based on game state

---

## 📊 **Performance Considerations**

### **Memory Management**
- ✅ **Lazy loading** - Sounds loaded on demand
- ✅ **Resource cleanup** - Proper pygame mixer shutdown
- ✅ **Error handling** - Graceful fallbacks for missing files

### **Audio Quality**
- ✅ **Configurable quality** - Adjustable sample rates
- ✅ **Volume control** - Separate SFX and music volumes
- ✅ **Mute support** - Complete audio disable

---

## 🎉 **Conclusion**

The sound system provides a solid foundation for audio in Starter Town Tactics:

- ✅ **Complete integration** with animation system
- ✅ **CLI support** with mute functionality
- ✅ **Comprehensive testing** suite
- ✅ **Error handling** and graceful degradation
- ✅ **Extensible architecture** for future enhancements

Ready for Phase 4 development and beyond! 