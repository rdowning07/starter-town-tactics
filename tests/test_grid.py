# tests/test_grid.py

"""Unit tests for the Grid and Tile classes."""

import pytest
from game.grid import Grid, Tile

def test_grid_initialization():
    """Test grid is initialized with correct dimensions and tiles."""
    grid = Grid(width=3, height=3)
    assert grid.width == 3
    assert grid.height == 3
    assert isinstance(grid.get_tile(0, 0), Tile)
    assert isinstance(grid.get_tile(2, 2), Tile)
    assert grid.get_tile(3, 3) is None

def test_tile_occupancy():
    """Test tile occupancy detection."""
    tile = Tile(1, 1)
    assert not tile.is_occupied()
    tile.unit = "DummyUnit"
    assert tile.is_occupied()

def test_get_tile_within_bounds():
    """Test retrieving tiles within grid bounds."""
    grid = Grid(2, 2)
    assert grid.get_tile(1, 1) is not None
    assert grid.get_tile(0, 0) is not None

def test_get_tile_out_of_bounds():
    """Test retrieving tile out of grid bounds returns None."""
    grid = Grid(2, 2)
    assert grid.get_tile(-1, 0) is None
    assert grid.get_tile(2, 2) is None
