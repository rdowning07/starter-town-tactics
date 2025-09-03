"""
Tests for the core objectives system.
"""
from unittest.mock import Mock

import pytest

from core.events import Event, EventType
from core.objectives import EliminateBoss, Escort, HoldZones, Objective, SurviveNTurns
from core.state import GameState, TurnController, Unit, UnitStats


class TestObjectiveBase:
    def test_objective_interface(self):
        """Test that Objective is a proper abstract base class."""
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            Objective()


class TestEliminateBoss:
    def test_eliminate_boss_initialization(self):
        """Test EliminateBoss initialization."""
        objective = EliminateBoss("boss1")
        assert objective.boss_id == "boss1"
        assert objective._dead == False

    def test_eliminate_boss_not_complete_initially(self):
        """Test that EliminateBoss is not complete initially."""
        objective = EliminateBoss("boss1")
        state = GameState()
        assert objective.is_complete(state) == False

    def test_eliminate_boss_complete_on_kill_event(self):
        """Test that EliminateBoss completes when boss is killed."""
        objective = EliminateBoss("boss1")
        state = GameState()

        # Create kill event
        kill_event = Event(EventType.UNIT_KILLED, {"unit_id": "boss1"}, 5)

        # Update objective
        objective.update_from_events([kill_event], state)

        assert objective.is_complete(state) == True
        assert objective._dead == True

    def test_eliminate_boss_ignores_other_events(self):
        """Test that EliminateBoss ignores non-kill events."""
        objective = EliminateBoss("boss1")
        state = GameState()

        # Create non-kill events
        events = [
            Event(EventType.UNIT_MOVED, {"unit_id": "boss1"}, 1),
            Event(EventType.UNIT_KILLED, {"unit_id": "other_unit"}, 2),
            Event(EventType.TURN_ENDED, {"side": "player"}, 3),
        ]

        # Update objective
        objective.update_from_events(events, state)

        assert objective.is_complete(state) == False
        assert objective._dead == False

    def test_eliminate_boss_summary(self):
        """Test EliminateBoss summary method."""
        objective = EliminateBoss("boss1")
        state = GameState()

        # Initial summary
        summary = objective.summary(state)
        assert "Defeat boss boss1" in summary
        assert "in progress" in summary

        # Complete summary
        kill_event = Event(EventType.UNIT_KILLED, {"unit_id": "boss1"}, 5)
        objective.update_from_events([kill_event], state)

        summary = objective.summary(state)
        assert "Defeat boss boss1" in summary
        assert "done" in summary


class TestSurviveNTurns:
    def test_survive_nturns_initialization(self):
        """Test SurviveNTurns initialization."""
        objective = SurviveNTurns(5)
        assert objective.n == 5

    def test_survive_nturns_not_complete_initially(self):
        """Test that SurviveNTurns is not complete initially."""
        objective = SurviveNTurns(5)
        state = GameState()
        assert objective.is_complete(state) == False

    def test_survive_nturns_complete_after_n_turns(self):
        """Test that SurviveNTurns completes after n turns."""
        objective = SurviveNTurns(3)
        state = GameState()

        # Set turn index to 3
        state.turn_controller.turn_index = 3

        assert objective.is_complete(state) == True

    def test_survive_nturns_failed_when_player_wiped(self):
        """Test that SurviveNTurns fails when player is wiped."""
        objective = SurviveNTurns(5)
        state = GameState()

        # Mock player_wiped to return True
        state.player_wiped = Mock(return_value=True)

        assert objective.is_failed(state) == True

    def test_survive_nturns_summary(self):
        """Test SurviveNTurns summary method."""
        objective = SurviveNTurns(5)
        state = GameState()
        state.turn_controller.turn_index = 2

        summary = objective.summary(state)
        assert "Survive 5 turns" in summary
        assert "(now 2)" in summary


