## 🧪 Test Infrastructure Update

### Summary
- Added `PYTHONPATH=.` to `Makefile` test commands.
- Converted `tests/test_turn_controller.py` to use absolute imports.

### Why?
Avoids brittle relative paths and `ModuleNotFoundError` across environments.

### Next
Use `make test` instead of raw `pytest` for consistent imports and coverage.
