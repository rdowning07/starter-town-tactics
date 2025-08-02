#!/usr/bin/env python3
"""
Tests for the comprehensive asset validation system.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the validator class
import sys
sys.path.insert(0, 'scripts')
from validate_assets import AssetValidator


class TestAssetValidator:
    """Test suite for AssetValidator class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = AssetValidator(self.temp_dir)
        
        # Create basic directory structure
        (Path(self.temp_dir) / "assets" / "units").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "castle").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "desert").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "dungeon").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "house").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "interior").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "village").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "terrain").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "water").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "worldmap").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "ui" / "cursors").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "ui" / "icons").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "ui" / "panels").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "effects" / "particles").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "effects" / "summoning").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "effects" / "aura").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "data").mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_directory_structure_success(self):
        """Test successful directory structure validation."""
        result = self.validator.validate_directory_structure()
        assert result is True
        assert len(self.validator.errors) == 0
        assert len(self.validator.info) > 0
    
    def test_validate_directory_structure_missing_dirs(self):
        """Test directory structure validation with missing directories."""
        # Remove a required directory
        import shutil
        shutil.rmtree(Path(self.temp_dir) / "assets" / "tiles" / "castle")
        
        result = self.validator.validate_directory_structure()
        assert result is False
        assert len(self.validator.errors) > 0
        assert "castle" in str(self.validator.errors[0])
    
    def test_validate_asset_tracker_success(self):
        """Test successful asset tracker validation."""
        # Create a valid assets tracker
        tracker_path = Path(self.temp_dir) / "data" / "assets_tracker.csv"
        tracker_content = """asset_path,asset_type,unit_type,team_variant,status,license,source,notes
assets/tiles/castle/castle.png,tile,castle,castle,actual,CC0,game_assets,Test tile
assets/tiles/desert/desert.png,tile,desert,desert,actual,CC0,game_assets,Test tile"""
        
        with open(tracker_path, 'w', encoding='utf-8') as f:
            f.write(tracker_content)
        
        result = self.validator.validate_asset_tracker()
        assert result is True
        assert len(self.validator.errors) == 0
        assert len(self.validator.info) > 0
    
    def test_validate_asset_tracker_missing_file(self):
        """Test asset tracker validation with missing file."""
        result = self.validator.validate_asset_tracker()
        assert result is False
        assert len(self.validator.errors) > 0
        assert "not found" in self.validator.errors[0]
    
    def test_validate_asset_tracker_invalid_structure(self):
        """Test asset tracker validation with invalid CSV structure."""
        tracker_path = Path(self.temp_dir) / "data" / "assets_tracker.csv"
        tracker_content = """invalid_field,another_field
test,value"""
        
        with open(tracker_path, 'w', encoding='utf-8') as f:
            f.write(tracker_content)
        
        result = self.validator.validate_asset_tracker()
        assert result is False
        assert len(self.validator.errors) > 0
        assert "missing fields" in self.validator.errors[0]
    
    def test_validate_placeholder_files_success(self):
        """Test successful placeholder files validation."""
        # Create placeholder files
        placeholder_files = [
            "assets/tiles/castle/castle.png",
            "assets/tiles/desert/desert.png",
            "assets/tiles/dungeon/dungeon.png",
            "assets/tiles/house/house.png",
            "assets/tiles/interior/inside.png",
            "assets/tiles/village/outside.png",
            "assets/tiles/terrain/terrain.png",
            "assets/tiles/water/water.png",
            "assets/tiles/worldmap/world.png",
            "assets/effects/summoning/portal.png",
            "assets/effects/aura/buff.png"
        ]
        
        for file_path in placeholder_files:
            full_path = Path(self.temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
        
        result = self.validator.validate_placeholder_files()
        assert result is True
        assert len(self.validator.errors) == 0
        assert len(self.validator.info) > 0
    
    def test_validate_placeholder_files_missing(self):
        """Test placeholder files validation with missing files."""
        result = self.validator.validate_placeholder_files()
        assert result is False
        assert len(self.validator.errors) > 0
        assert "Missing placeholder files" in self.validator.errors[0]
    
    def test_validate_sprite_mapping_success(self):
        """Test successful sprite mapping validation."""
        # Create a valid sprite mapping
        mapping_path = Path(self.temp_dir) / "sprite_mapping_master.yaml"
        mapping_content = """Recruit:
  sprite: assets/units/Recruit/blue_0_0.png
  color: blue
  tier: 1
PhoenixBinder:
  sprite: assets/units/PhoenixBinder/blue_1_0.png
  color: orange
  tier: 3"""
        
        with open(mapping_path, 'w', encoding='utf-8') as f:
            f.write(mapping_content)
        
        # Create the sprite files
        (Path(self.temp_dir) / "assets" / "units" / "Recruit").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "units" / "PhoenixBinder").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "units" / "Recruit" / "blue_0_0.png").touch()
        (Path(self.temp_dir) / "assets" / "units" / "PhoenixBinder" / "blue_1_0.png").touch()
        
        result = self.validator.validate_sprite_mapping()
        assert result is True
        assert len(self.validator.errors) == 0
        assert len(self.validator.info) > 0
    
    def test_validate_sprite_mapping_missing_file(self):
        """Test sprite mapping validation with missing file."""
        result = self.validator.validate_sprite_mapping()
        assert result is True  # Should be a warning, not an error
        assert len(self.validator.warnings) > 0
        assert "not found" in self.validator.warnings[0]
    
    def test_validate_tileset_mapping_success(self):
        """Test successful tileset mapping validation."""
        # Create a valid tileset mapping
        mapping_path = Path(self.temp_dir) / "data" / "tileset_mapping.yaml"
        mapping_content = """tilesets:
- file: assets/tiles/castle/castle.png
  layer: midground
  name: castle
  tags:
  - stone
  - indoors
  - royalty
  tile_size:
  - 32
  - 32"""
        
        with open(mapping_path, 'w', encoding='utf-8') as f:
            f.write(mapping_content)
        
        # Create the tileset file
        (Path(self.temp_dir) / "assets" / "tiles" / "castle" / "castl.png").touch()
        
        result = self.validator.validate_tileset_mapping()
        assert result is True
        assert len(self.validator.errors) == 0
        assert len(self.validator.info) > 0
    
    def test_generate_asset_report(self):
        """Test asset report generation."""
        # Create some test files
        (Path(self.temp_dir) / "assets" / "units" / "test_unit").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "units" / "test_unit" / "sprite.png").touch()
        
        # Create tiles directory and file
        (Path(self.temp_dir) / "assets" / "tiles" / "test_tile").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "tiles" / "test_tile" / "tile.png").touch()
        
        result = self.validator.generate_asset_report()
        assert result is True
        assert len(self.validator.info) > 0
        assert "Asset report generated" in self.validator.info[-1]
    
    def test_validate_all_success(self):
        """Test complete validation with all components present."""
        # Set up a complete valid environment
        self._setup_complete_environment()
        
        result = self.validator.validate_all()
        assert result is True
        assert len(self.validator.errors) == 0
    
    def test_validate_all_with_warnings(self):
        """Test complete validation with warnings but no errors."""
        # Set up environment with some missing optional files
        self._setup_complete_environment()
        
        # Remove some optional sprite files to create warnings
        sprite_file = Path(self.temp_dir) / "assets" / "units" / "Recruit" / "blue_0_0.png"
        if sprite_file.exists():
            sprite_file.unlink()
        
        result = self.validator.validate_all()
        assert result is True  # Should pass with warnings
        assert len(self.validator.errors) == 0
        assert len(self.validator.warnings) > 0
    
    def _setup_complete_environment(self):
        """Set up a complete valid environment for testing."""
        # Create assets tracker
        tracker_path = Path(self.temp_dir) / "data" / "assets_tracker.csv"
        tracker_content = """asset_path,asset_type,unit_type,team_variant,status,license,source,notes
assets/tiles/castle/castle.png,tile,castle,castle,actual,CC0,game_assets,Test tile"""
        
        with open(tracker_path, 'w', encoding='utf-8') as f:
            f.write(tracker_content)
        
        # Create placeholder files
        placeholder_files = [
            "assets/tiles/castle/castle.png",
            "assets/tiles/desert/desert.png",
            "assets/tiles/dungeon/dungeon.png",
            "assets/tiles/house/house.png",
            "assets/tiles/interior/inside.png",
            "assets/tiles/village/outside.png",
            "assets/tiles/terrain/terrain.png",
            "assets/tiles/water/water.png",
            "assets/tiles/worldmap/world.png",
            "assets/effects/summoning/portal.png",
            "assets/effects/aura/buff.png"
        ]
        
        for file_path in placeholder_files:
            full_path = Path(self.temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
        
        # Create sprite mapping
        mapping_path = Path(self.temp_dir) / "sprite_mapping_master.yaml"
        mapping_content = """Recruit:
  sprite: assets/units/Recruit/blue_0_0.png
  color: blue
  tier: 1"""
        
        with open(mapping_path, 'w', encoding='utf-8') as f:
            f.write(mapping_content)
        
        # Create sprite files
        (Path(self.temp_dir) / "assets" / "units" / "Recruit").mkdir(parents=True, exist_ok=True)
        (Path(self.temp_dir) / "assets" / "units" / "Recruit" / "blue_0_0.png").touch()
        
        # Create tileset mapping
        tileset_path = Path(self.temp_dir) / "data" / "tileset_mapping.yaml"
        tileset_content = """tilesets:
- file: assets/tiles/castle/castle.png
  layer: midground
  name: castle
  tags:
  - stone
  - indoors
  - royalty
  tile_size:
  - 32
  - 32"""
        
        with open(tileset_path, 'w', encoding='utf-8') as f:
            f.write(tileset_content)


if __name__ == "__main__":
    pytest.main([__file__]) 