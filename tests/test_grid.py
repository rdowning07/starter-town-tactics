from game.grid import Grid


def test_ascii_output(capsys):
    terrain = [
        ["plains", "forest"],
        ["plains", "plains"],
    ]
    grid = Grid(2, 2, terrain_layout=terrain)
    grid.print_ascii()

    captured = capsys.readouterr()
    expected_output = "Game Map:\n. F\n. .\n"
    assert captured.out == expected_output
