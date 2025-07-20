"""Unit tests for the Grid class."""

from game.grid import Grid


def test_grid_initialization():
    """Test grid is initialized with correct dimensions."""
    grid = Grid(width=10, height=10)
    assert grid.width == 10
    assert grid.height == 10
