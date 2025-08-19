"""
Core game engine components for Starter Town Tactics.

This module provides the command-event architecture foundation:
- Command pattern for game actions
- Event system for decoupled communication
- Game loop for orchestration
- RNG for deterministic randomness
- Game state management
"""

from .command import Command, Move, Attack, EndTurn
from .events import Event, EventBus, Subscriber
from .game_loop import GameLoop
from .rng import Rng
from .state import GameState, Controller

__all__ = [
    'Command', 'Move', 'Attack', 'EndTurn',
    'Event', 'EventBus', 'Subscriber',
    'GameLoop', 'Rng', 'GameState', 'Controller'
]
