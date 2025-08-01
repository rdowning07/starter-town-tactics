# 🧠 Starter Town Tactics

A turn-based tactical combat simulation inspired by classic tactical RPGs (Final Fantasy Tactics, Fire Emblem), built for learning game architecture, AI integration, and simulation.

**🎉 Technical Foundation Complete!** Ready for game development phase.

---

## 🎮 Features

- 🔁 **Turn-based simulation engine**
- ⚔️ **Action Point system**
- 🎯 **Finite State Machine for tactical phases**
- 🧠 **AI-controlled enemy turns**
- 💀 **Unit death and turn skipping**
- 🛠 **Scenario loader (YAML)**
- 📋 **Structured logging with event history**
- 🧪 **94 tests, 85% coverage, full mypy compliance**

---

## 📂 Project Structure

```
starter-town-tactics/
├── game/
│   ├── sim_runner.py             # Simulation loop (player/AI turns)
│   ├── turn_controller.py        # Turn order management
│   ├── action_point_manager.py   # AP cost + tracking
│   ├── tactical_state_machine.py # FSM for tactical UI state
│   ├── unit_manager.py           # HP/team/alive tracking
│   ├── game_state.py             # Central system hub
│   ├── ai_controller.py          # Simple AI logic
│   ├── grid.py                   # Grid-based game world
│   ├── input_state.py            # Input management
│   ├── keyboard_controller.py    # Keyboard input handling
│   ├── gamepad_controller.py     # Gamepad input handling
│   ├── unit.py                   # Unit entity management
│   ├── sprite_manager.py         # Asset management
│   └── overlay/                  # Grid overlays for movement, threats, terrain
│       ├── grid_overlay.py
│       └── overlay_state.py
│
├── devtools/
│   ├── sim_runner_demo.py        # CLI interactive demo
│   ├── scenario_loader.py        # Loads YAML config into GameState
│   └── scenarios/
│       └── demo_battle.yaml      # YAML-defined test scenario
│
├── tests/                        # 94 tests, 85% coverage
├── bin/                          # Developer utilities
│   └── safe-commit.sh
├── plan.md                       # Updated roadmap and weekly sprint plan
├── resumegpt.md                  # Personal learning + architecture continuity log
├── context_registry.py           # Canonical API contracts across modules
├── session_bootstrap.sh          # Loads persistent session context
├── Makefile                      # Developer commands
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🚀 Getting Started

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Tests
make test
make typecheck
make lint

# Play CLI demo
make play-sim-demo
make play-scenario-demo
```

---

## 🧪 Testing Strategy

- **Unit Tests** for each system (AP, FSM, AI, Sim, Turn)
- **Scenario Tests** with CLI output validation
- **mypy** for type safety
- **flake8** for code quality

---

## 🤖 AI-Driven Development

We use the following AI copilots:

| Tool     | Role                        |
|----------|-----------------------------|
| ChatGPT  | Lead architect & test driver |
| Cursor   | Inline refactor & code copilot |
| Claude   | Strategy review & test summarization |

---

## 🧠 Context Continuity Tools

| File | Purpose |
|------|---------|
| `context_registry.py` | Canonical interface contract tracker |
| `session_bootstrap.sh` | Loads plan, resume, and context into ChatGPT |
| `plan.md` | Sprint-by-sprint development plan |
| `resumegpt.md` | Persistent session log and state tracker |

---

## 🎮 Current Status

### ✅ Completed (Technical Foundation Sprint)
- **Test Integration**: 85%+ coverage across 94 tests
- **Input System**: Keyboard, mouse, gamepad support
- **AI Integration**: AIController with MCP support
- **Code Quality**: All pre-commit checks passing
- **Architecture**: Modular, testable, maintainable codebase
- **Documentation**: Comprehensive API contracts and guides

### 🚧 Next Phase (Game Development)
- **Battle System**: Combat mechanics, damage calculations, battle UI
- **Turn-Based Gameplay**: Action points, multiple action types, turn order
- **Visual Improvements**: Enhanced Pygame graphics, animations, HUD
- **Game Content**: Campaign levels, character progression, story elements

---

## 🔮 Roadmap

- [ ] Battle mechanics (attacks, damage resolution)
- [ ] Victory conditions and game objectives
- [ ] Terrain effects and overlays
- [ ] Pygame reintegration for graphical mode
- [ ] Agent-based scenario replays
- [ ] Audio narration from logs

---

## 👤 Author

Rob Downing, assisted by ChatGPT and Cursor.dev

Architecture, simulation, and AI by design — built as a learning lab and demo platform.

---

## 🧠 License

MIT License — for educational and demonstration purposes.
