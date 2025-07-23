import pytest

from game.sim_runner import simulate_battle


def test_simulation_runs_without_crashing():
    log = simulate_battle()
    assert isinstance(log, list)
    assert len(log) == 10
    assert all(isinstance(entry, str) for entry in log)
    assert any("PLAYER" in entry or "AI" in entry for entry in log)
