# Starter Town Tactics

A tile-based tactical simulation engine built in Python.  
Created by [rdowning07](https://github.com/rdowning07) for a PMIII → Principal PMT/SDM transition roadmap at Amazon.

---

## Features

- ✅ Grid-based map with terrain types and movement costs
- ✅ Units with customizable movement range, diagonal rules
- ✅ Defensive movement logic and validation (off-grid, occupied, etc.)
- ✅ Pytest test suite with high coverage of edge cases
- ✅ Modular Python architecture (`game/`, `tests/`)

---

## Getting Started

```bash
# From the root of the repo:
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m pytest

Learning Journey & AI Integration

This repo supports techincal growth from architecture to delivery leveraging AI.

✅ Technical Milestones
Built core classes: Tile, Grid, Unit, Game
Implemented terrain-movement logic and edge-case guards
Created full test suite with Pytest
Modularized Python packages for scaling
🤖 AI-Augmented Work
Used ChatGPT for:
Scaffolding architecture
Troubleshooting module/import errors
Refactoring test cases and CLI test runs
Tracking PM-style milestones in plan.md

Repo Structure
starter-town-tactics/
├── game/                # Core game logic
├── tests/               # Unit + integration test cases
├── plan.md              # Learning plan & milestone tracking
├── README.md
├── pytest.ini
└── ...
