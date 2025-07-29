## Sprint Recovery: 2025-07-29

### Context Loss Fix (Complete)
- [x] Add PYTHONPATH to Makefile to fix imports
- [x] Update test_turn_controller to use absolute imports
- [x] Confirm presence of __init__.py in test directories

### Next Steps
- [ ] Re-run all tests: `make clean && make test`
- [ ] Continue repairs for AI turn loop via SimRunner and TurnController
- [ ] Expand dummy_game if needed for additional test scaffolding
- [ ] Push changes once tests pass and structure is stable

### Future Safeguards
- Maintain `PYTHONPATH=.` in all scripts
- Ensure every subdir with test helpers has `__init__.py`
- Treat `Makefile` as a canonical test entrypoint
