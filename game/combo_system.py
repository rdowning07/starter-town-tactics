"""
Combo System - manages chainable combo attacks with full architecture integration.
Integrated with GameState, StatusEffects, FXManager, and includes validation and logging.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from game.status_effects import StatusEffectManager
from game.fx_manager import FXManager

# @api
# @refactor
@dataclass
class ComboStep:
    """Represents a single step in a combo sequence."""
    name: str
    action_func: Callable
    cooldown: int = 0
    description: str = ""
    fx_type: Optional[str] = None
    status_effect: Optional[str] = None
    status_duration: int = 3
    status_stacks: int = 1
    
    def execute(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Execute this combo step with validation and logging."""
        try:
            # Execute the action
            result = self.action_func(unit_id, game_state, combo_manager, **kwargs)
            
            # Apply status effect if specified
            if self.status_effect and hasattr(combo_manager, 'status_manager'):
                combo_manager.status_manager.add_effect(
                    unit_id, self.status_effect, 
                    duration=self.status_duration, 
                    stacks=self.status_stacks
                )
            
            # Trigger FX if specified
            if self.fx_type and hasattr(combo_manager, 'fx_manager'):
                unit_data = game_state.units.units.get(unit_id, {})
                if unit_data:
                    pos = (unit_data.get("x", 0) * 32, unit_data.get("y", 0) * 32)
                    combo_manager.fx_manager.trigger_fx(self.fx_type, pos)
            
            return result
        except Exception as e:
            if hasattr(combo_manager, 'logger') and combo_manager.logger:
                combo_manager.logger.log_event("combo_step_error", {
                    "unit": unit_id,
                    "step": self.name,
                    "error": str(e)
                })
            return False

