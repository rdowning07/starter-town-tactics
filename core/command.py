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

@dataclass(frozen=True)
class Attack:
    attacker_id: str
    target_id: str

@dataclass(frozen=True)
class EndTurn:
    unit_id: str
