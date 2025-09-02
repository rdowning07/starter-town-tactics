# Standard library imports
from __future__ import annotations
from typing import Optional

# Third-party imports
# (none)

# Local imports
from core.ai.bt import BTContext
from game.game_state import GameState

class BTAdapter(BTContext):
    """
    Adapts GameState/Unit APIs to the BTContext Protocol.
    Keep this tiny and deterministic.
    """
    def __init__(self, gs: GameState, unit_id: str, target_id: Optional[str] = None):
        self.gs = gs
        self.unit_id = unit_id
        self.target_id = target_id

    # --- Conditions ---
    def enemy_in_attack_range(self) -> bool:
        u = self.gs.units.get(self.unit_id)
        if not u or not self.target_id:
            return False
        t = self.gs.units.get(self.target_id)
        if not t:
            return False
        # Manhattan range check; replace with your real range calc
        dx = abs(u.get("x", 0) - t.get("x", 0))
        dy = abs(u.get("y", 0) - t.get("y", 0))
        in_range = (dx + dy) <= u.get("attack_range", 1)
        return in_range

    def can_move(self) -> bool:
        u = self.gs.units.get(self.unit_id)
        return bool(u and self.gs.ap_manager.get_ap(self.unit_id) > 0)

    def can_attack(self) -> bool:
        u = self.gs.units.get(self.unit_id)
        return bool(u and self.gs.ap_manager.get_ap(self.unit_id) > 0)

    # --- Actions ---
    def step_move_toward(self) -> bool:
        u = self.gs.units.get(self.unit_id)
        t = self.gs.units.get(self.target_id) if self.target_id else None
        if not u or not t:
            return False
        
        # Get current positions
        ux = u.get("x", 0)
        uy = u.get("y", 0)
        tx = t.get("x", 0)
        ty = t.get("y", 0)
        
        # Single-step greedy move toward target (placeholder)
        dx = 1 if tx > ux else (-1 if tx < ux else 0)
        dy = 1 if ty > uy else (-1 if ty < uy else 0)
        
        # Prefer horizontal then vertical; use your Move command if available
        nx, ny = (ux + dx, uy) if dx != 0 else (ux, uy + dy)
        
        # For now, just update the unit's position and consume AP
        # TODO: Integrate with your actual movement system
        if self.gs.ap_manager.can_spend(self.unit_id, 1):
            if self.gs.units.update_unit_position(self.unit_id, nx, ny):
                self.gs.ap_manager.spend(self.unit_id, 1)
                return True
        return False

    def step_attack(self) -> bool:
        u = self.gs.units.get(self.unit_id)
        if not u or not self.target_id:
            return False
        t = self.gs.units.get(self.target_id)
        if not t:
            return False
        if not self.enemy_in_attack_range():
            return False
        
        # For now, just damage the target and consume AP
        # TODO: Integrate with your actual combat system
        if self.gs.ap_manager.can_spend(self.unit_id, 1):
            current_hp = t.get("hp", 10)
            new_hp = max(0, current_hp - 2)  # Simple 2 damage attack
            if self.gs.units.update_unit_hp(self.target_id, new_hp):
                self.gs.ap_manager.spend(self.unit_id, 1)
                return True
        return False
