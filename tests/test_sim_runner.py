from game.game import Game
from game.sim_runner import SimRunner
from game.unit import Unit


def test_simulation_run():
    game = Game(5, 5)
    game.add_unit(Unit("SimHero", 2, 2, team="Blue"))
    game.add_unit(Unit("SimAI", 1, 1, team="AI"))  # Add an AI unit
    sim = SimRunner(game)
    sim.run()
    # Check that the log is not empty
    assert len(sim.log) > 0
    # Check that the log contains simulation start
    assert any("Simulation started" in entry for entry in sim.log)
    # Check that the log contains at least one player or AI action
    assert any("AI acted with" in entry or "Skipped player turn" in entry for entry in sim.log)
