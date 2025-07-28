from game.unit import Unit


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
