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
    mcp = MCP(strategy="nearest")

    move_x, move_y = mcp.decide_action(knight, game)

    assert move_x == 3
    assert move_y == 2


def test_mcp_no_targets_returns_current_position():
    knight = DummyUnit("Knight", 2, 2, "Blue")
    game = DummyGame([knight])
    mcp = MCP(strategy="nearest")

    move_x, move_y = mcp.decide_action(knight, game)

    assert move_x == 2
    assert move_y == 2


def test_mcp_moves_toward_closest_target():
    knight = DummyUnit("Knight", 2, 2, "Blue")
    goblin_far = DummyUnit("GoblinFar", 8, 8, "Red")
    goblin_near = DummyUnit("GoblinNear", 3, 3, "Red")
    game = DummyGame([knight, goblin_far, goblin_near])
    mcp = MCP(strategy="nearest")

    move_x, move_y = mcp.decide_action(knight, game)

    # Accept diagonal and orthogonal movement toward (3,3)
    assert (move_x, move_y) in [(3, 2), (2, 3), (3, 3)]


def test_mcp_unknown_strategy_defaults_to_no_op():
    knight = DummyUnit("Knight", 1, 1, "Blue")
    goblin = DummyUnit("Goblin", 5, 5, "Red")
    game = DummyGame([knight, goblin])
    mcp = MCP(strategy="aggressive")  # not yet implemented

    move_x, move_y = mcp.decide_action(knight, game)

    assert move_x == 1
    assert move_y == 1
