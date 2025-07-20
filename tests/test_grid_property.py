from game.grid import Grid


def test_ascii_output(capsys):
    terrain = [
        ["plains", "forest"],
        ["plains", "plains"],
    ]
    grid = Grid(2, 2, terrain_layout=terrain)
    grid.print_ascii(show_title=False)
    captured = capsys.readouterr()
    assert captured.out == ". F\n. .\n"
