# 🧠 Starter Town Tactics

A tactical, turn-based simulation game engine inspired by Final Fantasy Tactics and Fire Emblem. Designed as a learning platform to explore architecture, AI behavior, simulation loops, procedural storytelling, and now full visual rendering with cinematic camera control.

---

## 📦 Features

- ✅ Turn-based combat with AP and tactical states
- ✅ AI unit simulation with `SimRunner`
- ✅ Fully testable, type-checked codebase
- ✅ YAML-driven scenario loading with camera integration
- ✅ Terrain-aware movement overlays
- ✅ CLI and Pygame-ready demos
- ✅ Rich pre-commit hooks and Makefile
- ✅ Unit manager, GameState, FSM, AP system
- ✅ Sprite-based visual rendering (`renderer.py`)
- ✅ Animation system with metadata-driven configuration
- ✅ Visual FX system (screen shake, flash, particles)
- ✅ Sound system with animation frame triggers
- ✅ Cutscene-style YAML demo with cinematic playback
- ✅ AI-triggered animation logic with state transitions
- ✅ Camera controller with cinematic panning and smooth movement
- ✅ Scripted scenario actions and AI behaviors
- ✅ **Enhanced Game Loop** with integrated event and objective management
- ✅ **ObjectivesManager** for dynamic objective tracking and updates
- ✅ **EventManager** for turn-based events (reinforcements, storms, boss phases)
- ✅ **Enhanced AIController** with aggressive, defensive, and passive behaviors
- ✅ **Comprehensive Test Suite** with 96% code coverage for game systems
- ✅ **Command-Event Architecture** with decoupled game logic and event-driven communication
- ✅ **CLI Tools** for demos (`make play-demo`) and performance testing (`make soak`)
- ✅ **Deterministic RNG** for reproducible gameplay and testing

---

## 🏗️ Command-Event Architecture

The game now uses a modern command-event architecture for better testability and extensibility:

### Core Components
- **Commands**: Immutable game actions (`Move`, `Attack`, `EndTurn`)
- **Events**: Decoupled communication via `EventBus`
- **Game Loop**: Orchestrates command-event flow with deterministic RNG
- **Controllers**: Protocol-based AI and player input abstraction

### CLI Tools
```bash
# Run command-event architecture demo
make play-demo

# Performance testing (target: 3000+ ticks/sec)
make soak

# Future: Game replay functionality
make replay
```

### Performance
- **Current**: 800,000+ ticks/sec (excellent performance)
- **Target**: 3,000+ ticks/sec for CI gates
- **Deterministic**: Seeded RNG for reproducible gameplay

---

## 🗺 Scenario System

Scenarios are defined in YAML and include camera actions, AI behaviors, and scripted events:

```yaml
name: "Cinematic Battle"
description: "A dramatic battle with camera work"
map_id: "arena"
max_turns: 12

units:
  - name: "hero"
    team: player
    sprite: "knight"
    x: 5
    y: 5
    hp: 15
    ap: 6
    animation: "idle"
  - name: "enemy"
    team: enemy
    sprite: "rogue"
    x: 8
    y: 8
    hp: 12
    ap: 5
    animation: "idle"
    ai: "aggressive"

camera:
  - action: "pan"
    targets: 
      - [160, 160]  # Starting position
      - [320, 320]  # Intermediate position
      - [480, 480]  # Final position
    speed: 10
    delay: 0.5

ai:
  - unit: "enemy"
    action: "attack"
    target: "hero"
  - unit: "enemy"
    action: "move"
    target: [6, 6]

actions:
  - unit: "hero"
    action: "prepare_for_battle"
```

Terrain maps:

```
G G G G
R G F G
W G G G
```

---

## 🎥 Camera System

The integrated camera controller provides:

- **Cinematic Panning**: Smooth movement between multiple targets
- **Smooth Movement**: Gradual camera transitions
- **Target Following**: Automatic unit tracking
- **YAML Integration**: Camera actions defined in scenario files
- **Configurable Speed**: Adjustable movement rates
- **Delay Support**: Timing control between camera movements

---

## 🧪 Development

### 🛠 Makefile Targets

