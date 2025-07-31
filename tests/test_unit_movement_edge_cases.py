# tests/test_unit_movement_edge_cases.py

import pytest

from game.grid import Grid, Tile
from game.unit import Unit


@pytest.fixture
def grid_with_unit():
    grid = Grid(5, 5)
    unit = Unit("Blue Knight", 1, 1, team="Blue", move_range=1)
    grid.get_tile(1, 1).unit = unit
    return grid, unit


def test_move_off_grid(grid_with_unit):
    grid, unit = grid_with_unit
    success = unit.move(-1, 1, grid)
    assert not success
    assert unit.x == 1 and unit.y == 1


def test_move_into_occupied_tile(grid_with_unit):
    grid, unit = grid_with_unit
    blocker = Unit("Red Soldier", 1, 2, team="Red")
    grid.get_tile(1, 2).unit = blocker

    success = unit.move(1, 2, grid)
    assert not success
    assert unit.x == 1 and unit.y == 1


def test_move_to_same_position(grid_with_unit):
    grid, unit = grid_with_unit
    success = unit.move(1, 1, grid)
    assert not success
    assert unit.x == 1 and unit.y == 1


def test_move_beyond_range(grid_with_unit):
    grid, unit = grid_with_unit
    unit.move_range = 1

    # Too far: from (1,1) to (1,3), Manhattan distance = 2
    success = unit.move(1, 3, grid)
    assert not success
    assert unit.x == 1 and unit.y == 1

    # Setup a valid plains tile at (1,2) with movement_cost = 1
    grid.tiles[2][1] = Tile(1, 2, terrain_type="plains", movement_cost=1)

    # Valid move: (1,1) to (1,2), distance = 1, cost = 1
    success = unit.move(1, 2, grid)
    assert success
    assert unit.x == 1 and unit.y == 2


def test_diagonal_movement_not_allowed(grid_with_unit):
    grid, unit = grid_with_unit
    # Attempt to move diagonally from (1,1) to (2,2)
    success = unit.move(2, 2, grid)
    assert not success
    assert unit.x == 1 and unit.y == 1
