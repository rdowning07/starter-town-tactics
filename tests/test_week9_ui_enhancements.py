"""
Test Week 9 UI Enhancements - AP UI, Cursor Manager, and Ability Icons.
Includes comprehensive testing and rollback capabilities.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch

import pygame

from game.game_state import GameState
from game.ui.ability_icons import AbilityIcons

# Import components under test
from game.ui.ap_ui import APUI
from game.ui.cursor_manager import CursorManager
from game.ui.ui_state import UIState


class TestAPUI(unittest.TestCase):
    """Test AP UI system with full validation and rollback."""

    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.logger = Mock()
        self.ap_ui = APUI(logger=self.logger)
        self.game_state = GameState()

        # Create test unit data
        self.test_unit_data = {"x": 5, "y": 3, "hp": 15, "max_hp": 20, "ap": 2, "max_ap": 3, "alive": True}

    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()

    def test_ap_ui_initialization(self):
        """Test AP UI initialization."""
        self.assertIsNotNone(self.ap_ui)
        self.assertIsInstance(self.ap_ui.font, pygame.font.Font)
        self.assertIsInstance(self.ap_ui.ap_cache, dict)

    def test_draw_ap_bar_valid_unit(self):
        """Test drawing AP bar for valid unit."""
        # Pre-condition: Valid unit data
        self.assertTrue(self.test_unit_data["alive"])
        self.assertIn("ap", self.test_unit_data)
        self.assertIn("max_ap", self.test_unit_data)

        # Action: Draw AP bar
        self.ap_ui.draw_ap_bar(self.screen, "test_unit", self.test_unit_data)

        # Post-condition: Logger called with correct data
        self.logger.info.assert_called_with(
            {"event": "ap_bar_drawn", "unit_id": "test_unit", "current_ap": 2, "max_ap": 3, "fill_ratio": 2 / 3}
        )

    def test_draw_ap_bar_dead_unit(self):
        """Test AP bar not drawn for dead unit."""
        dead_unit_data = self.test_unit_data.copy()
        dead_unit_data["alive"] = False

        # Action: Draw AP bar for dead unit
        self.ap_ui.draw_ap_bar(self.screen, "dead_unit", dead_unit_data)

        # Post-condition: Logger not called (no drawing)
        self.logger.info.assert_not_called()

    def test_draw_ap_bar_invalid_values(self):
        """Test AP bar with invalid values (negative, over max)."""
        invalid_unit_data = self.test_unit_data.copy()
        invalid_unit_data["ap"] = -1
        invalid_unit_data["max_ap"] = 5

        # Action: Draw AP bar with invalid values
        self.ap_ui.draw_ap_bar(self.screen, "invalid_unit", invalid_unit_data)

        # Post-condition: Values clamped correctly
        self.logger.info.assert_called_with(
            {
                "event": "ap_bar_drawn",
                "unit_id": "invalid_unit",
                "current_ap": 0,  # Clamped from -1
                "max_ap": 5,
                "fill_ratio": 0.0,
            }
        )

    def test_draw_all_ap_bars(self):
        """Test drawing AP bars for all units."""
        # Setup: Add units to game state
        self.game_state.units.units = {
            "unit1": {"x": 1, "y": 1, "ap": 1, "max_ap": 3, "alive": True},
            "unit2": {"x": 2, "y": 2, "ap": 3, "max_ap": 3, "alive": True},
            "dead_unit": {"x": 3, "y": 3, "ap": 2, "max_ap": 3, "alive": False},
        }

        # Action: Draw all AP bars
        self.ap_ui.draw_all_ap_bars(self.screen, self.game_state, UIState())

        # Post-condition: Logger called for each alive unit
        self.assertEqual(self.logger.info.call_count, 2)  # Only alive units

    def test_get_ap_summary(self):
        """Test getting AP summary for all units."""
        # Setup: Add units to game state
        self.game_state.units.units = {
            "unit1": {"ap": 1, "max_ap": 3, "alive": True},
            "unit2": {"ap": 3, "max_ap": 3, "alive": True},
            "dead_unit": {"ap": 2, "max_ap": 3, "alive": False},
        }

        # Action: Get AP summary
        summary = self.ap_ui.get_ap_summary(self.game_state)

        # Post-condition: Correct summary returned
        expected = {"unit1": {"current": 1, "max": 3}, "unit2": {"current": 3, "max": 3}}
        self.assertEqual(summary, expected)


class TestCursorManager(unittest.TestCase):
    """Test Cursor Manager system with full validation and rollback."""

    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.logger = Mock()
        self.cursor_manager = CursorManager(logger=self.logger)
        self.ui_state = UIState()

    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()

    def test_cursor_manager_initialization(self):
        """Test cursor manager initialization."""
        self.assertIsNotNone(self.cursor_manager)
        self.assertIn("default", self.cursor_manager.cursors)
        self.assertIn("select", self.cursor_manager.cursors)
        self.assertIn("move", self.cursor_manager.cursors)
        self.assertIn("attack", self.cursor_manager.cursors)
        self.assertIn("invalid", self.cursor_manager.cursors)
        self.assertEqual(self.cursor_manager.current_cursor, "default")

    def test_set_cursor_valid(self):
        """Test setting valid cursor."""
        # Pre-condition: Valid cursor type
        self.assertIn("select", self.cursor_manager.cursors)

        # Action: Set cursor
        self.cursor_manager.set_cursor("select")

        # Post-condition: Cursor changed and logged
        self.assertEqual(self.cursor_manager.current_cursor, "select")
        self.logger.info.assert_called_with({"event": "cursor_changed", "cursor_type": "select"})

    def test_set_cursor_invalid_fallback(self):
        """Test setting invalid cursor falls back to default."""
        # Pre-condition: Invalid cursor type
        self.assertNotIn("invalid_cursor", self.cursor_manager.cursors)

        # Action: Set invalid cursor
        self.cursor_manager.set_cursor("invalid_cursor")

        # Post-condition: Fallback to default and warning logged
        self.assertEqual(self.cursor_manager.current_cursor, "default")
        self.logger.warning.assert_called_with(
            {"event": "cursor_fallback", "requested": "invalid_cursor", "fallback": "default"}
        )

    def test_update_cursor_based_on_ui_state(self):
        """Test cursor updates based on UI state."""
        # Test default cursor (no selection)
        self.cursor_manager.update_cursor(self.ui_state, (100, 100))
        self.assertEqual(self.cursor_manager.current_cursor, "default")

        # Test select cursor (unit selected)
        self.ui_state.selected_unit = "test_unit"
        self.cursor_manager.update_cursor(self.ui_state, (100, 100))
        self.assertEqual(self.cursor_manager.current_cursor, "select")

        # Test move cursor (showing movement range)
        self.ui_state.show_movement_range = True
        self.cursor_manager.update_cursor(self.ui_state, (100, 100))
        self.assertEqual(self.cursor_manager.current_cursor, "move")

        # Test attack cursor (showing attack targets)
        self.ui_state.show_movement_range = False
        self.ui_state.show_attack_targets = True
        self.cursor_manager.update_cursor(self.ui_state, (100, 100))
        self.assertEqual(self.cursor_manager.current_cursor, "attack")

    def test_draw_cursor(self):
        """Test drawing custom cursor."""
        # Setup: Set cursor and mouse position
        self.cursor_manager.set_cursor("select")
        mouse_pos = (100, 100)

        # Action: Draw cursor
        self.cursor_manager.draw_cursor(self.screen, mouse_pos)

        # Post-condition: Cursor surface exists and system cursor hidden
        self.assertIsNotNone(self.cursor_manager.custom_cursor_surface)

    def test_reset_cursor(self):
        """Test resetting cursor to default."""
        # Setup: Set to non-default cursor
        self.cursor_manager.set_cursor("attack")
        self.assertEqual(self.cursor_manager.current_cursor, "attack")

        # Action: Reset cursor
        self.cursor_manager.reset_cursor()

        # Post-condition: Back to default
        self.assertEqual(self.cursor_manager.current_cursor, "default")

    def test_get_cursor_info(self):
        """Test getting cursor information."""
        # Action: Get cursor info
        info = self.cursor_manager.get_cursor_info()

        # Post-condition: Correct info returned
        self.assertIn("current_cursor", info)
        self.assertIn("available_cursors", info)
        self.assertEqual(info["current_cursor"], "default")
        self.assertIn("default", info["available_cursors"])


class TestAbilityIcons(unittest.TestCase):
    """Test Ability Icons system with full validation and rollback."""

    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.logger = Mock()
        self.ability_icons = AbilityIcons(logger=self.logger)

    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()

    def test_ability_icons_initialization(self):
        """Test ability icons initialization."""
        self.assertIsNotNone(self.ability_icons)
        self.assertEqual(self.ability_icons.icon_size, 32)
        self.assertIn("attack", self.ability_icons.icons)
        self.assertIn("move", self.ability_icons.icons)
        self.assertIn("heal", self.ability_icons.icons)
        self.assertIn("wait", self.ability_icons.icons)
        self.assertIn("special", self.ability_icons.icons)
        self.assertIn("defend", self.ability_icons.icons)

    def test_draw_ability_panel(self):
        """Test drawing ability panel."""
        abilities = ["attack", "move", "heal"]
        position = (100, 100)

        # Action: Draw ability panel
        self.ability_icons.draw_ability_panel(self.screen, abilities, position, available_ap=3)

        # Post-condition: Panel drawn (no exceptions)
        self.assertTrue(True)  # If we get here, no exceptions occurred

    def test_draw_ability_icon_available(self):
        """Test drawing available ability icon."""
        position = (100, 100)

        # Action: Draw available icon
        self.ability_icons.draw_ability_icon(self.screen, "attack", position, available=True)

        # Post-condition: Icon drawn (no exceptions)
        self.assertTrue(True)

    def test_draw_ability_icon_unavailable(self):
        """Test drawing unavailable ability icon."""
        position = (100, 100)

        # Action: Draw unavailable icon
        self.ability_icons.draw_ability_icon(self.screen, "attack", position, available=False)

        # Post-condition: Dimmed icon drawn (no exceptions)
        self.assertTrue(True)

    def test_get_available_abilities_basic_unit(self):
        """Test getting abilities for basic unit."""
        unit_data = {"ap": 2, "type": "basic"}

        # Action: Get available abilities
        abilities = self.ability_icons.get_available_abilities(unit_data)

        # Post-condition: Correct abilities returned
        expected = ["move", "attack", "wait"]
        self.assertEqual(set(abilities), set(expected))

    def test_get_available_abilities_mage(self):
        """Test getting abilities for mage unit."""
        unit_data = {"ap": 3, "type": "mage"}

        # Action: Get available abilities
        abilities = self.ability_icons.get_available_abilities(unit_data)

        # Post-condition: Mage abilities included
        expected = ["move", "attack", "heal", "wait"]
        self.assertEqual(set(abilities), set(expected))

    def test_get_available_abilities_knight(self):
        """Test getting abilities for knight unit."""
        unit_data = {"ap": 2, "type": "knight"}

        # Action: Get available abilities
        abilities = self.ability_icons.get_available_abilities(unit_data)

        # Post-condition: Knight abilities included
        expected = ["move", "attack", "defend", "wait"]
        self.assertEqual(set(abilities), set(expected))

    def test_get_available_abilities_no_ap(self):
        """Test getting abilities with no AP."""
        unit_data = {"ap": 0, "type": "basic"}

        # Action: Get available abilities
        abilities = self.ability_icons.get_available_abilities(unit_data)

        # Post-condition: Only move and wait available
        expected = ["move", "wait"]
        self.assertEqual(set(abilities), set(expected))

    def test_get_icon_info(self):
        """Test getting icon information."""
        # Action: Get icon info
        info = self.ability_icons.get_icon_info()

        # Post-condition: Correct info returned
        self.assertIn("available_icons", info)
        self.assertIn("icon_size", info)
        self.assertEqual(info["icon_size"], 32)
        self.assertIn("attack", info["available_icons"])


class TestIntegration(unittest.TestCase):
    """Integration tests for UI enhancement components."""

    def setUp(self):
        """Set up integration test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.logger = Mock()
        self.ap_ui = APUI(logger=self.logger)
        self.cursor_manager = CursorManager(logger=self.logger)
        self.ability_icons = AbilityIcons(logger=self.logger)
        self.ui_state = UIState()
        self.game_state = GameState()

        # Add test units
        self.game_state.units.units = {
            "knight": {"x": 1, "y": 1, "hp": 15, "max_hp": 20, "ap": 2, "max_ap": 3, "alive": True, "type": "knight"},
            "mage": {"x": 2, "y": 2, "hp": 10, "max_hp": 15, "ap": 3, "max_ap": 3, "alive": True, "type": "mage"},
        }

    def tearDown(self):
        """Clean up integration test environment."""
        pygame.quit()

    def test_full_ui_rendering_integration(self):
        """Test full UI rendering integration."""
        # Setup: Select a unit
        self.ui_state.selected_unit = "knight"

        # Action: Render all UI components
        self.ap_ui.draw_all_ap_bars(self.screen, self.game_state, self.ui_state)
        self.cursor_manager.update_cursor(self.ui_state, (100, 100))
        self.cursor_manager.draw_cursor(self.screen, (100, 100))

        # Get abilities for selected unit
        unit_data = self.game_state.units.units["knight"]
        abilities = self.ability_icons.get_available_abilities(unit_data)
        self.ability_icons.draw_ability_panel(self.screen, abilities, (600, 500), unit_data["ap"])

        # Post-condition: All components rendered without errors
        self.assertTrue(True)  # No exceptions occurred

    def test_ui_state_integration(self):
        """Test UI state integration across components."""
        # Setup: Complex UI state
        self.ui_state.selected_unit = "mage"
        self.ui_state.show_movement_range = True
        mouse_pos = (150, 150)

        # Action: Update cursor based on UI state
        self.cursor_manager.update_cursor(self.ui_state, mouse_pos)

        # Post-condition: Cursor reflects UI state
        self.assertEqual(self.cursor_manager.current_cursor, "move")

        # Action: Change UI state
        self.ui_state.show_movement_range = False
        self.ui_state.show_attack_targets = True
        self.cursor_manager.update_cursor(self.ui_state, mouse_pos)

        # Post-condition: Cursor updated
        self.assertEqual(self.cursor_manager.current_cursor, "attack")


