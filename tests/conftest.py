"""Pytest fixtures for setting up common test objects."""

import pytest

from game.grid import Grid
from game.unit import Unit


@pytest.fixture
def grid_with_unit() -> tuple[Grid, Unit]:
    """Fixture providing a grid with a single Blue Knight unit placed at (1, 1)."""
    grid = Grid(5, 5)
    unit = Unit("Blue Knight", 1, 1, team="Blue", move_range=1)
    grid.get_tile(1, 1).unit = unit
    return grid, unit
