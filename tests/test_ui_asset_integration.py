"""
Test UI Asset Integration - Verifies ChatGPT's UI asset recommendations work with our architecture.
Tests asset loading, fallback mechanisms, and integration with existing systems.
"""

import unittest
import pygame
from unittest.mock import Mock, patch
import tempfile
import shutil
import os
from pathlib import Path

# Import components under test
from game.ui.ui_renderer import UIRenderer
from game.ui.health_ui import HealthUI
from game.ui.ap_ui import APUI
from game.ui.cursor_manager import CursorManager
from game.ui.ability_icons import AbilityIcons
from game.ui.ui_state import UIState
from game.game_state import GameState

class TestUIAssetIntegration(unittest.TestCase):
    """Test UI asset integration with existing architecture."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.ui_state = UIState()
        self.game_state = GameState()
        self.ui_renderer = UIRenderer(self.screen, 32)
        
        # Create test unit data
        self.test_unit_data = {
            "x": 5, "y": 3, "hp": 15, "max_hp": 20, "ap": 2, "max_ap": 3, "alive": True, "type": "knight"
        }
        self.game_state.units.units = {"test_unit": self.test_unit_data}
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_ui_asset_loading(self):
        """Test UI asset loading with fallback mechanisms."""
        # Test that UI assets are loaded
        self.assertIsNotNone(self.ui_renderer._ui_assets)
        self.assertGreater(len(self.ui_renderer._ui_assets), 0)
        
        # Test specific asset types
        expected_assets = [
            "healthbar", "apbar", "cursor", "select_cursor", "move_cursor",
            "attack_cursor", "invalid_cursor", "attack_icon", "move_icon",
            "heal_icon", "wait_icon", "special_icon", "defend_icon",
            "health_icon", "ap_icon", "status_panel", "turn_panel",
            "action_panel", "health_panel"
        ]
        
        for asset_type in expected_assets:
            self.assertIn(asset_type, self.ui_renderer._ui_assets)
            asset = self.ui_renderer._ui_assets[asset_type]
            self.assertIsInstance(asset, pygame.Surface)
    
    def test_ui_asset_fallback(self):
        """Test UI asset fallback when files are missing."""
        # Test getting assets with fallback
        healthbar = self.ui_renderer.get_ui_asset("healthbar")
        self.assertIsInstance(healthbar, pygame.Surface)
        self.assertEqual(healthbar.get_size(), (64, 8))
        
        apbar = self.ui_renderer.get_ui_asset("apbar")
        self.assertIsInstance(apbar, pygame.Surface)
        self.assertEqual(apbar.get_size(), (64, 8))
        
        cursor = self.ui_renderer.get_ui_asset("cursor")
        self.assertIsInstance(cursor, pygame.Surface)
        self.assertEqual(cursor.get_size(), (16, 16))
    
    def test_ui_asset_placeholder_creation(self):
        """Test placeholder creation for missing assets."""
        # Test placeholder creation for unknown asset
        unknown_asset = self.ui_renderer._create_ui_placeholder("unknown_asset")
        self.assertIsInstance(unknown_asset, pygame.Surface)
        self.assertEqual(unknown_asset.get_size(), (32, 32))
        
        # Test placeholder creation for known asset types
        healthbar_placeholder = self.ui_renderer._create_ui_placeholder("healthbar")
        self.assertIsInstance(healthbar_placeholder, pygame.Surface)
        self.assertEqual(healthbar_placeholder.get_size(), (64, 8))
    
    def test_health_ui_with_assets(self):
        """Test HealthUI integration with UI assets."""
        health_ui = HealthUI()
        
        # Test health bar drawing (should work with or without assets)
        health_ui.draw_health_bar(self.screen, "test_unit", self.test_unit_data)
        
        # Verify no exceptions occurred
        self.assertTrue(True)
    
    def test_ap_ui_with_assets(self):
        """Test APUI integration with UI assets."""
        ap_ui = APUI()
        
        # Test AP bar drawing (should work with or without assets)
        ap_ui.draw_ap_bar(self.screen, "test_unit", self.test_unit_data)
        
        # Verify no exceptions occurred
        self.assertTrue(True)
    
    def test_cursor_manager_with_assets(self):
        """Test CursorManager integration with UI assets."""
        cursor_manager = CursorManager()
        
        # Test cursor operations
        cursor_manager.set_cursor("select")
        self.assertEqual(cursor_manager.current_cursor, "select")
        
        cursor_manager.update_cursor(self.ui_state, (100, 100))
        cursor_manager.draw_cursor(self.screen, (100, 100))
        
        # Verify no exceptions occurred
        self.assertTrue(True)
    
    def test_ability_icons_with_assets(self):
        """Test AbilityIcons integration with UI assets."""
        ability_icons = AbilityIcons()
        
        # Test ability panel drawing
        abilities = ["attack", "move", "heal"]
        ability_icons.draw_ability_panel(self.screen, abilities, (100, 100), 3)
        
        # Test individual icon drawing
        ability_icons.draw_ability_icon(self.screen, "attack", (200, 200), True)
        
        # Verify no exceptions occurred
        self.assertTrue(True)
    
    def test_full_ui_rendering_integration(self):
        """Test full UI rendering integration with assets."""
        # Test all UI components together
        health_ui = HealthUI()
        ap_ui = APUI()
        cursor_manager = CursorManager()
        ability_icons = AbilityIcons()
        
        # Set up UI state
        self.ui_state.selected_unit = "test_unit"
        self.ui_state.show_movement_range = True
        
        # Render all components
        health_ui.draw_all_health_bars(self.screen, self.game_state, self.ui_state)
        ap_ui.draw_all_ap_bars(self.screen, self.game_state, self.ui_state)
        cursor_manager.update_cursor(self.ui_state, (100, 100))
        cursor_manager.draw_cursor(self.screen, (100, 100))
        
        # Get abilities for selected unit
        unit_data = self.game_state.units.units["test_unit"]
        abilities = ability_icons.get_available_abilities(unit_data)
        ability_icons.draw_ability_panel(self.screen, abilities, (600, 500), unit_data["ap"])
        
        # Verify no exceptions occurred
        self.assertTrue(True)
    
    def test_asset_manifest_generation(self):
        """Test asset manifest generation."""
        manifest_path = Path("assets/ui/ui_manifest.json")
        
        # Check if manifest was created
        if manifest_path.exists():
            import json
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Verify manifest structure
            self.assertIn("ui_assets", manifest)
            self.assertIn("assets", manifest["ui_assets"])
            self.assertGreater(len(manifest["ui_assets"]["assets"]), 0)
    
    def test_asset_file_existence(self):
        """Test that UI asset files were created."""
        expected_files = [
            "assets/ui/healthbar.png",
            "assets/ui/apbar.png",
            "assets/ui/cursors/cursor.png",
            "assets/ui/cursors/select.png",
            "assets/ui/cursors/move.png",
            "assets/ui/cursors/attack.png",
            "assets/ui/cursors/invalid.png",
            "assets/ui/icons/attack.png",
            "assets/ui/icons/move.png",
            "assets/ui/icons/heal.png",
            "assets/ui/icons/wait.png",
            "assets/ui/icons/special.png",
            "assets/ui/icons/defend.png",
            "assets/ui/icons/health.png",
            "assets/ui/icons/ap.png",
            "assets/ui/panels/status_panel.png",
            "assets/ui/panels/turn_panel.png",
            "assets/ui/panels/action_panel.png",
            "assets/ui/panels/health_panel.png",
        ]
        
        for file_path in expected_files:
            self.assertTrue(os.path.exists(file_path), f"Asset file missing: {file_path}")

class TestChatGPTRecommendationCompatibility(unittest.TestCase):
    """Test compatibility with ChatGPT's recommendations."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.ui_state = UIState()
        self.game_state = GameState()
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_chatgpt_asset_structure_compatibility(self):
        """Test that our implementation is compatible with ChatGPT's asset structure."""
        # ChatGPT's recommended structure
        chatgpt_structure = {
            "assets/ui/healthbar.png": (64, 8),
            "assets/ui/apbar.png": (64, 8),
            "assets/ui/cursors/cursor.png": (16, 16),
            "assets/ui/icons/attack.png": (32, 32),
            "assets/ui/icons/move.png": (32, 32),
            "assets/ui/icons/heal.png": (32, 32),
            "assets/ui/icons/wait.png": (32, 32),
            "assets/ui/panels/status_panel.png": (128, 32),
            "assets/ui/panels/turn_panel.png": (128, 32),
            "assets/ui/panels/action_panel.png": (128, 32),
        }
        
        # Verify our implementation supports this structure
        ui_renderer = UIRenderer(self.screen, 32)
        
        # Map ChatGPT's paths to our asset types
        path_to_asset_type = {
            "assets/ui/healthbar.png": "healthbar",
            "assets/ui/apbar.png": "apbar",
            "assets/ui/cursors/cursor.png": "cursor",
            "assets/ui/icons/attack.png": "attack_icon",
            "assets/ui/icons/move.png": "move_icon",
            "assets/ui/icons/heal.png": "heal_icon",
            "assets/ui/icons/wait.png": "wait_icon",
            "assets/ui/panels/status_panel.png": "status_panel",
            "assets/ui/panels/turn_panel.png": "turn_panel",
            "assets/ui/panels/action_panel.png": "action_panel",
        }
        
        for asset_path, expected_size in chatgpt_structure.items():
            asset_type = path_to_asset_type[asset_path]
            
            # Test that we can get the asset
            asset = ui_renderer.get_ui_asset(asset_type)
            self.assertIsInstance(asset, pygame.Surface)
            self.assertEqual(asset.get_size(), expected_size)
    
    def test_chatgpt_fallback_logic_compatibility(self):
        """Test that our fallback logic matches ChatGPT's recommendations."""
        ui_renderer = UIRenderer(self.screen, 32)
        
        # Test fallback for missing assets (ChatGPT's approach)
        missing_asset = ui_renderer.get_ui_asset("nonexistent_asset")
        self.assertIsInstance(missing_asset, pygame.Surface)
        
        # Test fallback for known assets
        healthbar = ui_renderer.get_ui_asset("healthbar")
        self.assertIsInstance(healthbar, pygame.Surface)
        self.assertEqual(healthbar.get_size(), (64, 8))
    
    def test_chatgpt_integration_pattern_compatibility(self):
        """Test that our integration pattern is compatible with ChatGPT's approach."""
        # ChatGPT's recommended integration pattern
        ui_renderer = UIRenderer(self.screen, 32)
        health_ui = HealthUI()
        ap_ui = APUI()
        
        # Test that components work together (ChatGPT's integration approach)
        test_unit_data = {
            "x": 1, "y": 1, "hp": 15, "max_hp": 20, "ap": 2, "max_ap": 3, "alive": True
        }
        
        # Test health bar rendering
        health_ui.draw_health_bar(self.screen, "test_unit", test_unit_data)
        
        # Test AP bar rendering
        ap_ui.draw_ap_bar(self.screen, "test_unit", test_unit_data)
        
        # Verify no exceptions occurred
        self.assertTrue(True)

