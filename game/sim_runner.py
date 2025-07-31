# @api
# game/sim_runner.py

from game.game import Game


class SimRunner:
    def __init__(self, game: Game):
        self.game = game
        self.turn_controller = game.turn_controller
        self.ai_controller = game.ai_controller
        self.log: list[str] = []  # ✅ FIX: Added missing log attribute

    def run(self, max_turns=1000):
        self.log.append('Simulation started')
        print('DEBUG: Simulation started')
        turns = 0
        while not self.game.is_over() and turns < max_turns:
            unit = self.game.get_current_unit()
            print(f'DEBUG: Turn {turns}, Current unit: {unit}')
            if self.turn_controller.is_ai_turn():
                print(f'DEBUG: AI turn for {unit}')
                self.ai_controller.take_action(unit)
                self.log.append(f"AI acted with {unit.name}")
                self.turn_controller.end_turn()
            else:
                print(f'DEBUG: Skipped player turn for {unit}')
                self.log.append(f"Skipped player turn for {unit.name}")
                self.turn_controller.end_turn()
            turns += 1
        if turns == max_turns:
            print("WARNING: Simulation reached max_turns limit!")
