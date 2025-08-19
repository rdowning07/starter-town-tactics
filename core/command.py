from dataclasses import dataclass
from typing import Protocol, Iterable, Any
from .events import Event

class Command(Protocol):
    def validate(self, s: Any) -> bool: ...
    def apply(self, s: Any) -> Iterable[Event]: ...

@dataclass(frozen=True)
class Move:
    unit_id: str
    to: tuple[int, int]
    
    def validate(self, s: Any) -> bool:
        # TODO: Add proper validation logic
        return True
    
    def apply(self, s: Any) -> Iterable[Event]:
        return [
            Event(type="unit_moved", payload={
                "unit_id": self.unit_id,
                "to": self.to
            })
        ]

@dataclass(frozen=True)
class Attack:
    attacker_id: str
    target_id: str
    
    def validate(self, s: Any) -> bool:
        # TODO: Add proper validation logic
        return True
    
    def apply(self, s: Any) -> Iterable[Event]:
        return [
            Event(type="attack_started", payload={
                "attacker_id": self.attacker_id,
                "target_id": self.target_id
            }),
            Event(type="damage_dealt", payload={
                "attacker_id": self.attacker_id,
                "target_id": self.target_id,
                "damage": 5  # TODO: Calculate actual damage
            }),
            Event(type="attack_ended", payload={
                "attacker_id": self.attacker_id,
                "target_id": self.target_id
            })
        ]

@dataclass(frozen=True)
class EndTurn:
    unit_id: str
    
    def validate(self, s: Any) -> bool:
        # TODO: Add proper validation logic
        return True
    
    def apply(self, s: Any) -> Iterable[Event]:
        return [
            Event(type="turn_ended", payload={
                "unit_id": self.unit_id
            })
        ]
