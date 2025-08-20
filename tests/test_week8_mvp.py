"""
Tests for Week 8 MVP functionality.
Tests camera system, input controller, and MVP game loop integration.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame
from pathlib import Path

# Import Week 8 systems
from game.camera import Camera, CameraController, initialize_camera, get_camera
from game.input_controller import InputController
from cli.mvp_game_loop import MVPGameLoop

# Import existing systems for integration tests
from game.game_state import GameState
from game.ui.ui_state import UIState


class TestCamera(unittest.TestCase):
    """Test camera system functionality."""
    
    def setUp(self):
        """Set up test camera."""
        self.screen_size = (800, 600)
        self.tile_size = 32
        self.world_size = (50, 40)
        self.camera = Camera(self.screen_size, self.tile_size, self.world_size)
    
    def test_camera_initialization(self):
        """Test camera initialization."""
        self.assertEqual(self.camera.screen_width, 800)
        self.assertEqual(self.camera.screen_height, 600)
        self.assertEqual(self.camera.tile_size, 32)
        self.assertEqual(self.camera.world_width, 50)
        self.assertEqual(self.camera.world_height, 40)
        self.assertEqual(self.camera.x, 0)
        self.assertEqual(self.camera.y, 0)
        self.assertEqual(self.camera.zoom, 1.0)
    
    def test_camera_movement(self):
        """Test camera movement and targeting."""
        # Set target
        self.camera.set_target(100, 200)
        self.assertEqual(self.camera.target_x, 100)
        self.assertEqual(self.camera.target_y, 200)
        
        # Update should move towards target
        initial_x, initial_y = self.camera.x, self.camera.y
        self.camera.update()
        
        # Should have moved towards target
        self.assertNotEqual(self.camera.x, initial_x)
        self.assertNotEqual(self.camera.y, initial_y)
        
        # After many updates, should reach target
        for _ in range(100):
            self.camera.update()
        
        self.assertAlmostEqual(self.camera.x, 100, delta=1)
        self.assertAlmostEqual(self.camera.y, 200, delta=1)
    
    def test_camera_bounds(self):
        """Test camera bounds enforcement."""
        # Try to set target outside bounds
        self.camera.set_target(-100, -100)
        self.camera.snap_to_target()
        
        # Should be clamped to bounds
        self.assertEqual(self.camera.x, 0)
        self.assertEqual(self.camera.y, 0)
        
        # Try to set target beyond max bounds
        self.camera.set_target(10000, 10000)
        self.camera.snap_to_target()
        
        # Should be clamped to max bounds
        self.assertEqual(self.camera.x, self.camera.max_x)
        self.assertEqual(self.camera.y, self.camera.max_y)
    
    def test_coordinate_transformations(self):
        """Test coordinate transformations."""
        self.camera.x = 100
        self.camera.y = 150
        
        # World to screen
        world_pos = (200, 300)
        screen_pos = self.camera.world_to_screen(world_pos)
        self.assertEqual(screen_pos, (100, 150))  # 200-100, 300-150
        
        # Screen to world
        screen_pos = (100, 150)
        world_pos = self.camera.screen_to_world(screen_pos)
        self.assertEqual(world_pos, (200.0, 300.0))  # 100+100, 150+150
    
    def test_tile_conversions(self):
        """Test tile coordinate conversions."""
        # Screen to tile
        screen_pos = (64, 96)  # 2 tiles right, 3 tiles down
        tile_pos = self.camera.screen_to_tile(screen_pos)
        self.assertEqual(tile_pos, (2, 3))
        
        # Tile to screen
        tile_pos = (2, 3)
        screen_pos = self.camera.tile_to_screen(tile_pos)
        self.assertEqual(screen_pos, (64, 96))
    
    def test_visible_tiles(self):
        """Test visible tile calculation."""
        self.camera.x = 0
        self.camera.y = 0
        
        start_x, start_y, end_x, end_y = self.camera.get_visible_tiles()
        
        # Should include screen area plus padding
        self.assertGreaterEqual(start_x, -1)  # Padding
        self.assertGreaterEqual(start_y, -1)  # Padding
        self.assertLessEqual(end_x, 50)  # World bounds
        self.assertLessEqual(end_y, 40)  # World bounds
    
    def test_center_on_tile(self):
        """Test centering camera on tile."""
        self.camera.center_on_tile(10, 15)
        self.camera.snap_to_target()
        
        # Camera should be centered on tile
        expected_x = 10 * 32 - 400  # tile_x * tile_size - screen_width/2
        expected_y = 15 * 32 - 300  # tile_y * tile_size - screen_height/2
        
        self.assertEqual(self.camera.x, max(0, expected_x))
        self.assertEqual(self.camera.y, max(0, expected_y))
    
    def test_zoom_functionality(self):
        """Test zoom functionality."""
        self.camera.set_zoom(2.0)
        self.assertEqual(self.camera.target_zoom, 2.0)
        
        # Update should move towards target zoom
        for _ in range(100):
            self.camera.update()
        
        self.assertAlmostEqual(self.camera.zoom, 2.0, delta=0.1)
        
        # Test zoom bounds
        self.camera.set_zoom(10.0)  # Above max
        self.assertEqual(self.camera.target_zoom, 5.0)  # Clamped to max
        
        self.camera.set_zoom(0.01)  # Below min
        self.assertEqual(self.camera.target_zoom, 0.1)  # Clamped to min


class TestCameraController(unittest.TestCase):
    """Test camera controller functionality."""
    
    def setUp(self):
        """Set up test camera controller."""
        self.camera = Camera((800, 600), 32, (50, 40))
        self.controller = CameraController(self.camera)
    
    def test_controller_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.camera, self.camera)
        self.assertIsNone(self.controller.follow_target)
        self.assertEqual(self.controller.pan_speed, 64)
    
    def test_panning(self):
        """Test camera panning."""
        initial_target_x = self.camera.target_x
        initial_target_y = self.camera.target_y
        
        # Pan right
        self.controller.pan("right")
        self.assertEqual(self.camera.target_x, initial_target_x + 64)
        
        # Pan down
        self.controller.pan("down")
        self.assertEqual(self.camera.target_y, initial_target_y + 64)
        
        # Fast pan left
        self.controller.pan("left", fast=True)
        self.assertEqual(self.camera.target_x, initial_target_x + 64 - 128)
    
    def test_following(self):
        """Test unit following."""
        unit_pos = (500, 400)
        self.controller.follow_unit(unit_pos)
        
        self.assertEqual(self.controller.follow_target, unit_pos)
        self.assertEqual(self.controller.follow_offset, (0, 0))
        
        # Update should move camera towards unit
        self.controller.update()
        
        # Should have set new target
        self.assertNotEqual(self.camera.target_x, 0)
        self.assertNotEqual(self.camera.target_y, 0)
    
    def test_zoom_controls(self):
        """Test zoom controls."""
        initial_zoom = self.camera.target_zoom
        
        self.controller.zoom_in()
        self.assertGreater(self.camera.target_zoom, initial_zoom)
        
        self.controller.zoom_out()
        self.assertLess(self.camera.target_zoom, initial_zoom * 1.2)
        
        self.controller.reset_zoom()
        self.assertEqual(self.camera.target_zoom, 1.0)


class TestInputController(unittest.TestCase):
    """Test input controller functionality."""
    
    def setUp(self):
        """Set up test input controller."""
        pygame.init()
        self.game_state = GameState()
        self.ui_state = UIState()
        self.camera = Camera((800, 600), 32)
        self.input_controller = InputController(self.game_state, self.ui_state, self.camera)
    
    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()
    
    def test_controller_initialization(self):
        """Test input controller initialization."""
        self.assertEqual(self.input_controller.game_state, self.game_state)
        self.assertEqual(self.input_controller.ui_state, self.ui_state)
        self.assertEqual(self.input_controller.camera, self.camera)
        self.assertIsNotNone(self.input_controller.camera_controller)
        self.assertIsNotNone(self.input_controller.game_actions)
    
    def test_key_bindings(self):
        """Test key binding system."""
        # Test default bindings exist
        self.assertIn(pygame.K_w, self.input_controller.key_bindings)
        self.assertIn(pygame.K_SPACE, self.input_controller.key_bindings)
        self.assertIn(pygame.K_ESCAPE, self.input_controller.key_bindings)
        
        # Test custom binding
        self.input_controller.set_key_binding(pygame.K_x, "custom_action")
        self.assertEqual(self.input_controller.key_bindings[pygame.K_x], "custom_action")
    
    @patch('pygame.event.Event')
    def test_keyboard_events(self, mock_event):
        """Test keyboard event handling."""
        # Test key down event
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_w
        
        self.input_controller.handle_event(mock_event)
        self.assertIn(pygame.K_w, self.input_controller.keys_held)
        
        # Test key up event
        mock_event.type = pygame.KEYUP
        mock_event.key = pygame.K_w
        
        self.input_controller.handle_event(mock_event)
        self.assertNotIn(pygame.K_w, self.input_controller.keys_held)
    
    @patch('pygame.event.Event')
    def test_mouse_events(self, mock_event):
        """Test mouse event handling."""
        # Test mouse button down
        mock_event.type = pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)
        
        self.input_controller.handle_event(mock_event)
        self.assertIn(1, self.input_controller.mouse_buttons)
        
        # Test mouse motion
        mock_event.type = pygame.MOUSEMOTION
        mock_event.pos = (200, 150)
        
        self.input_controller.handle_event(mock_event)
        self.assertEqual(self.input_controller.mouse_pos, (200, 150))
    
    def test_feature_toggles(self):
        """Test input feature toggles."""
        # Test enabling/disabling features
        self.input_controller.enable_feature("mouse_edge_panning", False)
        self.assertFalse(self.input_controller.enable_mouse_edge_panning)
        
        self.input_controller.enable_feature("keyboard_camera", False)
        self.assertFalse(self.input_controller.enable_keyboard_camera)
        
        self.input_controller.enable_feature("gamepad", False)
        self.assertFalse(self.input_controller.enable_gamepad)
    
    def test_debug_info(self):
        """Test debug information retrieval."""
        debug_info = self.input_controller.get_debug_info()
        
        self.assertIn("keys_held", debug_info)
        self.assertIn("mouse_pos", debug_info)
        self.assertIn("camera_pos", debug_info)
        self.assertIn("selected_unit", debug_info)


class TestMVPGameLoop(unittest.TestCase):
    """Test MVP game loop functionality."""
    
    def setUp(self):
        """Set up test MVP game loop."""
        # Mock pygame to avoid actual window creation
        pygame.init = Mock()
        pygame.display.set_mode = Mock(return_value=Mock())
        pygame.display.set_caption = Mock()
        pygame.time.Clock = Mock(return_value=Mock())
        pygame.font.Font = Mock(return_value=Mock())
        
        self.game_loop = MVPGameLoop((800, 600))
    
    def tearDown(self):
        """Clean up mocks."""
        pygame.quit()
    
    @patch('cli.mvp_game_loop.TerrainValidator')
    @patch('cli.mvp_game_loop.SpriteValidator')
    @patch('cli.mvp_game_loop.AssetValidator')
    @patch('cli.mvp_game_loop.MVPDemoScene')
    def test_initialization(self, mock_demo_scene, mock_asset_validator, 
                           mock_sprite_validator, mock_terrain_validator):
        """Test MVP game loop initialization."""
        # Mock validation results
        mock_terrain_validator.return_value.validate_all_terrain.return_value = {"grass": []}
        mock_sprite_validator.return_value.validate_all_sprites.return_value = {"knight": []}
        mock_asset_validator.return_value.validate_all_assets.return_value = {"ui": []}
        mock_demo_scene.return_value.initialize.return_value = True
        
        result = self.game_loop.initialize()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.game_loop.camera)
        self.assertIsNotNone(self.game_loop.game_state)
        self.assertIsNotNone(self.game_loop.ui_state)
    
    def test_demo_scenario_creation(self):
        """Test demo scenario creation."""
        self.game_loop._create_demo_scenario()
        
        # Check game state was configured
        self.assertEqual(self.game_loop.game_state.name, "MVP Demo - Week 8")
        
        # Check units were added
        units = self.game_loop.game_state.units.get_all_units()
        self.assertGreater(len(units), 0)
        
        # Check terrain was created
        self.assertGreater(len(self.game_loop.terrain_map), 0)
    
    def test_terrain_color_mapping(self):
        """Test terrain color mapping."""
        # Test known terrain types
        grass_color = self.game_loop._get_terrain_color("grass")
        self.assertEqual(grass_color, (50, 150, 50))
        
        stone_color = self.game_loop._get_terrain_color("stone")
        self.assertEqual(stone_color, (100, 100, 100))
        
        # Test unknown terrain type
        unknown_color = self.game_loop._get_terrain_color("unknown")
        self.assertEqual(unknown_color, (80, 80, 80))
    
    def test_unit_display_data(self):
        """Test unit display data retrieval."""
        self.game_loop._create_demo_scenario()
        
        # Test existing unit
        hero_data = self.game_loop._get_unit_display_data("player_hero")
        self.assertIsNotNone(hero_data)
        self.assertIn("position", hero_data)
        self.assertIn("team", hero_data)
        
        # Test non-existent unit
        fake_data = self.game_loop._get_unit_display_data("fake_unit")
        self.assertIsNone(fake_data)


class TestGlobalCameraFunctions(unittest.TestCase):
    """Test global camera functions."""
    
    def test_camera_initialization(self):
        """Test global camera initialization."""
        camera = initialize_camera((800, 600), 32, (50, 40))
        
        self.assertIsNotNone(camera)
        self.assertEqual(camera.screen_width, 800)
        self.assertEqual(camera.screen_height, 600)
        
        # Test getter
        retrieved_camera = get_camera()
        self.assertEqual(camera, retrieved_camera)


class TestIntegration(unittest.TestCase):
    """Integration tests for Week 8 systems."""
    
    def setUp(self):
        """Set up integration test environment."""
        pygame.init()
        self.game_state = GameState()
        self.ui_state = UIState()
        self.camera = Camera((800, 600))
        self.input_controller = InputController(self.game_state, self.ui_state, self.camera)
    
    def tearDown(self):
        """Clean up pygame."""
        pygame.quit()
    
    def test_camera_ui_integration(self):
        """Test camera integration with UI state."""
        # Set UI hover tile
        self.ui_state.hover_tile((5, 7))
        
        # Convert to screen coordinates
        screen_pos = self.camera.tile_to_screen((5, 7))
        
        # Should be valid screen coordinates
        self.assertIsInstance(screen_pos, tuple)
        self.assertEqual(len(screen_pos), 2)
    
    def test_input_camera_integration(self):
        """Test input controller integration with camera."""
        # Camera should be set
        self.assertEqual(self.input_controller.camera, self.camera)
        self.assertIsNotNone(self.input_controller.camera_controller)
        
        # Test camera control through input
        initial_target_x = self.camera.target_x
        
        # Simulate camera pan action
        self.input_controller._handle_action("camera_right", True)
        
        # Camera target should have moved
        self.assertGreater(self.camera.target_x, initial_target_x)
    
    def test_game_state_integration(self):
        """Test game state integration with new systems."""
        # Add a unit to game state
        self.game_state.units.register_unit("test_unit", "player", hp=20)
        
        # Test unit exists
        self.assertTrue(self.game_state.units.is_alive("test_unit"))
        self.assertEqual(self.game_state.units.get_team("test_unit"), "player")


if __name__ == "__main__":
    unittest.main()
