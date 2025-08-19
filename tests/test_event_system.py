"""
Tests for the enhanced event system with stable event types and canonical factories.
"""
import pytest
from unittest.mock import Mock
from core.events import (
    Event, EventType, EventBus, 
    ev_unit_moved, ev_unit_attacked, ev_unit_killed, 
    ev_turn_started, ev_turn_ended
)
from core.command import Move, Attack, EndTurn
from core.state import GameState, Unit, UnitStats
from core.objectives import EliminateBoss, Escort, HoldZones

class EventCollector:
    def __init__(self): 
        self.events = []
    def __call__(self, e): 
        self.events.append(e)

def subscribe_types(bus, types):
    def deco(fn): 
        bus.subscribe(fn, types)
        return fn
    return deco

class TestEventFactories:
    def test_ev_unit_moved(self):
        """Test UNIT_MOVED event factory."""
        event = ev_unit_moved("unit1", (1, 1), (2, 2), 5)
        assert event.type == EventType.UNIT_MOVED
        assert event.payload["unit_id"] == "unit1"
        assert event.payload["from"] == (1, 1)
        assert event.payload["to"] == (2, 2)
        assert event.tick == 5

    def test_ev_unit_attacked(self):
        """Test UNIT_ATTACKED event factory."""
        event = ev_unit_attacked("attacker1", "target1", 10, 5)
        assert event.type == EventType.UNIT_ATTACKED
        assert event.payload["attacker_id"] == "attacker1"
        assert event.payload["target_id"] == "target1"
        assert event.payload["damage"] == 10
        assert event.tick == 5

    def test_ev_unit_killed(self):
        """Test UNIT_KILLED event factory."""
        event = ev_unit_killed("unit1", "killer1", 5)
        assert event.type == EventType.UNIT_KILLED
        assert event.payload["unit_id"] == "unit1"
        assert event.payload["by"] == "killer1"
        assert event.tick == 5

    def test_ev_turn_started(self):
        """Test TURN_STARTED event factory."""
        event = ev_turn_started("unit1", "player", 3, 5)
        assert event.type == EventType.TURN_STARTED
        assert event.payload["unit_id"] == "unit1"
        assert event.payload["side"] == "player"
        assert event.payload["index"] == 3
        assert event.tick == 5

    def test_ev_turn_ended(self):
        """Test TURN_ENDED event factory."""
        event = ev_turn_ended("unit1", "player", 3, 5)
        assert event.type == EventType.TURN_ENDED
        assert event.payload["unit_id"] == "unit1"
        assert event.payload["side"] == "player"
        assert event.payload["index"] == 3
        assert event.tick == 5

class TestEventBusFiltering:
    def test_subscribe_without_filter(self):
        """Test subscribing without type filter receives all events."""
        bus = EventBus()
        collector = EventCollector()
        bus.subscribe(collector)
        
        events = [
            ev_unit_moved("unit1", (1, 1), (2, 2), 1),
            ev_unit_attacked("attacker1", "target1", 5, 2),
            ev_unit_killed("unit1", "killer1", 3)
        ]
        
        bus.publish(events)
        assert len(collector.events) == 3

    def test_subscribe_with_filter(self):
        """Test subscribing with type filter only receives specified events."""
        bus = EventBus()
        collector = EventCollector()
        bus.subscribe(collector, types=[EventType.UNIT_KILLED, EventType.UNIT_ATTACKED])
        
        events = [
            ev_unit_moved("unit1", (1, 1), (2, 2), 1),
            ev_unit_attacked("attacker1", "target1", 5, 2),
            ev_unit_killed("unit1", "killer1", 3)
        ]
        
        bus.publish(events)
        assert len(collector.events) == 2
        assert all(e.type in [EventType.UNIT_KILLED, EventType.UNIT_ATTACKED] for e in collector.events)

    def test_multiple_subscribers_with_filters(self):
        """Test multiple subscribers with different filters."""
        bus = EventBus()
        all_events = EventCollector()
        kill_events = EventCollector()
        move_events = EventCollector()
        
        bus.subscribe(all_events)  # No filter
        bus.subscribe(kill_events, types=[EventType.UNIT_KILLED])
        bus.subscribe(move_events, types=[EventType.UNIT_MOVED])
        
        events = [
            ev_unit_moved("unit1", (1, 1), (2, 2), 1),
            ev_unit_killed("unit1", "killer1", 2)
        ]
        
        bus.publish(events)
        assert len(all_events.events) == 2
        assert len(kill_events.events) == 1
        assert len(move_events.events) == 1

