"""Tests for grid overlay drawing functions."""

import pytest
import pygame

from game.grid import Grid
from game.overlay.overlay_state import OverlayState
from game.ui.grid_overlay_draw import (
    draw_attack_range,
    draw_movement_range,
    draw_terrain_overlay,
    draw_threat_zone,
)


class TestGridOverlayDraw:
    """Test grid overlay drawing functions."""

    @pytest.fixture
    def grid(self):
        """Create a test grid."""
        return Grid(3, 3)

    @pytest.fixture
    def overlay_state(self):
        """Create a test overlay state."""
        return OverlayState()

    @pytest.fixture
    def surface(self):
        """Create a test pygame surface."""
        pygame.init()
        surface = pygame.Surface((100, 100))
        yield surface
        pygame.quit()

    def test_draw_movement_range(self, surface, grid, overlay_state):
        """Test drawing movement range overlay."""
        # Add some movement tiles
        overlay_state.movement_tiles = {(1, 1), (2, 1)}
        
        # Should not raise any exceptions
        draw_movement_range(surface, grid, overlay_state)
        
        # Verify tiles were added to overlay state
        assert len(overlay_state.movement_tiles) == 2
        assert (1, 1) in overlay_state.movement_tiles
        assert (2, 1) in overlay_state.movement_tiles

    def test_draw_threat_zone(self, surface, grid, overlay_state):
        """Test drawing threat zone overlay."""
        # Add some threat tiles
        overlay_state.threat_tiles = {(0, 0), (1, 0)}
        
        # Should not raise any exceptions
        draw_threat_zone(surface, grid, overlay_state)
        
        # Verify tiles were added to overlay state
        assert len(overlay_state.threat_tiles) == 2
        assert (0, 0) in overlay_state.threat_tiles
        assert (1, 0) in overlay_state.threat_tiles

    def test_draw_attack_range(self, surface, grid, overlay_state):
        """Test drawing attack range overlay."""
        # Add some attack tiles
        overlay_state.attack_tiles = {(1, 2), (2, 2)}
        
        # Should not raise any exceptions
        draw_attack_range(surface, grid, overlay_state)
        
        # Verify tiles were added to overlay state
        assert len(overlay_state.attack_tiles) == 2
        assert (1, 2) in overlay_state.attack_tiles
        assert (2, 2) in overlay_state.attack_tiles

    def test_draw_terrain_overlay(self, surface, grid, overlay_state):
        """Test drawing terrain overlay."""
        # Add some terrain tiles
        overlay_state.terrain_tiles = {(0, 1), (0, 2)}
        
        # Should not raise any exceptions
        draw_terrain_overlay(surface, grid, overlay_state)
        
        # Verify tiles were added to overlay state
        assert len(overlay_state.terrain_tiles) == 2
        assert (0, 1) in overlay_state.terrain_tiles
        assert (0, 2) in overlay_state.terrain_tiles

    def test_draw_empty_overlays(self, surface, grid, overlay_state):
        """Test drawing overlays with empty tile sets."""
        # All tile sets should be empty initially
        assert len(overlay_state.movement_tiles) == 0
        assert len(overlay_state.threat_tiles) == 0
        assert len(overlay_state.attack_tiles) == 0
        assert len(overlay_state.terrain_tiles) == 0
        
        # Should not raise any exceptions
        draw_movement_range(surface, grid, overlay_state)
        draw_threat_zone(surface, grid, overlay_state)
        draw_attack_range(surface, grid, overlay_state)
        draw_terrain_overlay(surface, grid, overlay_state)

    def test_grid_get_tile_rect(self, grid):
        """Test that grid.get_tile_rect returns correct coordinates."""
        rect = grid.get_tile_rect(1, 1)
        assert rect == (32, 32, 32, 32)  # (x, y, width, height)
        
        rect = grid.get_tile_rect(0, 0)
        assert rect == (0, 0, 32, 32)
        
        rect = grid.get_tile_rect(2, 2)
        assert rect == (64, 64, 32, 32)

    def test_grid_get_tile_rect_out_of_bounds(self, grid):
        """Test that grid.get_tile_rect raises error for out of bounds."""
        with pytest.raises(ValueError):
            grid.get_tile_rect(-1, 0)
        
        with pytest.raises(ValueError):
            grid.get_tile_rect(0, -1)
        
        with pytest.raises(ValueError):
            grid.get_tile_rect(3, 0)  # width is 3, so 3 is out of bounds
        
        with pytest.raises(ValueError):
            grid.get_tile_rect(0, 3)  # height is 3, so 3 is out of bounds 