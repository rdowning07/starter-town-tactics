#!/usr/bin/env python3
"""
Tests for the asset viewer functionality.
"""

import os

# Import the viewer class
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "scripts")
from asset_viewer import AssetViewer


class TestAssetViewer:
    """Test suite for AssetViewer class."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.viewer = AssetViewer()

        # Create basic asset structure
        (Path(self.temp_dir) / "assets" / "units" / "test_unit").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "test_tile").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "effects" / "test_effect").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "ui" / "test_ui").mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test AssetViewer initialization."""
        assert self.viewer.screen_width == 1024
        assert self.viewer.screen_height == 768
        assert self.viewer.categories == ["units", "tiles", "effects", "ui"]
        assert self.viewer.current_category == 0
        assert self.viewer.current_asset_index == 0
        assert "units" in self.viewer.assets
        assert "tiles" in self.viewer.assets
        assert "effects" in self.viewer.assets
        assert "ui" in self.viewer.assets

    def test_get_unit_assets_empty(self):
        """Test getting unit assets when none exist."""
        with patch.object(Path, "exists", return_value=False):
            assets = self.viewer._get_unit_assets()
            assert assets == []

    def test_get_unit_assets_with_files(self):
        """Test getting unit assets with actual files."""
        # Create test unit files
        unit_dir = Path(self.temp_dir) / "assets" / "units" / "knight"
        unit_dir.mkdir(parents=True, exist_ok=True)
        (unit_dir / "blue_0_0.png").touch()
        (unit_dir / "red_1_0.png").touch()

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "iterdir", return_value=[unit_dir]):
                assets = self.viewer._get_unit_assets()
                assert len(assets) == 2
                assert any("knight" in asset[0] for asset in assets)

    def test_get_tile_assets_empty(self):
        """Test getting tile assets when none exist."""
        with patch.object(Path, "exists", return_value=False):
            assets = self.viewer._get_tile_assets()
            assert assets == []

    def test_get_tile_assets_with_files(self):
        """Test getting tile assets with actual files."""
        # Create test tile files
        tile_dir = Path(self.temp_dir) / "assets" / "tiles" / "castle"
        tile_dir.mkdir(parents=True, exist_ok=True)
        (tile_dir / "castle.png").touch()
        (tile_dir / "wall.png").touch()

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "iterdir", return_value=[tile_dir]):
                assets = self.viewer._get_tile_assets()
                assert len(assets) == 2
                assert any("castle" in asset[0] for asset in assets)

    def test_navigation_methods(self):
        """Test navigation methods."""
        # Test category navigation
        original_category = self.viewer.current_category
        self.viewer._next_category()
        assert self.viewer.current_category == (original_category + 1) % len(self.viewer.categories)

        self.viewer._previous_category()
        assert self.viewer.current_category == original_category

        # Test asset navigation (with mock assets)
        self.viewer.assets["units"] = [("test", "blue", "path")] * 3
        self.viewer.current_category = 0  # units
        self.viewer.current_asset_index = 0

        self.viewer._next_asset()
        assert self.viewer.current_asset_index == 1

        self.viewer._previous_asset()
        assert self.viewer.current_asset_index == 0

    def test_load_current_asset_none(self):
        """Test loading current asset when none exist."""
        self.viewer.assets["units"] = []
        asset = self.viewer.load_current_asset()
        assert asset is None

    def test_load_current_asset_invalid_index(self):
        """Test loading current asset with invalid index."""
        self.viewer.assets["units"] = [("test", "blue", "path")]
        self.viewer.current_asset_index = 5  # Out of bounds
        asset = self.viewer.load_current_asset()
        assert asset is None

    @patch("pygame.image.load")
    def test_load_current_asset_success(self, mock_load):
        """Test successful asset loading."""
        # Mock pygame surface with convert_alpha method
        mock_surface = MagicMock()
        mock_surface.convert_alpha.return_value = mock_surface
        mock_load.return_value = mock_surface

        self.viewer.assets["units"] = [("test", "blue", "test_path.png")]
        self.viewer.current_category = 0
        self.viewer.current_asset_index = 0

        asset = self.viewer.load_current_asset()
        assert asset == mock_surface
        mock_load.assert_called_once_with("test_path.png")
        mock_surface.convert_alpha.assert_called_once()

    def test_color_scheme(self):
        """Test color scheme initialization."""
        expected_colors = ["background", "text", "highlight", "error", "success"]
        for color_name in expected_colors:
            assert color_name in self.viewer.colors
            assert len(self.viewer.colors[color_name]) == 3  # RGB tuple

    def test_category_cycling(self):
        """Test that category cycling works correctly."""
        num_categories = len(self.viewer.categories)

        # Test forward cycling
        for i in range(num_categories + 1):
            self.viewer.current_category = i
            self.viewer._next_category()
            expected = (i + 1) % num_categories
            assert self.viewer.current_category == expected

        # Test backward cycling
        for i in range(num_categories + 1):
            self.viewer.current_category = i
            self.viewer._previous_category()
            expected = (i - 1) % num_categories
            assert self.viewer.current_category == expected


if __name__ == "__main__":
    pytest.main([__file__])
