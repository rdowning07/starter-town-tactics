"""
Objectives system for Starter Town Tactics.
This module provides various game objectives that can track progress
and determine victory/defeat conditions.
"""
from typing import Dict, Type, Any, List
from .base import Objective
from .eliminate_boss import EliminateBoss
from .survive import SurviveNTurns
from .hold_zones import HoldZones
from .escort import Escort
from .compound import Compound

# Objectives registry for type mapping
OBJECTIVE_REGISTRY: Dict[str, Type[Objective]] = {
    'EliminateBoss': EliminateBoss,
    'SurviveNTurns': SurviveNTurns,
    'HoldZones': HoldZones,
    'Escort': Escort,
    'Compound': Compound,
}

def create_objective(obj_config: Dict[str, Any]) -> Objective:
    """
    Create an objective from configuration.
    
    Args:
        obj_config: Dictionary with 'type' key and other parameters
        
    Returns:
        Configured objective instance
        
    Raises:
        ValueError: If objective type is unknown or configuration is invalid
    """
    obj_type = obj_config.get('type')
    if obj_type not in OBJECTIVE_REGISTRY:
        raise ValueError(f"Unknown objective type: {obj_type}")
    
    objective_class = OBJECTIVE_REGISTRY[obj_type]
    
    # Handle different objective types
    if obj_type == 'EliminateBoss':
        boss_id = obj_config.get('boss_id')
        if not boss_id:
            raise ValueError("EliminateBoss requires 'boss_id' parameter")
        return objective_class(boss_id)  # type: ignore
    
    elif obj_type == 'SurviveNTurns':
        n = obj_config.get('n')
        if n is None:
            raise ValueError("SurviveNTurns requires 'n' parameter")
        return objective_class(n)  # type: ignore
    
    elif obj_type == 'HoldZones':
        zones = obj_config.get('zones', [])
        duration = obj_config.get('duration', 5)
        return objective_class(zones, duration)  # type: ignore
    
    elif obj_type == 'Escort':
        escort_id = obj_config.get('escort_id')
        target_pos = obj_config.get('target_pos')
        if not escort_id or not target_pos:
            raise ValueError("Escort requires 'escort_id' and 'target_pos' parameters")
        return objective_class(escort_id, tuple(target_pos))  # type: ignore
    
    elif obj_type == 'Compound':
        sub_objectives_config = obj_config.get('list', [])
        if not sub_objectives_config:
            raise ValueError("Compound requires 'list' parameter with sub-objectives")
        
        sub_objectives = []
        for sub_config in sub_objectives_config:
            sub_objectives.append(create_objective(sub_config))
        
        return objective_class(sub_objectives)  # type: ignore
    
    else:
        # Fallback for simple objectives
        return objective_class()

__all__ = [
    'Objective', 'EliminateBoss', 'SurviveNTurns', 'HoldZones', 'Escort', 'Compound',
    'OBJECTIVE_REGISTRY', 'create_objective'
]
