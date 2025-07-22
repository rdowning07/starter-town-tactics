# 🧭 Starter Town Tactics – Strategic Build & Learning Plan

## 🎯 Purpose

This project is a tactical RPG prototype inspired by Fire Emblem and Final Fantasy Tactics. It's designed as a **learning vehicle** and **portfolio artifact** for transitioning from a Senior Program Manager (L6) at Amazon to a Principal PMT or SDM role.

---

## ✅ July 2025 Accomplishments (Week 1–2)

### 🔧 Technical Development

- Built tile-based grid engine and `Unit` movement system with terrain checks
- Designed and implemented a `SpriteManager` to modularly load images
- Completed unit selection, movement preview, and click-to-move with Pygame
- Added debug overlay with cursor location, turn tracking, and unit info
- Created 15+ Pytest-based tests covering units, movement, terrain, and rendering
- Integrated and passed pre-commit hooks:
  - `black` (code formatting)
  - `isort` (import sorting)
  - `mypy` (static typing)
  - `pylint` (code linting – minor style warnings only)

### 💡 AI-Enhanced Workflow

- Used ChatGPT and Cursor to:
  - Design Python OOP classes and structure
  - Write testable logic and validate behaviors
  - Explain Git/GitHub workflows in VS Code
  - Maintain documentation and development journals (`resumegpt.md`)

---

## 📈 Week 3 Kickoff – August 2025

### 🧩 Game Feature Roadmap

| Feature                      | Description                                                              |
|-----------------------------|--------------------------------------------------------------------------|
| 🧠 Input State Machine       | Add support for keyboard cursor, selection state, and turn flow          |
| ⌨️ Keyboard Navigation       | Enable Fire Emblem-style grid cursor using arrow keys / WASD             |
| 🔄 Turn Cycle Logic         | Add player vs enemy phase distinction and cycling                        |
| 🗃️ Modular Refactor          | Extract input, rendering, and game loop from `main.py`                   |
| ✅ Expanded Tests            | Validate keyboard input, selection logic, and phase control              |

---

## 📌 Strategic Learning Outcomes

- **Architecture**: Modularize monolithic code into scalable components
- **Testing**: Deepen test coverage for UI logic and interaction modes
- **AI Literacy**: Practice prompt engineering, LLM-assisted debugging
- **Product Thinking**: Ship, test, and iterate on end-to-end UX flows
- **AWS/AI Readiness**: Continue prep for AI Practitioner certification

---

## 🛠️ Tools & Stack

- **Python 3.11** with `pygame`, `pytest`
- **VS Code**, GitHub, pre-commit hooks
- **ChatGPT + Cursor** for co-programming, refactoring, and research
- **MCP & agent exploration** planned for tactical logic in Week 4+

---

## 🔚 Exit Criteria for August

- [ ] Turn system functional with state transitions
- [ ] Mouse and keyboard input unified under state machine
- [ ] GitHub Actions pipeline defined (test-on-push)
- [ ] Refactor complete (`main.py` split cleanly)
- [ ] Readme updated with new screenshots, keyboard guide

---

> ✅ This project is a living record of technical depth, design judgment, and career-ready learning. Each milestone closes the gap to SDM/PMT readiness.
