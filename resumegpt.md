## 2025-07-29: Fix for Persistent ImportError in test_turn_controller.py

### Problem
- Repeated ImportErrors due to `ModuleNotFoundError: No module named 'utils'` when running `make test`.

### Cause
- Relative and absolute imports broke due to `PYTHONPATH` not including project root (`.`).

### Fixes Applied
- `Makefile`: Updated `test`, `coverage`, and `htmlcov` to use `PYTHONPATH=.`.
- `test_turn_controller.py`: Switched to absolute import `from tests.utils.dummy_game`.
- Verified `tests/__init__.py` and `tests/utils/__init__.py` are present.

### Result
All test imports now resolve consistently during `make test` execution.
