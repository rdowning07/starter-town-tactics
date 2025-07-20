from game.grid import Grid

def test_ascii_output(capsys):
    grid = Grid(2, 2)
    grid.print_ascii()
    captured = capsys.readouterr()
    assert captured.out == ". .\n. .\n"
