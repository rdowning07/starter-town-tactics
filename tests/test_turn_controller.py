import pytest

from game.turn_controller import TurnController, TurnPhase


def test_initial_phase_is_player():
    tc = TurnController()
    assert tc.get_phase() == TurnPhase.PLAYER


def test_advance_player_to_ai():
    tc = TurnController()
    tc.advance_turn()
    assert tc.get_phase() == TurnPhase.AI


def test_advance_ai_to_player():
    tc = TurnController()
    tc.set_phase(TurnPhase.AI)
    tc.advance_turn()
    assert tc.get_phase() == TurnPhase.PLAYER


def test_invalid_phase_raises():
    tc = TurnController()
    with pytest.raises(ValueError):
        tc.set_phase("invalid")


def test_game_over_does_not_advance():
    tc = TurnController()
    tc.set_phase(TurnPhase.GAME_OVER)
    tc.advance_turn()
    assert tc.get_phase() == TurnPhase.GAME_OVER
