import pytest

from game.grid import Grid
from game.overlay.grid_overlay import GridOverlay
from game.unit import Unit


def test_movement_range_basic():
    grid = Grid(5, 5)
    unit = Unit("Hero", 2, 2, team="Blue", move_range=3)
    overlay = GridOverlay(None)
    reachable = overlay.movement_range(grid, unit, 3)
    assert (2, 2) in reachable
    assert len(reachable) > 1


def test_attack_range():
    grid = Grid(5, 5)
    unit = Unit("Archer", 2, 2, team="Red", move_range=2)
    overlay = GridOverlay(None)
    targets = overlay.attack_range(grid, unit, 1)
    assert (2, 2) in targets
    assert (3, 2) in targets


def test_threat_zone():
    grid = Grid(5, 5)
    unit = Unit("Soldier", 2, 2, team="Blue", move_range=2)
    overlay = GridOverlay(None)
    threats = overlay.threat_zone(grid, unit, 2, 1)
    assert (2, 2) in threats
    assert len(threats) > 1
