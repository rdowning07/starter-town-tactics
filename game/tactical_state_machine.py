# @api
from enum import Enum, auto
from typing import Optional


class TacticalState(Enum):
    IDLE = auto()
    SELECTING_UNIT = auto()
    PLANNING_MOVE = auto()
    CONFIRMING_MOVE = auto()
    PLANNING_ATTACK = auto()
    CONFIRMING_ATTACK = auto()
    TURN_END = auto()


class TacticalStateMachine:
    def __init__(self) -> None:
        self.state: TacticalState = TacticalState.IDLE
        self.previous_state: Optional[TacticalState] = None

    def transition_to(self, new_state: TacticalState) -> None:
        """Transition from current to new state with logging."""
        self.previous_state = self.state
        self.state = new_state
        print(f"[TacticalStateMachine] {self.previous_state.name} → " f"{self.state.name}")

    def cancel(self) -> None:
        """Revert to the previous state if canceling an action."""
        if self.previous_state:
            print(f"[TacticalStateMachine] Canceling → " f"{self.previous_state.name}")
            self.state, self.previous_state = self.previous_state, self.state

    def is_player_turn_active(self) -> bool:
        """Check if we're in an active decision phase for the player."""
        return self.state in {
            TacticalState.SELECTING_UNIT,
            TacticalState.PLANNING_MOVE,
            TacticalState.CONFIRMING_MOVE,
            TacticalState.PLANNING_ATTACK,
            TacticalState.CONFIRMING_ATTACK,
        }

    def reset(self) -> None:
        """Reset to idle, e.g., after AI turn or end of player turn."""
        self.previous_state = self.state
        self.state = TacticalState.IDLE

    def __str__(self) -> str:
        return f"TacticalStateMachine(state={self.state.name})"
