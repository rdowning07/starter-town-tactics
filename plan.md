# 🧠 Project Plan - Starter Town Tactics

## ✅ Phase 1: Technical Foundations (Complete)
- [x] Build AP + Turn Controller core
- [x] Integrate FSM (TacticalStateMachine)
- [x] SimRunner with AI and player input
- [x] CLI demo with interactive and auto-run modes
- [x] YAML scenario loader + integration
- [x] GameState hub and UnitManager design
- [x] Full test + type coverage (94 tests, 85% coverage)

### **🎯 CURSOR'S STRATEGIC ASSESSMENT & RECOMMENDATIONS**

**Cursor (AI Tech Lead) Analysis**: As an experienced tech lead who has designed FFT/Fire Emblem-style games, the original plan to jump straight to "Battle System Implementation" is premature. In tactical RPGs, the core gameplay loop is: **Movement → Positioning → Combat → Turn Management**.

**Key Insight**: Positioning is 80% of the strategy in FFT/Fire Emblem games. Players spend most time thinking about where to move to avoid threats and how to position for optimal attacks. Combat is just the resolution of good positioning.

**Strategic Concerns**:
- Missing critical **positioning and tactical depth** before combat
- Need **attack range visualization**, **threat zones**, **movement range preview**
- Turn system needs **action points**, **turn order**, **end turn validation**
- Without strong tactical positioning mechanics, combat feels shallow

## 🚧 Phase 2: Core Gameplay Features (Current)
- [ ] Battle system: attack, damage, death effects
- [ ] Team-based win conditions
- [ ] Map data loading from YAML
- [ ] Fog of war and vision radius
- [ ] Basic animation/visual feedback hooks

### **🎮 REVISED PLAN: Tactical-First Approach**

#### **Phase 2a: Enhanced Movement & Positioning (75% Complete)**
- [x] Attack range visualization overlays
- [x] Threat zone calculations and display
- [x] Movement range preview with pathfinding
- [ ] Terrain effects on positioning (cover, elevation)

#### **Phase 2b: Turn System Enhancement (85% Complete)**
- [x] Action point system (move + attack, or multiple moves)
- [x] Turn order display and initiative
- [x] End turn validation and confirmation
- [x] Turn state management (selecting, moving, attacking, ending)

#### **Phase 2c: Tactical UI Improvements (60% Complete)**
- [x] Clear visual feedback for valid/invalid actions
- [ ] Hover effects showing attack ranges and movement
- [x] Turn indicator and action point display
- [ ] Undo/redo functionality for moves

## 🧪 Testing + Quality
- [x] Full pytest suite (94 tests)
- [x] mypy compliant (100%)
- [x] Lint compliant (minor line length/style)
- [ ] Add integration tests for end-to-end scenario

## 🛠️ Tooling + Dev Experience
- [x] Updated Makefile with demo/play targets
- [x] Log formatting and emoji feedback
- [ ] Add coverage targets to Makefile
- [ ] Optional CI config (GitHub Actions)

## 🗺️ Phase 3: Visual and UX
- [ ] Restore Pygame engine loop
- [ ] Visual overlay hooks
- [ ] Sprite loading and animation support

## 🚀 Stretch Goals
- [ ] Agents as AI players (from scenario prompts)
- [ ] Audio narration or podcast log
- [ ] Online simulation replay via event logs

---

## 📌 Key Milestones

| Milestone                     | Status  |
|------------------------------|----------|
| Import System & PYTHONPATH   | ✅ Done |
| Keyboard Controller          | ✅ Done |
| Gamepad Controller + Vibe    | ✅ Done |
| AIController + MCP support   | ✅ Done |
| AIController Tests           | ✅ Done |
| Test Coverage (85%+)         | ✅ Done |
| Overlays (threat, attack, terrain, movement) | ✅ Done |
| Pre-commit compliance (black, isort, mypy) | ✅ Done |
| Canonical API contracts (# @api) | ✅ Done |
| Cursor + ChatGPT integration | ✅ Done |
| Code Refactoring             | ✅ Done |
| Context preservation system  | ✅ Done |
| **Technical Foundation Sprint** | ✅ **COMPLETED** |
| **Tactical Foundation Phase** | 🚧 **75% COMPLETE** |
| Enhanced Movement & Positioning | 🚧 90% Complete |
| Turn System Enhancement      | ✅ Complete |
| Combat System Implementation | 🚧 25% Complete |
| Visual and UI Improvements   | 🔮 Future |
| Game Content Creation        | 🔮 Future |
| Story + Art Framework        | 🔮 Future |

## 🔧 Technical Safeguards
- Maintain `PYTHONPATH=.` in all scripts and Makefile
- Ensure every subdir with test helpers has `__init__.py`
- Treat `Makefile` as canonical test entrypoint
- Run full test suite after each refactoring change
- Use # @api tags for canonical interfaces
- Maintain 85%+ test coverage
- Pre-commit hooks for code quality (black, isort, mypy)
- **NEW**: Maintain game balance and playability testing
- **NEW**: Regular playtesting and feedback integration
- **NEW**: Tactical depth validation (positioning mechanics)