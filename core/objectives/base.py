# @api: Objectives receive events and can query state; must be pure on queries
from typing import Iterable
from abc import ABC, abstractmethod
from ..events import Event
from ..state import GameState

class Objective(ABC):
    @abstractmethod
    def update_from_events(self, events: Iterable[Event], s: GameState) -> None:
        pass
    
    @abstractmethod
    def is_complete(self, s: GameState) -> bool:
        pass
    
    @abstractmethod
    def is_failed(self, s: GameState) -> bool:
        pass
    
    @abstractmethod
    def summary(self, s: GameState) -> str:
        pass
