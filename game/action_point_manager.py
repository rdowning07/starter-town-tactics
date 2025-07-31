# @api
from typing import Dict, Optional


class ActionPointManager:
    """
    Tracks and manages action points (AP) per unit.

    Usage:
        - Register units at turn start
        - Query how many AP they have left
        - Spend AP when actions are taken
        - Restore AP between turns
    """

    def __init__(self) -> None:
        self._unit_ap: Dict[str, int] = {}
        self._max_ap = 2  # default max AP per turn (move + attack)

    def register_unit(self, unit_id: str, ap: Optional[int] = None) -> None:
        """Start a new turn for a unit with fresh AP."""
        self._unit_ap[unit_id] = ap if ap is not None else self._max_ap

    def get_ap(self, unit_id: str) -> int:
        return self._unit_ap.get(unit_id, 0)

    def can_spend(self, unit_id: str, cost: int = 1) -> bool:
        return self._unit_ap.get(unit_id, 0) >= cost

    def spend(self, unit_id: str, cost: int = 1) -> bool:
        if self.can_spend(unit_id, cost):
            self._unit_ap[unit_id] -= cost
            return True
        return False

    def reset_all(self) -> None:
        for unit in self._unit_ap:
            self._unit_ap[unit] = self._max_ap

    def remove_unit(self, unit_id: str) -> None:
        self._unit_ap.pop(unit_id, None)

    def get_all_ap(self) -> Dict[str, int]:
        """Returns current AP for all registered units (for UI/debug)."""
        return dict(self._unit_ap)

    def set_max_ap(self, max_ap: int) -> None:
        self._max_ap = max_ap
