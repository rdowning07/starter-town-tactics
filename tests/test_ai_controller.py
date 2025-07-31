from game.ai_controller import AIController
from game.grid import Grid
from game.unit import Unit


def test_ai_update_moves_unit_down():
    grid = Grid(3, 3)
    unit = Unit("AIUnit", 1, 1, team="AI")
    grid.get_tile(1, 1).unit = unit
    ai = AIController([unit])
    ai.update(grid)
    assert unit.y == 2  # Should have moved down

def test_ai_take_action_moves_unit_down():
    grid = Grid(3, 3)
    unit = Unit("AIUnit", 1, 1, team="AI")
    unit.grid = grid
    grid.get_tile(1, 1).unit = unit
    ai = AIController([unit])
    ai.take_action(unit)
    assert unit.y == 2  # Should have moved down