class TestCommandEventIntegration:
    def test_move_command_emits_unit_moved(self):
        """Test that Move command emits UNIT_MOVED event."""
        state = GameState()
        unit = Unit("unit1", (1, 1), team="player")
        state.add_unit(unit)
        state.tick = 5
        
        move_cmd = Move("unit1", (2, 2))
        events = list(move_cmd.apply(state))
        
        assert len(events) == 1
        assert events[0].type == EventType.UNIT_MOVED
        assert events[0].payload["unit_id"] == "unit1"
        assert events[0].payload["from"] == (1, 1)
        assert events[0].payload["to"] == (2, 2)
        assert events[0].tick == 5

    def test_attack_command_emits_events(self):
        """Test that Attack command emits UNIT_ATTACKED and optionally UNIT_KILLED."""
        state = GameState()
        attacker = Unit("attacker1", (1, 1), stats=UnitStats(atk=10), team="player")
        target = Unit("target1", (2, 2), stats=UnitStats(hp=5, def_=0), team="enemy")
        state.add_unit(attacker)
        state.add_unit(target)
        state.tick = 5
        
        attack_cmd = Attack("attacker1", "target1")
        events = list(attack_cmd.apply(state))
        
        assert len(events) == 2  # UNIT_ATTACKED + UNIT_KILLED
        assert events[0].type == EventType.UNIT_ATTACKED
        assert events[1].type == EventType.UNIT_KILLED
        assert events[0].payload["attacker_id"] == "attacker1"
        assert events[0].payload["target_id"] == "target1"
        assert events[1].payload["unit_id"] == "target1"
        assert events[1].payload["by"] == "attacker1"

class TestObjectiveEventIntegration:
    def test_eliminate_boss_updates_on_unit_killed(self):
        """Test that EliminateBoss objective updates on UNIT_KILLED event."""
        objective = EliminateBoss("boss1")
        state = GameState()
        
        # Create kill event
        kill_event = ev_unit_killed("boss1", "player1", 5)
        
        # Update objective
        objective.update_from_events([kill_event], state)
        
        assert objective.is_complete(state) == True
        assert objective._dead == True

    def test_escort_updates_on_unit_moved(self):
        """Test that Escort objective updates on UNIT_MOVED event."""
        objective = Escort("unit1", (5, 5))
        state = GameState()
        
        # Create move event to goal
        move_event = ev_unit_moved("unit1", (1, 1), (5, 5), 5)
        
        # Update objective
        objective.update_from_events([move_event], state)
        
        assert objective.is_complete(state) == True
        assert objective._done == True

    def test_hold_zones_updates_on_turn_ended(self):
        """Test that HoldZones objective updates on TURN_ENDED event."""
        zones = [(1, 1), (2, 2)]
        objective = HoldZones(zones, 1, 3)
        state = GameState()
        
        # Mock controlled_by_player to return True for one zone
        state.controlled_by_player = Mock(side_effect=lambda pos: pos == (1, 1))
        
        # Create turn end event
        turn_event = ev_turn_ended("player1", "player", 1, 5)
        
        # Update objective
        objective.update_from_events([turn_event], state)
        
        assert objective.counter == 1

class TestEventOrdering:
    def test_attack_that_kills_ordering(self):
        """Test that attack that kills produces UNIT_ATTACKED then UNIT_KILLED."""
        state = GameState()
        attacker = Unit("attacker1", (1, 1), stats=UnitStats(atk=10), team="player")
        target = Unit("target1", (2, 2), stats=UnitStats(hp=5, def_=0), team="enemy")
        state.add_unit(attacker)
        state.add_unit(target)
        state.tick = 5
        
        attack_cmd = Attack("attacker1", "target1")
        events = list(attack_cmd.apply(state))
        
        # Check ordering: UNIT_ATTACKED first, then UNIT_KILLED
        assert len(events) == 2
        assert events[0].type == EventType.UNIT_ATTACKED
        assert events[1].type == EventType.UNIT_KILLED
        assert events[0].tick == events[1].tick  # Same tick

    def test_move_then_end_turn_ordering(self):
        """Test move then end turn produces proper turn event sequence."""
        # This would be tested with the full game loop
        # For now, we test the individual components
        state = GameState()
        unit = Unit("unit1", (1, 1), team="player")
        state.add_unit(unit)
        state.tick = 5
        
        # Move command
        move_cmd = Move("unit1", (2, 2))
        move_events = list(move_cmd.apply(state))
        
        assert len(move_events) == 1
        assert move_events[0].type == EventType.UNIT_MOVED

class TestEventBusErrorHandling:
    def test_subscriber_exception_does_not_stop_others(self):
        """Test that subscriber exceptions don't stop other subscribers."""
        bus = EventBus()
        
        def failing_subscriber(e):
            raise Exception("Subscriber error")
        
        def working_subscriber(e):
            working_subscriber.called = True
        
        working_subscriber.called = False
        
        bus.subscribe(failing_subscriber)
        bus.subscribe(working_subscriber)
        
        event = ev_unit_moved("unit1", (1, 1), (2, 2), 1)
        bus.publish([event])
        
        # Working subscriber should still be called
        assert working_subscriber.called == True

class TestEventTypeEnum:
    def test_event_type_values(self):
        """Test that EventType enum has correct string values."""
        assert EventType.UNIT_MOVED == "UNIT_MOVED"
        assert EventType.UNIT_ATTACKED == "UNIT_ATTACKED"
        assert EventType.UNIT_KILLED == "UNIT_KILLED"
        assert EventType.TURN_STARTED == "TURN_STARTED"
        assert EventType.TURN_ENDED == "TURN_ENDED"

    def test_event_type_comparison(self):
        """Test that EventType comparison works correctly."""
        event = ev_unit_moved("unit1", (1, 1), (2, 2), 1)
        assert event.type == EventType.UNIT_MOVED
        assert event.type != EventType.UNIT_KILLED
