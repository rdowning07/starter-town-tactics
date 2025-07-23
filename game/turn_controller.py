from enum import Enum, auto


class TurnPhase(Enum):
    PLAYER = auto()
    AI = auto()
    WAITING = auto()
    GAME_OVER = auto()


class TurnController:
    def __init__(self):
        self.phase = TurnPhase.PLAYER

    def get_phase(self):
        return self.phase

    def set_phase(self, new_phase):
        if not isinstance(new_phase, TurnPhase):
            raise ValueError("Invalid phase type")
        self.phase = new_phase

    def advance_turn(self):
        if self.phase == TurnPhase.PLAYER:
            self.phase = TurnPhase.AI
        elif self.phase == TurnPhase.AI:
            self.phase = TurnPhase.PLAYER
        elif self.phase == TurnPhase.WAITING:
            pass  # reserved for future states
        elif self.phase == TurnPhase.GAME_OVER:
            pass  # reserved for end state
