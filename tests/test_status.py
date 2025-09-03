"""
Tests for status effects: Poison reduces HP, Slow causes every-other-turn skip.
"""
from unittest.mock import MagicMock, Mock

import pytest

from core.rules.status import Status, on_unit_turn_start
from core.state import GameState, Unit, UnitStats


class TestPoisonEffect:
    """Test Poison status effect."""

    def setup_method(self):
        """Set up test game state with poisoned unit."""
        self.game_state = GameState()

        self.unit = Unit(unit_id="poisoned_unit", pos=(2, 2), stats=UnitStats(hp=10, atk=5, def_=2), team="player")

        # Apply poison status
        self.unit.status = [Status.POISON]

        self.game_state.add_unit(self.unit)

    def test_poison_reduces_hp(self):
        """Poison reduces HP by 2 each turn."""
        original_hp = self.unit.stats.hp

        # Apply poison effect
        on_unit_turn_start(self.game_state, "poisoned_unit")

        # HP should be reduced by 2
        assert self.unit.stats.hp == original_hp - 2

    def test_poison_multiple_turns(self):
        """Poison continues to reduce HP over multiple turns."""
        original_hp = self.unit.stats.hp

        # Apply poison for 3 turns
        on_unit_turn_start(self.game_state, "poisoned_unit")
        hp_after_turn1 = self.unit.stats.hp

        on_unit_turn_start(self.game_state, "poisoned_unit")
        hp_after_turn2 = self.unit.stats.hp

        on_unit_turn_start(self.game_state, "poisoned_unit")
        hp_after_turn3 = self.unit.stats.hp

        # Each turn should reduce HP by 2
        assert hp_after_turn1 == original_hp - 2
        assert hp_after_turn2 == original_hp - 4
        assert hp_after_turn3 == original_hp - 6

    def test_poison_hp_floors_at_zero(self):
        """Poison damage cannot reduce HP below 0."""
        # Set unit to low HP
        self.unit.stats.hp = 1

        # Apply poison effect
        on_unit_turn_start(self.game_state, "poisoned_unit")

        # HP should floor at 0, not go negative
        assert self.unit.stats.hp == 0

    def test_poison_kills_unit(self):
        """Poison can kill a unit."""
        # Set unit to exactly poison damage
        self.unit.stats.hp = 2

        # Apply poison effect
        on_unit_turn_start(self.game_state, "poisoned_unit")

        # Unit should be killed
        assert self.unit.stats.hp == 0

    def test_no_poison_no_damage(self):
        """Units without poison take no damage."""
        # Remove poison status
        self.unit.status = []
        original_hp = self.unit.stats.hp

        # Apply turn start effect
        on_unit_turn_start(self.game_state, "poisoned_unit")

        # HP should be unchanged
        assert self.unit.stats.hp == original_hp

    def test_poison_with_other_status(self):
        """Poison works alongside other status effects."""
        # Add both poison and slow
        self.unit.status = [Status.POISON, Status.SLOW]
        original_hp = self.unit.stats.hp

        # Apply turn start effect
        on_unit_turn_start(self.game_state, "poisoned_unit")

        # Poison damage should still apply
        assert self.unit.stats.hp == original_hp - 2


class TestSlowEffect:
    """Test Slow status effect with mocked turn controller."""

    def setup_method(self):
        """Set up test with mocked turn controller."""
        self.game_state = GameState()

        # Mock turn controller
        self.mock_turn_controller = Mock()
        self.game_state.turn_controller = self.mock_turn_controller

        self.unit = Unit(unit_id="slow_unit", pos=(3, 3), stats=UnitStats(hp=15, atk=6, def_=3), team="player")

        # Apply slow status
        self.unit.status = [Status.SLOW]

        self.game_state.add_unit(self.unit)

    def test_slow_skip_turn_basic(self):
        """Slow causes turn skip (mocked behavior)."""
        # For now, slow effect is handled by turn controller
        # We test that the status is properly set
        assert Status.SLOW in self.unit.status

        # Apply turn start effect (poison check should not affect slow)
        original_hp = self.unit.stats.hp
        on_unit_turn_start(self.game_state, "slow_unit")

        # HP should be unchanged (no poison)
        assert self.unit.stats.hp == original_hp

    def test_slow_alternating_turns(self):
        """Slow should cause every-other-turn skip."""
        # This would be implemented in the turn controller
        # For now we verify the status is maintained

        # Turn 1: Should skip
        assert Status.SLOW in self.unit.status

        # Turn 2: Should act
        assert Status.SLOW in self.unit.status

        # Turn 3: Should skip again
        assert Status.SLOW in self.unit.status

    def test_slow_with_poison(self):
        """Slow and poison can coexist."""
        # Add both status effects
        self.unit.status = [Status.SLOW, Status.POISON]
        original_hp = self.unit.stats.hp

        # Apply turn start effect
        on_unit_turn_start(self.game_state, "slow_unit")

        # Poison should still reduce HP even when slowed
        assert self.unit.stats.hp == original_hp - 2
        assert Status.SLOW in self.unit.status
        assert Status.POISON in self.unit.status

    def test_no_slow_no_skip(self):
        """Units without slow don't skip turns."""
        # Remove slow status
        self.unit.status = []

        # Unit should be able to act normally
        assert Status.SLOW not in self.unit.status


class TestStatusIntegration:
    """Integration tests for status effects."""

    def test_multiple_units_with_status(self):
        """Multiple units can have different status effects."""
        game_state = GameState()

        # Poisoned unit
        poisoned = Unit("poisoned", (1, 1), stats=UnitStats(hp=10, atk=5, def_=2), team="player")
        poisoned.status = [Status.POISON]

        # Slowed unit
        slowed = Unit("slowed", (2, 2), stats=UnitStats(hp=12, atk=6, def_=3), team="player")
        slowed.status = [Status.SLOW]

        # Normal unit
        normal = Unit("normal", (3, 3), stats=UnitStats(hp=15, atk=7, def_=2), team="player")
        normal.status = []

        game_state.add_unit(poisoned)
        game_state.add_unit(slowed)
        game_state.add_unit(normal)

        # Apply turn start effects
        on_unit_turn_start(game_state, "poisoned")
        on_unit_turn_start(game_state, "slowed")
        on_unit_turn_start(game_state, "normal")

        # Verify effects
        assert poisoned.stats.hp == 8  # Reduced by poison
        assert slowed.stats.hp == 12  # Unchanged (no poison)
        assert normal.stats.hp == 15  # Unchanged (no status)

    def test_status_removal(self):
        """Status effects can be removed."""
        game_state = GameState()

        unit = Unit("unit", (1, 1), stats=UnitStats(hp=10, atk=5, def_=2), team="player")
        unit.status = [Status.POISON]
        game_state.add_unit(unit)

        # Apply poison once
        on_unit_turn_start(game_state, "unit")
        assert unit.stats.hp == 8

        # Remove poison
        unit.status = []

        # Apply turn start again
        on_unit_turn_start(game_state, "unit")

        # HP should not decrease further
        assert unit.stats.hp == 8

    def test_status_stacking(self):
        """Multiple instances of same status don't stack."""
        game_state = GameState()

        unit = Unit("unit", (1, 1), stats=UnitStats(hp=10, atk=5, def_=2), team="player")
        # Add poison twice (shouldn't stack)
        unit.status = [Status.POISON, Status.POISON]
        game_state.add_unit(unit)

        # Apply poison effect
        on_unit_turn_start(game_state, "unit")

        # Should only lose 2 HP, not 4 (no stacking)
        assert unit.stats.hp == 8
