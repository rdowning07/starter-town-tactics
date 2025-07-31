# @api
# tests/test_turn_controller.py

from game.turn_controller import TurnController, TurnPhase
from game.game import Game
from tests.utils.dummy_game import DummyGame  # ✅ Absolute import


def test_turn_cycle():
    game = DummyGame()
    controller = TurnController(game)

    assert controller.current_phase == TurnPhase.PLAYER

    controller.next_turn()
    assert controller.current_phase == TurnPhase.ENEMY

    controller.next_turn()
    assert controller.current_phase == TurnPhase.PLAYER


def test_get_current_unit_returns_none_if_no_units():
    game = Game(2, 2)
    tc = TurnController(game)
    assert tc.get_current_unit() is None
