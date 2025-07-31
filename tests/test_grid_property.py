import pytest

from game.grid import Grid


def test_tile_retrieval_and_bounds():
    grid = Grid(3, 3)
    assert grid.get_tile(1, 1) is not None
    with pytest.raises(ValueError):
        grid.get_tile(3, 3)
    assert grid.is_within_bounds(2, 2)
    assert not grid.is_within_bounds(-1, 0)
