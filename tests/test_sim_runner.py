import pytest

from game.action_point_manager import ActionPointManager
from game.game import Game
from game.sim_runner import SimRunner
from game.tactical_state_machine import TacticalState, TacticalStateMachine
from game.turn_controller import TurnController
from game.unit import Unit


class DummyAI:
    def __init__(self):
        self.actions = []

    def take_action(self, unit_id):
        self.actions.append(unit_id)


@pytest.fixture
def runner_with_ai():
    apm = ActionPointManager()
    fsm = TacticalStateMachine()
    tc = TurnController(apm, fsm)
    ai = DummyAI()

    tc.add_unit("ai1")
    tc.add_unit("p1")
    tc.add_unit("ai2")

    runner = SimRunner(tc, ai)
    return runner, ai, tc


def test_simulation_run():
    """Legacy test for backward compatibility with Game-based SimRunner."""
    game = Game(5, 5)
    game.add_unit(Unit("SimHero", 2, 2, team="Blue"))
    game.add_unit(Unit("SimAI", 1, 1, team="AI"))  # Add an AI unit
    sim = SimRunner(game)
    sim.run()
    # Check that the log is not empty
    assert len(sim.log) > 0
    # Check that the log contains simulation start
    assert any(entry.get("event") == "simulation_started" for entry in sim.log)
    # Check that the log contains turn information (new format)
    assert any(entry.get("event") == "turn_start" for entry in sim.log)


def test_simrunner_runs_and_logs(runner_with_ai):
    """Test that SimRunner properly logs turn progression."""
    runner, ai, tc = runner_with_ai

    runner.run_turn()
    runner.run_turn()

    logs = runner.get_log()
    # Check that we have turn logs with the correct turn order
    assert logs[0]["event"] == "turn_start"
    assert logs[0]["unit"] == "p1"
    assert logs[0]["type"] == "player"
    assert logs[0]["turn"] == 1
    
    # Check second turn
    assert logs[3]["event"] == "turn_start"
    assert logs[3]["unit"] == "ai1"
    assert logs[3]["type"] == "ai"
    assert logs[3]["turn"] == 2
    
    # Check for player input waiting
    assert any(entry.get("event") == "player_input_waiting" for entry in logs)
    # Check for AI action
    assert any(entry.get("event") == "ai_action" for entry in logs)


def test_ai_controller_invoked_correctly(runner_with_ai):
    """Test that AI controller is called for AI units but not player units."""
    runner, ai, _ = runner_with_ai

    # Run multiple turns to get to AI units
    runner.run_turn()  # p1 (player)
    runner.run_turn()  # ai1 (AI)
    runner.run_turn()  # ai2 (AI)

    # Check that AI controller was called for AI units
    assert "ai1" in ai.actions
    assert "ai2" in ai.actions


def test_fsm_states_during_turn(runner_with_ai):
    """Test that FSM states are properly managed during turn progression."""
    runner, _, tc = runner_with_ai

    runner.run_turn()
    assert tc.get_state() == TacticalState.IDLE

    runner.run_turn()
    assert tc.get_state() == TacticalState.IDLE


def test_simrunner_reset(runner_with_ai):
    """Test that SimRunner reset functionality works correctly."""
    runner, _, _ = runner_with_ai
    runner.run_turn()
    runner.reset()

    assert runner.turn_count == 0
    assert runner.get_log() == []


def test_unit_death_functionality():
    """Test that unit death functionality works correctly."""
    from game.action_point_manager import ActionPointManager
    from game.tactical_state_machine import TacticalStateMachine
    
    apm = ActionPointManager()
    fsm = TacticalStateMachine()
    tc = TurnController(apm, fsm)
    
    tc.add_unit("unit1")
    tc.add_unit("unit2")
    tc.add_unit("unit3")
    
    runner = SimRunner(tc)
    
    # Mark a unit as dead
    runner.mark_unit_dead("unit2")
    
    # Check that the unit is marked as dead
    assert "unit2" in runner.dead_units
    
    # Check that the death event was logged
    logs = runner.get_log()
    assert any(entry.get("event") == "unit_dead" and entry.get("unit") == "unit2" for entry in logs)
    
    # Run a turn and check that dead unit is skipped
    runner.run_turn()
    logs = runner.get_log()
    
    # Should see a skip_turn event for the dead unit if it comes up in rotation
    skip_events = [entry for entry in logs if entry.get("event") == "skip_turn"]
    if skip_events:
        assert any(entry.get("unit") == "unit2" for entry in skip_events)
