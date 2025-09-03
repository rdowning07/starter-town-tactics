from .command import Command
from .events import EventBus
from .rng import Rng
from .state import GameState


class GameLoop:
    def __init__(self, rng, bus: EventBus) -> None:
        self.rng = rng
        self.bus = bus

    def tick(self, s) -> None:
        if s.is_over():
            return
        s.tick += 1  # monotonic tick counter for ordering

        # 1) Ensure TURN_STARTED is emitted when needed
        self.bus.publish(s.turn_controller.start_if_needed(s))

        # 2) Decide & apply one command
        controller = s.current_controller()
        cmd: Command = controller.decide(s)
        if cmd.validate(s):
            evts = list(cmd.apply(s))
            self.bus.publish(evts)

        # 3) Status/turn housekeeping may emit more events (e.g., Poison kill)
        post_evts = list(s.rules.on_post_action(s))  # optional hook that yields events
        self.bus.publish(post_evts)

        # 4) Turn advancement (emits TURN_ENDED + TURN_STARTED if flagged)
        self.bus.publish(s.turn_controller.maybe_advance(s))
