# @api
from typing import Dict, Optional


class UnitManager:
    """
    Central authority for unit metadata, like HP, team, status.
    Not responsible for turn order — that's TurnController.
    """

    def __init__(self) -> None:
        self.units: Dict[str, Dict] = {}
        self.fake_dead_units: set[str] = set()

    def register_unit(self, unit_id: str, team: str, hp: int = 10, x: int = 0, y: int = 0) -> None:
        """Register a new unit with validation."""
        if not unit_id or not team:
            raise ValueError("Unit ID and team must be non-empty strings")
        if hp <= 0:
            raise ValueError("HP must be positive")

        self.units[unit_id] = {
            "team": team,
            "hp": hp,
            "alive": True,
            "x": x,
            "y": y,
            "attack_range": 1,  # Default attack range
        }

    def get(self, unit_id: str) -> Optional[Dict]:
        """Get unit data by ID, returns None if unit doesn't exist."""
        return self.units.get(unit_id)

    def update_unit_position(self, unit_id: str, x: int, y: int) -> bool:
        """Update unit position, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        self.units[unit_id]["x"] = x
        self.units[unit_id]["y"] = y
        return True

    def update_unit_hp(self, unit_id: str, new_hp: int) -> bool:
        """Update unit HP, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        if new_hp < 0:
            new_hp = 0
        self.units[unit_id]["hp"] = new_hp
        if new_hp == 0:
            self.units[unit_id]["alive"] = False
        return True

    def get_team(self, unit_id: str) -> Optional[str]:
        """Get the team of a unit, returns None if unit doesn't exist."""
        unit = self.units.get(unit_id)
        return unit["team"] if unit else None

    def get_hp(self, unit_id: str) -> Optional[int]:
        """Get the current HP of a unit, returns None if unit doesn't exist."""
        unit = self.units.get(unit_id)
        return unit["hp"] if unit else None

    def set_hp(self, unit_id: str, hp: int) -> bool:
        """Set the HP of a unit, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        if hp < 0:
            hp = 0
        self.units[unit_id]["hp"] = hp
        if hp == 0:
            self.units[unit_id]["alive"] = False
        return True

    def is_alive(self, unit_id: str) -> bool:
        """Check if a unit is alive, returns False if unit doesn't exist."""
        unit = self.units.get(unit_id)
        return unit.get("alive", False) if unit else False

    def is_effectively_alive(self, unit_id: str) -> bool:
        """Check if a unit is effectively alive (including fake dead status)."""
        return self.is_alive(unit_id) or unit_id in self.fake_dead_units

    def any_alive(self, team: str) -> bool:
        """Check if any units of the specified team are alive."""
        return any(
            unit["alive"] and unit["team"] == team for unit in self.units.values()
        )

    def any_effectively_alive(self, team: str) -> bool:
        """Check if any units of the specified team are effectively alive."""
        return any(
            self.is_effectively_alive(uid) for uid in self.get_unit_ids_by_team(team)
        )

    def get_unit_ids_by_team(self, team: str) -> list[str]:
        """Get all unit IDs for a specific team."""
        return [uid for uid, unit in self.units.items() if unit["team"] == team]

    def damage_unit(self, unit_id: str, dmg: int) -> bool:
        """Damage a unit, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        if dmg < 0:
            dmg = 0

        current_hp = self.units[unit_id]["hp"]
        new_hp = max(0, current_hp - dmg)
        self.units[unit_id]["hp"] = new_hp

        if new_hp == 0:
            self.units[unit_id]["alive"] = False

        return True

    def heal_unit(self, unit_id: str, heal: int) -> bool:
        """Heal a unit, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        if heal < 0:
            heal = 0

        current_hp = self.units[unit_id]["hp"]
        # Assuming max HP is stored or calculated somehow
        max_hp = 10  # TODO: Make this configurable per unit
        new_hp = min(max_hp, current_hp + heal)
        self.units[unit_id]["hp"] = new_hp

        if new_hp > 0:
            self.units[unit_id]["alive"] = True

        return True

    def mark_as_fake_dead(self, unit_id: str) -> bool:
        """Mark a unit as fake dead, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        self.fake_dead_units.add(unit_id)
        return True

    def unmark_fake_dead(self, unit_id: str) -> bool:
        """Remove fake dead status from a unit, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        self.fake_dead_units.discard(unit_id)
        return True

    def get_all_units(self) -> Dict[str, Dict]:
        """Get all unit data."""
        return dict(self.units)

    def get_living_units(self) -> list[str]:
        """Get IDs of all living units."""
        return [uid for uid, u in self.units.items() if u["alive"]]

    def remove_unit(self, unit_id: str) -> bool:
        """Mark a unit as dead, returns False if unit doesn't exist."""
        if unit_id not in self.units:
            return False
        self.units[unit_id]["alive"] = False
        return True

    def unit_exists(self, unit_id: str) -> bool:
        """Check if a unit exists."""
        return unit_id in self.units

    def get_unit_count(self, team: Optional[str] = None) -> int:
        """Get the count of units, optionally filtered by team."""
        if team is None:
            return len(self.units)
        return len(self.get_unit_ids_by_team(team))
