# @api: Stable event names & payload shapes. Publish order is part of the contract.
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

class EventType(str, Enum):
    UNIT_MOVED   = "UNIT_MOVED"     # {unit_id, from, to}
    UNIT_ATTACKED= "UNIT_ATTACKED"  # {attacker_id, target_id, damage}
    UNIT_KILLED  = "UNIT_KILLED"    # {unit_id, by}
    TURN_STARTED = "TURN_STARTED"   # {unit_id, side, index}
    TURN_ENDED   = "TURN_ENDED"     # {unit_id, side, index}

@dataclass(frozen=True)
class Event:
    type: EventType
    payload: Dict[str, Any]
    tick: int  # monotonic from GameState.tick

Subscriber = Callable[[Event], None]

class EventBus:
    def __init__(self) -> None:
        self._subs: List[Tuple[Subscriber, Optional[Set[EventType]]]] = []

    def subscribe(self, fn: Subscriber, types: Optional[Iterable[EventType]] = None) -> None:
        self._subs.append((fn, set(types) if types else None))

    def publish(self, events: Iterable[Event]) -> None:
        for e in events:
            for fn, filt in self._subs:
                if filt is None or e.type in filt:
                    try:
                        fn(e)
                    except Exception:
                        # Log error but continue processing other subscribers
                        pass

# ---- Canonical factories (avoid ad-hoc dicts) ----
def ev_unit_moved(unit_id: str, from_pos: Tuple[int, int], to_pos: Tuple[int, int], tick: int) -> Event:
    return Event(EventType.UNIT_MOVED, {"unit_id": unit_id, "from": from_pos, "to": to_pos}, tick)

def ev_unit_attacked(attacker_id: str, target_id: str, damage: int, tick: int) -> Event:
    return Event(EventType.UNIT_ATTACKED, {"attacker_id": attacker_id, "target_id": target_id, "damage": damage}, tick)

def ev_unit_killed(unit_id: str, by: str, tick: int) -> Event:
    return Event(EventType.UNIT_KILLED, {"unit_id": unit_id, "by": by}, tick)

def ev_turn_started(unit_id: str, side: str, index: int, tick: int) -> Event:
    return Event(EventType.TURN_STARTED, {"unit_id": unit_id, "side": side, "index": index}, tick)

def ev_turn_ended(unit_id: str, side: str, index: int, tick: int) -> Event:
    return Event(EventType.TURN_ENDED, {"unit_id": unit_id, "side": side, "index": index}, tick)
