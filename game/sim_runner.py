"""Simulates a full round of turns for automated testing or scenario playback."""

from game.ai_controller import AIController
from game.game import Game
from game.input_state import InputState
from game.turn_controller import TurnController, TurnPhase
from game.unit import Unit
from game.mcp import MCP


def simulate_battle(use_mcp=False, strategy="nearest"):
    game = Game(10, 10)
    game.add_unit(Unit("Knight", 2, 2, team="Red"))
    game.add_unit(Unit("Goblin", 1, 1, team="Blue"))

    turn_controller = TurnController()
    mcp_agent = MCP(strategy=strategy) if use_mcp else None
    ai_controller = AIController(game, mcp_agent=mcp_agent)
    input_state = InputState(game)

    log = []

    for _ in range(10):  # Simulate 10 turns
        phase = turn_controller.get_phase()
        if phase == TurnPhase.PLAYER:
            input_state.cursor_x = 1
            input_state.cursor_y = 1
            input_state.confirm_selection()
            if input_state.selected_unit:
                input_state.cursor_x = 3
                input_state.cursor_y = 3
                input_state.confirm_selection()
            turn_controller.advance_turn()
        elif phase == TurnPhase.AI:
            ai_controller.take_turn()
            turn_controller.advance_turn()

        log.append(f"Turn {game.current_turn}: {phase.name} — Last action: {ai_controller.last_action}")

    return log


if __name__ == "__main__":
    log = simulate_battle(use_mcp=True)
    for entry in log:
        print(entry)
