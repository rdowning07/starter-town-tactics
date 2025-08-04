# 🧠 Starter Town Tactics

A tactical, turn-based simulation game engine inspired by Final Fantasy Tactics and Fire Emblem. Designed as a learning platform to explore architecture, AI behavior, simulation loops, procedural storytelling, and now full visual rendering.

---

## 📦 Features

- ✅ Turn-based combat with AP and tactical states
- ✅ AI unit simulation with `SimRunner`
- ✅ Fully testable, type-checked codebase
- ✅ YAML-driven scenario loading
- ✅ Terrain-aware movement overlays
- ✅ CLI and Pygame-ready demos
- ✅ Rich pre-commit hooks and Makefile
- ✅ Unit manager, GameState, FSM, AP system
- ✅ Sprite-based visual rendering (`renderer.py`)
- ✅ Animation system with metadata-driven configuration
- ✅ Visual FX system (screen shake, flash, particles)
- ✅ Sound system with animation frame triggers
- ✅ Cutscene-style YAML demo with cinematic playback

---

## 🗺 Scenario System

Scenarios are defined in YAML and include:

```yaml
name: "Arena Skirmish"
map_id: "arena"
max_turns: 12
units:
  - id: knight
    team: player
    hp: 15
    ap: 6
  - id: bandit
    team: ai
    hp: 12
    ap: 5
```

Terrain maps:

```
G G G G
R G F G
W G G G
```

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
- 97/97 tests passing
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
│   └── renderer.py              # NEW: visual renderer
├── devtools/
│   ├── scenario_loader.py
│   ├── map_loader.py
│   └── sim_runner_demo.py
├── maps/
│   ├── arena.map
│   ├── catacombs.map
├── assets/
│   ├── tiles/
│   ├── units/
├── tests/
├── README.md
├── plan.md
├── resumegpt.md
```

---

## 🚧 Roadmap

- [x] 🎨 Visual rendering for grid + terrain + units
- [x] 🌀 Add animation system (idle, move, attack, death)
- [x] 🎭 Add visual FX system (screen shake, flash, particles)
- [x] 🔊 Add sound system with animation triggers
- [x] 🎬 Add cutscene-style cinematic playback
- [ ] 🧠 Add enemy AI behavior for combat
- [ ] 🧪 Add debugger viewer mode with overlays
- [ ] 🗡️ Add attack system with effects + feedback
- [ ] 📦 Polish scenario content and YAML validators
