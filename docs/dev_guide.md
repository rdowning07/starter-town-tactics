# Developer Guide

## Setup Instructions

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
make clean
make test
```

**Current Status**: 97%+ test coverage across 61 tests ✅

## Pre-commit Hooks

Ensure the following tools are installed:
```bash
pre-commit install
pre-commit run --all-files
```

## Git Commit (Safe Mode)

Use `bin/safe-commit.sh`:
```bash
./bin/safe-commit.sh "Your commit message here"
```

## Architecture Continuity

### Context Loading

Use `session_bootstrap.sh` to resume context:
```bash
./session_bootstrap.sh
```

### Interface Contracts

All major APIs are marked using `# @api` or `# @contract` in:
- `context_registry.py`
- Used by Cursor and ChatGPT for test and refactor validation.

## Contribution Standards

- Follow TDD (test before or alongside code).
- Use `black`, `isort`, `mypy`, `flake8`, `pylint` compliance.
- Document interface drift in `context_registry.py`.
- Maintain 97%+ test coverage.

## Cursor Integration

`.cursor/config.json` indexes key files and defines instructional context to ensure architectural memory is retained across sessions.

---

## Current Development Phase

### ✅ Completed (Technical Foundation)
- **Test Integration**: 97%+ coverage achieved
- **Input System**: Multi-platform input handling
- **AI Integration**: Automated AI behavior
- **Code Quality**: All pre-commit checks passing
- **Architecture**: Modular, testable design

### 🚧 Next Phase (Game Development)
- **Battle System**: Combat mechanics, damage calculations
- **Turn-Based Gameplay**: Action points, multiple action types
- **Visual Improvements**: Enhanced Pygame graphics, animations
- **Game Content**: Campaign levels, character progression

---

## Quality Gates

- **Test Coverage**: Must maintain 97%+ coverage
- **Pre-commit**: All hooks must pass before commit
- **Type Safety**: Full mypy compliance required
- **Documentation**: API contracts must be up to date
- **Architecture**: Modular design with clear separation of concerns