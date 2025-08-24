"""
Tests for the new terrain system (TileCatalog and TerrainRenderer).
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pygame

from game.terrain_renderer import TerrainRenderer
from game.tile_catalog import TileCatalog


class TestTileCatalog(unittest.TestCase):
    """Test cases for TileCatalog."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.temp_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.temp_dir, "test_manifest.json")

    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()

    def test_tile_catalog_initialization(self):
        """Test TileCatalog initialization."""
        catalog = TileCatalog()
        self.assertIsInstance(catalog.tiles, dict)
        self.assertIsInstance(catalog.aliases, dict)
        self.assertEqual(catalog.tile_size, (32, 32))

    def test_load_manifest_file_not_found(self):
        """Test loading manifest when file doesn't exist."""
        catalog = TileCatalog("nonexistent_file.json")
        self.assertEqual(len(catalog.tiles), 0)
        self.assertEqual(len(catalog.aliases), 0)

    def test_create_placeholder_tile(self):
        """Test placeholder tile creation."""
        catalog = TileCatalog()
        placeholder = catalog.create_placeholder_tile((255, 0, 0))

        self.assertIsInstance(placeholder, pygame.Surface)
        self.assertEqual(placeholder.get_size(), (32, 32))

    def test_get_tile_count(self):
        """Test getting tile count."""
        catalog = TileCatalog()
        count = catalog.get_tile_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)

    def test_get_available_tiles(self):
        """Test getting available tile IDs."""
        catalog = TileCatalog()
        tiles = catalog.get_available_tiles()
        self.assertIsInstance(tiles, list)

    def test_get_available_aliases(self):
        """Test getting available aliases."""
        catalog = TileCatalog()
        aliases = catalog.get_available_aliases()
        self.assertIsInstance(aliases, list)

    def test_set_and_get_alias(self):
        """Test setting and getting custom aliases."""
        catalog = TileCatalog()
        catalog.set_alias("test_alias", "test_tile_id")

        mapping = catalog.get_alias_mapping()
        self.assertIn("test_alias", mapping)
        self.assertEqual(mapping["test_alias"], "test_tile_id")

    def test_get_tile_by_alias(self):
        """Test getting tile by alias."""
        catalog = TileCatalog()
        # Test with existing alias from manifest
        if catalog.aliases:
            alias_name = list(catalog.aliases.keys())[0]
            tile = catalog.get_tile_by_alias(alias_name)
            # Should return None if tile file doesn't exist, or a surface if it does
            self.assertTrue(tile is None or isinstance(tile, pygame.Surface))

    def test_get_tile_by_nonexistent_alias(self):
        """Test getting tile by nonexistent alias."""
        catalog = TileCatalog()
        tile = catalog.get_tile_by_alias("nonexistent_alias")
        self.assertIsNone(tile)


class TestTerrainRenderer(unittest.TestCase):
    """Test cases for TerrainRenderer."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.tile_catalog = TileCatalog()
        self.terrain_renderer = TerrainRenderer(self.tile_catalog)

    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()

    def test_terrain_renderer_initialization(self):
        """Test TerrainRenderer initialization."""
        self.assertIsInstance(self.terrain_renderer.tile_catalog, TileCatalog)
        self.assertIsInstance(self.terrain_renderer.terrain_mapping, dict)

    def test_default_terrain_mapping(self):
        """Test default terrain mapping."""
        expected_mapping = {
            "G": "grass",
            "F": "forest",
            "M": "stone",
            "W": "water",
            "R": "road",
            "#": "wall",
        }

        actual_mapping = self.terrain_renderer.get_terrain_mapping()
        self.assertEqual(actual_mapping, expected_mapping)

    def test_set_terrain_mapping(self):
        """Test setting custom terrain mapping."""
        custom_mapping = {"X": "custom_tile"}
        self.terrain_renderer.set_terrain_mapping(custom_mapping)

        actual_mapping = self.terrain_renderer.get_terrain_mapping()
        self.assertEqual(actual_mapping, custom_mapping)

    def test_add_terrain_mapping(self):
        """Test adding single terrain mapping."""
        self.terrain_renderer.add_terrain_mapping("X", "custom_tile")

        mapping = self.terrain_renderer.get_terrain_mapping()
        self.assertIn("X", mapping)
        self.assertEqual(mapping["X"], "custom_tile")

    def test_render_terrain_with_empty_map(self):
        """Test rendering empty terrain map."""
        surface = pygame.Surface((800, 600))
        empty_map = []

        # Should not raise any exceptions
        self.terrain_renderer.render_terrain(surface, empty_map)

    def test_render_terrain_with_simple_map(self):
        """Test rendering simple terrain map."""
        surface = pygame.Surface((800, 600))
        simple_map = [["G", "W"], ["R", "#"]]

        # Should not raise any exceptions
        self.terrain_renderer.render_terrain(surface, simple_map)

    def test_render_terrain_with_camera_offset(self):
        """Test rendering terrain with camera offset."""
        surface = pygame.Surface((800, 600))
        terrain_map = [["G", "W"], ["R", "#"]]

        # Should not raise any exceptions
        self.terrain_renderer.render_terrain(
            surface, terrain_map, camera_x=100, camera_y=50
        )

    def test_render_terrain_with_custom_tile_size(self):
        """Test rendering terrain with custom tile size."""
        surface = pygame.Surface((800, 600))
        terrain_map = [["G", "W"], ["R", "#"]]

        # Should not raise any exceptions
        self.terrain_renderer.render_terrain(surface, terrain_map, tile_size=64)


class TestTerrainSystemIntegration(unittest.TestCase):
    """Integration tests for the terrain system."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()

    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()

    def test_tile_catalog_and_renderer_integration(self):
        """Test integration between TileCatalog and TerrainRenderer."""
        catalog = TileCatalog()
        renderer = TerrainRenderer(catalog)

        # Test that they work together
        surface = pygame.Surface((800, 600))
        terrain_map = [["G", "W"], ["R", "#"]]

        # Should not raise any exceptions
        renderer.render_terrain(surface, terrain_map)

    def test_terrain_system_with_real_manifest(self):
        """Test terrain system with the actual tiles_manifest.json."""
        catalog = TileCatalog()
        renderer = TerrainRenderer(catalog)

        # Test that the system can load the real manifest
        self.assertIsInstance(catalog.tiles, dict)
        self.assertIsInstance(catalog.aliases, dict)
        self.assertIsInstance(renderer.terrain_mapping, dict)

    def test_terrain_system_performance(self):
        """Test terrain system performance with larger maps."""
        catalog = TileCatalog()
        renderer = TerrainRenderer(catalog)

        # Create a larger terrain map
        large_map = [["G"] * 20 for _ in range(20)]
        surface = pygame.Surface((800, 600))

        # Should not raise any exceptions and complete in reasonable time
        renderer.render_terrain(surface, large_map)


if __name__ == "__main__":
    unittest.main()
