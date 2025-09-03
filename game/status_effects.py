"""
Status Effects System - manages buffs/debuffs with full architecture integration.
Integrated with GameState, UnitManager, and includes validation and logging.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional


# @api
# @refactor
@dataclass
class StatusEffect:
    """Represents a status effect (buff or debuff) on a unit."""

    name: str
    duration: int
    effect_type: str  # "buff", "debuff", "neutral"
    effect_func: Optional[Callable] = None
    icon: Optional[str] = None
    description: str = ""
    stacks: int = 1
    max_stacks: int = 1

    def apply_effect(self, unit_data: Dict, game_state=None):
        """Apply the effect to a unit."""
        if self.effect_func:
            self.effect_func(unit_data, game_state, self)

    def tick(self, unit_data: Dict, game_state=None):
        """Process one turn of this effect."""
        self.duration -= 1
        self.apply_effect(unit_data, game_state)
        return self.duration > 0


class StatusEffectManager:
    """Manages status effects for all units with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.unit_effects: Dict[str, List[StatusEffect]] = {}
        self.effect_definitions = self._create_effect_definitions()

    def _create_effect_definitions(self) -> Dict[str, Callable]:
        """Define standard status effects."""
        return {
            "poison": self._create_poison_effect,
            "heal_over_time": self._create_heal_effect,
            "shield": self._create_shield_effect,
            "haste": self._create_haste_effect,
            "slow": self._create_slow_effect,
            "strength": self._create_strength_effect,
            "weakness": self._create_weakness_effect,
        }

    def add_effect(self, unit_id: str, effect_name: str, duration: int = 3, stacks: int = 1) -> bool:
        """Add a status effect to a unit with validation."""
        if effect_name not in self.effect_definitions:
            if self.logger:
                self.logger.log_event("status_effect_unknown", {"unit": unit_id, "effect": effect_name})
            return False

        # Create the effect
        effect = self.effect_definitions[effect_name](duration, stacks)

        # Initialize unit effects if needed
        if unit_id not in self.unit_effects:
            self.unit_effects[unit_id] = []

        # Check for existing effect of same type
        existing_effect = self._find_effect(unit_id, effect_name)
        if existing_effect:
            # Stack or refresh
            if existing_effect.stacks < existing_effect.max_stacks:
                existing_effect.stacks += min(stacks, existing_effect.max_stacks - existing_effect.stacks)
                existing_effect.duration = max(existing_effect.duration, duration)
            else:
                existing_effect.duration = max(existing_effect.duration, duration)
        else:
            # Add new effect
            self.unit_effects[unit_id].append(effect)

        if self.logger:
            self.logger.log_event(
                "status_effect_added", {"unit": unit_id, "effect": effect_name, "duration": duration, "stacks": stacks}
            )

        return True

    def remove_effect(self, unit_id: str, effect_name: str) -> bool:
        """Remove a status effect from a unit."""
        if unit_id not in self.unit_effects:
            return False

        effects = self.unit_effects[unit_id]
        for effect in effects[:]:  # Copy to avoid modification during iteration
            if effect.name == effect_name:
                effects.remove(effect)
                if self.logger:
                    self.logger.log_event("status_effect_removed", {"unit": unit_id, "effect": effect_name})
                return True

        return False

    def tick_effects(self, game_state) -> Dict[str, List[str]]:
        """Process all status effects for one turn."""
        if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
            return {"expired": [], "applied": []}

        expired_effects = []
        applied_effects = []

        for unit_id, effects in list(self.unit_effects.items()):
            unit_data = game_state.units.units.get(unit_id)
            if not unit_data or not unit_data.get("alive", True):
                # Remove effects from dead units
                del self.unit_effects[unit_id]
                continue

            for effect in effects[:]:  # Copy to avoid modification during iteration
                try:
                    # Apply effect and check if it should continue
                    still_active = effect.tick(unit_data, game_state)
                    applied_effects.append(f"{unit_id}:{effect.name}")

                    if not still_active:
                        effects.remove(effect)
                        expired_effects.append(f"{unit_id}:{effect.name}")

                        if self.logger:
                            self.logger.log_event("status_effect_expired", {"unit": unit_id, "effect": effect.name})

                except (ValueError, KeyError, AttributeError) as e:
                    # Remove problematic effects
                    effects.remove(effect)
                    if self.logger:
                        self.logger.log_event(
                            "status_effect_error", {"unit": unit_id, "effect": effect.name, "error": str(e)}
                        )

            # Clean up empty effect lists
            if not effects:
                del self.unit_effects[unit_id]

        return {"expired": expired_effects, "applied": applied_effects}

    def get_unit_effects(self, unit_id: str) -> List[StatusEffect]:
        """Get all status effects for a unit."""
        return self.unit_effects.get(unit_id, []).copy()

    def has_effect(self, unit_id: str, effect_name: str) -> bool:
        """Check if unit has a specific effect."""
        return self._find_effect(unit_id, effect_name) is not None

    def _find_effect(self, unit_id: str, effect_name: str) -> Optional[StatusEffect]:
        """Find a specific effect on a unit."""
        effects = self.unit_effects.get(unit_id, [])
        for effect in effects:
            if effect.name == effect_name:
                return effect
        return None

    # Effect Definitions
    def _create_poison_effect(self, duration: int, stacks: int) -> StatusEffect:
        """Create a poison effect."""

        def poison_func(unit_data: Dict, game_state, effect: StatusEffect):
            damage = effect.stacks
            old_hp = unit_data.get("hp", 0)
            unit_data["hp"] = max(0, old_hp - damage)

            # Post-condition validation
            assert unit_data["hp"] >= 0, "HP cannot be negative"
            assert unit_data["hp"] <= old_hp, "Poison should not heal"

        return StatusEffect(
            name="poison",
            duration=duration,
            effect_type="debuff",
            effect_func=poison_func,
            icon="poison",
            description=f"Takes {stacks} damage per turn",
            stacks=stacks,
            max_stacks=5,
        )

    def _create_heal_effect(self, duration: int, stacks: int) -> StatusEffect:
        """Create a heal over time effect."""

        def heal_func(unit_data: Dict, game_state, effect: StatusEffect):
            healing = effect.stacks
            old_hp = unit_data.get("hp", 0)
            max_hp = unit_data.get("max_hp", 20)
            unit_data["hp"] = min(max_hp, old_hp + healing)

            # Post-condition validation
            assert unit_data["hp"] >= old_hp, "Heal should not damage"
            assert unit_data["hp"] <= max_hp, "HP cannot exceed maximum"

        return StatusEffect(
            name="heal_over_time",
            duration=duration,
            effect_type="buff",
            effect_func=heal_func,
            icon="heal",
            description=f"Heals {stacks} HP per turn",
            stacks=stacks,
            max_stacks=3,
        )

    def _create_shield_effect(self, duration: int, stacks: int) -> StatusEffect:
        """Create a shield effect."""

        def shield_func(unit_data: Dict, game_state, effect: StatusEffect):
            # Shield provides temporary HP boost
            if "shield_hp" not in unit_data:
                unit_data["shield_hp"] = effect.stacks * 5

        return StatusEffect(
            name="shield",
            duration=duration,
            effect_type="buff",
            effect_func=shield_func,
            icon="shield",
            description=f"Absorbs {stacks * 5} damage",
            stacks=stacks,
            max_stacks=2,
        )

    def _create_haste_effect(self, duration: int, stacks: int) -> StatusEffect:
        """Create a haste effect."""

        def haste_func(unit_data: Dict, game_state, effect: StatusEffect):
            # Haste increases movement range
            if "movement_bonus" not in unit_data:
                unit_data["movement_bonus"] = 0
            unit_data["movement_bonus"] = effect.stacks

        return StatusEffect(
            name="haste",
            duration=duration,
            effect_type="buff",
            effect_func=haste_func,
            icon="haste",
            description=f"Movement +{stacks}",
            stacks=stacks,
            max_stacks=3,
        )

    def _create_slow_effect(self, duration: int, stacks: int) -> StatusEffect:
        """Create a slow effect."""

        def slow_func(unit_data: Dict, game_state, effect: StatusEffect):
            # Slow decreases movement range
            if "movement_penalty" not in unit_data:
                unit_data["movement_penalty"] = 0
            unit_data["movement_penalty"] = effect.stacks

        return StatusEffect(
            name="slow",
            duration=duration,
            effect_type="debuff",
            effect_func=slow_func,
            icon="slow",
            description=f"Movement -{stacks}",
            stacks=stacks,
            max_stacks=2,
        )

    def _create_strength_effect(self, duration: int, stacks: int) -> StatusEffect:
        """Create a strength effect."""

        def strength_func(unit_data: Dict, game_state, effect: StatusEffect):
            if "damage_bonus" not in unit_data:
                unit_data["damage_bonus"] = 0
            unit_data["damage_bonus"] = effect.stacks

        return StatusEffect(
            name="strength",
            duration=duration,
            effect_type="buff",
            effect_func=strength_func,
            icon="strength",
            description=f"Damage +{stacks}",
            stacks=stacks,
            max_stacks=3,
        )

    def _create_weakness_effect(self, duration: int, stacks: int) -> StatusEffect:
        """Create a weakness effect."""

        def weakness_func(unit_data: Dict, game_state, effect: StatusEffect):
            if "damage_penalty" not in unit_data:
                unit_data["damage_penalty"] = 0
            unit_data["damage_penalty"] = effect.stacks

        return StatusEffect(
            name="weakness",
            duration=duration,
            effect_type="debuff",
            effect_func=weakness_func,
            icon="weakness",
            description=f"Damage -{stacks}",
            stacks=stacks,
            max_stacks=2,
        )
