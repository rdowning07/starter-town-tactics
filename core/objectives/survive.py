from .base import Objective

class SurviveNTurns(Objective):
    def __init__(self, n_turns: int):
        self.n = n_turns
    
    def update_from_events(self, events, s): 
        pass
    
    def is_complete(self, s): 
        return s.turn_controller.turn_index >= self.n
    
    def is_failed(self, s): 
        return s.player_wiped()
    
    def summary(self, s): 
        return f"Survive {self.n} turns (now {s.turn_controller.turn_index})"
