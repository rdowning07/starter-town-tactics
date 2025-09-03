"""
Unit tests for Week 3 features.
Tests turn UI, health UI, win/loss logic, and sound manager integration.
"""

import unittest
from unittest.mock import Mock, patch

import pygame

from game.audio.sound_manager import SoundManager
from game.game_win_loss import GameWinLoss
from game.ui.health_ui import HealthUI
from game.ui.turn_ui import TurnUI
from game.ui.ui_state import UIState

# Initialize pygame for testing
pygame.init()


class TestWeek3Features(unittest.TestCase):
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
        self.game_state.sim_runner = Mock()
        self.game_state.sim_runner.turn_count = 5
        self.game_state.sim_runner.is_ai_turn.return_value = False
        self.game_state.turn_controller = Mock()
        self.game_state.turn_controller.get_current_unit.return_value = "player_1"
        self.game_state.turn_controller.turn_order = ["player_1", "player_2", "enemy_1", "enemy_2"]

    def test_turn_ui_initialization(self):
        """Test TurnUI initialization."""
        turn_ui = TurnUI()
        self.assertIsNotNone(turn_ui.font)
        self.assertIsNotNone(turn_ui.small_font)

    def test_health_ui_initialization(self):
        """Test HealthUI initialization."""
        health_ui = HealthUI()
        self.assertIsNotNone(health_ui.font)
        self.assertEqual(len(health_ui.health_cache), 0)

    def test_win_loss_initialization(self):
        """Test GameWinLoss initialization."""
        win_loss = GameWinLoss()
        self.assertEqual(win_loss.game_status, "playing")

    def test_victory_condition_all_enemies_dead(self):
        """Test victory condition when all enemies are dead."""
        win_loss = GameWinLoss()

        # Set all enemies to dead
        self.game_state.units.units["enemy_1"]["alive"] = False
        self.game_state.units.units["enemy_2"]["alive"] = False

        result = win_loss.check_victory_conditions(self.game_state)

        self.assertTrue(result)
        self.assertEqual(win_loss.get_game_status(), "victory")
        self.assertIn("All enemies defeated", win_loss.get_victory_message())

    def test_defeat_condition_all_players_dead(self):
        """Test defeat condition when all players are dead."""
        win_loss = GameWinLoss()

        # Set all players to dead
        self.game_state.units.units["player_1"]["alive"] = False
        self.game_state.units.units["player_2"]["alive"] = False

        result = win_loss.check_victory_conditions(self.game_state)

        self.assertTrue(result)
        self.assertEqual(win_loss.get_game_status(), "defeat")
        self.assertIn("All player units defeated", win_loss.get_defeat_message())

    def test_draw_condition_all_units_dead(self):
        """Test draw condition when all units are dead."""
        win_loss = GameWinLoss()

        # Set all units to dead
        for unit_data in self.game_state.units.units.values():
            unit_data["alive"] = False

        result = win_loss.check_victory_conditions(self.game_state)

        self.assertTrue(result)
        self.assertEqual(win_loss.get_game_status(), "draw")

    def test_health_bar_color_calculation(self):
        """Test health bar color calculation based on health percentage."""
        health_ui = HealthUI()

        # Create a real pygame surface for testing
        test_surface = pygame.Surface((100, 100))

        # Test healthy (green)
        unit_data = {"x": 0, "y": 0, "hp": 18, "max_hp": 20, "alive": True}
        health_ui.draw_health_bar(test_surface, "test_unit", unit_data)
        # Color is determined in the drawing method, so we test the logic

        # Test wounded (yellow) - would be yellow at 50%
        unit_data["hp"] = 10
        health_ui.draw_health_bar(test_surface, "test_unit", unit_data)

        # Test critical (red) - would be red at 20%
        unit_data["hp"] = 4
        health_ui.draw_health_bar(test_surface, "test_unit", unit_data)

    def test_health_validation(self):
        """Test health value validation."""
        health_ui = HealthUI()

        # Create a real pygame surface for testing
        test_surface = pygame.Surface((100, 100))

        # Test negative HP
        unit_data = {"x": 0, "y": 0, "hp": -5, "max_hp": 20, "alive": True}
        health_ui.draw_health_bar(test_surface, "test_unit", unit_data)
        # Should be clamped to 0

        # Test HP exceeding max
        unit_data = {"x": 0, "y": 0, "hp": 25, "max_hp": 20, "alive": True}
        health_ui.draw_health_bar(test_surface, "test_unit", unit_data)
        # Should be clamped to max_hp

    def test_sound_manager_initialization(self):
        """Test SoundManager initialization."""
        with patch("pygame.mixer.init"):
            sound_manager = SoundManager()
            self.assertTrue(sound_manager.sound_enabled)
            self.assertEqual(sound_manager.volume, 0.7)

    def test_sound_manager_volume_control(self):
        """Test sound manager volume control."""
        with patch("pygame.mixer.init"):
            sound_manager = SoundManager()

            # Test volume setting
            sound_manager.set_volume(0.5)
            self.assertEqual(sound_manager.volume, 0.5)

            # Test volume clamping
            sound_manager.set_volume(1.5)  # Should clamp to 1.0
            self.assertEqual(sound_manager.volume, 1.0)

            sound_manager.set_volume(-0.5)  # Should clamp to 0.0
            self.assertEqual(sound_manager.volume, 0.0)

    def test_sound_manager_enable_disable(self):
        """Test sound manager enable/disable functionality."""
        with patch("pygame.mixer.init"):
            sound_manager = SoundManager()

            # Test disable
            sound_manager.enable_sound(False)
            self.assertFalse(sound_manager.sound_enabled)

            # Test enable
            sound_manager.enable_sound(True)
            self.assertTrue(sound_manager.sound_enabled)

    def test_game_summary_generation(self):
        """Test game summary generation."""
        win_loss = GameWinLoss()

        summary = win_loss.get_game_summary(self.game_state)

        self.assertIn("status", summary)
        self.assertIn("turn_count", summary)
        self.assertIn("player_units", summary)
        self.assertIn("enemy_units", summary)

        # Check unit counts
        self.assertEqual(summary["player_units"]["alive"], 2)
        self.assertEqual(summary["enemy_units"]["alive"], 2)

    def test_health_summary_display(self):
        """Test health summary display functionality."""
        health_ui = HealthUI()

        # Test health summary generation
        summary = health_ui.draw_health_summary(Mock(), self.game_state, self.ui_state)

        # Method should execute without error
        self.assertIsNone(summary)  # draw_health_summary returns None

    def test_turn_ui_integration(self):
        """Test turn UI integration with game state."""
        turn_ui = TurnUI()

        # Test turn indicator drawing (real screen)
        test_screen = pygame.Surface((800, 600))
        turn_ui.draw_turn_indicator(test_screen, self.game_state, self.ui_state)

        # Test unit turn highlight
        turn_ui.draw_unit_turn_highlight(test_screen, self.game_state, self.ui_state)

        # Test turn progress
        turn_ui.draw_turn_progress(test_screen, self.game_state, self.ui_state)

    def test_custom_victory_conditions(self):
        """Test custom victory conditions."""
        win_loss = GameWinLoss()

        # Test turn-based victory
        self.game_state.victory_turns = 3
        self.game_state.sim_runner.turn_count = 5

        result = win_loss.check_custom_victory_conditions(self.game_state)
        self.assertTrue(result)
        self.assertEqual(win_loss.get_game_status(), "victory")

    def test_custom_defeat_conditions(self):
        """Test custom defeat conditions."""
        win_loss = GameWinLoss()

        # Test turn-based defeat
        self.game_state.defeat_turns = 3
        self.game_state.sim_runner.turn_count = 5

        result = win_loss.check_defeat_conditions(self.game_state)
        self.assertTrue(result)
        self.assertEqual(win_loss.get_game_status(), "defeat")


if __name__ == "__main__":
    unittest.main()
