"""
Unit tests for game actions functionality.
Tests movement, attacks, and UI state integration.
"""

import unittest
import pygame
from unittest.mock import Mock, patch
from game.ui.game_actions import GameActions
from game.ui.ui_state import UIState

class TestGameActions(unittest.TestCase):
    def setUp(self):
        self.game_actions = GameActions()
        self.ui_state = UIState()
        
        # Create mock game state
        self.game_state = Mock()
        self.game_state.units = Mock()
        self.game_state.units.units = {
            "player_1": {"x": 2, "y": 2, "hp": 20, "team": "player", "alive": True},
            "enemy_1": {"x": 5, "y": 5, "hp": 18, "team": "enemy", "alive": True}
        }
        self.game_state.sim_runner = Mock()
        self.game_state.sim_runner.is_ai_turn.return_value = False

    def test_select_player_unit(self):
        """Test selecting a player unit."""
        # Create mock event
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (64, 64)  # Tile (2, 2) * 32
        
        with patch('game.ui.game_actions.screen_to_tile', return_value=(2, 2)):
            with patch('game.ui.game_actions.get_unit_at_tile', return_value="player_1"):
                self.game_actions.handle_mouse_click(event, self.game_state, self.ui_state)
        
        self.assertEqual(self.ui_state.selected_unit, "player_1")
        self.assertTrue(self.ui_state.show_action_menu)

    def test_move_unit(self):
        """Test moving a unit."""
        # Setup: select a unit
        self.ui_state.select_unit("player_1")
        self.ui_state.set_movement_range([(3, 2), (2, 3)])
        
        # Create mock event for movement
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (96, 64)  # Tile (3, 2) * 32
        
        with patch('game.ui.game_actions.screen_to_tile', return_value=(3, 2)):
            with patch('game.ui.game_actions.get_unit_at_tile', return_value=None):
                self.game_actions.handle_mouse_click(event, self.game_state, self.ui_state)
        
        # Check unit moved
        self.assertEqual(self.game_state.units.units["player_1"]["x"], 3)
        self.assertEqual(self.game_state.units.units["player_1"]["y"], 2)
        
        # Check turn ended
        self.game_state.sim_runner.run_turn.assert_called_once()

    def test_attack_unit(self):
        """Test attacking a unit."""
        # Setup: select a unit
        self.ui_state.select_unit("player_1")
        self.ui_state.set_attack_targets([(5, 5)])
        
        # Create mock event for attack
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (160, 160)  # Tile (5, 5) * 32
        
        with patch('game.ui.game_actions.screen_to_tile', return_value=(5, 5)):
            with patch('game.ui.game_actions.get_unit_at_tile', return_value="enemy_1"):
                self.game_actions.handle_mouse_click(event, self.game_state, self.ui_state)
        
        # Check target took damage
        self.assertEqual(self.game_state.units.units["enemy_1"]["hp"], 13)  # 18 - 5
        
        # Check turn ended
        self.game_state.sim_runner.run_turn.assert_called_once()

    def test_attack_kills_unit(self):
        """Test that attacking can kill units."""
        # Setup: select a unit and set target HP low
        self.ui_state.select_unit("player_1")
        self.ui_state.set_attack_targets([(5, 5)])
        self.game_state.units.units["enemy_1"]["hp"] = 3  # Low HP
        
        # Create mock event for attack
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (160, 160)  # Tile (5, 5) * 32
        
        with patch('game.ui.game_actions.screen_to_tile', return_value=(5, 5)):
            with patch('game.ui.game_actions.get_unit_at_tile', return_value="enemy_1"):
                self.game_actions.handle_mouse_click(event, self.game_state, self.ui_state)
        
        # Check target died
        self.assertEqual(self.game_state.units.units["enemy_1"]["hp"], 0)
        self.assertFalse(self.game_state.units.units["enemy_1"]["alive"])
        
        # Check death was marked
        self.game_state.sim_runner.mark_unit_dead.assert_called_once_with("enemy_1")

    def test_ignore_ai_turn(self):
        """Test that input is ignored during AI turn."""
        self.game_state.sim_runner.is_ai_turn.return_value = True
        
        # Create mock event
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (64, 64)
        
        with patch('game.ui.game_actions.screen_to_tile', return_value=(2, 2)):
            with patch('game.ui.game_actions.get_unit_at_tile', return_value="player_1"):
                self.game_actions.handle_mouse_click(event, self.game_state, self.ui_state)
        
        # Check unit was not selected
        self.assertIsNone(self.ui_state.selected_unit)

    def test_action_menu_click_move(self):
        """Test clicking move button in action menu."""
        # Setup: select a unit
        self.ui_state.select_unit("player_1")
        self.ui_state.action_menu_pos = (100, 100)
        
        with patch('game.ui.game_actions.calculate_movement_range', return_value=[(3, 2), (2, 3)]):
            self.game_actions.handle_action_menu_click((110, 115), self.game_state, self.ui_state)
        
        # Check movement range was set
        self.assertTrue(self.ui_state.show_movement_range)
        self.assertEqual(self.ui_state.movement_tiles, [(3, 2), (2, 3)])

    def test_action_menu_click_attack(self):
        """Test clicking attack button in action menu."""
        # Setup: select a unit
        self.ui_state.select_unit("player_1")
        self.ui_state.action_menu_pos = (100, 100)
        
        with patch('game.ui.game_actions.calculate_attack_targets', return_value=[(5, 5)]):
            self.game_actions.handle_action_menu_click((110, 150), self.game_state, self.ui_state)
        
        # Check attack targets were set
        self.assertTrue(self.ui_state.show_attack_targets)
        self.assertEqual(self.ui_state.attack_targets, [(5, 5)])

    def test_is_player_unit(self):
        """Test player unit identification."""
        # Test player unit
        self.assertTrue(self.game_actions._is_player_unit(self.game_state, "player_1"))
        
        # Test enemy unit
        self.assertFalse(self.game_actions._is_player_unit(self.game_state, "enemy_1"))
        
        # Test dead unit
        self.game_state.units.units["player_1"]["alive"] = False
        self.assertFalse(self.game_actions._is_player_unit(self.game_state, "player_1"))

    def test_calculate_damage(self):
        """Test damage calculation."""
        attacker_data = {"hp": 20, "team": "player"}
        target_data = {"hp": 18, "team": "enemy"}
        
        damage = self.game_actions._calculate_damage(attacker_data, target_data)
        
        # Check damage is reasonable
        self.assertEqual(damage, 5)  # Base damage
        self.assertGreaterEqual(damage, 0)
        self.assertLessEqual(damage, 20)

if __name__ == "__main__":
    unittest.main()
