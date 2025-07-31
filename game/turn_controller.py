# @api
from typing import TYPE_CHECKING, Any, List, Optional, Union

from game.action_point_manager import ActionPointManager
from game.tactical_state_machine import TacticalState

if TYPE_CHECKING:
    from game.game import Game
    from game.tactical_state_machine import TacticalStateMachine


class TurnController:
    def __init__(
        self,
        game_or_apm: Optional[Union["Game", ActionPointManager, Any]] = None,
        tactical_state_machine: Optional["TacticalStateMachine"] = None,
    ):
        self.units: List[str] = []
        self.current_index = 0
        self.current_turn = 0  # Add turn counter
        self.game = None
        self.action_point_manager = None
        self.tactical_state_machine = tactical_state_machine

        # Handle different constructor arguments
        if isinstance(game_or_apm, ActionPointManager):
            self.action_point_manager = game_or_apm
        elif game_or_apm is not None and hasattr(
            game_or_apm, "units"
        ):  # Assume it's a Game object or similar
            self.game = game_or_apm
            # Initialize units from game if available
            for unit in game_or_apm.units:
                self.add_unit(unit.name if hasattr(unit, "name") else str(unit))

    def add_unit(self, unit_id: str) -> None:
        self.units.append(unit_id)

    def remove_unit(self, unit_id: str) -> None:
        """Remove a unit from the turn order."""
        if unit_id in self.units:
            # Find the index of the unit to remove
            unit_index = self.units.index(unit_id)
            
            # Remove the unit
            self.units.remove(unit_id)
            
            # Adjust current_index if necessary
            if self.units:  # Only adjust if there are still units
                if unit_index <= self.current_index:
                    # If we removed a unit at or before current_index, 
                    # we need to adjust current_index
                    self.current_index = max(0, self.current_index - 1)
                # Ensure current_index is within bounds
                self.current_index = self.current_index % len(self.units)
            else:
                # No units left, reset current_index
                self.current_index = 0

    def next_turn(self) -> str:
        self.current_index = (self.current_index + 1) % len(self.units)
        self.current_turn += 1  # Increment turn counter
        current_unit = self.get_current_unit()
        if self.action_point_manager:
            self.action_point_manager.register_unit(current_unit)
        # Update tactical state machine
        if self.tactical_state_machine:
            self.tactical_state_machine.transition_to(TacticalState.SELECTING_UNIT)
        return current_unit

    def get_current_unit(self) -> str:
        return self.units[self.current_index]

    def end_turn(self) -> None:
        """End the current turn and advance to the next unit."""
        if self.units:
            self.current_turn += 1
            self.current_index = (self.current_index + 1) % len(self.units)
            current_unit = self.get_current_unit()
            if self.action_point_manager:
                self.action_point_manager.register_unit(current_unit)
            # Reset tactical state machine
            if self.tactical_state_machine:
                self.tactical_state_machine.reset()

    def can_act(self, cost: int = 1) -> bool:
        if not self.action_point_manager:
            return True
        unit_id = self.get_current_unit()
        return self.action_point_manager.can_spend(unit_id, cost)

    def spend_ap(self, cost: int = 1) -> bool:
        if not self.action_point_manager:
            return True
        unit_id = self.get_current_unit()
        return self.action_point_manager.spend(unit_id, cost)

    def is_ai_turn(self) -> bool:
        """Check if the current turn belongs to an AI unit."""
        if not self.units:
            return False
        current_unit_id = self.get_current_unit()
        # Simple heuristic: if unit ID contains 'ai' or 'enemy', it's AI
        return "ai" in current_unit_id.lower() or "enemy" in current_unit_id.lower()

    def get_state(self):
        """Get the current tactical state."""
        if self.tactical_state_machine:
            return self.tactical_state_machine.state
        return None

    def set_state(self, state):
        """Set the tactical state."""
        if self.tactical_state_machine:
            self.tactical_state_machine.transition_to(state)
