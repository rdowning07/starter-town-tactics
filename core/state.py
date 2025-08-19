from typing import Protocol, Optional
from .events import Event

class Controller(Protocol):
    def decide(self, state: 'GameState') -> 'Command': ...

class GameState:
    def __init__(self) -> None:
        self.objectives = None  # Will be ObjectivesManager
        self.turn_controller = None  # Will be TurnController
        self._current_controller: Optional[Controller] = None
        self._is_over = False
    
    def is_over(self) -> bool:
        return self._is_over
    
    def current_controller(self) -> Controller:
        if self._current_controller is None:
            raise RuntimeError("No controller set")
        return self._current_controller
    
    def set_controller(self, controller: Controller) -> None:
        self._current_controller = controller
    
    def set_over(self, is_over: bool) -> None:
        self._is_over = is_over
