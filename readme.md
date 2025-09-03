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
- ✅ **Comprehensive Test Suite** with 95% test success rate (86/91 tests passing)
- ✅ **Command-Event Architecture** with decoupled game logic and event-driven communication
- ✅ **CLI Tools** for demos (`make play-demo`) and performance testing (`make soak`)
- ✅ **Deterministic RNG** for reproducible gameplay and testing
- ✅ **Rules Engine** with height/facing combat bonuses and status effects (Poison, Slow)
- ✅ **A* Pathfinding** with obstacle avoidance and unreachable target handling
- ✅ **Objectives System** with EliminateBoss, SurviveNTurns, HoldZones, Escort, and Compound objectives
- ✅ **Pygame Adapter** with deterministic visual demo and pull-only rendering
- ✅ **Performance Gates** achieving 612,059 TPS (204x above requirement)
- ✅ **Week 8 MVP**: Fully playable game loop with camera system, enhanced input handling, and YAML-based scenarios
- ✅ **Camera System**: Smooth panning, zoom controls, coordinate transformations, and viewport management
- ✅ **Input Integration**: Mouse/keyboard controls with camera awareness and double-click actions
- ✅ **Asset Integration**: Week 7 validation pipeline integrated into game loop initialization
- ✅ **Demo Scenarios**: Rich YAML scenarios with units, events, combos, and victory conditions
- ✅ **Test Coverage**: 26 additional tests for MVP functionality (all passing)
- ✅ **Fighter Unit Integration**: Complete fighter unit with 8 animation states and frame-based animations
- ✅ **Terrain System**: TileCatalog and TerrainRenderer with tiles_manifest.json support
- ✅ **Animation System**: AnimationCatalog and UnitRenderer supporting both frame-based and sprite sheet animations
- ✅ **Behavior Tree AI**: Sophisticated AI system with Composite/Strategy patterns and Protocol-based DI
- ✅ **Code Quality**: Pylint score improved from 8.09/10 to 9.72/10 with comprehensive error fixes

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

# Behavior Tree AI demo
make ai-bt-demo

# Enhanced BT demo (Friday demo ready)
make ai-bt-demo-enhanced

# Visual BT demo (Friday demo ready)
make ai-bt-demo-visual

# Test BT system
make test-bt

# Future: Game replay functionality
make replay
```

### Performance
- **Current**: 612,059 ticks/sec (excellent performance)
- **Target**: 3,000+ ticks/sec for CI gates (204x achieved)
- **Deterministic**: Seeded RNG for reproducible gameplay

---

## ⚔️ 4v4 Tactical Combat System

The game now features a complete 4v4 tactical combat system with professional gameplay mechanics:

### Player Team (4 Units)
- **‍♂️ Fighter (Player)**: WASD movement, melee attacks (3 damage)
- **🧙‍♂️ Mage (AI)**: Fireball projectiles, range 3 (2 damage)
- **‍♀️ Healer (AI)**: Smart healing of lowest HP ally (3 HP per heal)
- **🏹 Ranger (AI)**: Arrow projectiles, range 2, AP regeneration (2 damage)

### Enemy Team (4 Bandits)
- **4 Bandits (AI)**: All using the same bandit sprites with different poses
- **Smart targeting**: Each bandit independently pursues the fighter
- **Collision detection**: No bandits can occupy the same tile
- **Individual stats**: Each bandit has separate HP and AP tracking

### Combat Features
- ✅ **Multi-unit tactical combat** with 8 units total
- ✅ **Smart AI targeting** (mage/ranger target closest bandit)
- ✅ **Collision detection** (no tile sharing)
- ✅ **Individual unit tracking** (separate HP/AP for each bandit)
- ✅ **Visual variety** (different sprites and animations)
- ✅ **Professional combat flow** (damage, healing, positioning, projectiles)

### CLI Demo
```bash
# Run 4v4 tactical combat demo
python cli/ai_bt_fighter_demo.py
```

## 🤖 Behavior Tree AI System

The game now features a sophisticated Behavior Tree (BT) AI system that demonstrates advanced design patterns and clean architecture:

### Design Patterns Demonstrated
- **Composite Pattern**: BT nodes (Sequence, Selector) compose complex behaviors
- **Strategy Pattern**: Actions and conditions as swappable strategies
- **Protocol-based DI**: Clean interfaces via Python Protocols
- **Adapter Pattern**: Safe integration with existing game systems

### AI Capabilities
- **Planning-based AI**: Structured decision trees beyond simple heuristics
- **Deterministic Behavior**: Predictable AI for testing and debugging
- **Extensible Foundation**: Easy to add new behaviors and conditions
- **Fallback Logic**: Graceful degradation to heuristic AI when BT fails

### CLI Tools
```bash
# Run Behavior Tree AI demo
make ai-bt-demo

