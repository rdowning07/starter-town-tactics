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

### `game/overlay/`
- Rendering overlays such as threat zones, movement range, etc.
- ✅ Complete with grid overlays and visual feedback

### `game/ui/`
- Debug and visual overlays (non-core).
- ✅ Complete with debug information display

### `tests/`
- Pytest test suite for all gameplay logic, targeting 100% coverage.
- ✅ **97%+ coverage achieved** across 61 tests

---

## Development Tools

- **Cursor**: AI-based code editor with `.cursor/config.json` for file indexing and architectural context.
- **ChatGPT**: Acts as Principal Engineer and Test Architect.
- **Claude**: Used for summarization and exploratory code analysis.
- **VS Code**: Main local IDE.
- **Pre-commit Hooks**: Enforce linting, typing, and formatting before pushes.

---

## Current Development Phase

### ✅ Completed (Technical Foundation)
- **Test Coverage**: 97%+ across all modules
- **Input System**: Multi-platform input handling (keyboard, mouse, gamepad)
- **AI Integration**: Automated AI behavior and simulation
- **Code Quality**: All pre-commit checks passing
- **Architecture**: Modular, testable, maintainable design
- **Documentation**: Comprehensive API contracts and guides

### 🚧 Next Phase (Game Development)
- **Battle System**: Combat mechanics, damage calculations, battle UI
- **Turn-Based Gameplay**: Action points, multiple action types, turn order
- **Visual Improvements**: Enhanced Pygame graphics, animations, HUD
- **Game Content**: Campaign levels, character progression, story elements

---

## Quality Metrics

- **Test Coverage**: 97%+ (61 tests)
- **Code Quality**: All pre-commit hooks passing
- **Type Safety**: Full mypy compliance
- **Documentation**: Complete API contracts and guides
- **Architecture**: Modular design with clear separation of concerns