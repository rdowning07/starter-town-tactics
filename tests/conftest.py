import pytest
from game.grid import Grid
from game.unit import Unit

@pytest.fixture
def grid_with_unit():
    grid = Grid(3, 3)
    unit = Unit("Knight", 1, 1, team="Blue")
    grid.get_tile(1, 1).unit = unit
    return grid, unit
