# Architecture Overview

## Project: Starter Town Tactics

Starter Town Tactics is a Python-based tactical RPG inspired by Final Fantasy Tactics. It is structured around modular components and test-driven development.

**🎉 Technical Foundation Complete!** The project has achieved 97%+ test coverage and is ready for game development phase.

---

## Key Architectural Components

### `game/`
- Core gameplay logic, models, and controllers.
- Interfaces follow `# @api` and `# @contract` tags for stability tracking.

| Module                | Description                                      | Status |
|-----------------------|--------------------------------------------------|---------|
| `input_state.py`      | Tracks real-time input states                   | ✅ Complete |
| `keyboard_controller.py` | Handles keyboard input                         | ✅ Complete |
| `gamepad_controller.py`  | Handles gamepad button mapping                | ✅ Complete |
| `mcp.py`              | Master control program orchestrating inputs     | ✅ Complete |
| `grid.py`             | Manages tiles and unit positioning              | ✅ Complete |
| `unit.py`             | Contains unit stats, movement, and interaction  | ✅ Complete |
| `turn_controller.py`  | Manages player and AI turn phases               | ✅ Complete |
| `sim_runner.py`       | Headless simulation loop for automated testing  | ✅ Complete |
| `ai_controller.py`    | AI behavior and decision making                 | ✅ Complete |
| `sprite_manager.py`   | Asset management and sprite handling            | ✅ Complete |
| `renderer.py`         | Visual rendering for grid, terrain, and units   | ✅ Complete |
| `fx_manager.py`       | Visual effects (screen shake, flash, particles) | ✅ Complete |
| `sound_manager.py`    | Audio playback with animation triggers          | ✅ Complete |

### `game/overlay/`
- Rendering overlays such as threat zones, movement range, etc.
- ✅ Complete with grid overlays and visual feedback

### `game/ui/`
- Debug and visual overlays (non-core).
- ✅ Complete with debug information display

### `tests/`
- Pytest test suite for all gameplay logic, targeting 100% coverage.
- ✅ **97%+ coverage achieved** across 97 tests

### `devtools/`
- Development and testing utilities for animation, scenarios, and demos.
- ✅ Complete with CLI and visual animation testers, scenario automation

---

## Animation & FX System Architecture

### Animation Metadata System
- **`animation_metadata.json`**: Unit-specific animation configuration
- **Frame-based triggers**: `fx_at` and `sound_at` arrays for precise timing
- **Animation types**: idle, walk, attack, hurt, die, stun with configurable properties
- **Metadata structure**: frame_count, frame_duration, loop, fx_type, triggers

### FXManager Integration
- **Visual effects**: screen shake, flash, spark, glow, particle systems
- **Frame-aware triggering**: Effects triggered at specific animation frames
- **Camera integration**: Screen shake affects rendering offset
- **Extensible design**: Easy to add new effect types

### SoundManager Integration
- **Audio triggers**: Sound effects played at specific animation frames
- **File management**: Automatic .wav file loading and playback
- **Mute support**: CLI flag for silent operation
- **Resource cleanup**: Proper audio resource management

### Scenario Automation
- **YAML-driven demos**: `demo_cutscene.yaml` for cinematic playback
- **AI-triggered animations**: Units automatically transition through animation states
- **CLI playback**: `make play-scenario-animated` for automated demos
- **Visual feedback**: Real-time animation and FX display

## Development Tools

- **Cursor**: AI-based code editor with `.cursor/config.json` for file indexing and architectural context.
- **ChatGPT**: Acts as Principal Engineer and Test Architect.
- **Claude**: Used for summarization and exploratory code analysis.
- **VS Code**: Main local IDE.
- **Pre-commit Hooks**: Enforce linting, typing, and formatting before pushes.

---

## Current Development Phase

### ✅ Completed (Technical Foundation + Visual Systems)
- **Test Coverage**: 97%+ across all modules
- **Input System**: Multi-platform input handling (keyboard, mouse, gamepad)
- **AI Integration**: Automated AI behavior and simulation
- **Code Quality**: All pre-commit checks passing
- **Architecture**: Modular, testable, maintainable design
- **Documentation**: Comprehensive API contracts and guides
- **Visual Rendering**: Complete Pygame integration with sprite management
- **Animation System**: Metadata-driven animation with FX and sound triggers
- **FX & Sound**: Screen shake, flash, particles, and audio integration

### 🚧 Next Phase (Gameplay Polish)
- **Camera System**: Cinematic panning and movement
- **Scripted Actions**: Advanced scenario branching and actions
- **Animation Combos**: Complex animation sequences and branching
- **Enhanced AI**: More sophisticated behaviors and strategies
- **Performance**: Optimization and polish

---

## Quality Metrics

- **Test Coverage**: 97%+ (97 tests)
- **Code Quality**: All pre-commit hooks passing
- **Type Safety**: Full mypy compliance
- **Documentation**: Complete API contracts and guides
- **Architecture**: Modular design with clear separation of concerns
- **Animation System**: Metadata-driven configuration with FX/sound integration