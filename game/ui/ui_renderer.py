"""
UI Renderer - renders UI elements with asset integration and architecture support.
Integrated with GameState, SimRunner, and existing asset systems.
"""

import pygame
from typing import Optional, Dict, Tuple
from game.ui.ui_state import UIState

# @api
# @refactor
class UIRenderer:
    """Render UI overlays with asset integration and architecture support."""
    
    def __init__(self, screen: pygame.Surface, tile_size: int = 32, asset_manifest: Optional[Dict] = None):
        self.screen = screen
        self.tile_size = tile_size
        self.asset_manifest = asset_manifest or {}
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Cache for placeholder assets
        self._placeholder_cache: Dict[str, pygame.Surface] = {}
        self._render_stats = {"elements_rendered": 0, "placeholders_used": 0}

    def _get_placeholder(self, key: str, creator_func, *args, **kwargs) -> pygame.Surface:
        """Get or create a placeholder asset."""
        if key not in self._placeholder_cache:
            self._placeholder_cache[key] = creator_func(*args, **kwargs)
        return self._placeholder_cache[key]

    def create_placeholder_button(self, width: int, height: int) -> pygame.Surface:
        """Create a placeholder button surface."""
        surface = pygame.Surface((width, height))
        surface.fill((100, 100, 100))  # Gray background
        pygame.draw.rect(surface, (200, 200, 200), surface.get_rect(), 2)  # Border
        return surface

    def create_placeholder_panel(self, width: int, height: int) -> pygame.Surface:
        """Create a placeholder panel surface."""
        surface = pygame.Surface((width, height))
        surface.fill((50, 50, 50))  # Dark background
        pygame.draw.rect(surface, (150, 150, 150), surface.get_rect(), 1)  # Border
        return surface

    def draw_button(self, rect: pygame.Rect, text: str, state: str = "normal", 
                   color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a button with text."""
        # Get button asset or create placeholder
        button_key = f"button_{state}"
        button_img = self._get_placeholder(button_key, self.create_placeholder_button, rect.width, rect.height)
        
        # Draw button background
        self.screen.blit(button_img, rect.topleft)
        
        # Draw text
        text_color = (255, 255, 255) if state == "normal" else (200, 200, 200)
        self.draw_text(text, rect.center, text_color)
        self._render_stats["elements_rendered"] += 1

    def draw_text(self, text: str, pos: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 255),
                  font: Optional[pygame.font.Font] = None) -> None:
        """Draw text at position."""
        if font is None:
            font = self.font
        
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=pos)
        self.screen.blit(surf, rect)

    def draw_panel(self, rect: pygame.Rect, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a panel background."""
        panel_img = self._get_placeholder("panel", self.create_placeholder_panel, rect.width, rect.height)
        self.screen.blit(panel_img, rect.topleft)

    def draw_highlight(self, rect: pygame.Rect, color: Tuple[int, int, int] = (255, 255, 0), 
                      alpha: int = 128) -> None:
        """Draw a highlight overlay."""
        highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
        highlight.fill((color[0], color[1], color[2], alpha))
        self.screen.blit(highlight, rect.topleft)

    def draw_action_menu(self, ui_state: UIState) -> None:
        """Draw the action menu."""
        if not ui_state.show_action_menu or not ui_state.action_menu_pos:
            return
        
        x, y = ui_state.action_menu_pos
        menu_width = 120
        menu_height = 80
        
        # Draw menu background
        menu_rect = pygame.Rect(x, y, menu_width, menu_height)
        self.draw_panel(menu_rect)
        
        # Draw action buttons
        actions = [("Move", (x + 10, y + 10)), ("Attack", (x + 10, y + 45))]
        
        for action_text, pos in actions:
            button_rect = pygame.Rect(pos[0], pos[1], 100, 25)
            self.draw_button(button_rect, action_text)

    def draw_hud(self, game_state, ui_state: UIState) -> None:
        """Draw the game HUD."""
        # Side panel
        panel_rect = pygame.Rect(0, 0, 200, self.screen.get_height())
        self.draw_panel(panel_rect)
        
        # Turn info
        self.draw_text(f"Turn: {getattr(game_state, 'turn_count', 0)}", (100, 20))
        
        # Current unit info
        if ui_state.selected_unit:
            self.draw_text(f"Unit: {ui_state.selected_unit}", (100, 50))
            # Get unit data from game state if available
            if hasattr(game_state, 'units') and hasattr(game_state.units, 'units'):
                unit_data = game_state.units.units.get(ui_state.selected_unit, {})
                self.draw_text(f"HP: {unit_data.get('hp', 0)}", (100, 80))
                self.draw_text(f"Team: {unit_data.get('team', 'unknown')}", (100, 110))
        
        # Game state info
        if hasattr(game_state, 'sim_runner') and game_state.sim_runner.is_ai_turn():
            self.draw_text("AI Turn", (100, 150), (255, 0, 0))
        else:
            self.draw_text("Player Turn", (100, 150), (0, 255, 0))

    def draw_tooltip(self, ui_state: UIState) -> None:
        """Draw tooltip if active."""
        if not ui_state.show_tooltip or not ui_state.tooltip_pos:
            return
        
        x, y = ui_state.tooltip_pos
        
        # Create tooltip surface
        text_surf = self.small_font.render(ui_state.tooltip_text, True, (255, 255, 255))
        padding = 5
        tooltip_width = text_surf.get_width() + padding * 2
        tooltip_height = text_surf.get_height() + padding * 2
        
        # Position tooltip (avoid going off screen)
        if x + tooltip_width > self.screen.get_width():
            x = self.screen.get_width() - tooltip_width
        if y + tooltip_height > self.screen.get_height():
            y = self.screen.get_height() - tooltip_height
        
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        
        # Draw tooltip background
        pygame.draw.rect(self.screen, (0, 0, 0, 200), tooltip_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), tooltip_rect, 1)
        
        # Draw tooltip text
        self.screen.blit(text_surf, (x + padding, y + padding))

    def draw_movement_range(self, ui_state: UIState, tile_size: int = 32) -> None:
        """Draw movement range highlights."""
        if not ui_state.show_movement_range:
            return
        
        for tile_x, tile_y in ui_state.movement_tiles:
            rect = pygame.Rect(tile_x * tile_size, tile_y * tile_size, tile_size, tile_size)
            self.draw_highlight(rect, (0, 255, 0), 64)  # Green highlight

    def draw_attack_targets(self, ui_state: UIState, tile_size: int = 32) -> None:
        """Draw attack target highlights."""
        if not ui_state.show_attack_targets:
            return
        
        for tile_x, tile_y in ui_state.attack_targets:
            rect = pygame.Rect(tile_x * tile_size, tile_y * tile_size, tile_size, tile_size)
            self.draw_highlight(rect, (255, 0, 0), 64)  # Red highlight

    def render_ui(self, game_state, ui_state: UIState) -> None:
        """Main UI rendering function with full architecture integration."""
        if ui_state.current_screen == "game":
            # Draw HUD
            self.draw_hud(game_state, ui_state)
            
            # Draw action menu
            self.draw_action_menu(ui_state)
            
            # Draw movement/attack highlights
            self.draw_movement_range(ui_state, self.tile_size)
            self.draw_attack_targets(ui_state, self.tile_size)
            
            # Draw tooltip
            self.draw_tooltip(ui_state)
            
            # Draw hover highlight (Week 1 compatibility)
            if ui_state.hovered_tile:
                x, y = ui_state.hovered_tile
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, (200, 200, 0), rect, 3)

            # Draw selected unit highlight (Week 1 compatibility)
            if ui_state.selected_unit is not None:
                # For demo, draw a red box at unit position (stub)
                # TODO: Replace with actual unit position lookup
                rect = pygame.Rect(100, 100, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, (255, 0, 0), rect, 3)

    def get_render_stats(self):
        """Get rendering statistics for validation."""
        return self._render_stats.copy()