class ComboManager:
    """Manages combo attacks with full architecture integration."""
    
    def __init__(self, status_manager: Optional[StatusEffectManager] = None, 
                 fx_manager: Optional[FXManager] = None, logger=None):
        self.status_manager = status_manager
        self.fx_manager = fx_manager
        self.logger = logger
        self.active_combos: Dict[str, List[ComboStep]] = {}
        self.cooldowns: Dict[str, Dict[str, int]] = {}
        self.combo_definitions = self._create_combo_definitions()
    
    def _create_combo_definitions(self) -> Dict[str, List[ComboStep]]:
        """Define standard combo sequences."""
        return {
            "basic_attack_chain": [
                ComboStep("slash", self._slash_attack, cooldown=1, 
                         description="Basic slash attack", fx_type="damage"),
                ComboStep("thrust", self._thrust_attack, cooldown=2,
                         description="Follow-up thrust", fx_type="damage"),
                ComboStep("finisher", self._finisher_attack, cooldown=3,
                         description="Combo finisher", fx_type="critical")
            ],
            "magic_chain": [
                ComboStep("fireball", self._fireball_attack, cooldown=2,
                         description="Fireball spell", fx_type="damage", 
                         status_effect="poison", status_duration=3),
                ComboStep("explosion", self._explosion_attack, cooldown=3,
                         description="Explosive finish", fx_type="critical")
            ],
            "defensive_chain": [
                ComboStep("block", self._block_action, cooldown=1,
                         description="Defensive block", status_effect="shield", 
                         status_duration=2),
                ComboStep("counter", self._counter_attack, cooldown=2,
                         description="Counter attack", fx_type="damage")
            ],
            "buff_chain": [
                ComboStep("haste", self._haste_buff, cooldown=2,
                         description="Speed buff", status_effect="haste", 
                         status_duration=4),
                ComboStep("strength", self._strength_buff, cooldown=3,
                         description="Power buff", status_effect="strength", 
                         status_duration=3)
            ]
        }
    
    def add_combo(self, unit_id: str, combo_name: str) -> bool:
        """Add a combo sequence to a unit."""
        if combo_name not in self.combo_definitions:
            if self.logger:
                self.logger.log_event("combo_unknown", {
                    "unit": unit_id,
                    "combo": combo_name
                })
            return False
        
        self.active_combos[unit_id] = self.combo_definitions[combo_name].copy()
        
        if self.logger:
            self.logger.log_event("combo_added", {
                "unit": unit_id,
                "combo": combo_name,
                "steps": len(self.active_combos[unit_id])
            })
        
        return True
    
    def remove_combo(self, unit_id: str) -> bool:
        """Remove combo from a unit."""
        if unit_id in self.active_combos:
            del self.active_combos[unit_id]
            if unit_id in self.cooldowns:
                del self.cooldowns[unit_id]
            
            if self.logger:
                self.logger.log_event("combo_removed", {
                    "unit": unit_id
                })
            return True
        return False
    
    def execute_combo(self, unit_id: str, game_state, **kwargs) -> Dict[str, Any]:
        """Execute a unit's combo sequence."""
        if unit_id not in self.active_combos:
            return {"success": False, "reason": "No active combo"}
        
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return {"success": False, "reason": "Invalid game state"}
        
        unit_data = game_state.units.units.get(unit_id)
        if not unit_data or not unit_data.get("alive", True):
            return {"success": False, "reason": "Unit not alive"}
        
        executed_steps = []
        failed_steps = []
        
        for step in self.active_combos[unit_id]:
            # Check cooldown
            unit_cooldowns = self.cooldowns.get(unit_id, {})
            if unit_cooldowns.get(step.name, 0) > 0:
                failed_steps.append(f"{step.name} (on cooldown)")
                continue
            
            # Execute step
            try:
                result = step.execute(unit_id, game_state, self, **kwargs)
                if result:
                    executed_steps.append(step.name)
                    # Set cooldown
                    if step.cooldown > 0:
                        if unit_id not in self.cooldowns:
                            self.cooldowns[unit_id] = {}
                        self.cooldowns[unit_id][step.name] = step.cooldown
                else:
                    failed_steps.append(f"{step.name} (execution failed)")
            except Exception as e:
                failed_steps.append(f"{step.name} (error: {e})")
                if self.logger:
                    self.logger.log_event("combo_step_exception", {
                        "unit": unit_id,
                        "step": step.name,
                        "error": str(e)
                    })
        
        # Log execution
        if self.logger:
            self.logger.log_event("combo_executed", {
                "unit": unit_id,
                "executed_steps": executed_steps,
                "failed_steps": failed_steps,
                "total_steps": len(self.active_combos[unit_id])
            })
        
        return {
            "success": len(executed_steps) > 0,
            "executed_steps": executed_steps,
            "failed_steps": failed_steps,
            "total_steps": len(self.active_combos[unit_id])
        }
    
    def tick_cooldowns(self):
        """Process cooldowns for all units."""
        for unit_id, cd_dict in list(self.cooldowns.items()):
            for step_name in list(cd_dict.keys()):
                cd_dict[step_name] -= 1
                if cd_dict[step_name] <= 0:
                    del cd_dict[step_name]
            
            # Clean up empty cooldown dicts
            if not cd_dict:
                del self.cooldowns[unit_id]
    
    def get_combo_status(self, unit_id: str) -> Dict[str, Any]:
        """Get combo status for a unit."""
        if unit_id not in self.active_combos:
            return {"has_combo": False}
        
        combo_steps = self.active_combos[unit_id]
        unit_cooldowns = self.cooldowns.get(unit_id, {})
        
        step_status = []
        for step in combo_steps:
            cooldown_remaining = unit_cooldowns.get(step.name, 0)
            step_status.append({
                "name": step.name,
                "description": step.description,
                "cooldown_remaining": cooldown_remaining,
                "ready": cooldown_remaining == 0
            })
        
        return {
            "has_combo": True,
            "steps": step_status,
            "total_steps": len(combo_steps),
            "ready_steps": sum(1 for step in step_status if step["ready"])
        }
    
    def get_available_combos(self) -> List[str]:
        """Get list of available combo definitions."""
        return list(self.combo_definitions.keys())
    
    # Combo Action Definitions
    def _slash_attack(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Basic slash attack."""
        # Simple damage calculation
        damage = 8
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_slash_attack", {
                "unit": unit_id,
                "damage": damage
            })
        return True
    
    def _thrust_attack(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Follow-up thrust attack."""
        damage = 12
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_thrust_attack", {
                "unit": unit_id,
                "damage": damage
            })
        return True
    
    def _finisher_attack(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Combo finisher attack."""
        damage = 20
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_finisher_attack", {
                "unit": unit_id,
                "damage": damage
            })
        return True
    
    def _fireball_attack(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Fireball spell attack."""
        damage = 15
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_fireball_attack", {
                "unit": unit_id,
                "damage": damage
            })
        return True
    
    def _explosion_attack(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Explosive finish attack."""
        damage = 25
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_explosion_attack", {
                "unit": unit_id,
                "damage": damage
            })
        return True
    
    def _block_action(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Defensive block action."""
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_block_action", {
                "unit": unit_id
            })
        return True
    
    def _counter_attack(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Counter attack after block."""
        damage = 18
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_counter_attack", {
                "unit": unit_id,
                "damage": damage
            })
        return True
    
    def _haste_buff(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Speed buff action."""
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_haste_buff", {
                "unit": unit_id
            })
        return True
    
    def _strength_buff(self, unit_id: str, game_state, combo_manager, **kwargs):
        """Strength buff action."""
        if hasattr(combo_manager, 'logger') and combo_manager.logger:
            combo_manager.logger.log_event("combo_strength_buff", {
                "unit": unit_id
            })
        return True
