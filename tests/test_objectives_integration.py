"""
Integration tests for objectives with command-event system.
"""
from unittest.mock import Mock

import pytest

from core import (
    Attack,
    EliminateBoss,
    EndTurn,
    Escort,
    Event,
    EventBus,
    GameLoop,
    GameState,
    HoldZones,
    Move,
    Rng,
    SurviveNTurns,
    Unit,
    UnitStats,
)
from core.events import EventType


class TestObjectivesWithGameLoop:
    def test_eliminate_boss_with_attack_command(self):
        """Test that EliminateBoss objective updates when boss is attacked."""
        # Create game state
        state = GameState()

        # Create boss unit with low HP so it gets killed
        boss_stats = UnitStats(hp=5, atk=5, def_=0, h=0)
        boss = Unit("boss1", (5, 5), "N", boss_stats, team="enemy")
        state.add_unit(boss)

        # Create player unit
        player_stats = UnitStats(hp=15, atk=8, def_=3, h=1)
        player = Unit("player1", (4, 5), "E", player_stats, team="player")
        state.add_unit(player)

        # Create objective
        objective = EliminateBoss("boss1")

        # Create attack command
        attack_cmd = Attack(attacker_id="player1", target_id="boss1")

        # Mock event bus
        events_received = []

        def event_handler(event):
            events_received.append(event)

        bus = EventBus()
        bus.subscribe(event_handler)

        # Apply command
        if attack_cmd.validate(state):
            events = list(attack_cmd.apply(state))
            bus.publish(events)

            # Update objective
            objective.update_from_events(events, state)

        # Check that events were generated
        assert len(events_received) > 0
        assert any(e.type == EventType.UNIT_ATTACKED for e in events_received)
        assert any(e.type == EventType.UNIT_KILLED for e in events_received)

    def test_survive_nturns_with_turn_advancement(self):
        """Test that SurviveNTurns objective tracks turn advancement."""
        # Create game state
        state = GameState()
        state.turn_controller.turn_index = 0

        # Create objective
        objective = SurviveNTurns(3)

        # Check initial state
        assert objective.is_complete(state) == False

        # Advance turns
        state.turn_controller.turn_index = 2
        assert objective.is_complete(state) == False

        state.turn_controller.turn_index = 3
        assert objective.is_complete(state) == True

    def test_escort_with_move_command(self):
        """Test that Escort objective updates when unit moves to goal."""
        # Create game state
        state = GameState()

        # Create unit to escort
        escort_unit = Unit("unit1", (1, 1), "N", UnitStats(), team="player")
        state.add_unit(escort_unit)

        # Create objective
        goal = (5, 5)
        objective = Escort("unit1", goal)

        # Create move command
        move_cmd = Move(unit_id="unit1", to=goal)

        # Mock event bus
        events_received = []

        def event_handler(event):
            events_received.append(event)

        bus = EventBus()
        bus.subscribe(event_handler)

        # Apply command
        if move_cmd.validate(state):
            events = list(move_cmd.apply(state))
            bus.publish(events)

            # Update objective
            objective.update_from_events(events, state)

        # Check that events were generated
        assert len(events_received) > 0
        assert any(e.type == EventType.UNIT_MOVED for e in events_received)

        # Check that events were generated
        assert len(events_received) > 0
        assert any(e.type == EventType.UNIT_MOVED for e in events_received)

        # Check objective completion
        assert objective.is_complete(state) == True

    def test_hold_zones_with_zone_control(self):
        """Test that HoldZones objective tracks zone control."""
        # Create game state
        state = GameState()

        # Create zones
        zones = [(1, 1), (2, 2), (3, 3)]
        objective = HoldZones(zones, 2, 3)  # Hold 2 zones for 3 turns

        # Create player unit in zone (1, 1)
        player1 = Unit("player1", (1, 1), "N", UnitStats(), team="player")
        state.add_unit(player1)

        # Create another player unit in zone (2, 2)
        player2 = Unit("player2", (2, 2), "N", UnitStats(), team="player")
        state.add_unit(player2)

        # Create player turn end event
        turn_event = Event(EventType.TURN_ENDED, {"side": "player"}, 5)

        # Update objective
        objective.update_from_events([turn_event], state)

        # Should increment counter since 2 zones are held (>= k=2)
        assert objective.counter == 1

    def test_multiple_objectives_integration(self):
        """Test multiple objectives working together in a game scenario."""
        # Create game state
        state = GameState()
        state.turn_controller.turn_index = 0

        # Create units
        boss = Unit("boss1", (5, 5), "N", UnitStats(hp=5, def_=0), team="enemy")
        player = Unit("player1", (4, 5), "E", UnitStats(atk=10), team="player")
        escort_unit = Unit("unit1", (1, 1), "N", UnitStats(), team="player")

        state.add_unit(boss)
        state.add_unit(player)
        state.add_unit(escort_unit)

        # Create objectives
        eliminate = EliminateBoss("boss1")
        survive = SurviveNTurns(5)
        escort = Escort("unit1", (3, 3))

        # Create commands
        attack_cmd = Attack(attacker_id="player1", target_id="boss1")
        move_cmd = Move(unit_id="unit1", to=(3, 3))

        # Mock event bus
        events_received = []

        def event_handler(event):
            events_received.append(event)

        bus = EventBus()
        bus.subscribe(event_handler)

        # Apply attack command
        if attack_cmd.validate(state):
            events = list(attack_cmd.apply(state))
            bus.publish(events)

            eliminate.update_from_events(events, state)

        # Apply move command
        if move_cmd.validate(state):
            events = list(move_cmd.apply(state))
            bus.publish(events)

            escort.update_from_events(events, state)

        # Advance turns
        state.turn_controller.turn_index = 5

        # Check objective states
        assert eliminate.is_complete(state) == True
        assert survive.is_complete(state) == True
        assert escort.is_complete(state) == True

    def test_objective_summaries(self):
        """Test that all objectives provide meaningful summaries."""
        state = GameState()
        state.turn_controller.turn_index = 2

        # Test EliminateBoss summary
        eliminate = EliminateBoss("boss1")
        summary = eliminate.summary(state)
        assert "Defeat boss boss1" in summary
        assert "in progress" in summary

        # Test SurviveNTurns summary
        survive = SurviveNTurns(5)
        summary = survive.summary(state)
        assert "Survive 5 turns" in summary
        assert "(now 2)" in summary

        # Test Escort summary
        escort = Escort("unit1", (5, 5))
        summary = escort.summary(state)
        assert "Escort unit1 to (5, 5)" in summary
        assert "in progress" in summary

        # Test HoldZones summary
        zones = [(1, 1), (2, 2)]
        hold = HoldZones(zones, 1, 3)
        summary = hold.summary(state)
        assert "Hold 1/2 zones" in summary
        assert "for 3 turns" in summary
