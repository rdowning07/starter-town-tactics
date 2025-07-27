import pytest
from game.sim_runner import simulate_battle


def test_simulation_runs_without_crashing():
    log = simulate_battle()

    # Validate log is a list
    assert isinstance(log, list), "Log should be a list"

    # Validate turn count
    assert len(log) == 10, "Log should contain 10 turn entries"

    # Validate each log entry is a string and includes a phase label
    for entry in log:
        assert isinstance(entry, str), "Each log entry should be a string"
        assert "Turn" in entry, "Each log entry should include 'Turn'"
        assert "PLAYER" in entry or "AI" in entry, "Each log should indicate a phase"
