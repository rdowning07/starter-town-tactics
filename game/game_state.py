# @api
from game.action_point_manager import ActionPointManager
from game.ai_controller import AIController
from game.sim_runner import SimRunner
from game.tactical_state_machine import TacticalStateMachine
from game.turn_controller import TurnController
from game.unit_manager import UnitManager


class GameState:
    """
    Dependency hub and global context for all game systems.
    Owns and wires: FSM, TurnController, AP, AI, Units, SimRunner
    """

    def __init__(self):
        self.ap = ActionPointManager()
        self.fsm = TacticalStateMachine()
        self.turns = TurnController(self.ap, self.fsm)
        self.units = UnitManager()
        self.ai = AIController([])
        self.sim = SimRunner(self.turns, self.ai)

    def add_unit(self, unit_id: str, team: str, ap: int = 2, hp: int = 10):
        self.units.register_unit(unit_id, team, hp=hp)
        self.turns.add_unit(unit_id)
        self.ap.register_unit(unit_id, ap=ap)

    def get_current_unit(self) -> str:
        return self.turns.get_current_unit()

    def is_ai_turn(self) -> bool:
        uid = self.get_current_unit()
        return self.units.get_team(uid) == "ai"

    def is_game_over(self) -> bool:
        return self.sim.phase == "GAME_OVER"

    def damage_unit(self, unit_id: str, dmg: int):
        self.units.damage_unit(unit_id, dmg)
        if not self.units.is_alive(unit_id):
            self.turns.remove_unit(unit_id)
            self.sim.mark_unit_dead(unit_id)
