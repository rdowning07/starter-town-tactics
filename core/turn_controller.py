from dataclasses import dataclass
from typing import Iterable, List

from .events import Event, ev_turn_ended, ev_turn_started


@dataclass
class TurnController:
    turn_index: int = 0
    _pending_end: bool = False
    _current_unit_id: str = "player1"  # Default unit
    _current_side: str = "player"  # Default side

    @property
    def current_unit_id(self) -> str:
        return self._current_unit_id

    @property
    def current_side(self) -> str:
        return self._current_side

    def flag_end_of_turn(self) -> None:
        self._pending_end = True

    def start_if_needed(self, s) -> Iterable[Event]:
        # Called at the beginning of a turn (or game start)
        if s.turn_started_this_tick:
            yield ev_turn_started(self.current_unit_id, self.current_side, self.schedule_index(), s.tick)

    def maybe_advance(self, s) -> Iterable[Event]:
        if not self._pending_end:
            return ()
        # close current
        evts: List[Event] = [ev_turn_ended(self.current_unit_id, self.current_side, self.schedule_index(), s.tick)]
        # advance scheduling to next unit/side
        self._advance_schedule(s)
        self._pending_end = False
        # open next
        evts.append(ev_turn_started(self.current_unit_id, self.current_side, self.schedule_index(), s.tick))
        return evts

    def schedule_index(self) -> int:
        return self.turn_index

    def _advance_schedule(self, s) -> None:
        # rotate to next unit; increment turn_index as your design requires
        self.turn_index += 1
        # For now, simple rotation between player and enemy
        if self._current_side == "player":
            self._current_side = "enemy"
            self._current_unit_id = "enemy1"
        else:
            self._current_side = "player"
            self._current_unit_id = "player1"
