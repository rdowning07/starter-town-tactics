from game.unit import Unit
from game.grid import Grid, Tile


def test_unit_initialization():
    unit = Unit("Hero", 1, 1, team="Blue")
    assert unit.name == "Hero"
    assert unit.team == "Blue"
    assert unit.x == 1
    assert unit.y == 1


def test_unit_move_to():
    unit = Unit("Knight", 0, 0, team="Red")
    unit.move_to(3, 3)
    assert unit.x == 3
    assert unit.y == 3

def test_unit_move_with_grid():
    grid = Grid(3, 3)
    unit = Unit("Scout", 1, 1, team="Red", move_range=2)
    grid.get_tile(1, 1).unit = unit
    grid.tiles[2][1] = Tile(1, 2, terrain_type="plains", movement_cost=1)
    moved = unit.move(1, 2, grid)
    assert moved
    assert unit.x == 1 and unit.y == 2

def test_unit_is_alive():
    unit = Unit("Hero", 1, 1, team="Blue", health=10)
    assert unit.is_alive()
    unit.hp = 0
    assert not unit.is_alive()

def test_unit_take_damage():
    unit = Unit("Hero", 1, 1, team="Blue", health=10)
    unit.take_damage(3)
    assert unit.hp == 7
    unit.take_damage(10)
    assert unit.hp == 0

def test_move_returns_false_if_out_of_bounds():
    grid = Grid(2, 2)
    unit = Unit("A", 0, 0, "Red")
    grid.get_tile(0, 0).unit = unit
    assert not unit.move(-1, 0, grid)
    assert not unit.move(0, -1, grid)
    assert not unit.move(2, 0, grid)
    assert not unit.move(0, 2, grid)
