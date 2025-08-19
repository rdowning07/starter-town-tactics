"""
Core game engine components for Starter Town Tactics.

This module provides the command-event architecture foundation:
- Command pattern for game actions
- Event system for decoupled communication
- Game loop for orchestration
- RNG for deterministic randomness
- Game state management
- Rules engine for deterministic mechanics
- Objectives system for victory/defeat conditions
"""

from .command import Command, Move, Attack, EndTurn
from .events import Event, EventBus, Subscriber
from .game_loop import GameLoop
from .rng import Rng
from .state import GameState, Controller, Unit, UnitStats, Map, Tile, UnitRef, TurnController
from .rules import DamageResult, apply_attack, Status, on_unit_turn_start, a_star
from .objectives import Objective, EliminateBoss, SurviveNTurns, HoldZones, Escort

__all__ = [
    'Command', 'Move', 'Attack', 'EndTurn',
    'Event', 'EventBus', 'Subscriber',
    'GameLoop', 'Rng', 'GameState', 'Controller',
    'Unit', 'UnitStats', 'Map', 'Tile', 'UnitRef', 'TurnController',
    'DamageResult', 'apply_attack', 'Status', 'on_unit_turn_start', 'a_star',
    'Objective', 'EliminateBoss', 'SurviveNTurns', 'HoldZones', 'Escort'
]
