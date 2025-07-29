# @api
# game/sim_runner.py

from game.game import Game
from game.unit import Unit

class SimRunner:
    def __init__(self, game: Game):
        self.game = game
        self.turn_controller = game.turn_controller
        self.ai_controller = game.ai_controller
        self.log = []  # ✅ FIX: Added missing log attribute

    def run(self):
        while not self.game.is_over():
            unit = self.game.get_current_unit()
            if self.turn_controller.is_ai_turn():
                self.ai_controller.take_action(unit)
                self.log.append(f"AI acted with {unit.name}")
                self.turn_controller.end_turn()
            else:
                self.log.append(f"Skipped player turn for {unit.name}")
                self.turn_controller.end_turn()
