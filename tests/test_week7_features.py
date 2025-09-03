"""
Unit tests for Week 7 features.
Tests terrain validation, sprite validation, animation management, and MVP demo scene.
"""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pygame

from game.animation_manager import Animation, AnimationManager, get_animation_manager
from game.asset_validator import AssetValidationResult
from game.sprite_validator import SpriteValidator, validate_sprites
from game.terrain_validator import TerrainValidator, validate_terrain

# Initialize pygame for testing
pygame.init()


class TestWeek7Features(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.terrain_dir = self.assets_dir / "terrain"
        self.units_dir = self.assets_dir / "units"

        # Create directory structure
        self.terrain_dir.mkdir(parents=True)
        self.units_dir.mkdir(parents=True)

        # Create test terrain directories
        for terrain_type in ["grass", "stone", "water"]:
            (self.terrain_dir / terrain_type).mkdir()

        # Create test unit directories
        for unit_type in ["knight", "mage", "archer"]:
            (self.units_dir / unit_type).mkdir()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    # Terrain Validator Tests
    def test_terrain_validator_initialization(self):
        """Test TerrainValidator initialization."""
        validator = TerrainValidator(self.terrain_dir)

        self.assertEqual(validator.asset_dir, self.terrain_dir)
        self.assertEqual(validator.expected_tile_size, (32, 32))
        self.assertIn("grass", validator.terrain_types)
        self.assertIn("stone", validator.terrain_types)

    def test_terrain_validation_result(self):
        """Test AssetValidationResult for terrain."""
        result = AssetValidationResult("test/path.png")

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

        result.add_error("Test error")

        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Test error")

    @patch("pygame.image.load")
    @patch("pathlib.Path.stat")
    @patch("pathlib.Path.mkdir")
    def test_terrain_file_validation(self, mock_mkdir, mock_stat, mock_image_load):
        """Test terrain file validation."""
        # Mock image
        mock_img = Mock()
        mock_img.get_size.return_value = (32, 32)
        mock_img.get_alpha.return_value = None
        mock_image_load.return_value = mock_img

        # Mock file stats with proper attributes
        mock_stat_obj = Mock()
        mock_stat_obj.st_size = 1024  # 1KB file
        mock_stat_obj.st_mode = 0o644  # Regular file mode
        mock_stat.return_value = mock_stat_obj

        # Mock directory creation
        mock_mkdir.return_value = None

        validator = TerrainValidator(self.terrain_dir)
        result = AssetValidationResult("test.png")

        validator._validate_terrain_file(Path("test.png"), "grass", result)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.metadata["resolution"], (32, 32))
        self.assertEqual(result.metadata["terrain_type"], "grass")

    @patch("pygame.image.load")
    def test_terrain_file_validation_wrong_size(self, mock_image_load):
        """Test terrain file validation with wrong size."""
        # Mock image with wrong size
        mock_img = Mock()
        mock_img.get_size.return_value = (64, 64)  # Wrong size
        mock_img.get_alpha.return_value = None
        mock_image_load.return_value = mock_img

        validator = TerrainValidator(self.terrain_dir)
        result = AssetValidationResult("test.png")

        validator._validate_terrain_file(Path("test.png"), "grass", result)

        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

    def test_terrain_validation_missing_directory(self):
        """Test terrain validation with missing directory."""
        validator = TerrainValidator(Path("nonexistent"))
        results = validator.validate_all_terrain()

        self.assertEqual(len(results), 0)

    def test_terrain_csv_generation(self):
        """Test terrain CSV report generation."""
        validator = TerrainValidator(self.terrain_dir)

        # Create some test results
        results = {"grass": [AssetValidationResult("grass.png"), AssetValidationResult("grass_edge.png")]}

        # Add metadata to results
        results["grass"][0].metadata["resolution"] = (32, 32)
        results["grass"][0].metadata["has_transparency"] = False
        results["grass"][0].metadata["file_size_mb"] = 0.1

        validator._generate_terrain_csv(results)

        csv_file = validator.qa_report_dir / "terrain_report.csv"
        self.assertTrue(csv_file.exists())

    # Sprite Validator Tests
    def test_sprite_validator_initialization(self):
        """Test SpriteValidator initialization."""
        validator = SpriteValidator(self.units_dir)

        self.assertEqual(validator.asset_dir, self.units_dir)
        self.assertEqual(validator.expected_frame_size, (64, 64))
        self.assertIn("knight", validator.unit_types)
        self.assertIn("mage", validator.unit_types)

    def test_sprite_sheet_validation(self):
        """Test sprite sheet validation."""
        # Create a real sprite sheet surface (192x64 = 3 frames)
        sprite_sheet = pygame.Surface((192, 64))
        sprite_sheet.fill((255, 255, 255))  # White background

        # Save it to a temporary file
        sprite_file = self.units_dir / "knight" / "idle.png"
        sprite_file.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(sprite_sheet, str(sprite_file))

        validator = SpriteValidator(self.units_dir)
        result = AssetValidationResult("test.png")

        validator._validate_sprite_sheet(sprite_file, "knight", "idle", result)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.metadata["frame_count"], 3)
        self.assertEqual(result.metadata["unit_type"], "knight")
        self.assertEqual(result.metadata["animation_type"], "idle")

    @patch("pygame.image.load")
    def test_sprite_sheet_validation_wrong_size(self, mock_image_load):
        """Test sprite sheet validation with wrong size."""
        # Mock sprite sheet with wrong height
        mock_img = Mock()
        mock_img.get_size.return_value = (192, 128)  # Wrong height
        mock_img.get_alpha.return_value = None
        mock_image_load.return_value = mock_img

        validator = SpriteValidator(self.units_dir)
        result = AssetValidationResult("test.png")

        validator._validate_sprite_sheet(Path("test.png"), "knight", "idle", result)

        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)

    def test_sprite_sheet_slicing(self):
        """Test sprite sheet frame slicing."""
        # Create a mock sprite sheet surface
        sheet = pygame.Surface((192, 64))  # 3 frames of 64x64
        sheet.fill((255, 0, 0))  # Red background

        validator = SpriteValidator(self.units_dir)
        frames = validator._slice_sprite_sheet(sheet, 3)

        self.assertEqual(len(frames), 3)
        for frame in frames:
            self.assertEqual(frame.get_size(), (64, 64))

    def test_frame_validation(self):
        """Test individual frame validation."""
        # Create test frames
        frames = []
        for i in range(3):
            frame = pygame.Surface((64, 64))
            frame.fill((i * 50, i * 50, i * 50))  # Different colors
            frames.append(frame)

        validator = SpriteValidator(self.units_dir)
        validation = validator._validate_frames(frames, "knight", "idle")

        self.assertEqual(validation["total_frames"], 3)
        self.assertEqual(validation["valid_frames"], 3)
        self.assertEqual(len(validation["frame_issues"]), 0)

    def test_animation_consistency_check(self):
        """Test animation consistency checking."""
        # Create frames with different colors
        frames = []
        for i in range(3):
            frame = pygame.Surface((64, 64))
            frame.fill((i * 100, i * 100, i * 100))  # Very different colors
            frames.append(frame)

        validator = SpriteValidator(self.units_dir)
        consistency = validator._check_animation_consistency(frames)

        # Should detect large color changes
        self.assertFalse(consistency["consistent"])
        self.assertGreater(len(consistency["issues"]), 0)

    # Animation Manager Tests
    def test_animation_initialization(self):
        """Test Animation initialization."""
        # Create test frames
        frames = []
        for i in range(3):
            frame = pygame.Surface((64, 64))
            frame.fill((255, 255, 255))
            frames.append(frame)

        animation = Animation(frames, 100, "test_anim")

        self.assertEqual(animation.name, "test_anim")
        self.assertEqual(animation.frame_count, 3)
        self.assertEqual(animation.frame_time, 100)
        self.assertTrue(animation.valid)
        self.assertTrue(animation.playing)

    def test_animation_validation(self):
        """Test animation validation."""
        # Create frames with different sizes (invalid)
        frames = []
        for i in range(3):
            frame = pygame.Surface((64 + i, 64))  # Different widths
            frame.fill((255, 255, 255))
            frames.append(frame)

        animation = Animation(frames, 100, "test_anim")

        self.assertFalse(animation.valid)
        self.assertGreater(len(animation.frame_errors), 0)

    def test_animation_update(self):
        """Test animation frame updating."""
        # Create test frames
        frames = []
        for i in range(3):
            frame = pygame.Surface((64, 64))
            frame.fill((255, 255, 255))
            frames.append(frame)

        animation = Animation(frames, 100, "test_anim")

        # Update animation
        animation.update(50)  # Half frame time
        self.assertEqual(animation.index, 0)

        animation.update(100)  # Full frame time
        self.assertEqual(animation.index, 1)

    def test_animation_manager_initialization(self):
        """Test AnimationManager initialization."""
        manager = AnimationManager()

        self.assertEqual(len(manager.animations), 0)
        self.assertEqual(manager.qa_data["total_animations"], 0)
        self.assertEqual(manager.qa_data["valid_animations"], 0)

    def test_animation_loading(self):
        """Test animation loading."""
        # Create a real sprite sheet surface
        sprite_sheet = pygame.Surface((192, 64))
        sprite_sheet.fill((255, 255, 255))  # White background

        # Save it to a temporary file
        sprite_file = self.units_dir / "knight" / "idle.png"
        sprite_file.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(sprite_sheet, str(sprite_file))

        manager = AnimationManager()
        success = manager.load_animation("knight_idle", sprite_file, 200)

        self.assertTrue(success)
        self.assertIn("knight_idle", manager.animations)
        self.assertEqual(manager.qa_data["total_animations"], 1)

    def test_animation_manager_qa_report(self):
        """Test animation manager QA reporting."""
        manager = AnimationManager()

        # Create test animation
        frames = []
        for i in range(2):
            frame = pygame.Surface((64, 64))
            frame.fill((255, 255, 255))
            frames.append(frame)

        animation = Animation(frames, 100, "test_anim")
        manager.animations["test_anim"] = animation

        qa_report = manager.get_qa_report()

        self.assertIn("summary", qa_report)
        self.assertIn("animations", qa_report)
        self.assertIn("test_anim", qa_report["animations"])

    def test_global_animation_manager(self):
        """Test global animation manager functions."""
        # Test global manager access
        manager1 = get_animation_manager()
        manager2 = get_animation_manager()

        self.assertIs(manager1, manager2)  # Should be same instance

    # MVP Demo Scene Tests
    def test_mvp_demo_scene_initialization(self):
        """Test MVPDemoScene initialization."""
        from cli.mvp_demo_scene import MVPDemoScene

        demo = MVPDemoScene()

        self.assertEqual(demo.screen_size, (800, 600))
        self.assertEqual(demo.tile_size, 32)
        self.assertEqual(demo.grid_width, 25)  # 800 // 32
        self.assertEqual(demo.grid_height, 18)  # 600 // 32
        self.assertEqual(demo.current_terrain_type, "grass")
        self.assertEqual(demo.current_unit_type, "knight")

    def test_mvp_demo_asset_loading(self):
        """Test MVP demo asset loading."""
        from cli.mvp_demo_scene import MVPDemoScene

        demo = MVPDemoScene()

        # Test terrain loading
        demo._load_terrain_tiles()
        # Should handle missing terrain gracefully

        # Test unit loading
        demo._load_unit_sprites()
        # Should handle missing units gracefully

        # Test animation loading
        demo._load_animations()
        # Should handle missing animations gracefully

    def test_mvp_demo_cycling(self):
        """Test MVP demo asset cycling."""
        from cli.mvp_demo_scene import MVPDemoScene

        demo = MVPDemoScene()

        # Add some test assets
        demo.terrain_tiles = {"grass": None, "stone": None, "water": None}
        demo.unit_sprites = {"knight": None, "mage": None, "archer": None}

        # Test terrain cycling
        original_terrain = demo.current_terrain_type
        demo._cycle_terrain(1)
        self.assertNotEqual(demo.current_terrain_type, original_terrain)

        # Test unit cycling
        original_unit = demo.current_unit_type
        demo._cycle_unit(1)
        self.assertNotEqual(demo.current_unit_type, original_unit)

    def test_mvp_demo_qa_report_generation(self):
        """Test MVP demo QA report generation."""
        from cli.mvp_demo_scene import MVPDemoScene

        demo = MVPDemoScene()

        # Mock validation results
        terrain_results = {"grass": [AssetValidationResult("grass.png")]}
        sprite_results = {"knight": [AssetValidationResult("knight.png")]}
        asset_results = {"terrain": [AssetValidationResult("test.png")]}

        # Should not crash
        demo._generate_qa_report(terrain_results, sprite_results, asset_results)

    # Integration Tests
    def test_terrain_sprite_integration(self):
        """Test integration between terrain and sprite validation."""
        terrain_validator = TerrainValidator(self.terrain_dir)
        sprite_validator = SpriteValidator(self.units_dir)

        # Both should handle missing directories gracefully
        terrain_results = terrain_validator.validate_all_terrain()
        sprite_results = sprite_validator.validate_all_sprites()

        # Should return results for all defined terrain types (even if missing)
        # Terrain validator validates all 8 defined terrain types
        self.assertEqual(len(terrain_results), 8)
        # Sprite validator validates all 5 defined unit types
        self.assertEqual(len(sprite_results), 5)

    def test_animation_validation_integration(self):
        """Test integration between sprite validation and animation manager."""
        sprite_validator = SpriteValidator(self.units_dir)
        animation_manager = AnimationManager(sprite_validator)

        # Should work together without errors
        sprite_results = sprite_validator.validate_all_sprites()
        animation_qa = animation_manager.get_qa_report()

        self.assertIsInstance(sprite_results, dict)
        self.assertIsInstance(animation_qa, dict)

    def test_asset_validation_pipeline(self):
        """Test complete asset validation pipeline."""
        from game.asset_validator import AssetValidator

        asset_validator = AssetValidator(self.assets_dir)
        terrain_validator = TerrainValidator(self.terrain_dir)
        sprite_validator = SpriteValidator(self.units_dir)

        # All validators should work together
        asset_results = asset_validator.validate_all_assets()
        terrain_results = terrain_validator.validate_all_terrain()
        sprite_results = sprite_validator.validate_all_sprites()

        # Should all return results (even if empty)
        self.assertIsInstance(asset_results, dict)
        self.assertIsInstance(terrain_results, dict)
        self.assertIsInstance(sprite_results, dict)


if __name__ == "__main__":
    unittest.main()
