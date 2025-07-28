import pytest
from game.grid import Grid


class DummyUnit:
    def __init__(self, x, y, name="U", team="Blue"):
        self.x = x
        self.y = y
        self.name = name
        self.team = team


def test_place_unit_success():
    grid = Grid(2, 2)
    unit = DummyUnit(1, 1)
    grid.place_unit(unit)

    tile = grid.get_tile(1, 1)
    assert tile.unit == unit
    assert tile.get_symbol() == "U"


def test_place_unit_out_of_bounds():
    grid = Grid(2, 2)
    unit = DummyUnit(3, 3)

    with pytest.raises(ValueError):
        grid.place_unit(unit)


def test_terrain_movement_costs():
    terrain = [["plains", "forest"], ["mountain", "plains"]]
    grid = Grid(2, 2, terrain_layout=terrain)

    assert grid.get_tile(0, 0).movement_cost == 1  # plains
    assert grid.get_tile(1, 0).movement_cost == 2  # forest
    assert grid.get_tile(0, 1).movement_cost == 3  # mountain


def test_is_within_bounds():
    grid = Grid(3, 3)
    assert grid.is_within_bounds(0, 0)
    assert grid.is_within_bounds(2, 2)
    assert not grid.is_within_bounds(-1, 0)
    assert not grid.is_within_bounds(3, 3)


def test_get_tile_out_of_bounds():
    grid = Grid(2, 2)
    assert grid.get_tile(5, 5) is None
