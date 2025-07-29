# @api
# tests/test_turn_controller.py

from game.turn_controller import TurnController, TurnPhase
from tests.utils.dummy_game import DummyGame  # ✅ Absolute import


def test_turn_cycle():
    game = DummyGame()
    controller = TurnController(game)

    assert controller.current_phase == TurnPhase.PLAYER

    controller.next_turn()
    assert controller.current_phase == TurnPhase.ENEMY

    controller.next_turn()
    assert controller.current_phase == TurnPhase.PLAYER
