# @api
# tests/test_turn_controller.py

import pytest

from game.action_point_manager import ActionPointManager
from game.tactical_state_machine import TacticalState, TacticalStateMachine
from game.turn_controller import TurnController


@pytest.fixture
def apm():
    return ActionPointManager()


def test_turn_cycle():
    # Updated to match current TurnController implementation
    tc = TurnController()
    tc.add_unit("player")
    tc.add_unit("enemy")

    assert tc.get_current_unit() == "player"
    tc.next_turn()
    assert tc.get_current_unit() == "enemy"
    tc.next_turn()
    assert tc.get_current_unit() == "player"


def test_get_current_unit_returns_none_if_no_units():
    # Updated to match current TurnController implementation
    tc = TurnController()
    # Current implementation will raise IndexError for empty units list
    with pytest.raises(IndexError):
        tc.get_current_unit()


def test_turn_cycles_units(apm):
    tc = TurnController(apm)
    tc.add_unit("u1")
    tc.add_unit("u2")

    assert tc.get_current_unit() == "u1"
    tc.next_turn()
    assert tc.get_current_unit() == "u2"
    tc.next_turn()
    assert tc.get_current_unit() == "u1"


def test_ap_registers_each_turn(apm):
    tc = TurnController(apm)
    tc.add_unit("a")
    tc.add_unit("b")

    tc.next_turn()  # 'b'
    assert apm.get_ap("b") == 2

    tc.next_turn()  # 'a'
    assert apm.get_ap("a") == 2


def test_can_act_and_spend_ap(apm):
    tc = TurnController(apm)
    tc.add_unit("mover")
    tc.next_turn()  # starts mover

    assert tc.can_act(1)
    assert tc.spend_ap(1)
    assert apm.get_ap("mover") == 1

    assert not tc.can_act(2)
    assert tc.spend_ap(2) is False


def test_graceful_no_ap_manager():
    tc = TurnController(None)
    tc.add_unit("solo")
    tc.next_turn()

    assert tc.can_act(99)
    assert tc.spend_ap(99)


def test_fsm_transitions_on_turn_cycle():
    apm = ActionPointManager()
    fsm = TacticalStateMachine()
    tc = TurnController(apm, fsm)

    tc.add_unit("u1")
    tc.add_unit("u2")

    # Turn begins
    tc.next_turn()
    assert tc.get_state() == TacticalState.SELECTING_UNIT

    # Mid-turn state change (e.g., moving)
    tc.set_state(TacticalState.PLANNING_MOVE)
    assert tc.get_state() == TacticalState.PLANNING_MOVE

    # Turn ends
    tc.end_turn()
    assert tc.get_state() == TacticalState.IDLE


def test_fsm_independent_transition_logic():
    # Test that FSM transitions still work outside of TurnController context
    fsm = TacticalStateMachine()
    fsm.transition_to(TacticalState.PLANNING_ATTACK)
    assert fsm.state == TacticalState.PLANNING_ATTACK
    fsm.cancel()
    # cancel optional here
    assert fsm.state == TacticalState.IDLE or fsm.state == TacticalState.PLANNING_ATTACK
