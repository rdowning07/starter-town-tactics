"""
Unit tests for Week 5 features.
Tests combo system, advanced particle FX, dynamic event triggers, and integration.
"""

import unittest
from unittest.mock import Mock, patch

import pygame

from game.combo_system import ComboManager, ComboStep
from game.event_triggers import EventManager, EventTrigger
from game.fx_manager import FXManager
from game.status_effects import StatusEffectManager
from game.ui.ui_state import UIState

# Initialize pygame for testing
pygame.init()


class TestWeek5Features(unittest.TestCase):
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

    def test_combo_step_creation(self):
        """Test ComboStep dataclass creation."""

        def test_action(unit_id, game_state, combo_manager):
            return True

        step = ComboStep(
            name="test_slash",
            action_func=test_action,
            cooldown=2,
            description="Test slash attack",
            fx_type="damage",
            status_effect="poison",
            status_duration=3,
        )

        self.assertEqual(step.name, "test_slash")
        self.assertEqual(step.cooldown, 2)
        self.assertEqual(step.description, "Test slash attack")
        self.assertEqual(step.fx_type, "damage")
        self.assertEqual(step.status_effect, "poison")
        self.assertEqual(step.status_duration, 3)

    def test_combo_manager_initialization(self):
        """Test ComboManager initialization."""
        status_manager = StatusEffectManager()
        fx_manager = FXManager()
        combo_manager = ComboManager(status_manager, fx_manager)

        self.assertEqual(len(combo_manager.active_combos), 0)
        self.assertEqual(len(combo_manager.cooldowns), 0)
        self.assertIn("basic_attack_chain", combo_manager.combo_definitions)
        self.assertIn("magic_chain", combo_manager.combo_definitions)

    def test_add_combo(self):
        """Test adding combo to unit."""
        combo_manager = ComboManager()

        result = combo_manager.add_combo("player_1", "basic_attack_chain")

        self.assertTrue(result)
        self.assertIn("player_1", combo_manager.active_combos)
        combo_steps = combo_manager.active_combos["player_1"]
        self.assertEqual(len(combo_steps), 3)  # slash, thrust, finisher
        self.assertEqual(combo_steps[0].name, "slash")

    def test_add_unknown_combo(self):
        """Test adding unknown combo returns False."""
        combo_manager = ComboManager()

        result = combo_manager.add_combo("player_1", "unknown_combo")

        self.assertFalse(result)
        self.assertEqual(len(combo_manager.active_combos), 0)

    def test_execute_combo_success(self):
        """Test successful combo execution."""
        logger = Mock()
        fx_manager = Mock()
        combo_manager = ComboManager(fx_manager=fx_manager, logger=logger)
        combo_manager.add_combo("player_1", "basic_attack_chain")

        result = combo_manager.execute_combo("player_1", self.game_state)

        print(f"DEBUG: Combo result = {result}")
        print(f"DEBUG: Logger calls = {logger.method_calls}")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["executed_steps"]), 3)
        self.assertEqual(result["executed_steps"], ["slash", "thrust", "finisher"])

    def test_execute_combo_no_combo(self):
        """Test executing combo when unit has no combo."""
        combo_manager = ComboManager()

        result = combo_manager.execute_combo("player_1", self.game_state)

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "No active combo")

    def test_execute_combo_dead_unit(self):
        """Test executing combo on dead unit."""
        combo_manager = ComboManager()
        combo_manager.add_combo("player_1", "basic_attack_chain")

        # Kill unit
        self.game_state.units.units["player_1"]["alive"] = False

        result = combo_manager.execute_combo("player_1", self.game_state)

        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "Unit not alive")

    def test_combo_cooldowns(self):
        """Test combo cooldown system."""
        logger = Mock()
        fx_manager = Mock()
        combo_manager = ComboManager(fx_manager=fx_manager, logger=logger)
        combo_manager.add_combo("player_1", "basic_attack_chain")

        # Execute combo (sets cooldowns)
        combo_manager.execute_combo("player_1", self.game_state)

        # Check cooldowns are set
        unit_cooldowns = combo_manager.cooldowns.get("player_1", {})
        self.assertIn("slash", unit_cooldowns)
        self.assertIn("thrust", unit_cooldowns)
        self.assertIn("finisher", unit_cooldowns)

        # Tick cooldowns
        combo_manager.tick_cooldowns()

        # Check cooldowns decreased
        # Note: slash cooldown was 1, so it gets removed when it reaches 0
        self.assertNotIn("slash", unit_cooldowns)  # removed when reaches 0
        self.assertEqual(unit_cooldowns["thrust"], 1)  # cooldown was 2
        self.assertEqual(unit_cooldowns["finisher"], 2)  # cooldown was 3

    def test_get_combo_status(self):
        """Test getting combo status for unit."""
        combo_manager = ComboManager()
        combo_manager.add_combo("player_1", "basic_attack_chain")

        status = combo_manager.get_combo_status("player_1")

        self.assertTrue(status["has_combo"])
        self.assertEqual(status["total_steps"], 3)
        self.assertEqual(status["ready_steps"], 3)  # All steps ready initially

    def test_get_combo_status_no_combo(self):
        """Test getting combo status for unit without combo."""
        combo_manager = ComboManager()

        status = combo_manager.get_combo_status("player_1")

        self.assertFalse(status["has_combo"])

    def test_remove_combo(self):
        """Test removing combo from unit."""
        combo_manager = ComboManager()
        combo_manager.add_combo("player_1", "basic_attack_chain")

        result = combo_manager.remove_combo("player_1")

        self.assertTrue(result)
        self.assertNotIn("player_1", combo_manager.active_combos)

    def test_event_trigger_creation(self):
        """Test EventTrigger dataclass creation."""

        def test_condition(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger(
            name="test_event",
            condition_func=test_condition,
            effect_func=test_effect,
            description="Test event",
            fx_type="explosion",
            fx_position=(100, 100),
            one_time=True,
            cooldown=5,
        )

        self.assertEqual(event.name, "test_event")
        self.assertEqual(event.description, "Test event")
        self.assertEqual(event.fx_type, "explosion")
        self.assertEqual(event.fx_position, (100, 100))
        self.assertTrue(event.one_time)
        self.assertEqual(event.cooldown, 5)

    def test_event_manager_initialization(self):
        """Test EventManager initialization."""
        fx_manager = FXManager()
        event_manager = EventManager(fx_manager)

        self.assertEqual(len(event_manager.events), 0)
        self.assertIn("trap_activation", event_manager.event_definitions)
        self.assertIn("hazard_trigger", event_manager.event_definitions)

    def test_create_event(self):
        """Test creating event using predefined definitions."""
        event_manager = EventManager()

        event = event_manager.create_event("trap_activation", position=(5, 5), damage=10)

        self.assertIsNotNone(event)
        self.assertEqual(event.name, "trap_activation")
        self.assertEqual(event.fx_position, (5, 5))

    def test_create_unknown_event(self):
        """Test creating unknown event returns None."""
        event_manager = EventManager()

        event = event_manager.create_event("unknown_event")

        self.assertIsNone(event)

    def test_add_event(self):
        """Test adding event to manager."""
        event_manager = EventManager()

        def test_condition(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", test_condition, test_effect)

        result = event_manager.add_event(event)

        self.assertTrue(result)
        self.assertEqual(len(event_manager.events), 1)
        self.assertEqual(event_manager.events[0].name, "test_event")

    def test_evaluate_events(self):
        """Test event evaluation."""
        event_manager = EventManager()

        # Create a simple event that always triggers
        def always_true(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", always_true, test_effect)
        event_manager.add_event(event)

        triggered = event_manager.evaluate_events(self.game_state)

        self.assertIn("test_event", triggered)
        self.assertTrue(event.triggered)

    def test_evaluate_events_condition_false(self):
        """Test event evaluation when condition is false."""
        event_manager = EventManager()

        # Create event that never triggers
        def always_false(game_state):
            return False

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", always_false, test_effect)
        event_manager.add_event(event)

        triggered = event_manager.evaluate_events(self.game_state)

        self.assertEqual(len(triggered), 0)
        self.assertFalse(event.triggered)

    def test_evaluate_events_one_time(self):
        """Test one-time events don't trigger again."""
        event_manager = EventManager()

        def always_true(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", always_true, test_effect, one_time=True)
        event_manager.add_event(event)

        # First evaluation
        triggered1 = event_manager.evaluate_events(self.game_state)
        self.assertIn("test_event", triggered1)

        # Second evaluation
        triggered2 = event_manager.evaluate_events(self.game_state)
        self.assertEqual(len(triggered2), 0)

    def test_evaluate_events_cooldown(self):
        """Test event cooldown system."""
        logger = Mock()
        event_manager = EventManager(logger=logger)

        # Create event with cooldown but no one-time restriction
        def always_true(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", always_true, test_effect, cooldown=3, one_time=False)
        event_manager.add_event(event)

        # First evaluation
        triggered1 = event_manager.evaluate_events(self.game_state)
        self.assertIn("test_event", triggered1)
        self.assertEqual(event.current_cooldown, 3)

        # Second evaluation (should be on cooldown)
        triggered2 = event_manager.evaluate_events(self.game_state)
        self.assertEqual(len(triggered2), 0)
        # Cooldown should be decremented from 3 to 2
        self.assertEqual(event.current_cooldown, 2)

    def test_get_event_status(self):
        """Test getting event status."""
        event_manager = EventManager()

        def test_condition(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", test_condition, test_effect)
        event_manager.add_event(event)

        status = event_manager.get_event_status()

        self.assertEqual(status["total_events"], 1)
        self.assertEqual(status["triggered_events"], 0)
        self.assertEqual(len(status["events"]), 1)
        self.assertEqual(status["events"][0]["name"], "test_event")

    def test_remove_event(self):
        """Test removing event by name."""
        event_manager = EventManager()

        def test_condition(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", test_condition, test_effect)
        event_manager.add_event(event)

        result = event_manager.remove_event("test_event")

        self.assertTrue(result)
        self.assertEqual(len(event_manager.events), 0)

    def test_reset_events(self):
        """Test resetting all events."""
        event_manager = EventManager()

        def test_condition(game_state):
            return True

        def test_effect(game_state, event_manager):
            return True

        event = EventTrigger("test_event", test_condition, test_effect)
        event_manager.add_event(event)

        # Trigger event
        event_manager.evaluate_events(self.game_state)
        self.assertTrue(event.triggered)

        # Reset events
        event_manager.reset_events()
        self.assertFalse(event.triggered)

    def test_fx_manager_week5_methods(self):
        """Test FXManager Week 5 additions."""
        fx_manager = FXManager()

        # Test spark FX
        fx_manager.trigger_spark_fx((100, 100), 8)
        self.assertTrue(fx_manager.is_effect_active("spark"))

        # Test fire FX
        fx_manager.trigger_fire_fx((200, 200), 1.0)
        self.assertTrue(fx_manager.is_effect_active("fire"))

        # Test ice FX
        fx_manager.trigger_ice_fx((300, 300), 1.0)
        self.assertTrue(fx_manager.is_effect_active("ice"))

        # Test combo FX
        fx_manager.trigger_combo_fx((400, 400), 2)
        self.assertTrue(fx_manager.is_effect_active("combo"))

        # Test explosion FX
        fx_manager.trigger_explosion_fx((500, 500), 25)
        self.assertTrue(fx_manager.is_effect_active("explosion"))

        # Test magic FX
        fx_manager.trigger_magic_fx((600, 600), "arcane")
        self.assertTrue(fx_manager.is_effect_active("magic"))

    def test_combo_integration_with_status_effects(self):
        """Test combo system integration with status effects."""
        status_manager = StatusEffectManager()
        fx_manager = FXManager()
        combo_manager = ComboManager(status_manager, fx_manager)

        # Add magic chain combo (includes poison status effect)
        combo_manager.add_combo("player_1", "magic_chain")

        # Execute combo
        result = combo_manager.execute_combo("player_1", self.game_state)

        self.assertTrue(result["success"])

        # Check that status effect was applied
        effects = status_manager.get_unit_effects("player_1")
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].name, "poison")

    def test_event_integration_with_fx(self):
        """Test event system integration with FX manager."""
        fx_manager = FXManager()
        event_manager = EventManager(fx_manager)

        # Create trap event with FX
        trap_event = event_manager.create_event("trap_activation", position=(5, 5), damage=10)
        event_manager.add_event(trap_event)

        # Move unit to trap position
        self.game_state.units.units["player_1"]["x"] = 5
        self.game_state.units.units["player_1"]["y"] = 5

        # Evaluate events
        triggered = event_manager.evaluate_events(self.game_state)

        self.assertIn("trap_activation", triggered)
        # FX should be triggered (explosion at trap position)


if __name__ == "__main__":
    unittest.main()
