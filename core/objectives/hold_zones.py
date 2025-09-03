from ..events import EventType
from .base import Objective


class HoldZones(Objective):
    def __init__(self, zones: list[tuple[int, int]], k: int, turns: int):
        self.zones = set(zones)
        self.k = k
        self.turns = turns
        self.counter = 0

    def update_from_events(self, events, s):
        # count at end of player turn only (look for TURN_ENDED side=player)
        for e in events:
            if e.type == EventType.TURN_ENDED and e.payload.get("side") == "player":
                held = sum(1 for z in self.zones if s.controlled_by_player(z))
                self.counter = self.counter + 1 if held >= self.k else 0

    def is_complete(self, s):
        return self.counter >= self.turns

    def is_failed(self, s):
        return False

    def summary(self, s):
        return f"Hold {self.k}/{len(self.zones)} zones for {self.turns} turns (streak {self.counter})"
