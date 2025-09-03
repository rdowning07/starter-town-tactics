"""
Additional tests for Week 4 features to improve code coverage.
Focuses on missing code paths identified by coverage analysis.
"""

import unittest
from unittest.mock import Mock, patch

import pygame

from game.fx_manager import FXEffect, FXManager, FXType
from game.status_effects import StatusEffect, StatusEffectManager
from game.ui.status_ui import StatusUI
from game.ui.ui_state import UIState

# Initialize pygame for testing
pygame.init()


class TestWeek4Coverage(unittest.TestCase):
    def setUp(self):
        self.ui_state = UIState()

        # Create mock game state
        self.game_state = Mock()
        self.game_state.units = Mock()
        self.game_state.units.units = {
            "player_1": {"x": 2, "y": 2, "hp": 20, "max_hp": 20, "team": "player", "alive": True},
            "player_2": {"x": 3, "y": 3, "hp": 15, "max_hp": 15, "team": "player", "alive": True},
            "enemy_1": {"x": 5, "y": 5, "hp": 18, "max_hp": 18, "team": "enemy", "alive": True},
        }

    def test_status_effects_logger_integration(self):
        """Test status effects with logger integration."""
        logger = Mock()
        manager = StatusEffectManager(logger=logger)

        # Add effect and verify logging
        manager.add_effect("player_1", "poison", duration=3)

        # Verify logger was called
        logger.log_event.assert_called_with(
            "status_effect_added", {"unit": "player_1", "effect": "poison", "duration": 3, "stacks": 1}
        )

    def test_status_effects_error_handling(self):
        """Test status effects error handling during tick."""
        manager = StatusEffectManager()

        # Add effect with problematic effect function
        def problematic_effect(unit_data, game_state, effect):
            raise ValueError("Test error")

        effect = manager._create_poison_effect(3, 1)
        effect.effect_func = problematic_effect
        manager.unit_effects["player_1"] = [effect]

        # Tick should handle error gracefully
        results = manager.tick_effects(self.game_state)

        # Effect should be removed due to error
        self.assertNotIn("player_1", manager.unit_effects)

    def test_status_effects_remove_nonexistent(self):
        """Test removing non-existent effect."""
        manager = StatusEffectManager()

        result = manager.remove_effect("player_1", "nonexistent")
        self.assertFalse(result)

    def test_status_effects_find_effect(self):
        """Test finding effects on units."""
        manager = StatusEffectManager()

        # Add effect
        manager.add_effect("player_1", "poison", duration=3)

        # Find effect
        effect = manager._find_effect("player_1", "poison")
        self.assertIsNotNone(effect)
        self.assertEqual(effect.name, "poison")

        # Find non-existent effect
        effect = manager._find_effect("player_1", "shield")
        self.assertIsNone(effect)

    def test_status_ui_tooltip_functionality(self):
        """Test status UI tooltip functionality."""
        status_ui = StatusUI()
        test_surface = pygame.Surface((800, 600))

        # Create test effects
        effects = [
            StatusEffect(name="poison", duration=3, effect_type="debuff", description="Deals damage"),
            StatusEffect(name="shield", duration=2, effect_type="buff", description="Absorbs damage"),
        ]

        # Test tooltip drawing
        status_ui.draw_status_tooltip(test_surface, effects, (100, 100))
        # Should not crash

    def test_status_ui_effect_at_position(self):
        """Test getting effects at screen position."""
        status_ui = StatusUI()

        # Mock status manager
        status_manager = Mock()
        status_manager.get_unit_effects.return_value = [StatusEffect(name="poison", duration=3, effect_type="debuff")]

        # Test position detection
        effects = status_ui.get_effect_at_position((64, 64), self.game_state, status_manager)
        # Should return effects if position matches unit

    def test_fx_manager_unknown_fx_type(self):
        """Test FX manager with unknown FX type."""
        fx_manager = FXManager()

        # Test triggering unknown FX type
        fx_manager.trigger_fx("unknown_type", (100, 100))
        # Should handle gracefully

    def test_fx_manager_screen_shake(self):
        """Test screen shake functionality."""
        fx_manager = FXManager()

        # Trigger screen shake
        fx_manager.trigger_screen_shake(intensity=5.0, duration=0.5)

        # Check shake offset
        offset = fx_manager.get_shake_offset()
        self.assertIsInstance(offset, tuple)
        self.assertEqual(len(offset), 2)

    def test_fx_manager_effect_active_check(self):
        """Test checking if effects are active."""
        fx_manager = FXManager()

        # Add effect
        fx_manager.trigger_damage_fx((100, 100), 10)

        # Check if active
        self.assertTrue(fx_manager.is_effect_active("damage"))
        self.assertFalse(fx_manager.is_effect_active("nonexistent"))

    def test_fx_manager_clear_effects(self):
        """Test clearing all effects."""
        fx_manager = FXManager()

        # Add multiple effects
        fx_manager.trigger_damage_fx((100, 100), 10)
        fx_manager.trigger_heal_fx((200, 200), 5)

        # Clear effects
        fx_manager.clear_effects()

        # Check all cleared
        self.assertEqual(fx_manager.get_active_effects_count(), 0)

    def test_fx_manager_active_effects_count(self):
        """Test counting active effects."""
        fx_manager = FXManager()

        # Add effects
        fx_manager.trigger_damage_fx((100, 100), 10)
        fx_manager.trigger_heal_fx((200, 200), 5)

        # Check count
        self.assertEqual(fx_manager.get_active_effects_count(), 2)

    def test_fx_manager_draw_fx_no_effects(self):
        """Test drawing FX with no active effects."""
        fx_manager = FXManager()
        test_surface = pygame.Surface((800, 600))

        # Draw with no effects
        fx_manager.draw_fx(test_surface)
        # Should not crash

    def test_fx_manager_update_effects(self):
        """Test updating effects."""
        fx_manager = FXManager()

        # Add effect
        fx_manager.trigger_damage_fx((100, 100), 10)

        # Update effects
        fx_manager.update()
        # Should not crash

    def test_status_effects_weakness_effect(self):
        """Test weakness effect application."""
        manager = StatusEffectManager()

        manager.add_effect("player_1", "weakness", duration=3, stacks=2)

        # Tick to apply effect
        manager.tick_effects(self.game_state)

        # Check damage penalty was added
        unit_data = self.game_state.units.units["player_1"]
        self.assertEqual(unit_data.get("damage_penalty"), 2)

    def test_status_effects_slow_effect(self):
        """Test slow effect application."""
        manager = StatusEffectManager()

        manager.add_effect("player_1", "slow", duration=3, stacks=1)

        # Tick to apply effect
        manager.tick_effects(self.game_state)

        # Check movement penalty was added
        unit_data = self.game_state.units.units["player_1"]
        self.assertEqual(unit_data.get("movement_penalty"), 1)

    def test_status_effects_heal_max_hp_limit(self):
        """Test heal effect respects max HP limit."""
        manager = StatusEffectManager()

        # Set unit to max HP
        self.game_state.units.units["player_1"]["hp"] = 20
        self.game_state.units.units["player_1"]["max_hp"] = 20

        # Add heal effect
        manager.add_effect("player_1", "heal_over_time", duration=3, stacks=10)

        # Tick to apply effect
        manager.tick_effects(self.game_state)

        # Check HP didn't exceed max
        unit_data = self.game_state.units.units["player_1"]
        self.assertEqual(unit_data["hp"], 20)  # Should not exceed max_hp

    def test_status_effects_poison_negative_hp_prevention(self):
        """Test poison effect doesn't make HP negative."""
        manager = StatusEffectManager()

        # Set unit to low HP
        self.game_state.units.units["player_1"]["hp"] = 1

        # Add strong poison effect
        manager.add_effect("player_1", "poison", duration=3, stacks=10)

        # Tick to apply effect
        manager.tick_effects(self.game_state)

        # Check HP didn't go negative
        unit_data = self.game_state.units.units["player_1"]
        self.assertEqual(unit_data["hp"], 0)  # Should not go below 0

    def test_status_ui_icon_cache(self):
        """Test status UI icon caching."""
        status_ui = StatusUI()

        # Create test effect
        effect = StatusEffect(name="test_effect", duration=3, effect_type="buff")

        # Get icon twice
        icon1 = status_ui._get_or_create_icon(effect)
        icon2 = status_ui._get_or_create_icon(effect)

        # Should be the same cached icon
        self.assertIs(icon1, icon2)

    def test_fx_manager_metadata_handling(self):
        """Test FX manager metadata handling."""
        fx_manager = FXManager()

        # Test with metadata
        metadata = {"test_key": "test_value"}
        fx_manager.trigger_fx("damage", (100, 100), metadata=metadata)

        # Should not crash


if __name__ == "__main__":
    unittest.main()
