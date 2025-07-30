# Project Plan

## Test Integration Plan ✅ COMPLETED
- ✅ Add missing unit tests for uncovered lines in ai_controller.py, gamepad_controller.py, grid.py, turn_controller.py, unit.py, sprite_manager.py, and input_state.py.
- ✅ Run the test suite and confirm coverage is near or at 100%.
- ✅ Remove debug prints and clean up test scaffolding.
- ✅ Document any tricky or non-obvious test cases.

## Refactoring Plan 🚧 IN PROGRESS

### High-Level Refactoring
- Review all modules for code smells, long functions, and unclear variable names.
- Incrementally refactor large or complex functions into smaller, focused ones.
- Remove dead code and unused imports.
- Improve naming for clarity and consistency.
- Add or update docstrings and inline comments for all public classes and methods.
- Modularize code where possible (e.g., split large files, group related logic).
- Run the full test suite after each change to ensure no regressions.
- Update README and developer documentation to reflect any interface changes.
- Use code reviews or pair programming for major refactors.
- Repeat as needed to maintain a clean, maintainable codebase.

### Tactical Refactoring Tasks
1. **Create automated context preservation system:**
   - [ ] `context_registry.py` for canonical interfaces
   - [ ] `session_bootstrap.sh` for resuming full dev context
2. **Resolve mypy drift:**
   - [ ] Add missing type annotations (log, get_cursor_sprite, etc.)
   - [ ] Re-align class signatures with updated usage
3. **Modularize debug_overlay and main loop:**
   - [ ] Validate `draw_debug_overlay` contract
   - [ ] Split `main.py` into `main.py`, `app.py`, `loop.py`
4. **Refactor with Cursor and # @api alignment:**
   - [ ] Safely modify methods with tests present
   - [ ] Track regressions and fixes with test pins

### Development Workflow Improvements
- [ ] Build GitHub Action for contract regression checks
- [ ] Add LLM-aware `.devcontainer.json` for VS Code + Cursor
- [ ] Maintain `PYTHONPATH=.` in all scripts and Makefile
- [ ] Ensure every subdir with test helpers has `__init__.py`
- [ ] Treat `Makefile` as canonical test entrypoint
- [ ] Run full test suite after each refactoring change

---

## 📌 Key Milestones

| Milestone                     | Status  |
|------------------------------|----------|
| Import System & PYTHONPATH   | ✅ Done |
| Keyboard Controller          | ✅ Done |
| Gamepad Controller + Vibe    | ✅ Done |
| AIController + MCP support   | ✅ Done |
| AIController Tests           | ✅ Done |
| Test Coverage (100%)         | ✅ Done |
| Overlays (threat, attack, terrain, movement) | ✅ Done |
| Pre-commit compliance (black, isort, mypy) | ✅ Done |
| Canonical API contracts (# @api) | ✅ Done |
| Cursor + ChatGPT integration | ✅ Done |
| Code Refactoring             | 🚧 Next |
| Context preservation system  | 🔮 Future |
| GitHub Actions & containers  | 🔮 Future |
| Story + Art Framework        | 🔮 Future |

## 🔧 Technical Safeguards
- Maintain `PYTHONPATH=.` in all scripts and Makefile
- Ensure every subdir with test helpers has `__init__.py`
- Treat `Makefile` as canonical test entrypoint
- Run full test suite after each refactoring change
- Use # @api tags for canonical interfaces
- Maintain 97%+ test coverage
- Pre-commit hooks for code quality (black, isort, mypy)