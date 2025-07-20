from game.unit import Unit

def test_unit_movement():
    unit = Unit("Test", 1, 1, team="Blue")
    unit.move_to(2, 2)
    assert unit.x == 2 and unit.y == 2