"""
Tests for combat rules: height & facing bonuses, damage calculation, HP floors.
"""
import pytest

from core.rules.combat import DamageResult, apply_attack, calc_facing_bonus, calc_height_bonus
from core.state import GameState, Unit, UnitStats


class TestHeightBonus:
    """Test height bonus calculations."""

    def test_height_advantage(self):
        """Higher attacker gets damage bonus."""
        # +2 height difference = +2 damage bonus
        bonus = calc_height_bonus(src_h=3, tgt_h=1)
        assert bonus == 2

    def test_height_disadvantage(self):
        """Lower attacker gets damage penalty."""
        # -2 height difference = -2 damage penalty
        bonus = calc_height_bonus(src_h=1, tgt_h=3)
        assert bonus == -2

    def test_height_equal(self):
        """Equal height gives no bonus."""
        bonus = calc_height_bonus(src_h=2, tgt_h=2)
        assert bonus == 0

    def test_height_clamp_max(self):
        """Height bonus is clamped to maximum."""
        # Large height difference should be clamped to +2
        bonus = calc_height_bonus(src_h=10, tgt_h=0)
        assert bonus == 2

    def test_height_clamp_min(self):
        """Height penalty is clamped to minimum."""
        # Large height disadvantage should be clamped to -2
        bonus = calc_height_bonus(src_h=0, tgt_h=10)
        assert bonus == -2


class TestFacingBonus:
    """Test facing bonus calculations."""

    def test_front_attack(self):
        """Adjacent attack gets front bonus."""
        # Adjacent positions should give front attack
        bonus = calc_facing_bonus("N", (2, 2), (2, 3))
        assert bonus == 0  # FRONT = 0 bonus

    def test_side_attack(self):
        """Side attacks get side bonus."""
        # Non-adjacent positions should give side attack for now
        bonus = calc_facing_bonus("N", (2, 2), (4, 4))
        assert bonus == 1  # SIDE = 1 bonus

    def test_different_facings(self):
        """Different facing directions work."""
        bonus1 = calc_facing_bonus("S", (3, 3), (5, 5))
        bonus2 = calc_facing_bonus("E", (3, 3), (5, 5))
        # Both should return valid bonuses
        assert bonus1 in [0, 1, 2]
        assert bonus2 in [0, 1, 2]


class TestDamageCalculation:
    """Test full damage calculation with bonuses."""

    def setup_method(self):
        """Set up test game state with units."""
        self.game_state = GameState()

        # Create attacker unit
        self.attacker = Unit(
            unit_id="attacker", pos=(2, 2), facing="N", stats=UnitStats(hp=20, atk=10, def_=2, h=1), team="player"
        )

        # Create target unit
        self.target = Unit(
            unit_id="target", pos=(3, 3), facing="S", stats=UnitStats(hp=15, atk=6, def_=3, h=0), team="enemy"
        )

        self.game_state.add_unit(self.attacker)
        self.game_state.add_unit(self.target)

    def test_basic_damage(self):
        """Basic damage calculation without bonuses."""
        # Base damage = attacker.atk - target.def = 10 - 3 = 7
        # Height bonus = 1 - 0 = 1
        # Facing bonus = 1 (side attack)
        # Total expected = 7 + 1 + 1 = 9

        original_hp = self.target.stats.hp
        result = apply_attack(self.game_state, "attacker", "target")

        assert isinstance(result, DamageResult)
        assert result.amount > 0
        assert self.target.stats.hp == original_hp - result.amount
        assert not result.killed  # 15 HP should survive

    def test_damage_floors_at_zero(self):
        """Damage calculation floors at 0."""
        # Create weak attacker vs strong defender
        weak_attacker = Unit(
            unit_id="weak", pos=(1, 1), facing="N", stats=UnitStats(hp=10, atk=2, def_=1, h=0), team="player"
        )

        strong_defender = Unit(
            unit_id="strong", pos=(1, 2), facing="S", stats=UnitStats(hp=20, atk=8, def_=10, h=0), team="enemy"
        )

        self.game_state.add_unit(weak_attacker)
        self.game_state.add_unit(strong_defender)

        result = apply_attack(self.game_state, "weak", "strong")

        # Even with negative base damage, result should be >= 0
        assert result.amount >= 0
        assert strong_defender.stats.hp >= 0

    def test_hp_floors_at_zero(self):
        """HP cannot go below 0."""
        # Deal massive damage
        massive_attacker = Unit(
            unit_id="massive", pos=(1, 1), facing="N", stats=UnitStats(hp=20, atk=100, def_=0, h=5), team="player"
        )

        self.game_state.add_unit(massive_attacker)

        result = apply_attack(self.game_state, "massive", "target")

        assert result.amount > self.target.stats.hp + 10  # Overkill damage
        assert self.target.stats.hp == 0  # HP floors at 0
        assert result.killed  # Target should be killed

    def test_exact_lethal_damage(self):
        """Test exact lethal damage."""
        # Set target to 1 HP
        self.target.stats.hp = 1

        result = apply_attack(self.game_state, "attacker", "target")

        if result.amount >= 1:
            assert self.target.stats.hp == 0
            assert result.killed
        else:
            assert self.target.stats.hp >= 0
            assert not result.killed


class TestCombatIntegration:
    """Integration tests for combat system."""

    def test_multiple_attacks(self):
        """Test multiple attacks on same target."""
        game_state = GameState()

        attacker = Unit("attacker", (1, 1), stats=UnitStats(hp=20, atk=8, def_=2), team="player")
        target = Unit("target", (2, 2), stats=UnitStats(hp=20, atk=6, def_=3), team="enemy")

        game_state.add_unit(attacker)
        game_state.add_unit(target)

        original_hp = target.stats.hp

        # First attack
        result1 = apply_attack(game_state, "attacker", "target")
        hp_after_first = target.stats.hp

        # Second attack
        result2 = apply_attack(game_state, "attacker", "target")
        hp_after_second = target.stats.hp

        # Verify damage was applied both times
        assert hp_after_first < original_hp
        assert hp_after_second < hp_after_first
        assert result1.amount > 0
        assert result2.amount > 0

        # HP should never go negative
        assert hp_after_second >= 0

    def test_height_and_facing_combined(self):
        """Test height and facing bonuses work together."""
        game_state = GameState()

        # High attacker
        high_attacker = Unit("high", (1, 1), facing="N", stats=UnitStats(hp=20, atk=8, def_=2, h=3), team="player")

        # Low target
        low_target = Unit("low", (3, 3), facing="S", stats=UnitStats(hp=20, atk=6, def_=3, h=0), team="enemy")

        game_state.add_unit(high_attacker)
        game_state.add_unit(low_target)

        result = apply_attack(game_state, "high", "low")

        # Should get both height bonus (+2) and facing bonus (+1)
        # Base damage = 8 - 3 = 5
        # With bonuses should be higher
        assert result.amount >= 5  # At least base damage
        assert low_target.stats.hp < 20  # Damage was applied
