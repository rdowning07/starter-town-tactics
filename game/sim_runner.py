from game.game import Game
from game.unit import Unit

class SimRunner:
    def __init__(self, game: Game):
        self.game = game
        self.turn_controller = game.turn_controller
        self.ai_controller = game.ai_controller

    def run(self):
        while not self.game.is_over():
            unit = self.game.get_current_unit()
            if self.turn_controller.is_ai_turn():
                self.ai_controller.take_action(unit)
                self.turn_controller.end_turn()
            else:
                # For now, we skip player turns in simulation
                self.turn_controller.end_turn()
