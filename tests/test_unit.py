from game.unit import Unit


def test_unit_movement():
    unit = Unit("Test", 1, 1, team="Blue", move_range=2)
    unit.move_to(2, 2)
    assert unit.x == 2
    assert unit.y == 2


def test_unit_attributes():
    unit = Unit("Test", 1, 1, team="Red", move_range=3)
    assert unit.name == "Test"
    assert unit.team == "Red"
    assert unit.move_range == 3
