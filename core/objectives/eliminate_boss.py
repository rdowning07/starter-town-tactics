from .base import Objective
from ..events import Event, EventType

class EliminateBoss(Objective):
    def __init__(self, boss_id: str):
        self.boss_id = boss_id
        self._dead = False
    
    def update_from_events(self, events, s):
        for e in events:
            if e.type == EventType.UNIT_KILLED and e.payload.get("unit_id") == self.boss_id:
                self._dead = True
    
    def is_complete(self, s): 
        return self._dead
    
    def is_failed(self, s): 
        return False
    
    def summary(self, s): 
        return f"Defeat boss {self.boss_id} – {'done' if self._dead else 'in progress'}"
