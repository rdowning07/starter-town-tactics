# tests/test_mcp.py

import pytest
from game.mcp import MCP


class DummyUnit:
    def __init__(self, name, x, y, team):
        self.name = name
        self.x = x
        self.y = y
        self.team = team


class DummyGame:
    def __init__(self, units):
        self.units = units


def test_mcp_moves_toward_enemy():
    knight = DummyUnit("Knight", 2, 2, "Blue")
    goblin = DummyUnit("Goblin", 4, 2, "Red")
    game = DummyGame([knight, goblin])
    mcp = MCP()

    move_x, move_y = mcp.decide_action(knight, game)

    assert move_x == 3  # one step toward Goblin on x axis
    assert move_y == 2


def test_mcp_no_targets_returns_current_position():
    knight = DummyUnit("Knight", 2, 2, "Blue")
    game = DummyGame([knight])
    mcp = MCP()

    move_x, move_y = mcp.decide_action(knight, game)

    assert move_x == 2
    assert move_y == 2


def test_mcp_moves_toward_closest_target():
    knight = DummyUnit("Knight", 2, 2, "Blue")
    goblin_far = DummyUnit("GoblinFar", 8, 8, "Red")
    goblin_near = DummyUnit("GoblinNear", 3, 3, "Red")
    game = DummyGame([knight, goblin_far, goblin_near])
    mcp = MCP()

    move_x, move_y = mcp.decide_action(knight, game)

    assert (move_x, move_y) == (3, 2) or (2, 3)  # either direction toward nearest
