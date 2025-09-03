#!/usr/bin/env python3
"""
Test fighter integration with frame-based animation system.
"""

from pathlib import Path

import pytest

from game.AnimationCatalog import AnimationCatalog
from game.UnitRenderer import UnitRenderer


class TestFighterIntegration:
    """Test fighter unit integration."""

    def test_animation_catalog_loads_fighter(self):
        """Test that AnimationCatalog can load fighter animations."""
        catalog = AnimationCatalog(Path("assets/units/_metadata/animation_metadata.json"))

        # Check that fighter unit exists
        assert catalog.has_unit("fighter")

        # Check that all expected states exist
        expected_states = [
            "idle_down",
            "idle_up",
            "idle_left",
            "idle_right",
            "walk_down",
            "walk_up",
            "walk_left",
            "walk_right",
        ]

        for state in expected_states:
            assert catalog.has_state("fighter", state), f"Missing state: {state}"

        # Check that frames were loaded
        assert len(catalog._frames) > 0, "No frames were loaded"

    def test_fighter_metadata_structure(self):
        """Test that fighter metadata has correct structure."""
        catalog = AnimationCatalog(Path("assets/units/_metadata/animation_metadata.json"))

        # Test idle animation
        idle_meta = catalog.get("fighter", "idle_down")
        assert idle_meta is not None
        assert "frame_files" in idle_meta
        assert idle_meta["frames"] == 1
        assert idle_meta["frame_duration_ms"] == 125
        assert idle_meta["loop"] is False

        # Test walk animation
        walk_meta = catalog.get("fighter", "walk_down")
        assert walk_meta is not None
        assert "frame_files" in walk_meta
        assert walk_meta["frames"] == 2
        assert walk_meta["frame_duration_ms"] == 125
        assert walk_meta["loop"] is True

    def test_unit_renderer_initialization(self):
        """Test that UnitRenderer can be initialized with fighter catalog."""
        catalog = AnimationCatalog(Path("assets/units/_metadata/animation_metadata.json"))
        renderer = UnitRenderer(catalog, tile_size=(32, 32))

        assert renderer.catalog == catalog
        assert renderer.tile_w == 32
        assert renderer.tile_h == 32

    def test_frame_loading(self):
        """Test that individual frames can be loaded."""
        catalog = AnimationCatalog(Path("assets/units/_metadata/animation_metadata.json"))

        # Test that a specific frame can be loaded
        frame_surface = catalog.get_frame("../fighter/down_stand.png")
        assert frame_surface is not None
        assert hasattr(frame_surface, "get_size")

    def test_animation_states(self):
        """Test that all fighter animation states are properly defined."""
        catalog = AnimationCatalog(Path("assets/units/_metadata/animation_metadata.json"))

        # Test all idle states
        for direction in ["down", "up", "left", "right"]:
            state = f"idle_{direction}"
            meta = catalog.get("fighter", state)
            assert meta is not None, f"Missing {state}"
            assert len(meta["frame_files"]) == 1, f"{state} should have 1 frame"

        # Test all walk states
        for direction in ["down", "up", "left", "right"]:
            state = f"walk_{direction}"
            meta = catalog.get("fighter", state)
            assert meta is not None, f"Missing {state}"
            assert len(meta["frame_files"]) == 2, f"{state} should have 2 frames"
