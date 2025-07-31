from game.grid import Grid
from game.tile import Tile


def test_ascii_output_with_title(capsys):
    grid = Grid(2, 2)
    # Manually set terrain types after grid creation
    # grid.tiles[y][x] indexing - y is row, x is column
    grid.tiles[0][0] = Tile(0, 0, terrain_type="plains", movement_cost=1)
    grid.tiles[0][1] = Tile(1, 0, terrain_type="forest", movement_cost=2)
    grid.tiles[1][0] = Tile(0, 1, terrain_type="plains", movement_cost=1)
    grid.tiles[1][1] = Tile(1, 1, terrain_type="plains", movement_cost=1)

    grid.print_ascii(show_title=True)

    captured = capsys.readouterr()
    assert "Grid (2x2):" in captured.out
    assert ".F" in captured.out  # First row: plains, forest
    assert ".." in captured.out  # Second row: plains, plains


def test_ascii_output_without_title(capsys):
    grid = Grid(2, 2)
    # Manually set terrain types after grid creation
    # grid.tiles[y][x] indexing - y is row, x is column
    grid.tiles[0][0] = Tile(0, 0, terrain_type="plains", movement_cost=1)
    grid.tiles[0][1] = Tile(1, 0, terrain_type="forest", movement_cost=2)
    grid.tiles[1][0] = Tile(0, 1, terrain_type="plains", movement_cost=1)
    grid.tiles[1][1] = Tile(1, 1, terrain_type="plains", movement_cost=1)

    grid.print_ascii(show_title=False)

    captured = capsys.readouterr()
    assert "Grid (2x2):" not in captured.out
    assert ".F" in captured.out  # First row: plains, forest
    assert ".." in captured.out  # Second row: plains, plains
