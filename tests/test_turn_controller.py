from game.turn_controller import TurnController



def test_turn_cycle():
    controller = TurnController()
    assert controller.current_phase == TurnPhase.PLAYER
    controller.next_turn()
    assert controller.current_phase == TurnPhase.ENEMY
    controller.next_turn()
    assert controller.current_phase == TurnPhase.PLAYER
