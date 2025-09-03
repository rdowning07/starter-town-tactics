"""
Integration tests for the core rules engine with command-event system.
"""
from unittest.mock import Mock

import pytest

from core import DamageResult, GameState, Status, Unit, UnitRef, UnitStats, a_star, apply_attack, on_unit_turn_start


class TestRulesIntegration:
    def test_combat_with_height_and_facing(self):
        """Test complete combat calculation with height and facing bonuses."""
        # Create game state
        state = GameState()

        # Create attacker (higher ground, facing target)
        attacker_stats = UnitStats(hp=20, atk=8, def_=3, h=2)  # Height 2
        attacker = Unit("attacker", (5, 5), "E", attacker_stats)
        state.add_unit(attacker)

        # Create target (lower ground, in front)
        target_stats = UnitStats(hp=15, atk=6, def_=2, h=0)  # Height 0
        target = Unit("target", (6, 5), "W", target_stats)
        state.add_unit(target)

        # Apply attack
        result = apply_attack(state, "attacker", "target")

        # Verify damage calculation:
        # Base: 8 atk - 2 def = 6
        # Height: attacker higher by 2 = -2 bonus (target advantage)
        # Facing: adjacent = 0 bonus
        # Total: 6 + (-2) + 0 = 4 damage
        assert result.amount == 4
        assert result.killed == False
        assert target.stats.hp == 11  # 15 - 4

    def test_status_effects_integration(self):
        """Test status effects with game state."""
        state = GameState()

        # Create unit with poison
        unit_stats = UnitStats(hp=10, atk=5, def_=2, h=0)
        unit = Unit("poisoned_unit", (5, 5), "N", unit_stats)
        unit.status.append(Status.POISON)
        state.add_unit(unit)

        # Apply turn start effects
        on_unit_turn_start(state, "poisoned_unit")

        # Should take 2 poison damage
        assert unit.stats.hp == 8

    def test_pathfinding_with_terrain(self):
        """Test A* pathfinding with terrain costs."""
        state = GameState()

        # Create a simple 5x5 map with some high-cost terrain
        state.map = Mock()
        state.map.width = 5
        state.map.height = 5

        # Mock tile costs
        def mock_tile(pos):
            tile = Mock()
            if pos == (2, 2):  # Center tile is expensive
                tile.move_cost = 5
            else:
                tile.move_cost = 1
            return tile

        state.map.tile = mock_tile
        state.map.in_bounds = lambda pos: 0 <= pos[0] < 5 and 0 <= pos[1] < 5
        state.map.blocked = lambda pos: False

        # Find path from (0,0) to (4,4)
        path = a_star(state, (0, 0), (4, 4), 10)

        assert path is not None
        assert path[0] == (0, 0)
        assert path[-1] == (4, 4)

        # Path should avoid expensive center tile if possible
        # With max_cost=10, it should find a path around the center
        assert (2, 2) not in path or len(path) <= 10

    def test_command_event_with_rules(self):
        """Test that rules integrate with command-event system."""
        from core import Attack, Event, EventBus

        # Create game state with units
        state = GameState()
        attacker = Unit("attacker", (5, 5), "E", UnitStats(hp=20, atk=8, def_=3, h=1))
        target = Unit("target", (6, 5), "W", UnitStats(hp=15, atk=6, def_=2, h=0))
        state.add_unit(attacker)
        state.add_unit(target)

        # Create attack command
        attack_cmd = Attack(attacker_id="attacker", target_id="target")

        # Mock event bus
        events_received = []

        def event_handler(event):
            events_received.append(event)

        bus = EventBus()
        bus.subscribe(event_handler)

        # Apply command (this would normally be done by GameLoop)
        if attack_cmd.validate(state):
            events = list(attack_cmd.apply(state))
            bus.publish(events)

        # Verify events were generated
        assert len(events_received) > 0
        assert any(e.type == "attack_started" for e in events_received)
        assert any(e.type == "damage_dealt" for e in events_received)
        assert any(e.type == "attack_ended" for e in events_received)
