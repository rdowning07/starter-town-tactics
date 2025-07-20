# Starter Town Tactics

**A tactical tile-based RPG simulation engine written in Python.**

---

## 📌 Overview

Starter Town Tactics is a simplified turn-based tactics game, inspired by **Final Fantasy Tactics** and similar grid-based strategy games. It models movement, terrain costs, unit interactions, and turn progression for future AI-driven or GUI-based expansion.

---

## ✅ Current Sprint Summary (Sprint Wrap: 2025-07-20)

- ✅ All 13 tests passing with `pytest`
- ✅ `black`, `isort`, and `mypy` passing in pre-commit
- ⚠️ `pylint` passes with minor warnings (code rating: ~9.3/10)
- ✅ `resumegpt.md` created to support future development resumption
- ✅ Modularized and fully working:
  - `unit.py`
  - `grid.py`
  - `tile.py`
  - `game.py`
  - `main.py`

---

## 📂 Project Structure

```
starter-town-tactics/
├── game/
│   ├── __init__.py
│   ├── game.py         # Game loop and turn management
│   ├── grid.py         # Grid and tile management
│   ├── tile.py         # Terrain and symbol logic
│   ├── unit.py         # Unit behavior and movement
│   └── main.py         # Sample script to run the game
├── tests/              # Pytest-based unit tests
│   ├── conftest.py
│   ├── test_game.py
│   ├── test_grid.py
│   ├── test_grid_output.py
│   ├── test_grid_property.py
│   ├── test_unit.py
│   ├── test_unit_movement_edge_cases.py
│   └── test_unit_terrain_cost.py
├── readme.md           # (You are here)
├── resumegpt.md        # Sprint resumption state for ChatGPT sessions
├── pytest.ini
└── .pre-commit-config.yaml
```

---

## 🧪 How to Run Tests

Make sure you're inside your virtual environment (`venv`), then run:

```bash
pytest
```

---

## 🚦 Terrain Types

Terrain types affect movement cost and are displayed with symbols in `print_ascii()`.

| Terrain   | Symbol | Movement Cost |
|-----------|--------|----------------|
| Plains    | `.`    | 1              |
| Forest    | `F`    | 1              |
| Mountain  | `M`    | 3              |
| Water     | `W`    | Unwalkable     |

---

## 🕹️ Example Output (ASCII Map)

```
Game Map:
. F
. .
```

---

## 👣 Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/rdowning07/starter-town-tactics.git
   cd starter-town-tactics
   ```

2. Set up your environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the sample game:
   ```bash
   python -m game.main
   ```

---

## 🛠️ Next Sprint Preview

- Add more terrain types
- Introduce attack/defense mechanics
- Start AI movement planning
- Connect to GUI for basic visualization

---

## 🤖 Development Tools

- Python 3.11+
- `pytest`, `black`, `isort`, `mypy`, `pylint`
- GitHub with pre-commit hooks

---

## 🧠 Resume This Project in ChatGPT

Use `resumegpt.md` to reopen this context with a clean state and pick up development from where you left off.

---

## 🧾 License

MIT License

---