class TestHoldZones:
    def test_hold_zones_initialization(self):
        """Test HoldZones initialization."""
        zones = [(1, 1), (2, 2), (3, 3)]
        objective = HoldZones(zones, 2, 3)
        assert objective.zones == set(zones)
        assert objective.k == 2
        assert objective.turns == 3
        assert objective.counter == 0

    def test_hold_zones_not_complete_initially(self):
        """Test that HoldZones is not complete initially."""
        zones = [(1, 1), (2, 2)]
        objective = HoldZones(zones, 1, 2)
        state = GameState()
        assert objective.is_complete(state) == False

    def test_hold_zones_updates_on_player_turn_end(self):
        """Test that HoldZones updates on player turn end."""
        zones = [(1, 1), (2, 2)]
        objective = HoldZones(zones, 1, 2)
        state = GameState()

        # Mock controlled_by_player to return True for one zone
        state.controlled_by_player = Mock(side_effect=lambda pos: pos == (1, 1))

        # Create player turn end event
        turn_event = Event(EventType.TURN_ENDED, {"side": "player"}, 5)

        # Update objective
        objective.update_from_events([turn_event], state)

        # Should increment counter since 1 zone is held (>= k=1)
        assert objective.counter == 1

    def test_hold_zones_resets_counter_when_not_enough_held(self):
        """Test that HoldZones resets counter when not enough zones held."""
        zones = [(1, 1), (2, 2)]
        objective = HoldZones(zones, 2, 3)  # Need to hold 2 zones
        state = GameState()

        # Set initial counter
        objective.counter = 2

        # Mock controlled_by_player to return False for all zones
        state.controlled_by_player = Mock(return_value=False)

        # Create player turn end event
        turn_event = Event(EventType.TURN_ENDED, {"side": "player"}, 5)

        # Update objective
        objective.update_from_events([turn_event], state)

        # Should reset counter since 0 zones held (< k=2)
        assert objective.counter == 0

    def test_hold_zones_ignores_non_player_turns(self):
        """Test that HoldZones ignores non-player turn events."""
        zones = [(1, 1)]
        objective = HoldZones(zones, 1, 2)
        state = GameState()

        # Create non-player turn end event
        turn_event = Event(EventType.TURN_ENDED, {"side": "enemy"}, 5)

        # Update objective
        objective.update_from_events([turn_event], state)

        # Should not change counter
        assert objective.counter == 0

    def test_hold_zones_summary(self):
        """Test HoldZones summary method."""
        zones = [(1, 1), (2, 2), (3, 3)]
        objective = HoldZones(zones, 2, 3)
        objective.counter = 1

        state = GameState()
        summary = objective.summary(state)

        assert "Hold 2/3 zones" in summary
        assert "for 3 turns" in summary
        assert "streak 1" in summary


class TestEscort:
    def test_escort_initialization(self):
        """Test Escort initialization."""
        objective = Escort("unit1", (5, 5))
        assert objective.unit_id == "unit1"
        assert objective.goal == (5, 5)
        assert objective._dead == False
        assert objective._done == False

    def test_escort_not_complete_initially(self):
        """Test that Escort is not complete initially."""
        objective = Escort("unit1", (5, 5))
        state = GameState()
        assert objective.is_complete(state) == False
        assert objective.is_failed(state) == False

    def test_escort_complete_on_goal_reached(self):
        """Test that Escort completes when unit reaches goal."""
        objective = Escort("unit1", (5, 5))
        state = GameState()

        # Create move event to goal
        move_event = Event(EventType.UNIT_MOVED, {"unit_id": "unit1", "to": (5, 5)}, 5)

        # Update objective
        objective.update_from_events([move_event], state)

        assert objective.is_complete(state) == True
        assert objective._done == True

    def test_escort_failed_on_unit_killed(self):
        """Test that Escort fails when unit is killed."""
        objective = Escort("unit1", (5, 5))
        state = GameState()

        # Create kill event
        kill_event = Event(EventType.UNIT_KILLED, {"unit_id": "unit1"}, 5)

        # Update objective
        objective.update_from_events([kill_event], state)

        assert objective.is_failed(state) == True
        assert objective._dead == True

    def test_escort_ignores_other_events(self):
        """Test that Escort ignores irrelevant events."""
        objective = Escort("unit1", (5, 5))
        state = GameState()

        # Create irrelevant events
        events = [
            Event(EventType.UNIT_MOVED, {"unit_id": "other_unit", "to": (5, 5)}, 1),
            Event(EventType.UNIT_KILLED, {"unit_id": "other_unit"}, 2),
            Event(EventType.TURN_ENDED, {"side": "player"}, 3),
        ]

        # Update objective
        objective.update_from_events(events, state)

        assert objective.is_complete(state) == False
        assert objective.is_failed(state) == False

    def test_escort_summary(self):
        """Test Escort summary method."""
        objective = Escort("unit1", (5, 5))
        state = GameState()

        # Initial summary
        summary = objective.summary(state)
        assert "Escort unit1 to (5, 5)" in summary
        assert "in progress" in summary

        # Complete summary
        move_event = Event(EventType.UNIT_MOVED, {"unit_id": "unit1", "to": (5, 5)}, 5)
        objective.update_from_events([move_event], state)

        summary = objective.summary(state)
        assert "Escort unit1 to (5, 5)" in summary
        assert "done" in summary


class TestObjectivesIntegration:
    def test_multiple_objectives_together(self):
        """Test multiple objectives working together."""
        # Create objectives
        eliminate = EliminateBoss("boss1")
        survive = SurviveNTurns(3)
        escort = Escort("unit1", (5, 5))

        state = GameState()
        state.turn_controller.turn_index = 2

        # Test initial state
        assert eliminate.is_complete(state) == False
        assert survive.is_complete(state) == False
        assert escort.is_complete(state) == False

        # Update with events
        events = [
            Event(EventType.UNIT_KILLED, {"unit_id": "boss1"}, 1),
            Event(EventType.UNIT_MOVED, {"unit_id": "unit1", "to": (5, 5)}, 2),
        ]

        eliminate.update_from_events(events, state)
        escort.update_from_events(events, state)

        # Check results
        assert eliminate.is_complete(state) == True
        assert survive.is_complete(state) == False  # Still need 1 more turn
        assert escort.is_complete(state) == True
