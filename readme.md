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
- 115/115 tests passing
- 87%+ test coverage
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
│   └── CameraController.py      # Camera system
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
    └── ...
```

---

## 🎯 Current Phase: Gameplay Polish

**Phase 5** focuses on enhancing the core gameplay experience:

### ✅ Completed
- 📷 Camera movement and cinematic panning
- 🎭 Scripted scenario actions and branching
- 🎬 YAML-driven camera integration

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
```

---

## 📊 Metrics

- **Test Coverage**: 87%+ overall, 100% core systems
- **Total Assets**: 413+ files validated and tracked
- **Animation Integration**: 6 units fully integrated with metadata
- **Scenarios**: 6 YAML scenarios with camera integration
- **Code Quality**: Pylint 7.28/10, mypy compliant

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

*Built with Python, Pygame, and a passion for tactical gameplay.*
