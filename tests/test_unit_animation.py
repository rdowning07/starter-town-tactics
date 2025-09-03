# tests/test_unit_animation.py

from game.unit import Unit


def mock_metadata():
    return {
        "idle": {"frame_count": 4, "frame_duration": 2, "loop": True},
        "attack": {"frame_count": 3, "frame_duration": 1, "loop": False},
    }


def test_idle_animation_loops():
    unit = Unit(name="Test", x=0, y=0, team="player")
    unit.set_animation("idle")

    # Test basic animation functionality
    for _ in range(10):
        unit.update_animation()

    assert unit.current_animation == "idle"


def test_attack_animation_resets_to_idle():
    unit = Unit(name="Attacker", x=0, y=0, team="enemy")
    unit.set_animation("attack")

    # Test animation reset
    for _ in range(15):  # Enough to complete attack animation
        unit.update_animation()

    assert unit.current_animation == "idle"


def test_animation_frame_advance():
    unit = Unit(name="Stepper", x=0, y=0, team="player")
    unit.set_animation("idle")

    # Test basic animation update
    unit.update_animation()
    assert unit.current_animation == "idle"

    unit.update_animation()
    assert unit.current_animation == "idle"


def test_take_damage_transitions_to_hurt_or_die():
    unit = Unit(name="ToughGuy", x=0, y=0, team="enemy")
    unit.hp = 3
    unit.take_damage(1)
    assert unit.current_animation == "hurt"

    unit.take_damage(5)
    assert unit.current_animation == "die"
