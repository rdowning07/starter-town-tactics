"""
Enhanced renderer that uses the asset manager for rich visual output.
"""

import pygame
from typing import Optional
from .asset_manager import AssetManager


class EnhancedRenderer:
    """Enhanced renderer with asset integration."""
    
    def __init__(self, screen: pygame.Surface, asset_manager: AssetManager, tile_size: int = 32):
        self.screen = screen
        self.assets = asset_manager
        self.tile_size = tile_size
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw(self, game_state) -> None:
        """Draw the complete game state with rich visuals."""
        # Clear screen
        self.screen.fill((12, 12, 16))
        
        # Draw terrain grid
        self._draw_terrain_grid()
        
        # Draw units with sprites
        self._draw_units(game_state)
        
        # Draw UI overlay
        self._draw_ui_overlay(game_state)
        
        # Draw debug info
        self._draw_debug_info(game_state)
    
    def _draw_terrain_grid(self) -> None:
        """Draw the terrain grid with proper tiles."""
        grid_width, grid_height = 10, 10
        
        for y in range(grid_height):
            for x in range(grid_width):
                # Try to get terrain sprite, fallback to colored rectangle
                terrain_sprite = self.assets.get_terrain_sprite("grass")
                
                if terrain_sprite:
                    # Scale sprite to tile size
                    scaled_sprite = pygame.transform.scale(terrain_sprite, (self.tile_size, self.tile_size))
                    self.screen.blit(scaled_sprite, (x * self.tile_size, y * self.tile_size))
                else:
                    # Fallback: colored rectangle
                    color = (32, 48, 32)
                    pygame.draw.rect(self.screen, color,
                                   (x * self.tile_size, y * self.tile_size,
                                    self.tile_size - 1, self.tile_size - 1))
    
    def _draw_units(self, game_state) -> None:
        """Draw units with proper sprites and animations."""
        for unit_id, unit_data in game_state.units.get_all_units().items():
            x = unit_data.get("x", 0)
            y = unit_data.get("y", 0)
            team = unit_data.get("team", "player")
            hp = unit_data.get("hp", 10)
            
            # Determine unit type (simplified - could be enhanced)
            unit_type = "knight" if team == "player" else "goblin"
            
            # Try to get unit sprite
            unit_sprite = self.assets.get_unit_sprite(unit_type, "idle")
            
            if unit_sprite:
                # Scale sprite to tile size
                scaled_sprite = pygame.transform.scale(unit_sprite, (self.tile_size, self.tile_size))
                self.screen.blit(scaled_sprite, (x * self.tile_size, y * self.tile_size))
            else:
                # Fallback: colored rectangle
                color = (80, 160, 255) if team == "player" else (200, 80, 80)
                pygame.draw.rect(self.screen, color,
                               (x * self.tile_size, y * self.tile_size,
                                self.tile_size, self.tile_size))
            
            # Draw unit ID
            text = self.small_font.render(unit_id, True, (255, 255, 255))
            self.screen.blit(text, (x * self.tile_size + 2, y * self.tile_size + 2))
            
            # Draw HP bar
            self._draw_hp_bar(x, y, hp, 10)  # Assuming max HP of 10
    
    def _draw_hp_bar(self, x: int, y: int, current_hp: int, max_hp: int) -> None:
        """Draw a health bar for a unit."""
        bar_width = self.tile_size - 4
        bar_height = 4
        bar_x = x * self.tile_size + 2
        bar_y = y * self.tile_size + self.tile_size - 6
        
        # Background
        pygame.draw.rect(self.screen, (64, 64, 64),
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_ratio = current_hp / max_hp
        fill_width = int(bar_width * health_ratio)
        
        if health_ratio > 0.5:
            color = (0, 255, 0)  # Green
        elif health_ratio > 0.25:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
        
        if fill_width > 0:
            pygame.draw.rect(self.screen, color,
                           (bar_x, bar_y, fill_width, bar_height))
    
    def _draw_ui_overlay(self, game_state) -> None:
        """Draw UI overlay with game information."""
        # Draw panel background
        panel_width = 200
        panel_height = 150
        panel_x = self.screen.get_width() - panel_width - 10
        panel_y = 10
        
        # Try to get UI panel sprite
        panel_sprite = self.assets.get_ui_element("menu_bg")
        if panel_sprite:
            scaled_panel = pygame.transform.scale(panel_sprite, (panel_width, panel_height))
            self.screen.blit(scaled_panel, (panel_x, panel_y))
        else:
            # Fallback: colored rectangle
            pygame.draw.rect(self.screen, (32, 32, 48),
                           (panel_x, panel_y, panel_width, panel_height))
            pygame.draw.rect(self.screen, (128, 128, 128),
                           (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw game info
        y_offset = panel_y + 10
        info_lines = [
            f"Turn: {game_state.sim_runner.turn_count}",
            f"Phase: {game_state.sim_runner.phase}",
            f"Current: {game_state.turn_controller.get_current_unit()}",
            f"Player HP: {game_state.units.get_hp('player1') or 0}",
            f"Enemy HP: {game_state.units.get_hp('enemy1') or 0}",
        ]
        
        for line in info_lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 25
    
    def _draw_debug_info(self, game_state) -> None:
        """Draw debug information."""
        debug_lines = [
            f"Units: {len(game_state.units.get_all_units())}",
            f"Turn Controller Units: {len(game_state.turn_controller.units)}",
            f"Assets Loaded: {len(self.assets.images)} images, {len(self.assets.sounds)} sounds",
        ]
        
        y_offset = 10
        for line in debug_lines:
            text = self.small_font.render(line, True, (128, 128, 128))
            self.screen.blit(text, (10, y_offset))
            y_offset += 18