# Test BT system
make test-bt
```

### Example BT Logic
```python
# AI decision tree: If in range → Attack, else MoveToward target
bt = Selector([
    Sequence([Condition("enemy_in_attack_range"),
              Condition("can_attack"),
              Action("step_attack")]),
    Sequence([Condition("can_move"),
              Action("step_move_toward")])
])
```

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
make quality                     # Run comprehensive code quality checks
make pre-commit                  # Run pre-commit workflow (fix-imports + format + lint + test)
make fix-imports                 # Fix import order automatically
make format                      # Format code with black and isort
make play-sim-demo               # Interactive demo (basic)
make play-sim-demo-auto          # Auto-run demo
make play-scenario-demo          # Play YAML scenario
make play-scenario-demo-auto     # Auto-run YAML scenario
make play-scenario-animated      # Cinematic cutscene demo
make test-animation-metadata     # Test animation system
make play-demo                   # Command-event architecture demo
make soak                        # Performance testing
make fighter-demo                # Standalone fighter demo with movement
make fighter-integrated-demo     # Fighter integrated into main game architecture
make units-fx-demo               # Units and FX demo
make new-terrain-demo            # New terrain system demo
```

### 🔧 Code Quality Infrastructure

The project now includes comprehensive code quality automation:

- **Pre-commit Hooks**: Automatic formatting, linting, and testing on every commit
- **Coding Standards**: Documented patterns and architectural guidelines (`docs/coding_standards.md`)
- **IDE Integration**: VS Code settings for real-time quality feedback
- **Automated Scripts**: `scripts/code_quality.py` for comprehensive validation
- **Quality Gates**: Enforced standards prevent issues from accumulating

**Quick Quality Check:**
```bash
make quality  # Runs all quality checks in sequence
```

### ✅ Test Status
- 97/102 tests passing (95% success rate) - includes new fighter integration tests
- Comprehensive test coverage for core systems including fighter animations
- 100% mypy compliant (all type errors resolved)
- **Code Quality**: Pylint score 9.72/10 (up from 8.09/10) with automated enforcement
- **Standards**: Documented coding patterns and architectural guidelines
- **Fighter Integration**: 11 new tests covering animation system and game integration

---

## 📁 Project Structure

```
starter-town-tactics/
├── core/                        # Command-event architecture
│   ├── command.py              # Command protocol and implementations
│   ├── events.py               # Event system and EventBus
│   ├── game_loop.py            # Main game loop orchestration
│   ├── rng.py                  # Deterministic random number generation
│   ├── state.py                # Game state and controller protocol
│   ├── rules/                  # Rules engine
│   │   ├── combat.py           # Height/facing bonuses, damage calculation
│   │   ├── status.py           # Status effects (Poison, Slow)
│   │   └── move.py             # A* pathfinding algorithm
│   └── objectives/             # Objectives system
│       ├── base.py             # Base objective protocol
│       ├── eliminate_boss.py   # EliminateBoss objective
│       ├── survive.py          # SurviveNTurns objective
│       ├── hold_zones.py       # HoldZones objective
│       ├── escort.py           # Escort objective
│       └── compound.py         # Compound objective (multiple sub-objectives)
├── adapters/                   # Interface adapters
│   └── pygame/                 # Pygame rendering adapter
│       ├── renderer.py         # Pull-only renderer for game snapshots
│       └── input.py            # Input controller for human turns
├── cli/                        # Command-line tools
│   ├── play_demo.py            # Command-event architecture demo with pygame
│   ├── soak.py                 # Performance testing tool
│   └── replay.py               # Future game replay functionality
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
│   ├── ai_controller.py         # Enhanced AI behaviors
│   ├── AnimationCatalog.py      # Frame-based animation loader
│   ├── UnitRenderer.py          # Unit rendering with animations
│   ├── TileCatalog.py           # Terrain tile management
│   ├── terrain_renderer.py      # Terrain rendering system
│   └── demo_base.py             # Base class for demos with timeout
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
│   │   ├── fighter/            # Fighter unit frames (24 PNG files)
│   │   └── _metadata/          # Animation metadata (animation_metadata.json)
│   ├── terrain/                 # Terrain tiles and sheets
│   │   └── sheets/             # Organized tile sheets (TileA1, TileA2, etc.)
│   ├── ui/                      # UI elements
│   ├── effects/                 # Visual effects
│   ├── scenarios/               # Demo scenarios
│   │   ├── demo.yaml           # Command-event demo with compound objectives
│   │   └── fighter_demo.yaml   # Fighter unit demo scenario
│   └── sfx/                     # Sound effects
├── docs/                        # Architecture documentation
│   ├── ADR-0001-command-event.md # Architecture decision record
│   ├── architecture.md          # System architecture overview
│   ├── perf.md                  # Performance documentation
│   └── weekly-brief.md          # Development progress tracking
└── tests/
    ├── test_core_command_event.py # Command-event system tests
    ├── test_combat.py           # Combat rules engine tests
    ├── test_status.py           # Status effects tests
    ├── test_astar.py            # A* pathfinding tests
    ├── test_objectives.py       # Objectives system tests
    ├── test_determinism.py      # Determinism and replay tests
    ├── test_scenario_loader.py  # Enhanced with camera tests
    ├── test_cameracontroller.py # Camera system tests
    ├── test_game_loop.py        # Enhanced game loop tests
    ├── test_objectives_manager.py # Objectives manager tests
    ├── test_event_manager.py    # Event manager tests
    ├── test_integration_examples.py # Integration tests
    ├── test_fighter_integration.py # Fighter animation system tests
    ├── test_fighter_game_integration.py # Fighter game integration tests
    ├── test_terrain_system.py   # Terrain system tests
    └── ...
```

