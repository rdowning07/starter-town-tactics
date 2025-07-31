# Project Plan

## ✅ SPRINT COMPLETED - Technical Foundation Phase

### Test Integration Plan ✅ COMPLETED
- ✅ Add missing unit tests for uncovered lines in ai_controller.py, gamepad_controller.py, grid.py, turn_controller.py, unit.py, sprite_manager.py, and input_state.py.
- ✅ Run the test suite and confirm coverage is near or at 100%.
- ✅ Remove debug prints and clean up test scaffolding.
- ✅ Document any tricky or non-obvious test cases.

### Refactoring Plan ✅ COMPLETED
- ✅ Review all modules for code smells, long functions, and unclear variable names.
- ✅ Incrementally refactor large or complex functions into smaller, focused ones.
- ✅ Remove dead code and unused imports.
- ✅ Improve naming for clarity and consistency.
- ✅ Add or update docstrings and inline comments for all public classes and methods.
- ✅ Modularize code where possible (e.g., split large files, group related logic).
- ✅ Run the full test suite after each change to ensure no regressions.
- ✅ Update README and developer documentation to reflect any interface changes.
- ✅ Use code reviews or pair programming for major refactors.
- ✅ Repeat as needed to maintain a clean, maintainable codebase.

### Tactical Refactoring Tasks ✅ COMPLETED
1. **Create automated context preservation system:**
   - ✅ `context_registry.py` for canonical interfaces
   - ✅ `session_bootstrap.sh` for resuming full dev context
2. **Resolve mypy drift:**
   - ✅ Add missing type annotations (log, get_cursor_sprite, etc.)
   - ✅ Re-align class signatures with updated usage
3. **Modularize debug_overlay and main loop:**
   - ✅ Validate `draw_debug_overlay` contract
   - ✅ Split `main.py` into `main.py`, `app.py`, `loop.py`
4. **Refactor with Cursor and # @api alignment:**
   - ✅ Safely modify methods with tests present
   - ✅ Track regressions and fixes with test pins

### Development Workflow Improvements ✅ COMPLETED
- ✅ Build GitHub Action for contract regression checks
- ✅ Add LLM-aware `.devcontainer.json` for VS Code + Cursor
- ✅ Maintain `PYTHONPATH=.` in all scripts and Makefile
- ✅ Ensure every subdir with test helpers has `__init__.py`
- ✅ Treat `Makefile` as canonical test entrypoint
- ✅ Run full test suite after each refactoring change

---

## 🎮 NEXT PHASE - Game Development

### **🎯 CURSOR'S STRATEGIC ASSESSMENT & RECOMMENDATIONS**

**Cursor (AI Tech Lead) Analysis**: As an experienced tech lead who has designed FFT/Fire Emblem-style games, the original plan to jump straight to "Battle System Implementation" is premature. In tactical RPGs, the core gameplay loop is: **Movement → Positioning → Combat → Turn Management**.

**Key Insight**: Positioning is 80% of the strategy in FFT/Fire Emblem games. Players spend most time thinking about where to move to avoid threats and how to position for optimal attacks. Combat is just the resolution of good positioning.

**Strategic Concerns**:
- Missing critical **positioning and tactical depth** before combat
- Need **attack range visualization**, **threat zones**, **movement range preview**
- Turn system needs **action points**, **turn order**, **end turn validation**
- Without strong tactical positioning mechanics, combat feels shallow

### **🎮 REVISED PLAN: Tactical-First Approach**

#### **Phase 1: Tactical Foundation (Next 2-3 weeks) 🚧 IN PROGRESS**

1. **Enhanced Movement & Positioning:**
   - [ ] Attack range visualization overlays
   - [ ] Threat zone calculations and display
   - [ ] Movement range preview with pathfinding
   - [ ] Terrain effects on positioning (cover, elevation)

2. **Turn System Enhancement:**
   - [ ] Action point system (move + attack, or multiple moves)
   - [ ] Turn order display and initiative
   - [ ] End turn validation and confirmation
   - [ ] Turn state management (selecting, moving, attacking, ending)

3. **Tactical UI Improvements:**
   - [ ] Clear visual feedback for valid/invalid actions
   - [ ] Hover effects showing attack ranges and movement
   - [ ] Turn indicator and action point display
   - [ ] Undo/redo functionality for moves

#### **Phase 2: Combat System (After tactical foundation) 🔮 FUTURE**

1. **Basic Combat Mechanics:**
   - [ ] Attack range validation
   - [ ] Damage calculation (weapon + stats + terrain)
   - [ ] Combat animations and feedback
   - [ ] Death and unit removal

2. **Combat UI:**
   - [ ] Attack preview (damage, hit chance)
   - [ ] Combat resolution display
   - [ ] Health bars and status effects

#### **Phase 3: Game Content 🔮 FUTURE**
- [ ] Character classes and progression
- [ ] Campaign levels and missions
- [ ] Story elements and dialogue

### **🔧 CURSOR'S TECHNICAL RECOMMENDATIONS**

#### **Immediate Next Steps:**
1. **Enhance `InputState`** with action point tracking
2. **Extend `Grid`** with range calculation methods
3. **Improve `TurnController`** with action point system
4. **Add tactical overlays** for ranges and threats

#### **Architecture Considerations:**
- **Range Calculation Service**: Centralized logic for attack/movement ranges
- **Action Point Manager**: Track and validate available actions
- **Tactical State Machine**: Manage turn phases (select → move → attack → end)
- **Overlay System**: Visual feedback for tactical information

---

## 📌 Key Milestones

| Milestone                     | Status  |
|------------------------------|----------|
| Import System & PYTHONPATH   | ✅ Done |
| Keyboard Controller          | ✅ Done |
| Gamepad Controller + Vibe    | ✅ Done |
| AIController + MCP support   | ✅ Done |
| AIController Tests           | ✅ Done |
| Test Coverage (97%+)         | ✅ Done |
| Overlays (threat, attack, terrain, movement) | ✅ Done |
| Pre-commit compliance (black, isort, mypy) | ✅ Done |
| Canonical API contracts (# @api) | ✅ Done |
| Cursor + ChatGPT integration | ✅ Done |
| Code Refactoring             | ✅ Done |
| Context preservation system  | ✅ Done |
| **Technical Foundation Sprint** | ✅ **COMPLETED** |
| **Tactical Foundation Phase** | 🚧 **CURRENT** |
| Enhanced Movement & Positioning | 🚧 Next |
| Turn System Enhancement      | 🔮 Future |
| Combat System Implementation | 🔮 Future |
| Visual and UI Improvements   | 🔮 Future |
| Game Content Creation        | 🔮 Future |
| Story + Art Framework        | 🔮 Future |

## 🔧 Technical Safeguards
- Maintain `PYTHONPATH=.` in all scripts and Makefile
- Ensure every subdir with test helpers has `__init__.py`
- Treat `Makefile` as canonical test entrypoint
- Run full test suite after each refactoring change
- Use # @api tags for canonical interfaces
- Maintain 97%+ test coverage
- Pre-commit hooks for code quality (black, isort, mypy)
- **NEW**: Maintain game balance and playability testing
- **NEW**: Regular playtesting and feedback integration
- **NEW**: Tactical depth validation (positioning mechanics)