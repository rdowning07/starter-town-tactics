"""
Unit tests for enhanced UI system with architecture integration.
Tests both new enhanced features and backward compatibility.
"""

import unittest
from game.ui.ui_state import UIState

class TestUIState(unittest.TestCase):
    def setUp(self):
        self.ui = UIState()

    def test_initial_state(self):
        """Test that UIState initializes with correct default values."""
        self.assertEqual(self.ui.current_screen, "game")
        self.assertIsNone(self.ui.selected_unit)
        self.assertIsNone(self.ui.hovered_unit)
        self.assertIsNone(self.ui.hovered_tile)
        self.assertIsNone(self.ui.selected_tile)
        self.assertFalse(self.ui.show_action_menu)
        self.assertIsNone(self.ui.action_menu_pos)
        self.assertFalse(self.ui.show_movement_range)
        self.assertFalse(self.ui.show_attack_targets)
        self.assertEqual(len(self.ui.movement_tiles), 0)
        self.assertEqual(len(self.ui.attack_targets), 0)
        self.assertFalse(self.ui.show_tooltip)
        self.assertEqual(self.ui.tooltip_text, "")
        self.assertIsNone(self.ui.tooltip_pos)

    def test_select_unit(self):
        """Test unit selection functionality."""
        self.ui.select_unit("player_1")
        self.assertEqual(self.ui.selected_unit, "player_1")
        self.assertTrue(self.ui.show_action_menu)
        print(f"[UIState] Selected unit: {self.ui.selected_unit}")

    def test_deselect_unit(self):
        """Test unit deselection functionality."""
        self.ui.select_unit("player_1")
        self.ui.deselect_unit()
        self.assertIsNone(self.ui.selected_unit)
        self.assertFalse(self.ui.show_action_menu)
        print(f"[UIState] Deselected unit: {self.ui.selected_unit}")

    def test_reset_selection(self):
        """Test reset selection functionality."""
        self.ui.select_unit("player_1")
        self.ui.set_movement_range([(1, 1), (2, 2)])
        self.ui.set_attack_targets([(3, 3)])
        
        self.ui.reset_selection()
        
        self.assertIsNone(self.ui.selected_unit)
        self.assertFalse(self.ui.show_action_menu)
        self.assertFalse(self.ui.show_movement_range)
        self.assertFalse(self.ui.show_attack_targets)
        self.assertEqual(len(self.ui.movement_tiles), 0)
        self.assertEqual(len(self.ui.attack_targets), 0)

    def test_hover_tile(self):
        """Test tile hover functionality."""
        self.ui.hover_tile((2, 3))
        self.assertEqual(self.ui.hovered_tile, (2, 3))

    def test_set_movement_range(self):
        """Test movement range setting."""
        tiles = [(1, 1), (2, 2), (3, 3)]
        self.ui.set_movement_range(tiles)
        
        self.assertTrue(self.ui.show_movement_range)
        self.assertFalse(self.ui.show_attack_targets)
        self.assertEqual(self.ui.movement_tiles, tiles)

    def test_set_attack_targets(self):
        """Test attack targets setting."""
        targets = [(4, 4), (5, 5)]
        self.ui.set_attack_targets(targets)
        
        self.assertTrue(self.ui.show_attack_targets)
        self.assertFalse(self.ui.show_movement_range)
        self.assertEqual(self.ui.attack_targets, targets)

    def test_tooltip_functionality(self):
        """Test tooltip show/hide functionality."""
        self.ui.show_tooltip_at("Test tooltip", (100, 100))
        
        self.assertTrue(self.ui.show_tooltip)
        self.assertEqual(self.ui.tooltip_text, "Test tooltip")
        self.assertEqual(self.ui.tooltip_pos, (100, 100))
        
        self.ui.hide_tooltip()
        
        self.assertFalse(self.ui.show_tooltip)
        self.assertEqual(self.ui.tooltip_text, "")
        self.assertIsNone(self.ui.tooltip_pos)

    # Backward compatibility tests
    def test_backward_compatibility_select_unit(self):
        """Test backward compatibility with selected_unit_id property."""
        self.ui.select_unit("player_1")
        self.assertEqual(self.ui.selected_unit_id, "player_1")

    def test_backward_compatibility_action_menu_visible(self):
        """Test backward compatibility with action_menu_visible property."""
        self.ui.select_unit("player_1")
        self.assertTrue(self.ui.action_menu_visible)

    def test_backward_compatibility_update_hover(self):
        """Test backward compatibility with update_hover method."""
        self.ui.update_hover((2, 3))
        self.assertEqual(self.ui.hovered_tile, (2, 3))

    def test_backward_compatibility_deselect_unit(self):
        """Test backward compatibility with deselect_unit method."""
        self.ui.select_unit("player_1")
        self.ui.deselect_unit()
        self.assertIsNone(self.ui.selected_unit)
        self.assertFalse(self.ui.show_action_menu)

if __name__ == "__main__":
    unittest.main()
