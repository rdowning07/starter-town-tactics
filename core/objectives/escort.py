from .base import Objective
from ..events import EventType

class Escort(Objective):
    def __init__(self, unit_id: str, goal: tuple[int,int]):
        self.unit_id = unit_id
        self.goal = goal
        self._dead = False
        self._done = False
    
    def update_from_events(self, events, s):
        for e in events:
            if e.type == EventType.UNIT_KILLED and e.payload.get("unit_id") == self.unit_id:
                self._dead = True
            if e.type == EventType.UNIT_MOVED and e.payload.get("unit_id") == self.unit_id and e.payload.get("to") == self.goal:
                self._done = True
    
    def is_complete(self, s): 
        return self._done
    
    def is_failed(self, s): 
        return self._dead
    
    def summary(self, s): 
        return f"Escort {self.unit_id} to {self.goal} – {'done' if self._done else 'in progress'}"
