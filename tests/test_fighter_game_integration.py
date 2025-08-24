#!/usr/bin/env python3
"""
Test fighter integration with the main game architecture.
"""

from pathlib import Path

import pytest

from game.AnimationCatalog import AnimationCatalog
from game.grid import Grid
from game.renderer import Renderer
from game.sprite_manager import SpriteManager
from game.unit import Unit
from game.unit_manager import UnitManager
from game.UnitRenderer import UnitRenderer


class TestFighterGameIntegration:
    """Test fighter unit integration with main game systems."""

    def test_sprite_manager_fighter_support(self):
        """Test that SpriteManager can load and provide fighter sprites."""
        sprite_manager = SpriteManager()
        sprite_manager.load_assets()

        # Test that fighter animations are loaded
        assert sprite_manager.animation_catalog is not None
        assert sprite_manager.animation_catalog.has_unit("fighter")

        # Test that fighter sprites can be retrieved
        fighter_sprite = sprite_manager.get_unit_sprite("fighter", state="idle_down")
        assert fighter_sprite is not None

    def test_renderer_fighter_support(self):
        """Test that Renderer can render fighter units."""
        import pygame

        pygame.init()

        screen = pygame.Surface((800, 600))
        sprite_manager = SpriteManager()
        sprite_manager.load_assets()

        renderer = Renderer(screen, sprite_manager)

        # Create a grid with a fighter unit
        grid = Grid(5, 5)
        unit = Unit("fighter_1", "player", 2, 2)
        grid.get_tile(2, 2).unit = unit

        # Create unit manager
        unit_manager = UnitManager()
        unit_manager.register_unit("fighter_1", "player", hp=10)

        # Test that rendering doesn't crash
        try:
            renderer.render_units(unit_manager, grid)
            assert True  # If we get here, rendering succeeded
        except Exception as e:
            pytest.fail(f"Renderer failed to render fighter: {e}")

        pygame.quit()

    def test_unit_manager_fighter_registration(self):
        """Test that UnitManager can handle fighter units."""
        unit_manager = UnitManager()

        # Register fighter units
        unit_manager.register_unit("fighter_1", "player", hp=10)
        unit_manager.register_unit("fighter_2", "enemy", hp=8)

        # Verify registration
        assert unit_manager.get_team("fighter_1") == "player"
        assert unit_manager.get_hp("fighter_1") == 10
        assert unit_manager.get_team("fighter_2") == "enemy"
        assert unit_manager.get_hp("fighter_2") == 8

        # Test damage/healing
        unit_manager.damage_unit("fighter_1", 3)
        assert unit_manager.get_hp("fighter_1") == 7

        unit_manager.heal_unit("fighter_1", 2)
        assert unit_manager.get_hp("fighter_1") == 9

    def test_fighter_animation_states(self):
        """Test that all fighter animation states work."""
        catalog = AnimationCatalog(
            Path("assets/units/_metadata/animation_metadata.json")
        )

        # Test all animation states
        states = [
            "idle_down",
            "idle_up",
            "idle_left",
            "idle_right",
            "walk_down",
            "walk_up",
            "walk_left",
            "walk_right",
        ]

        for state in states:
            meta = catalog.get("fighter", state)
            assert meta is not None, f"Missing animation state: {state}"
            assert "frame_files" in meta, f"State {state} missing frame_files"
            assert len(meta["frame_files"]) > 0, f"State {state} has no frames"

    def test_fighter_integration_workflow(self):
        """Test the complete fighter integration workflow."""
        # 1. Load animation catalog
        catalog = AnimationCatalog(
            Path("assets/units/_metadata/animation_metadata.json")
        )
        assert catalog.has_unit("fighter")

        # 2. Create unit renderer
        renderer = UnitRenderer(catalog, tile_size=(32, 32))

        # 3. Create sprite manager
        sprite_manager = SpriteManager()
        sprite_manager.load_assets()

        # 4. Create unit manager
        unit_manager = UnitManager()
        unit_manager.register_unit("fighter_1", "player", hp=10)

        # 5. Create grid with fighter
        grid = Grid(5, 5)
        unit = Unit("fighter_1", "player", 2, 2)
        grid.get_tile(2, 2).unit = unit

        # 6. Test that everything works together
        import pygame

        pygame.init()
        screen = pygame.Surface((800, 600))

        # Test sprite retrieval
        fighter_sprite = sprite_manager.get_unit_sprite("fighter", state="idle_down")
        assert fighter_sprite is not None

        # Test rendering
        game_renderer = Renderer(screen, sprite_manager)
        try:
            game_renderer.render_units(unit_manager, grid)
            assert True  # Success
        except Exception as e:
            pytest.fail(f"Integration workflow failed: {e}")

        pygame.quit()

    def test_fighter_metadata_structure(self):
        """Test that fighter metadata has the correct structure for game integration."""
        catalog = AnimationCatalog(
            Path("assets/units/_metadata/animation_metadata.json")
        )

        # Test fighter metadata
        fighter_meta = catalog._units.get("fighter", {})
        assert "idle_down" in fighter_meta
        assert "walk_down" in fighter_meta

        # Test metadata structure
        idle_meta = fighter_meta["idle_down"]
        assert "frame_files" in idle_meta
        assert "frames" in idle_meta
        assert "frame_duration_ms" in idle_meta
        assert "origin" in idle_meta
        assert "loop" in idle_meta

        # Test that frames are accessible
        frame_files = idle_meta["frame_files"]
        assert len(frame_files) > 0
        assert all(isinstance(f, str) for f in frame_files)
