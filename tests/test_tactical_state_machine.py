import pytest
from game.tactical_state_machine import TacticalState, TacticalStateMachine


def test_state_transitions():
    sm = TacticalStateMachine()
    assert sm.state == TacticalState.IDLE

    sm.transition_to(TacticalState.SELECTING_UNIT)
    assert sm.state == TacticalState.SELECTING_UNIT

    sm.transition_to(TacticalState.PLANNING_MOVE)
    sm.cancel()
    assert sm.state == TacticalState.SELECTING_UNIT


def test_reset_behavior():
    sm = TacticalStateMachine()
    sm.transition_to(TacticalState.PLANNING_ATTACK)
    sm.reset()
    assert sm.state == TacticalState.IDLE
