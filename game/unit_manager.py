# @api
from typing import Dict


class UnitManager:
    """
    Central authority for unit metadata, like HP, team, status.
    Not responsible for turn order — that's TurnController.
    """

    def __init__(self) -> None:
        self.units: Dict[str, Dict] = {}

    def register_unit(self, unit_id: str, team: str, hp: int = 10) -> None:
        self.units[unit_id] = {
            "team": team,
            "hp": hp,
            "alive": True,
        }

    def get_team(self, unit_id: str) -> str:
        return self.units[unit_id]["team"]

    def is_alive(self, unit_id: str) -> bool:
        return self.units.get(unit_id, {}).get("alive", False)

    def damage_unit(self, unit_id: str, dmg: int) -> None:
        if unit_id not in self.units:
            return
        self.units[unit_id]["hp"] -= dmg
        if self.units[unit_id]["hp"] <= 0:
            self.units[unit_id]["alive"] = False

    def get_all_units(self) -> Dict[str, Dict]:
        return dict(self.units)

    def get_living_units(self) -> list[str]:
        return [uid for uid, u in self.units.items() if u["alive"]]

    def remove_unit(self, unit_id: str) -> None:
        if unit_id in self.units:
            self.units[unit_id]["alive"] = False
