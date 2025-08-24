"""Objectives management system."""

from __future__ import annotations




class ObjectivesManager:
    """Manages game objectives and their dynamic updates based on game state."""

    def __init__(self, game_state):
        self.game_state = game_state
        self.current_objective = ""
        self.objective_history = []

    def set_objective(self, objective: str) -> None:
        """Sets the current objective and triggers a game event if necessary."""
        if objective != self.current_objective:
            self.objective_history.append(self.current_objective)
            self.current_objective = objective
            print(f"🎯 New Objective: {objective}")
            # Additional logic can be added to trigger in-game events (e.g., notifications, effects)

    def get_current_objective(self) -> str:
        """Get the current objective."""
        return self.current_objective

    def get_objective_history(self) -> list[str]:
        """Get the history of objectives."""
        return list(self.objective_history)

    def update_objectives(self) -> None:
        """Updates the current objectives based on game state."""
        if self.game_state.has_won():
            self.set_objective("Victory! The enemies have been defeated.")
        elif self.game_state.has_lost():
            self.set_objective("Defeat. You lost the battle.")
        else:
            # Check if all enemies are defeated but game isn't over
            if not self.game_state.units.any_effectively_alive("ai"):
                self.set_objective("Survive until reinforcements arrive!")
            else:
                self.set_objective("Defeat all enemies!")

    def reset(self) -> None:
        """Reset objectives to initial state."""
        self.current_objective = ""
        self.objective_history.clear()


def update_objective_flow(game_state, objectives_manager: ObjectivesManager) -> None:
    """Example of how objectives are updated dynamically."""
    if game_state.has_won():
        objectives_manager.set_objective("Victory! The enemies have been defeated.")
    elif game_state.has_lost():
        objectives_manager.set_objective("Defeat. You lost the battle.")
    else:
        objectives_manager.update_objectives()
