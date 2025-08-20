"""
Game Actions - handles player input for movement and attacks with full architecture integration.
Integrated with GameState, SimRunner, TurnController, and includes validation and logging.
"""

import pygame
from typing import Optional, Tuple
from game.ui.ui_state import UIState
from game.ui.input_handler import screen_to_tile, get_unit_at_tile, calculate_movement_range, calculate_attack_targets

# @api
# @refactor
class GameActions:
    """Handles player input for movement and attacks with full architecture integration."""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def handle_mouse_click(self, event: pygame.event.Event, game_state, ui_state: UIState, tile_size: int = 32):
        """Handle mouse click events with full game state integration."""
        if not hasattr(game_state, 'sim_runner') or game_state.sim_runner.is_ai_turn():
            return  # Ignore during AI turn
        
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        
        pos = event.pos
        tile_pos = screen_to_tile(pos, tile_size)
        
        # Unit selection
        unit_id = get_unit_at_tile(game_state, tile_pos)
        if unit_id and self._is_player_unit(game_state, unit_id):
            self._select_unit(ui_state, unit_id, pos)
        elif ui_state.selected_unit:
            # Check move
            if tile_pos in ui_state.movement_tiles:
                self._move_unit(game_state, ui_state.selected_unit, tile_pos)
                ui_state.reset_selection()
            # Check attack
            elif tile_pos in ui_state.attack_targets:
                self._attack_unit(game_state, ui_state.selected_unit, tile_pos)
                ui_state.reset_selection()
            else:
                # Clicked elsewhere, deselect
                ui_state.reset_selection()
    
    def handle_action_menu_click(self, pos: Tuple[int, int], game_state, ui_state: UIState):
        """Handle clicks on action menu buttons."""
        if not ui_state.show_action_menu or not ui_state.action_menu_pos:
            return
        
        x, y = ui_state.action_menu_pos
        move_rect = pygame.Rect(x + 10, y + 10, 100, 25)
        attack_rect = pygame.Rect(x + 10, y + 45, 100, 25)
        
        if move_rect.collidepoint(pos):
            # Show movement range
            movement_range = calculate_movement_range(game_state, ui_state.selected_unit)
            ui_state.set_movement_range(movement_range)
            if self.logger:
                self.logger.log_event("movement_range_shown", {
                    "unit": ui_state.selected_unit,
                    "tiles": len(movement_range)
                })
        elif attack_rect.collidepoint(pos):
            # Show attack targets
            attack_targets = calculate_attack_targets(game_state, ui_state.selected_unit)
            ui_state.set_attack_targets(attack_targets)
            if self.logger:
                self.logger.log_event("attack_targets_shown", {
                    "unit": ui_state.selected_unit,
                    "targets": len(attack_targets)
                })
    
    def _select_unit(self, ui_state: UIState, unit_id: str, pos: Tuple[int, int]):
        """Select a unit and show action menu."""
        ui_state.select_unit(unit_id)
        ui_state.action_menu_pos = pos
        if self.logger:
            self.logger.log_event("unit_selected", {"unit": unit_id})
    
    def _move_unit(self, game_state, unit_id: str, target_tile: Tuple[int, int]):
        """Move unit with validation and logging."""
        # Pre-conditions
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return False
        
        unit_data = game_state.units.units.get(unit_id)
        if not unit_data:
            return False
        
        old_pos = (unit_data.get("x"), unit_data.get("y"))
        
        # Perform move
        unit_data["x"], unit_data["y"] = target_tile
        
        # Post-conditions
        assert unit_data["x"] == target_tile[0], "X coordinate not updated"
        assert unit_data["y"] == target_tile[1], "Y coordinate not updated"
        
        # Log the action
        if self.logger:
            self.logger.log_event("unit_moved", {
                "unit": unit_id,
                "from": old_pos,
                "to": target_tile
            })
        
        # End turn
        if hasattr(game_state, 'sim_runner'):
            game_state.sim_runner.run_turn()
        
        return True
    
    def _attack_unit(self, game_state, unit_id: str, target_tile: Tuple[int, int]):
        """Attack unit with damage validation and logging."""
        # Pre-conditions
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return False
        
        target_unit_id = get_unit_at_tile(game_state, target_tile)
        if not target_unit_id:
            return False
        
        attacker_data = game_state.units.units.get(unit_id, {})
        target_data = game_state.units.units.get(target_unit_id, {})
        
        if not attacker_data or not target_data:
            return False
        
        # Calculate damage
        damage = self._calculate_damage(attacker_data, target_data)
        old_hp = target_data.get("hp", 0)
        
        # Apply damage
        target_data["hp"] = max(0, old_hp - damage)
        
        # Post-conditions
        assert target_data["hp"] >= 0, "HP cannot be negative"
        assert target_data["hp"] <= old_hp, "HP should not increase from attack"
        
        # Check for death
        if target_data["hp"] <= 0:
            target_data["alive"] = False
            if hasattr(game_state, 'sim_runner'):
                game_state.sim_runner.mark_unit_dead(target_unit_id)
        
        # Log the action
        if self.logger:
            self.logger.log_event("unit_attacked", {
                "attacker": unit_id,
                "target": target_unit_id,
                "damage": damage,
                "target_hp_after": target_data["hp"],
                "target_died": target_data["hp"] <= 0
            })
        
        # End turn
        if hasattr(game_state, 'sim_runner'):
            game_state.sim_runner.run_turn()
        
        return True
    
    def _calculate_damage(self, attacker_data: dict, target_data: dict) -> int:
        """Calculate attack damage with validation."""
        base_damage = 5
        # Add modifiers based on unit stats, equipment, etc.
        damage = base_damage
        
        # Ensure damage is reasonable
        assert 0 <= damage <= 20, f"Damage {damage} out of reasonable range"
        return damage
    
    def _is_player_unit(self, game_state, unit_id: str) -> bool:
        """Check if unit belongs to player team."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return False
        
        unit_data = game_state.units.units.get(unit_id, {})
        return unit_data.get("team") == "player" and unit_data.get("alive", True)