class TestPerformanceAndMemory(unittest.TestCase):
    """Test performance and memory usage of UI asset integration."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_asset_loading_performance(self):
        """Test performance of asset loading."""
        import time
        
        start_time = time.time()
        ui_renderer = UIRenderer(self.screen, 32)
        load_time = time.time() - start_time
        
        # Asset loading should be fast (< 100ms)
        self.assertLess(load_time, 0.1, f"Asset loading took {load_time:.3f}s, should be < 0.1s")
    
    def test_asset_cache_efficiency(self):
        """Test efficiency of asset caching."""
        ui_renderer = UIRenderer(self.screen, 32)
        
        # Test that assets are cached
        initial_cache_size = len(ui_renderer._ui_assets)
        self.assertGreater(initial_cache_size, 0)
        
        # Test that getting the same asset multiple times doesn't create duplicates
        for _ in range(10):
            asset = ui_renderer.get_ui_asset("healthbar")
            self.assertIsInstance(asset, pygame.Surface)
        
        # Cache size should remain the same
        final_cache_size = len(ui_renderer._ui_assets)
        self.assertEqual(initial_cache_size, final_cache_size)
    
    def test_memory_usage(self):
        """Test memory usage of UI assets."""
        import sys
        
        # Get initial memory usage
        initial_memory = sys.getsizeof(pygame.Surface((1, 1)))
        
        # Create UI renderer
        ui_renderer = UIRenderer(self.screen, 32)
        
        # Calculate approximate memory usage
        total_memory = 0
        for asset_type, asset in ui_renderer._ui_assets.items():
            width, height = asset.get_size()
            # Approximate memory usage: width * height * 4 bytes (RGBA)
            asset_memory = width * height * 4
            total_memory += asset_memory
        
        # Total memory should be reasonable (< 1MB for all UI assets)
        self.assertLess(total_memory, 1024 * 1024, f"UI assets using {total_memory} bytes, should be < 1MB")

if __name__ == "__main__":
    unittest.main()
