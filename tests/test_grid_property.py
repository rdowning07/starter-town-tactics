from hypothesis import given
from hypothesis.strategies import integers
from game.grid import Grid

@given(x=integers(min_value=-5, max_value=10), y=integers(min_value=-5, max_value=10))
def test_tile_bounds(x, y):
    grid = Grid(5, 5)
    tile = grid.get_tile(x, y)
    if 0 <= x < 5 and 0 <= y < 5:
        assert tile is not None
    else:
        assert tile is None
