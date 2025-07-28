# Starter Town Tactics

A turn-based tactical RPG learning project inspired by Final Fantasy Tactics, written in Python using Pygame.

---

## 🔧 Development Status

- **Total Tests:** 39
- **Passing:** 31
- **Failing:** 8
- **Coverage:** 83%

### Known Issues
- Input normalization (key casing) inconsistency
- Terrain movement validation is incomplete
- Some modules have interdependencies that need decoupling
- Build is in mid-refactor state; game runs but test suite fails on critical logic

---

## 🛠️ Next Steps
- Fix remaining test failures
- Re-establish a consistent input handling system (mouse, keyboard, gamepad)
- Finalize turn cycle integration and terrain movement rules
- Reach stable build milestone before continuing gameplay features

---

## 💡 Sprint Retrospective Summary
- Integrated phased turn logic via `TurnPhase`
- Restored `SimRunner` simulation and added event logging
- Implemented cursor and terrain overlays
- Confirmed rendering and tile system are robust

---

## 💾 Local Dev
Use the following to run tests:
```bash
make clean
make test
```
To skip pre-commit temporarily when committing:
```bash
git commit --no-verify -m "Save work"
```