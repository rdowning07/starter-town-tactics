"""
Test suite for the core command-event architecture.

This module tests the new command-event system including:
- Command protocol and dataclasses
- Event system and EventBus
- GameLoop orchestration
- RNG deterministic behavior
- GameState management
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List

from core import (
    Command, Move, Attack, EndTurn,
    Event, EventBus, Subscriber,
    GameLoop, Rng, GameState, Controller
)


class TestCommands:
    """Test command dataclasses and protocol."""
    
    def test_move_command_creation(self):
        """Test Move command can be created with correct attributes."""
        move = Move(unit_id="player1", to=(5, 5))
        assert move.unit_id == "player1"
        assert move.to == (5, 5)
    
    def test_attack_command_creation(self):
        """Test Attack command can be created with correct attributes."""
        attack = Attack(attacker_id="player1", target_id="enemy1")
        assert attack.attacker_id == "player1"
        assert attack.target_id == "enemy1"
    
    def test_end_turn_command_creation(self):
        """Test EndTurn command can be created with correct attributes."""
        end_turn = EndTurn(unit_id="player1")
        assert end_turn.unit_id == "player1"
    
    def test_commands_are_immutable(self):
        """Test that command dataclasses are frozen and immutable."""
        move = Move(unit_id="player1", to=(5, 5))
        
        with pytest.raises(Exception):  # Should raise for frozen dataclass
            move.unit_id = "player2"


class TestEventSystem:
    """Test event system and EventBus."""
    
    def test_event_creation(self):
        """Test Event can be created with type and payload."""
        event = Event(type="unit_moved", payload={"unit_id": "player1", "to": (5, 5)}, tick=0)
        assert event.type == "unit_moved"
        assert event.payload["unit_id"] == "player1"
        assert event.payload["to"] == (5, 5)
    
    def test_event_is_immutable(self):
        """Test that Event is frozen and immutable."""
        event = Event(type="test", payload={"key": "value"}, tick=0)
        
        with pytest.raises(Exception):  # Should raise for frozen dataclass
            event.type = "modified"
    
    def test_event_bus_initialization(self):
        """Test EventBus initializes with empty subscribers."""
        bus = EventBus()
        assert len(bus._subs) == 0
    
    def test_event_bus_subscribe(self):
        """Test EventBus can subscribe functions."""
        bus = EventBus()
        subscriber = Mock()
        
        bus.subscribe(subscriber)
        assert len(bus._subs) == 1
        assert subscriber in [sub[0] for sub in bus._subs]
    
    def test_event_bus_publish_single_event(self):
        """Test EventBus publishes events to all subscribers."""
        bus = EventBus()
        subscriber1 = Mock()
        subscriber2 = Mock()
        
        bus.subscribe(subscriber1)
        bus.subscribe(subscriber2)
        
        event = Event(type="test", payload={"message": "hello"}, tick=0)
        bus.publish([event])
        
        subscriber1.assert_called_once_with(event)
        subscriber2.assert_called_once_with(event)
    
    def test_event_bus_publish_multiple_events(self):
        """Test EventBus publishes multiple events to all subscribers."""
        bus = EventBus()
        subscriber = Mock()
        bus.subscribe(subscriber)
        
        events = [
            Event(type="event1", payload={"id": 1}, tick=0),
            Event(type="event2", payload={"id": 2}, tick=1),
            Event(type="event3", payload={"id": 3}, tick=2)
        ]
        
        bus.publish(events)
        
        assert subscriber.call_count == 3
        calls = subscriber.call_args_list
        assert calls[0][0][0] == events[0]
        assert calls[1][0][0] == events[1]
        assert calls[2][0][0] == events[2]
    
    def test_event_bus_no_subscribers(self):
        """Test EventBus handles publishing with no subscribers gracefully."""
        bus = EventBus()
        event = Event(type="test", payload={"message": "hello"}, tick=0)
        
        # Should not raise any exception
        bus.publish([event])


class TestRng:
    """Test deterministic random number generation."""
    
    def test_rng_initialization(self):
        """Test Rng initializes with seed."""
        rng = Rng(seed=42)
        assert rng._r is not None
    
    def test_rng_deterministic_behavior(self):
        """Test Rng produces same sequence with same seed."""
        rng1 = Rng(seed=42)
        rng2 = Rng(seed=42)
        
        # Generate multiple numbers
        results1 = [rng1.randint(1, 100) for _ in range(10)]
        results2 = [rng2.randint(1, 100) for _ in range(10)]
        
        assert results1 == results2
    
    def test_rng_different_seeds_produce_different_sequences(self):
        """Test Rng produces different sequences with different seeds."""
        rng1 = Rng(seed=42)
        rng2 = Rng(seed=1337)
        
        results1 = [rng1.randint(1, 100) for _ in range(10)]
        results2 = [rng2.randint(1, 100) for _ in range(10)]
        
        assert results1 != results2
    
    def test_rng_bounds(self):
        """Test Rng respects min and max bounds."""
        rng = Rng(seed=42)
        
        for _ in range(100):
            result = rng.randint(5, 10)
            assert 5 <= result <= 10


class TestGameState:
    """Test GameState management."""
    
    def test_game_state_initialization(self):
        """Test GameState initializes with default values."""
        state = GameState()
        assert state.objectives is None
        assert state.turn_controller is not None  # Now has default TurnController
        assert state._current_controller is None
        assert state._is_over is False
    
    def test_game_state_is_over(self):
        """Test GameState is_over returns correct value."""
        state = GameState()
        assert state.is_over() is False
        
        state.set_over(True)
        assert state.is_over() is True
    
    def test_game_state_set_over(self):
        """Test GameState set_over updates internal state."""
        state = GameState()
        state.set_over(True)
        assert state._is_over is True
        
        state.set_over(False)
        assert state._is_over is False
    
    def test_game_state_current_controller_none(self):
        """Test GameState current_controller raises when no controller set."""
        state = GameState()
        
        with pytest.raises(RuntimeError, match="No controller set"):
            state.current_controller()
    
    def test_game_state_set_and_get_controller(self):
        """Test GameState can set and get controller."""
        state = GameState()
        controller = Mock()
        
        state.set_controller(controller)
        assert state.current_controller() == controller


class TestGameLoop:
    """Test GameLoop orchestration."""
    
    def test_game_loop_initialization(self):
        """Test GameLoop initializes with Rng and EventBus."""
        rng = Rng(seed=42)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        
        assert loop.rng == rng
        assert loop.bus == bus
    
    def test_game_loop_tick_when_game_over(self):
        """Test GameLoop tick does nothing when game is over."""
        rng = Rng(seed=42)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        state = GameState()
        state.set_over(True)
        
        # Should not raise any exception and do nothing
        loop.tick(state)
    
    def test_game_loop_tick_with_valid_command(self):
        """Test GameLoop tick processes valid commands."""
        rng = Rng(seed=42)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        state = GameState()
        
        # Mock controller that returns a valid command
        controller = Mock()
        command = Mock()
        command.validate.return_value = True
        command.apply.return_value = [Event(type="test", payload={}, tick=0)]
        
        controller.decide.return_value = command
        state.set_controller(controller)
        
        # Mock objectives and turn_controller
        state.objectives = Mock()
        state.turn_controller = Mock()
        state.turn_controller.start_if_needed.return_value = []
        state.turn_controller.maybe_advance.return_value = []
        
        # Subscribe to events to verify they're published
        events_received = []
        def test_subscriber(event):
            events_received.append(event)
        
        bus.subscribe(test_subscriber)
        
        loop.tick(state)
        
        # Verify command was validated and applied
        command.validate.assert_called_once_with(state)
        command.apply.assert_called_once_with(state)
        
        # Verify events were published
        assert len(events_received) == 1
        assert events_received[0].type == "test"
        
        # Verify objectives and turn controller were updated
        state.objectives.update_from_events.assert_called_once()
        state.turn_controller.maybe_advance.assert_called_once_with(state)
    
    def test_game_loop_tick_with_invalid_command(self):
        """Test GameLoop tick skips invalid commands."""
        rng = Rng(seed=42)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        state = GameState()
        
        # Mock controller that returns an invalid command
        controller = Mock()
        command = Mock()
        command.validate.return_value = False
        
        controller.decide.return_value = command
        state.set_controller(controller)
        
        # Mock objectives and turn_controller
        state.objectives = Mock()
        state.turn_controller = Mock()
        state.turn_controller.start_if_needed.return_value = []
        state.turn_controller.maybe_advance.return_value = []
        
        loop.tick(state)
        
        # Verify command was validated but not applied
        command.validate.assert_called_once_with(state)
        command.apply.assert_not_called()
        
        # Verify objectives and turn controller were not updated
        state.objectives.update_from_events.assert_not_called()
        state.turn_controller.maybe_advance.assert_not_called()


class TestIntegration:
    """Test integration between components."""
    
    def test_full_command_event_flow(self):
        """Test complete flow from command creation to event processing."""
        # Setup
        rng = Rng(seed=42)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        state = GameState()
        
        # Create a simple command implementation
        class TestMoveCommand:
            def __init__(self, unit_id: str, to: tuple[int, int]):
                self.unit_id = unit_id
                self.to = to
            
            def validate(self, s: GameState) -> bool:
                return True
            
            def apply(self, s: GameState) -> List[Event]:
                from core.events import EventType
                return [
                    Event(type=EventType.UNIT_MOVED, payload={
                        "unit_id": self.unit_id,
                        "to": self.to
                    }, tick=s.tick)
                ]
        
        # Mock controller
        controller = Mock()
        command = TestMoveCommand("player1", (5, 5))
        controller.decide.return_value = command
        state.set_controller(controller)
        
        # Mock objectives and turn_controller
        state.objectives = Mock()
        state.turn_controller = Mock()
        state.turn_controller.start_if_needed.return_value = []
        state.turn_controller.maybe_advance.return_value = []
        
        # Subscribe to events
        events_received = []
        def test_subscriber(event):
            events_received.append(event)
        
        bus.subscribe(test_subscriber)
        
        # Execute
        loop.tick(state)
        
        # Verify
        assert len(events_received) == 1
        from core.events import EventType
        assert events_received[0].type == EventType.UNIT_MOVED
        assert events_received[0].payload["unit_id"] == "player1"
        assert events_received[0].payload["to"] == (5, 5)
        
        state.objectives.update_from_events.assert_called_once()
        state.turn_controller.maybe_advance.assert_called_once_with(state)
    
    def test_multiple_commands_and_events(self):
        """Test processing multiple commands and events."""
        rng = Rng(seed=42)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        state = GameState()
        
        # Create command that generates multiple events
        class MultiEventCommand:
            def validate(self, s: GameState) -> bool:
                return True
            
            def apply(self, s: GameState) -> List[Event]:
                from core.events import EventType
                return [
                    Event(type=EventType.UNIT_ATTACKED, payload={"attacker": "player1"}, tick=s.tick),
                    Event(type=EventType.UNIT_ATTACKED, payload={"damage": 5}, tick=s.tick),
                    Event(type=EventType.UNIT_ATTACKED, payload={"target": "enemy1"}, tick=s.tick)
                ]
        
        controller = Mock()
        command = MultiEventCommand()
        controller.decide.return_value = command
        state.set_controller(controller)
        
        state.objectives = Mock()
        state.turn_controller = Mock()
        state.turn_controller.start_if_needed.return_value = []
        state.turn_controller.maybe_advance.return_value = []
        
        events_received = []
        def test_subscriber(event):
            events_received.append(event)
        
        bus.subscribe(test_subscriber)
        
        loop.tick(state)
        
        # Verify all events were received
        from core.events import EventType
        assert len(events_received) == 3
        assert events_received[0].type == EventType.UNIT_ATTACKED
        assert events_received[1].type == EventType.UNIT_ATTACKED
        assert events_received[2].type == EventType.UNIT_ATTACKED
        
        # Verify each event was processed by subscriber
        assert events_received[0].payload["attacker"] == "player1"
        assert events_received[1].payload["damage"] == 5
        assert events_received[2].payload["target"] == "enemy1"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_event_bus_subscriber_raises_exception(self):
        """Test EventBus handles subscriber exceptions gracefully."""
        bus = EventBus()
        
        def bad_subscriber(event):
            raise ValueError("Subscriber error")
        
        def good_subscriber(event):
            pass
        
        bus.subscribe(bad_subscriber)
        bus.subscribe(good_subscriber)
        
        event = Event(type="test", payload={}, tick=0)
        
        # Should not raise exception, should continue processing
        bus.publish([event])
    
    def test_game_loop_with_no_objectives_or_turn_controller(self):
        """Test GameLoop handles missing objectives and turn_controller."""
        rng = Rng(seed=42)
        bus = EventBus()
        loop = GameLoop(rng, bus)
        state = GameState()
        
        # Don't set objectives or turn_controller
        controller = Mock()
        command = Mock()
        command.validate.return_value = True
        command.apply.return_value = []
        
        controller.decide.return_value = command
        state.set_controller(controller)
        
        # Should not raise AttributeError
        loop.tick(state)
    
    def test_rng_edge_cases(self):
        """Test RNG with edge case bounds."""
        rng = Rng(seed=42)
        
        # Same min and max
        result = rng.randint(5, 5)
        assert result == 5
        
        # Large range
        result = rng.randint(1, 1000000)
        assert 1 <= result <= 1000000
        
        # Negative bounds
        result = rng.randint(-10, -5)
        assert -10 <= result <= -5
