# Starter Town Tactics

A Final Fantasy Tactics–inspired tactical RPG built in Python using `pygame`, developed as a learning project to:
- Deepen software architecture and AI integration skills
- Transition from PMIII to TPM/SDM roles at Amazon
- Demonstrate mastery of interface design, simulation systems, and test-driven workflows

---

## 🧱 Project Structure

```
starter-town-tactics/
├── game/                   # Core game logic and architecture
│   ├── ai_controller.py
│   ├── game.py
│   ├── grid.py
│   ├── input_state.py
│   ├── keyboard_controller.py
│   ├── mcp.py
│   ├── sprite_manager.py
│   ├── turn_controller.py
│   ├── unit.py
│   └── overlay/            # Grid overlays for movement, threats, terrain
│       ├── grid_overlay.py
│       └── overlay_state.py
├── tests/                  # Pytest unit tests for all modules
│   └── utils/
│       └── dummy_game.py
├── bin/                    # Developer utilities
│   └── safe-commit.sh
├── plan.md                 # Updated roadmap and weekly sprint plan
├── resumegpt.md           # Personal learning + architecture continuity log
├── context_registry.py    # Canonical API contracts across modules
├── session_bootstrap.sh   # Loads persistent session context
├── Makefile               # `make test`, `make lint`, `make typecheck`, etc.
└── README.md              # This file
```

---

## 🧪 Testing & Quality Gates

This project is built with full CI discipline:
- ✅ `pytest` + `pytest-cov` (non-integration tests only)
- ✅ `mypy` (strict type checking)
- ✅ `flake8`, `pylint`, `black`, `isort` (pre-commit hooks)
- ✅ `make test`, `make lint`, `make typecheck`, `make clean`
- ✅ `bin/safe-commit.sh` for VS Code push reliability

**Current test coverage:** 97% across 61 tests

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

## 🔜 Coming Soon (added to plan)

We will create:
- `docs/architecture.md`: Overview of the component design
- `docs/dev_guide.md`: How to contribute, run tests, extend systems
