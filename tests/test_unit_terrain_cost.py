from game.grid import Grid, Tile
from game.unit import Unit


def test_unit_movement_within_terrain_cost():
    grid = Grid(3, 3)
    unit = Unit("Hero", 1, 1, team="Red", move_range=2)
    grid.get_tile(1, 1).unit = unit

    # Set terrain at (1, 2) to mountain (cost 3)
    grid.tiles[2][1] = Tile(1, 2, terrain_type="mountain", movement_cost=3)

    moved = unit.move(1, 2, grid)
    assert not moved  # Too costly to move


def test_unit_movement_on_walkable_terrain():
    grid = Grid(3, 3)
    unit = Unit("Scout", 1, 1, team="Red", move_range=2)
    grid.get_tile(1, 1).unit = unit

    # Set terrain at (1, 2) to forest (cost 1)
    grid.tiles[2][1] = Tile(1, 2, terrain_type="forest", movement_cost=1)

    moved = unit.move(1, 2, grid)
    assert moved  # Should be able to move