---

## 🎯 Current Phase: Visual Integration & Final Fantasy Tactics

**Phase 8** MAJOR PROGRESS - Visual integration and Final Fantasy Tactics-style gameplay implementation:

### ✅ Completed (Phases 1-7)
- 📷 Camera movement and cinematic panning
- 🎭 Scripted scenario actions and branching
- 🎬 YAML-driven camera integration
- 🎮 **Enhanced Game Loop** with turn-based progression and event management
- 🎯 **ObjectivesManager** for dynamic objective tracking and updates
- ⚡ **EventManager** for turn-based events (reinforcements, storms, boss phases)
- 🤖 **Enhanced AIController** with behavior-based decision making
- 🧪 **Comprehensive Testing** with 86/91 tests passing (95% success rate)
- 🏗️ **Command-Event Architecture** with decoupled game logic and event-driven communication
- 🚀 **CLI Tools** for demos and performance testing (612k+ ticks/sec)
- 🎲 **Rules Engine**: Height-based combat, facing direction, status effects (Poison/Slow) ✅
- 🗺️ **A* Pathfinding**: Advanced movement algorithms with obstacle avoidance ✅
- 🎯 **Objectives System**: EliminateBoss, SurviveNTurns, HoldZones, Escort, Compound ✅
- 🎮 **Pygame Adapter**: Deterministic visual demo with pull-only rendering ✅
- ⚡ **CI Integration**: Performance gates achieving 612,059 TPS (204x above requirement) ✅
- 🔧 **Type Safety**: 100% mypy compliance with all type errors resolved ✅
- 📄 **Documentation**: Comprehensive weekly brief and performance tracking ✅

### 🎨 Current Visual Integration Status
**UI System**: Complete and functional (HealthUI, APUI, TurnUI, StatusUI, CursorManager, AbilityIcons)
- ✅ 19 UI assets with fallback mechanisms
- ✅ UI asset demo and multi-unit demo working
- ✅ Comprehensive asset validation and testing systems

**Fighter Unit Integration**: Complete and production-ready
- ✅ **Fighter Unit**: 24 individual frame files with 8 animation states
- ✅ **Animation System**: AnimationCatalog supporting frame-based and sprite sheet animations
- ✅ **Terrain System**: TileCatalog and TerrainRenderer with 300+ terrain tiles
- ✅ **Game Integration**: Fighter works in main game architecture with UnitManager/Renderer
- ✅ **Demo Applications**: Standalone and integrated demos with movement controls

**Asset Status**: Major improvement with fighter integration
- ✅ **Fighter Unit**: 1/1 fully integrated with animations (100% success)
- ✅ **Terrain System**: Complete tile catalog with 300+ tiles organized by sheets
- ✅ **UI Elements**: 19/19 UI assets (100% - working)
- ✅ **Sound Effects**: 8/8 valid WAV files (100% - working)
- ⚠️ **Other Units**: 22 units still need integration (next phase)

