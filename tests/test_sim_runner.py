from game.game import Game
from game.sim_runner import SimRunner
from game.unit import Unit


def test_simulation_run():
    game = Game(5, 5)
    game.add_unit(Unit("SimHero", 2, 2, team="Blue"))
    sim = SimRunner(game)
    sim.run()
    assert len(sim.log) > 0
