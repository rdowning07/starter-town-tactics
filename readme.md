# Starter Town Tactics

A tactical RPG engine inspired by Final Fantasy Tactics and Pathfinder, designed to support AI-driven and player-controlled gameplay. Developed as part of a learning journey into AI, game architecture, and software engineering.

---

## 🎮 Features

- Grid-based tactical combat
- Keyboard, mouse, and gamepad input support
- Turn-based game loop with phase control
- AI agent logic via `AIController` and pluggable `MCP` strategies
- Full unit selection, movement, and interaction
- ASCII rendering system for testing and prototyping

---

## 🧠 AI Integration

- **AIController**: Controls enemy turns with either hardcoded logic or a pluggable MCP agent.
- **MCP (Map-Command-Predict)**: Pluggable AI decision engine supporting:
  - `"nearest"`: Move toward the closest enemy
  - Future support for: `"aggressive"`, `"defensive"`, `"flank"`

---

## 🧪 Testing

- 44 tests across modules including input, AI, unit movement, and edge cases
- Full suite runnable with `./test_debug.sh`

```bash
./test_debug.sh
```

---

## 🧪 Simulation

- `sim_runner.py` runs a sample 10-turn battle with or without MCP:

```bash
python sim_runner.py
```

---

## 🧰 Dev Scripts

- `./dev_push.sh "message"`: Force-add, commit, push
- `./test_debug.sh`: Run all tests with verbose debug

Make scripts executable:
```bash
chmod +x dev_push.sh test_debug.sh
```

---

## 🚧 Roadmap

- [x] Input state machine for all input types
- [x] MCP integration into AI turns
- [ ] Richer terrain and pathfinding
- [ ] Fog of war and visibility
- [ ] Story + cutscene scaffolding
- [ ] Art + animation system

---

## 📁 Structure

```
game/
├── ai_controller.py
├── gamepad_controller.py
├── keyboard_controller.py
├── input_state.py
├── mcp.py
├── sprite_manager.py
├── turn_controller.py
├── unit.py
tests/
├── test_ai_controller.py
├── test_input_state.py
├── test_mcp.py
├── ...
```

---

This project is part of a career progression initiative focused on learning AI, architecture, and PMT-level software leadership through hands-on development.