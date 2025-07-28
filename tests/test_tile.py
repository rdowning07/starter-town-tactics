# tests/test_tile.py

from game.tile import Tile
from game.unit import Unit


def test_tile_initialization_defaults():
    tile = Tile(1, 2)
    assert tile.x == 1
    assert tile.y == 2
    assert tile.terrain_type == "plains"
    assert tile.movement_cost == 1
    assert tile.unit is None


def test_tile_is_walkable_without_unit():
    tile = Tile(0, 0)
    assert tile.is_walkable()


def test_tile_is_not_walkable_with_unit():
    tile = Tile(0, 0)
    tile.unit = Unit("Knight", 0, 0, "Blue")
    assert not tile.is_walkable()


def test_tile_symbol_for_unit():
    tile = Tile(0, 0)
    tile.unit = Unit("Goblin", 0, 0, "Red")
    assert tile.get_symbol() == "G"


def test_tile_symbol_for_forest_and_mountain():
    forest = Tile(0, 0, terrain_type="forest")
    mountain = Tile(0, 0, terrain_type="mountain")
    unknown = Tile(0, 0, terrain_type="swamp")

    assert forest.get_symbol() == "F"
    assert mountain.get_symbol() == "M"
    assert unknown.get_symbol() == "."
