from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .events import Event, ev_unit_attacked, ev_unit_killed, ev_unit_moved
from .state import GameState


class Command(ABC):
    @abstractmethod
    def validate(self, s: GameState) -> bool:
        pass

    @abstractmethod
    def apply(self, s: GameState) -> Iterable[Event]:
        pass


@dataclass(frozen=True)
class Move(Command):
    unit_id: str
    to: Tuple[int, int]

    def validate(self, s: GameState) -> bool:
        u = s.unit(self.unit_id)
        return s.rules.can_move(u, self.to)  # path cost & occupancy checks

    def apply(self, s: GameState) -> Iterable[Event]:
        u = s.unit(self.unit_id)
        frm = u.pos
        s.rules.move_unit(u, self.to)  # actually update state (pure+mut)
        yield ev_unit_moved(self.unit_id, frm, self.to, s.tick)


@dataclass(frozen=True)
class Attack(Command):
    attacker_id: str
    target_id: str

    def validate(self, s: GameState) -> bool:
        return s.rules.can_attack(s.unit(self.attacker_id), s.unit(self.target_id))

    def apply(self, s: GameState) -> Iterable[Event]:
        a, t = s.unit(self.attacker_id), s.unit(self.target_id)
        dmg = s.rules.apply_attack(a, t)  # returns int damage; sets hp
        yield ev_unit_attacked(a.id, t.id, dmg, s.tick)
        if t.stats.hp <= 0:
            yield ev_unit_killed(t.id, a.id, s.tick)


@dataclass(frozen=True)
class EndTurn(Command):
    unit_id: str

    def validate(self, s: GameState) -> bool:
        return s.turn_controller.current_unit_id == self.unit_id

    def apply(self, s: GameState) -> Iterable[Event]:
        # TurnController will emit TURN_ENDED/STARTED. Nothing to emit here.
        s.turn_controller.flag_end_of_turn()  # set a bit the loop will consume
        return ()
