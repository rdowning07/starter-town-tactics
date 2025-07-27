# tests/test_ai_controller.py

import pytest
from game.ai_controller import AIController


class DummyUnit:
    def __init__(self, name, x, y, team):
        self.name = name
        self.x = x
        self.y = y
        self.team = team
        self.last_move = None

    def move_to(self, x, y):
        self.last_move = (x, y)
        self.x = x
        self.y = y


class DummyGame:
    def __init__(self, units):
        self.units = units
        self.turns = 0

    def next_turn(self):
        self.turns += 1


class DummyMCP:
    def decide_action(self, unit, game):
        return unit.x + 1, unit.y + 1


def test_aicontroller_uses_mcp():
    knight = DummyUnit("Knight", 1, 1, "Blue")
    goblin = DummyUnit("Goblin", 5, 5, "Red")
    game = DummyGame([knight, goblin])
    mcp = DummyMCP()

    controller = AIController.with_mcp(game, mcp)
    controller.take_turn()

    assert knight.last_move == (2, 2)
    assert controller.last_action == "Knight used MCP"
    assert game.turns == 1


def test_aicontroller_fallback_when_no_mcp():
    knight = DummyUnit("Knight", 1, 1, "Blue")
    goblin = DummyUnit("Goblin", 3, 1, "Red")
    game = DummyGame([knight, goblin])

    controller = AIController(game)
    controller.take_turn()

    assert knight.last_move == (2, 1)
    assert "Knight moved toward" in controller.last_action
    assert game.turns == 1


def test_aicontroller_no_targets_noop():
    knight = DummyUnit("Knight", 2, 2, "Blue")
    game = DummyGame([knight])

    controller = AIController(game)
    controller.take_turn()

    assert knight.last_move is None
    assert controller.last_action == "No targets"
    assert game.turns == 0
