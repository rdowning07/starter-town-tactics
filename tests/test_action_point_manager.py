import pytest

from game.action_point_manager import ActionPointManager


@pytest.fixture
def apm():
    return ActionPointManager()


def test_register_unit_default_ap(apm):
    apm.register_unit("unit_1")
    assert apm.get_ap("unit_1") == 2  # default max AP


def test_register_unit_custom_ap(apm):
    apm.register_unit("unit_2", ap=5)
    assert apm.get_ap("unit_2") == 5


def test_spend_and_validate(apm):
    apm.register_unit("unit_3")
    assert apm.can_spend("unit_3", 2)
    assert apm.spend("unit_3", 1)
    assert apm.get_ap("unit_3") == 1
    assert not apm.can_spend("unit_3", 2)


def test_spend_fails_if_insufficient(apm):
    apm.register_unit("unit_4", ap=1)
    success = apm.spend("unit_4", 3)
    assert not success
    assert apm.get_ap("unit_4") == 1  # unchanged


def test_reset_all_units(apm):
    apm.register_unit("unit_5", ap=0)
    apm.reset_all()
    assert apm.get_ap("unit_5") == 2  # back to default max


def test_remove_unit_safely(apm):
    apm.register_unit("ghost_unit", ap=1)
    apm.remove_unit("ghost_unit")
    assert apm.get_ap("ghost_unit") == 0
    apm.remove_unit("nonexistent")  # should not raise


def test_set_new_max_ap(apm):
    apm.set_max_ap(4)
    apm.register_unit("unit_max")
    assert apm.get_ap("unit_max") == 4