```bash
make test                        # Run full test suite
make lint                        # Run flake8
make typecheck                   # Run mypy type checks
make validate-assets             # Validate asset structure
make viewer                      # Launch asset viewer
make play-sim-demo               # Interactive demo (basic)
make play-sim-demo-auto          # Auto-run demo
make play-scenario-demo          # Play YAML scenario
make play-scenario-demo-auto     # Auto-run YAML scenario
make play-scenario-animated      # Cinematic cutscene demo
make test-animation-metadata     # Test animation system
```

### ✅ Test Status
- 173/173 tests passing (58 new tests added)
- 32%+ test coverage (improved from baseline)
- mypy compliant
- Lint: minor cosmetic issues

---

## 📁 Project Structure

```
starter-town-tactics/
├── game/
│   ├── grid.py
│   ├── tile.py
│   ├── unit_manager.py
│   ├── game_state.py
│   ├── turn_controller.py
│   ├── sim_runner.py
│   ├── tactical_state_machine.py
│   ├── renderer.py              # Visual renderer
│   ├── CameraController.py      # Camera system
│   ├── game_loop.py             # Enhanced game loop
│   ├── objectives_manager.py    # Dynamic objective tracking
│   ├── event_manager.py         # Turn-based event system
│   └── ai_controller.py         # Enhanced AI behaviors
├── devtools/
│   ├── scenario_loader.py       # Enhanced with camera integration
│   ├── map_loader.py
│   ├── sim_runner_demo.py
│   └── scenarios/               # YAML scenario files
│       ├── demo_cutscene.yaml
│       ├── demo_battle.yaml
│       ├── skirmish_4v4.yaml
│       ├── boss_fake_death.yaml
│       ├── survive_the_horde.yaml
│       └── scripted_loss_intro.yaml
├── maps/
│   ├── arena.map
│   ├── catacombs.map
│   └── forest_edge.map
├── assets/
│   ├── units/                   # Unit sprites and animations
│   ├── tiles/                   # Terrain tiles
│   ├── ui/                      # UI elements
│   ├── effects/                 # Visual effects
│   └── sfx/                     # Sound effects
└── tests/
    ├── test_scenario_loader.py  # Enhanced with camera tests
    ├── test_cameracontroller.py # Camera system tests
    ├── test_game_loop.py        # Enhanced game loop tests
    ├── test_objectives_manager.py # Objectives manager tests
    ├── test_event_manager.py    # Event manager tests
    ├── test_integration_examples.py # Integration tests
    └── ...
```

---

## 🎯 Current Phase: Gameplay Polish

**Phase 5** focuses on enhancing the core gameplay experience:

### ✅ Completed
- 📷 Camera movement and cinematic panning
- 🎭 Scripted scenario actions and branching
- 🎬 YAML-driven camera integration
- 🎮 **Enhanced Game Loop** with turn-based progression and event management
- 🎯 **ObjectivesManager** for dynamic objective tracking and updates
- ⚡ **EventManager** for turn-based events (reinforcements, storms, boss phases)
- 🤖 **Enhanced AIController** with behavior-based decision making
- 🧪 **Comprehensive Testing** with 58 new tests and 96% coverage for game systems

### 🚧 In Progress
- 🌀 Advanced animation branching and combos
- 🧠 Enhanced AI behaviors and strategies
- ⚡ Performance optimization and polish

### 🎨 Optional Asset Standardization
- Standardize unit sprite naming conventions
- Create animation metadata for all units
- Optimize asset file sizes and formats

---

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo>
cd starter-town-tactics
make setup

# Run tests
make test

# Play demos
make play-scenario-animated    # Cinematic demo
make play-sim-demo            # Basic simulation
python demo_enhanced_game_loop.py  # Enhanced game loop demo
```

---

## 📊 Metrics

- **Test Coverage**: 32%+ overall, 96%+ game systems
- **Total Assets**: 413+ files validated and tracked
- **Animation Integration**: 6 units fully integrated with metadata
- **Scenarios**: 6 YAML scenarios with camera integration
- **Code Quality**: Pylint 7.28/10, mypy compliant
- **Game Systems**: Enhanced game loop with 58 new tests

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

*Built with Python, Pygame, and a passion for tactical gameplay.*
