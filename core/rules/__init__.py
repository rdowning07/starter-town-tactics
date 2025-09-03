"""
Core rules engine for Starter Town Tactics.
This module provides deterministic game mechanics:
- Combat calculation with height and facing modifiers
- Status effects (Poison, Slow)
- A* pathfinding for movement
"""
from .combat import DamageResult, apply_attack, calc_facing_bonus, calc_height_bonus
from .move import a_star, heuristic, terrain_cost
from .status import Status, on_unit_turn_start

__all__ = [
    "DamageResult",
    "apply_attack",
    "calc_height_bonus",
    "calc_facing_bonus",
    "Status",
    "on_unit_turn_start",
    "a_star",
    "terrain_cost",
    "heuristic",
]
