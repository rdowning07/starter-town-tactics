from dataclasses import dataclass
from typing import Callable, Iterable, List, Dict, Any

@dataclass(frozen=True)
class Event:
    type: str
    payload: Dict[str, Any]

Subscriber = Callable[[Event], None]

class EventBus:
    def __init__(self) -> None:
        self._subs: List[Subscriber] = []
    
    def subscribe(self, fn: Subscriber) -> None:
        self._subs.append(fn)
    
    def publish(self, events: Iterable[Event]) -> None:
        for e in events:
            for sub in self._subs:
                sub(e)
