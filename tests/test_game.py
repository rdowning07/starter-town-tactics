from game.game import Game
from game.unit import Unit


def test_add_unit():
    game = Game(3, 3)
    unit = Unit("Test", 1, 1, team="Red")
    game.add_unit(unit)
    tile = game.grid.get_tile(1, 1)
    assert tile.unit == unit


def test_game_turns():
    game = Game(3, 3)
    assert game.current_turn == 0
    game.next_turn()
    assert game.current_turn == 1
