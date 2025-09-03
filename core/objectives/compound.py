# @api: Compound objective that contains multiple sub-objectives
from typing import Any, Dict, Iterable, List

from ..events import Event
from ..state import GameState
from .base import Objective


class Compound(Objective):
    """
    Compound objective that manages multiple sub-objectives.
    Completes when all sub-objectives are complete.
    Fails if any sub-objective fails.
    """

    def __init__(self, objectives: List[Objective]):
        self.objectives = objectives
        self._complete = False
        self._failed = False

    def update_from_events(self, events: Iterable[Event], s: GameState) -> None:
        """Update all sub-objectives from events."""
        if self._complete or self._failed:
            return

        # Update all sub-objectives
        for objective in self.objectives:
            objective.update_from_events(events, s)

        # Check completion/failure status
        self._check_status(s)

    def _check_status(self, s: GameState) -> None:
        """Check if compound objective is complete or failed."""
        # Fail if any sub-objective fails
        if any(obj.is_failed(s) for obj in self.objectives):
            self._failed = True
            return

        # Complete if all sub-objectives are complete
        if all(obj.is_complete(s) for obj in self.objectives):
            self._complete = True

    def is_complete(self, s: GameState) -> bool:
        return self._complete

    def is_failed(self, s: GameState) -> bool:
        return self._failed

    def summary(self, s: GameState) -> str:
        if self._complete:
            return "All objectives completed!"
        elif self._failed:
            return "One or more objectives failed"
        else:
            completed = sum(1 for obj in self.objectives if obj.is_complete(s))
            total = len(self.objectives)
            return f"Objectives: {completed}/{total} complete"

    def get_sub_objectives(self) -> List[Objective]:
        """Get list of sub-objectives."""
        return list(self.objectives)
