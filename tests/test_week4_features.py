"""
Unit tests for Week 4 features.
Tests status effects, status UI, enhanced FX manager, and integration.
"""

import unittest
from unittest.mock import Mock, patch

import pygame

from game.fx_manager import FXManager
from game.status_effects import StatusEffect, StatusEffectManager
from game.ui.status_ui import StatusUI
from game.ui.ui_state import UIState

# Initialize pygame for testing
pygame.init()


class TestWeek4Features(unittest.TestCase):
    def setUp(self):
        self.ui_state = UIState()

        # Create mock game state
        self.game_state = Mock()
        self.game_state.units = Mock()
        self.game_state.units.units = {
            "player_1": {"x": 2, "y": 2, "hp": 20, "max_hp": 20, "team": "player", "alive": True},
            "player_2": {"x": 3, "y": 3, "hp": 15, "max_hp": 15, "team": "player", "alive": True},
            "enemy_1": {"x": 5, "y": 5, "hp": 18, "max_hp": 18, "team": "enemy", "alive": True},
            "enemy_2": {"x": 6, "y": 6, "hp": 12, "max_hp": 12, "team": "enemy", "alive": True},
        }

    def test_status_effect_creation(self):
        """Test StatusEffect dataclass creation."""
        effect = StatusEffect(
            name="poison", duration=3, effect_type="debuff", description="Deals damage over time", stacks=2
        )

        self.assertEqual(effect.name, "poison")
        self.assertEqual(effect.duration, 3)
        self.assertEqual(effect.effect_type, "debuff")
        self.assertEqual(effect.stacks, 2)
        self.assertEqual(effect.max_stacks, 1)  # Default

    def test_status_effect_manager_initialization(self):
        """Test StatusEffectManager initialization."""
        manager = StatusEffectManager()

        self.assertEqual(len(manager.unit_effects), 0)
        self.assertIn("poison", manager.effect_definitions)
        self.assertIn("heal_over_time", manager.effect_definitions)
        self.assertIn("shield", manager.effect_definitions)

    def test_add_poison_effect(self):
        """Test adding poison effect to a unit."""
        manager = StatusEffectManager()

        result = manager.add_effect("player_1", "poison", duration=3, stacks=2)

        self.assertTrue(result)
        self.assertIn("player_1", manager.unit_effects)
        effects = manager.get_unit_effects("player_1")
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].name, "poison")
        self.assertEqual(effects[0].duration, 3)
        self.assertEqual(effects[0].stacks, 2)

    def test_add_unknown_effect(self):
        """Test adding unknown effect returns False."""
        manager = StatusEffectManager()

        result = manager.add_effect("player_1", "unknown_effect", duration=3)

        self.assertFalse(result)
        self.assertEqual(len(manager.unit_effects), 0)

    def test_effect_stacking(self):
        """Test that effects stack properly."""
        manager = StatusEffectManager()

        # Add first poison effect
        manager.add_effect("player_1", "poison", duration=3, stacks=1)
        # Add second poison effect (should stack)
        manager.add_effect("player_1", "poison", duration=2, stacks=2)

        effects = manager.get_unit_effects("player_1")
        self.assertEqual(len(effects), 1)  # Should be combined
        self.assertEqual(effects[0].stacks, 3)  # 1 + 2
        self.assertEqual(effects[0].duration, 3)  # Max of 3 and 2

    def test_effect_max_stacking(self):
        """Test that effects don't exceed max stacks."""
        manager = StatusEffectManager()

        # Add poison effects beyond max stacks (5)
        for i in range(7):
            manager.add_effect("player_1", "poison", duration=3, stacks=1)

        effects = manager.get_unit_effects("player_1")
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].stacks, 5)  # Should be capped at max_stacks

    def test_remove_effect(self):
        """Test removing effects from units."""
        manager = StatusEffectManager()

        manager.add_effect("player_1", "poison", duration=3)
        manager.add_effect("player_1", "shield", duration=2)

        result = manager.remove_effect("player_1", "poison")

        self.assertTrue(result)
        effects = manager.get_unit_effects("player_1")
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].name, "shield")

    def test_tick_effects_poison(self):
        """Test poison effect application during tick."""
        manager = StatusEffectManager()

        # Add poison effect
        manager.add_effect("player_1", "poison", duration=2, stacks=3)
        initial_hp = self.game_state.units.units["player_1"]["hp"]

        # Tick effects
        results = manager.tick_effects(self.game_state)

        # Check damage was applied
        final_hp = self.game_state.units.units["player_1"]["hp"]
        self.assertEqual(final_hp, initial_hp - 3)  # 3 damage from 3 stacks

        # Check effect is still active
        effects = manager.get_unit_effects("player_1")
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].duration, 1)  # Duration decreased

    def test_tick_effects_heal(self):
        """Test heal over time effect application during tick."""
        manager = StatusEffectManager()

        # Damage unit first
        self.game_state.units.units["player_1"]["hp"] = 10

        # Add heal effect
        manager.add_effect("player_1", "heal_over_time", duration=2, stacks=5)
        initial_hp = self.game_state.units.units["player_1"]["hp"]

        # Tick effects
        results = manager.tick_effects(self.game_state)

        # Check healing was applied
        final_hp = self.game_state.units.units["player_1"]["hp"]
        self.assertEqual(final_hp, initial_hp + 5)  # 5 healing from 5 stacks

    def test_tick_effects_expiration(self):
        """Test that effects expire properly."""
        manager = StatusEffectManager()

        # Add effect with 1 turn duration
        manager.add_effect("player_1", "poison", duration=1)

        # Tick effects (should expire)
        results = manager.tick_effects(self.game_state)

        # Check effect expired
        self.assertIn("player_1:poison", results["expired"])
        effects = manager.get_unit_effects("player_1")
        self.assertEqual(len(effects), 0)

    def test_dead_unit_cleanup(self):
        """Test that effects are removed from dead units."""
        manager = StatusEffectManager()

        # Add effect to unit
        manager.add_effect("player_1", "poison", duration=3)

        # Kill unit
        self.game_state.units.units["player_1"]["alive"] = False

        # Tick effects
        results = manager.tick_effects(self.game_state)

        # Check effects were cleaned up
        self.assertNotIn("player_1", manager.unit_effects)

    def test_status_ui_initialization(self):
        """Test StatusUI initialization."""
        status_ui = StatusUI()

        self.assertIsNotNone(status_ui.font)
        self.assertEqual(len(status_ui.icon_cache), 0)
        self.assertEqual(status_ui.icon_size, 16)

    def test_status_icon_creation(self):
        """Test status icon placeholder creation."""
        status_ui = StatusUI()

        # Create test effect
        effect = StatusEffect(name="poison", duration=3, effect_type="debuff")

        # Get icon (should create placeholder)
        icon = status_ui._get_or_create_icon(effect)

        self.assertIsNotNone(icon)
        self.assertEqual(icon.get_width(), 16)
        self.assertEqual(icon.get_height(), 16)

    def test_status_ui_drawing(self):
        """Test status UI drawing methods."""
        status_ui = StatusUI()
        test_surface = pygame.Surface((800, 600))

        # Create test effects
        effects = [
            StatusEffect(name="poison", duration=3, effect_type="debuff", stacks=2),
            StatusEffect(name="shield", duration=2, effect_type="buff", stacks=1),
        ]

        unit_data = {"x": 5, "y": 5, "alive": True}

        # Test drawing (should not crash)
        status_ui.draw_status_icons(test_surface, "test_unit", unit_data, effects)

    def test_fx_manager_week4_methods(self):
        """Test FXManager Week 4 additions."""
        fx_manager = FXManager()

        # Test damage FX
        fx_manager.trigger_damage_fx((100, 100), 15)
        self.assertTrue(fx_manager.is_effect_active("damage"))

        # Test heal FX
        fx_manager.trigger_heal_fx((200, 200), 8)
        self.assertTrue(fx_manager.is_effect_active("heal"))

        # Test critical FX
        fx_manager.trigger_critical_fx((300, 300))
        self.assertTrue(fx_manager.is_effect_active("critical"))

        # Test status apply FX
        fx_manager.trigger_status_apply_fx((400, 400), "buff")
        self.assertTrue(fx_manager.is_effect_active("status_apply"))

    def test_fx_manager_drawing(self):
        """Test FXManager drawing methods."""
        fx_manager = FXManager()
        test_surface = pygame.Surface((800, 600))

        # Add effects
        fx_manager.trigger_damage_fx((100, 100), 10)
        fx_manager.trigger_heal_fx((200, 200), 5)
        fx_manager.trigger_critical_fx((300, 300))

        # Test drawing (should not crash)
        fx_manager.draw_fx(test_surface)

    def test_has_effect(self):
        """Test checking if unit has specific effect."""
        manager = StatusEffectManager()

        manager.add_effect("player_1", "poison", duration=3)

        self.assertTrue(manager.has_effect("player_1", "poison"))
        self.assertFalse(manager.has_effect("player_1", "shield"))
        self.assertFalse(manager.has_effect("player_2", "poison"))

    def test_shield_effect_application(self):
        """Test shield effect provides temporary HP."""
        manager = StatusEffectManager()

        manager.add_effect("player_1", "shield", duration=3, stacks=2)

        # Tick to apply effect
        manager.tick_effects(self.game_state)

        # Check shield HP was added
        unit_data = self.game_state.units.units["player_1"]
        self.assertEqual(unit_data.get("shield_hp"), 10)  # 2 stacks * 5 HP

    def test_haste_effect_application(self):
        """Test haste effect provides movement bonus."""
        manager = StatusEffectManager()

        manager.add_effect("player_1", "haste", duration=3, stacks=2)

        # Tick to apply effect
        manager.tick_effects(self.game_state)

        # Check movement bonus was added
        unit_data = self.game_state.units.units["player_1"]
        self.assertEqual(unit_data.get("movement_bonus"), 2)

    def test_strength_effect_application(self):
        """Test strength effect provides damage bonus."""
        manager = StatusEffectManager()

        manager.add_effect("player_1", "strength", duration=3, stacks=3)

        # Tick to apply effect
        manager.tick_effects(self.game_state)

        # Check damage bonus was added
        unit_data = self.game_state.units.units["player_1"]
        self.assertEqual(unit_data.get("damage_bonus"), 3)


if __name__ == "__main__":
    unittest.main()