### 🎯 Phase 8 Goals: Final Fantasy Tactics Visual Pipeline
**Week 10**: Terrain Foundation ✅ COMPLETED
- ✅ Created comprehensive terrain system with 300+ tiles organized by sheets
- ✅ Implemented TileCatalog and TerrainRenderer components
- ✅ Created terrain demo with visual validation
- ✅ Integrated with existing Grid system via tiles_manifest.json

**Week 11**: Unit Sprites & Animations ✅ MAJOR PROGRESS
- ✅ Created complete fighter unit with 24 frame files and 8 animation states
- ✅ Enhanced animation system with AnimationCatalog supporting frame-based animations
- ✅ Implemented UnitRenderer component with proper positioning and timing
- ✅ Created fighter demo with visual validation and movement controls
- ✅ Integrated fighter into main game architecture (SpriteManager, Renderer, UnitManager)

**Week 12**: AI Integration & Friday Demo Preparation ✅ MAJOR PROGRESS
- ✅ **Behavior Tree AI System** - Core runtime implemented with Composite, Strategy, and Observer patterns
- ✅ **BT Adapter Integration** - Clean separation between AI logic and game engine via BTContext protocol
- ✅ **Visual Demo Phase 1 Complete** - Pygame integration showing fighter vs AI bandit with real-time BT decision display
- ✅ **Design Pattern Showcase** - Live demonstration of architectural patterns in action
- ✅ **Playable Demo** - WASD movement, SPACE attacks, working AI that executes actions
- ✅ **4v4 Tactical Combat System** - Complete 4v4 tactical combat with 4 player units vs 4 AI bandits
- ✅ **Multi-Unit AI** - Smart targeting, collision detection, individual unit tracking
- ✅ **Professional Combat Flow** - Damage, healing, projectiles, visual effects
- 🔄 **Phase 2 Complete** - 4v4 tactical combat system fully functional
- ⏳ **Phase 3 Next** - Architecture improvements (Factory, Scheduler, VictoryService)

**Week 13**: Visual Effects & Particles
- Create 59+ effect assets with smooth animations
- Enhance FXManager with VisualEffect class
- Implement particle system with performance optimization
- Create effects demo with visual validation

**Week 13**: Gameplay Integration
- Create complete tactical game demo
- Integrate all visual layers (Terrain → Units → Effects → UI)
- Implement interactive gameplay with visual feedback
- Performance optimization and testing

**Week 14**: Final Fantasy Tactics Polish
- Advanced visual features (camera, lighting, weather)
- Audio integration with music and sound effects
- Professional visual quality and polish
- User experience optimization

### 📋 Future Enhancement Opportunities
1. **Visual Assets**: Replace 95% stub assets with real art
2. **Test Coverage**: Improve remaining 5 failing tests
3. **Performance**: Further optimization opportunities
4. **Features**: Additional objective types, enhanced AI behaviors
5. **Code Quality**: Leverage automated infrastructure for continuous improvement

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
make play-demo                    # Command-event architecture demo
make soak                         # Performance testing
make play-scenario-animated       # Cinematic demo
make play-sim-demo               # Basic simulation
```

---

## 📊 Metrics

- **Test Success Rate**: 97/102 tests passing (95% success rate) - includes fighter integration tests
- **Type Safety**: 100% mypy compliance (all errors resolved)
- **Code Quality**: Pylint score 9.72/10 (up from 8.09/10) with automated enforcement
- **Performance**: 612,059 TPS (204x above 3000 TPS requirement)
- **Total Assets**: 800+ files validated and tracked with major integration progress
- **UI Assets**: 19/19 working (100% success rate)
- **Fighter Unit**: 24/24 frame files integrated (100% success)
- **Terrain Assets**: 300+ tiles organized and integrated (100% success)
- **Sound Assets**: 8/8 valid WAV files (100% success)
- **Animation Integration**: Fighter unit fully integrated with 8 animation states
- **AI Integration**: Behavior Tree system with BT Adapter and working AI controller
- **Scenarios**: 7 YAML scenarios including fighter demo
- **Game Systems**: Complete rules engine with combat, pathfinding, objectives
- **Architecture**: Command-event system with deterministic RNG + BT AI system
- **Demo**: Multiple visual demos including 4v4 tactical combat with smart AI and projectiles

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

*Built with Python, Pygame, and a passion for tactical gameplay.*
