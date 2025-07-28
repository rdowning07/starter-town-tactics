from game.unit import Unit


class AIController:
    def __init__(self, game):
        self.game = game

    def take_turn(self):
        for unit in self.game.units:
            if unit.team == "Red":
                target_x, target_y = unit.x + 1, unit.y
                unit.move(target_x, target_y)
