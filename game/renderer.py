# game/renderer.py
# @api: provides rendering for tiles, units, and overlays using pygame
# @refactor: will expand to include animation, UI, and FX layers

import pygame
from typing import TYPE_CHECKING, Optional
from game.overlay.overlay_state import OverlayState
from game.grid import Grid
from game.tile import TILE_SIZE
from game.unit_manager import UnitManager
from game.sprite_manager import SpriteManager
from game.fx_manager import FXManager

if TYPE_CHECKING:
    from game.game_state import GameState


class Renderer:
    def __init__(self, screen: pygame.Surface, sprite_manager: SpriteManager):
        self.screen = screen
        self.sprite_manager = sprite_manager

    def render(self, game_state: "GameState", overlay_state: OverlayState, fx_manager: Optional[FXManager] = None) -> None:
        """Main render entrypoint per frame."""
        self.screen.fill((0, 0, 0))  # Clear screen

        # Get screen shake offset from FX manager
        offset_x, offset_y = 0, 0
        if fx_manager:
            offset_x, offset_y = fx_manager.get_shake_offset()

        # Create grid from terrain data if needed
        if hasattr(game_state, 'terrain_grid') and game_state.terrain_grid:
            grid = Grid.from_terrain(game_state.terrain_grid)
        else:
            # Fallback to default grid
            grid = Grid(10, 10)  # Default size

        self.render_grid(grid, offset_x, offset_y)
        self.render_overlays(grid, overlay_state, offset_x, offset_y)
        self.render_units(game_state.units, grid, offset_x, offset_y)

        pygame.display.flip()

    def render_grid(self, grid: Grid, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render the terrain grid."""
        for y in range(grid.height):
            for x in range(grid.width):
                tile = grid.get_tile(x, y)
                sprite_data = self.sprite_manager.get_terrain_sprite(tile.terrain)
                if sprite_data:
                    # Handle both file paths and pygame.Surface objects
                    if isinstance(sprite_data, str):
                        # It's a file path
                        try:
                            sprite = pygame.image.load(sprite_data)
                            adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                            self.screen.blit(sprite, adjusted_position)
                        except (pygame.error, FileNotFoundError):
                            # Fallback: draw colored rectangle
                            color = self._get_terrain_color(tile.terrain)
                            adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                            pygame.draw.rect(
                                self.screen,
                                color,
                                pygame.Rect(adjusted_position[0], adjusted_position[1], TILE_SIZE, TILE_SIZE)
                            )
                    else:
                        # It's already a pygame.Surface
                        adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                        self.screen.blit(sprite_data, adjusted_position)
                else:
                    # No sprite available, draw colored rectangle
                    color = self._get_terrain_color(tile.terrain)
                    adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                    pygame.draw.rect(
                        self.screen,
                        color,
                        pygame.Rect(adjusted_position[0], adjusted_position[1], TILE_SIZE, TILE_SIZE)
                    )

    def render_overlays(self, grid: Grid, overlay_state: OverlayState, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render movement and threat overlays."""
        # Render movement tiles
        if overlay_state.show_movement:
            for (x, y) in overlay_state.movement_tiles:
                if grid.is_within_bounds(x, y):
                    adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 255, 100),  # Blue semi-transparent
                        pygame.Rect(adjusted_position[0], adjusted_position[1], TILE_SIZE, TILE_SIZE),
                        width=2,
                    )
        
        # Render threat tiles
        if overlay_state.show_threat:
            for (x, y) in overlay_state.threat_tiles:
                if grid.is_within_bounds(x, y):
                    adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                    pygame.draw.rect(
                        self.screen,
                        (255, 0, 0, 100),  # Red semi-transparent
                        pygame.Rect(adjusted_position[0], adjusted_position[1], TILE_SIZE, TILE_SIZE),
                        width=2,
                    )

    def render_units(self, unit_manager: UnitManager, grid: Grid, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render all living units."""
        # Scan the grid for placed units
        for y in range(grid.height):
            for x in range(grid.width):
                tile = grid.get_tile(x, y)
                if tile.unit and tile.unit.is_alive():
                    # This is a Unit object with x, y coordinates
                    unit = tile.unit
                    sprite_data = self.sprite_manager.get_unit_sprite(unit.name)
                    if sprite_data:
                        # Handle both file paths and pygame.Surface objects
                        if isinstance(sprite_data, str):
                            # It's a file path
                            try:
                                sprite = pygame.image.load(sprite_data)
                                adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                                self.screen.blit(sprite, adjusted_position)
                            except (pygame.error, FileNotFoundError):
                                # Fallback: draw colored circle
                                color = (255, 255, 0) if unit.team == "player" else (255, 0, 0)
                                center = (x * TILE_SIZE + TILE_SIZE // 2 + offset_x, y * TILE_SIZE + TILE_SIZE // 2 + offset_y)
                                pygame.draw.circle(self.screen, color, center, TILE_SIZE // 3)
                        else:
                            # It's already a pygame.Surface
                            adjusted_position = (x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y)
                            self.screen.blit(sprite_data, adjusted_position)
                    else:
                        # No sprite available, draw colored circle
                        color = (255, 255, 0) if unit.team == "player" else (255, 0, 0)
                        center = (x * TILE_SIZE + TILE_SIZE // 2 + offset_x, y * TILE_SIZE + TILE_SIZE // 2 + offset_y)
                        pygame.draw.circle(self.screen, color, center, TILE_SIZE // 3)
                    
                    # Also check if this unit exists in UnitManager for additional data
                    if unit_manager.unit_exists(unit.name):
                        unit_data = unit_manager.get_all_units()[unit.name]
                        # Could render HP/AP indicators here
                        self._render_unit_indicators(x, y, unit_data)

    def _render_unit_indicators(self, x: int, y: int, unit_data: dict, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render unit status indicators (HP, AP, etc.)."""
        # Render HP bar
        hp = unit_data.get("hp", 0)
        max_hp = 10  # TODO: Make this configurable
        hp_ratio = hp / max_hp if max_hp > 0 else 0
        
        # HP bar background
        bar_width = TILE_SIZE - 4
        bar_height = 4
        bar_x = x * TILE_SIZE + 2
        bar_y = y * TILE_SIZE + 2
        
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),  # Red background
            pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        )
        
        # HP bar fill
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            pygame.draw.rect(
                self.screen,
                (0, 255, 0),  # Green fill
                pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            )

    def _get_terrain_color(self, terrain: str) -> tuple[int, int, int]:
        """Get color for terrain type."""
        terrain_colors = {
            "G": (34, 139, 34),    # Forest green
            "F": (0, 100, 0),      # Dark green
            "W": (0, 191, 255),    # Deep sky blue
            "R": (139, 69, 19),    # Saddle brown
            "M": (105, 105, 105),  # Dim gray
        }
        return terrain_colors.get(terrain, (128, 128, 128))  # Default gray

    def _get_unit_position(self, unit_id: str, grid: Grid) -> tuple[int | None, int | None]:
        """Get unit position from grid or other source."""
        # This method is now deprecated since we scan the grid directly
        # Keeping for backward compatibility
        for y in range(grid.height):
            for x in range(grid.width):
                tile = grid.get_tile(x, y)
                if tile.unit and tile.unit.name == unit_id:
                    return x, y
        return None, None

# game/renderer.py

def draw_unit(self, unit, surface):
    sprite = self.sprite_manager.get_sprite(
        unit.sprite_name,
        unit.current_animation,
        unit.animation_frame
    )
    surface.blit(sprite, unit.position)