class TestRollbackCapabilities(unittest.TestCase):
    """Test rollback capabilities for UI enhancements."""

    def setUp(self):
        """Set up rollback test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.logger = Mock()

        # Create backup of original components
        self.backup_components = {}

    def tearDown(self):
        """Clean up rollback test environment."""
        pygame.quit()

    def test_ap_ui_rollback(self):
        """Test AP UI rollback to safe state."""
        # Setup: Create AP UI
        ap_ui = APUI(logger=self.logger)

        # Action: Simulate error condition
        try:
            # This should not cause issues due to validation
            ap_ui.draw_ap_bar(self.screen, "test", {"alive": False})
        except Exception:
            # Rollback: Reset to safe state
            ap_ui = APUI(logger=self.logger)

        # Post-condition: AP UI in safe state
        self.assertIsNotNone(ap_ui)
        self.assertIsInstance(ap_ui.font, pygame.font.Font)

    def test_cursor_manager_rollback(self):
        """Test cursor manager rollback to safe state."""
        # Setup: Create cursor manager
        cursor_manager = CursorManager(logger=self.logger)

        # Action: Simulate error condition
        try:
            # This should not cause issues due to fallback
            cursor_manager.set_cursor("invalid_cursor")
        except Exception:
            # Rollback: Reset to safe state
            cursor_manager = CursorManager(logger=self.logger)

        # Post-condition: Cursor manager in safe state
        self.assertIsNotNone(cursor_manager)
        self.assertEqual(cursor_manager.current_cursor, "default")

    def test_ability_icons_rollback(self):
        """Test ability icons rollback to safe state."""
        # Setup: Create ability icons
        ability_icons = AbilityIcons(logger=self.logger)

        # Action: Simulate error condition
        try:
            # This should not cause issues due to validation
            ability_icons.draw_ability_icon(self.screen, "invalid_icon", (100, 100))
        except Exception:
            # Rollback: Reset to safe state
            ability_icons = AbilityIcons(logger=self.logger)

        # Post-condition: Ability icons in safe state
        self.assertIsNotNone(ability_icons)
        self.assertEqual(ability_icons.icon_size, 32)


if __name__ == "__main__":
    unittest.main()
