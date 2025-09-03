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

from .command import Attack, Command, EndTurn, Move
from .events import Event, EventBus, Subscriber
from .game_loop import GameLoop
from .objectives import EliminateBoss, Escort, HoldZones, Objective, SurviveNTurns
from .rng import Rng
from .rules import DamageResult, Status, a_star, apply_attack, on_unit_turn_start
from .state import Controller, GameState, Map, Tile, TurnController, Unit, UnitRef, UnitStats

__all__ = [
    "Command",
    "Move",
    "Attack",
    "EndTurn",
    "Event",
    "EventBus",
    "Subscriber",
    "GameLoop",
    "Rng",
    "GameState",
    "Controller",
    "Unit",
    "UnitStats",
    "Map",
    "Tile",
    "UnitRef",
    "TurnController",
    "DamageResult",
    "apply_attack",
    "Status",
    "on_unit_turn_start",
    "a_star",
    "Objective",
    "EliminateBoss",
    "SurviveNTurns",
    "HoldZones",
    "Escort",
]
