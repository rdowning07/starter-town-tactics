from .rng import Rng
from .command import Command
from .events import EventBus
from .state import GameState

class GameLoop:
    def __init__(self, rng: Rng, bus: EventBus) -> None:
        self.rng = rng
        self.bus = bus

    def tick(self, s: GameState) -> None:
        if s.is_over():
            return
        controller = s.current_controller()   # AI or player adapter
        cmd: Command = controller.decide(s)
        if cmd.validate(s):
            events = list(cmd.apply(s))
            self.bus.publish(events)
            s.objectives.update_from_events(events)
            s.turn_controller.maybe_advance(s)
