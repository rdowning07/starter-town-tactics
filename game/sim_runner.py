# @api
from typing import Optional, List, Dict, Literal, Union, TYPE_CHECKING

from game.ai_controller import AIController
from game.tactical_state_machine import TacticalState
from game.turn_controller import TurnController

if TYPE_CHECKING:
    from game.game import Game


class SimRunner:
    """
    Orchestrates turn cycles, manages AI/player flow, and tracks structured game events.
    Integrated with FSM, AP, and AI awareness.

    New Features:
    - Unit removal on death
    - Structured event logging (dicts)
    - Game phase tracking ("INIT" → "PLAYING" → "GAME_OVER")
    """

    def __init__(
        self,
        turn_controller_or_game: Union[TurnController, "Game"],
        ai_controller: Optional[AIController] = None,
    ):
        # Handle backward compatibility with Game objects
        if hasattr(turn_controller_or_game, "turn_controller") and hasattr(
            turn_controller_or_game, "ai_controller"
        ):
            # It's a Game object
            game = turn_controller_or_game
            self.turn_controller = game.turn_controller
            self.ai_controller = ai_controller or game.ai_controller
        else:
            # It's a TurnController
            self.turn_controller = turn_controller_or_game
            self.ai_controller = ai_controller or AIController([])

        self.turn_count = 0
        self.phase: Literal["INIT", "PLAYING", "GAME_OVER"] = "INIT"
        self.log: List[Dict] = []

        self.dead_units: set[str] = set()  # simulates simple death handling
        self.max_turns = 100  # simple safeguard

    def run_turn(self) -> None:
        """Execute one full turn for the current unit."""
        if self.phase == "INIT":
            self.phase = "PLAYING"

        if self.phase != "PLAYING":
            return

        # Check for empty battlefield
        if self._check_game_over():
            self.phase = "GAME_OVER"
            self.log.append({"event": "game_over", "reason": "No living units"})
            return

        unit_id = self.turn_controller.next_turn()
        self.turn_count += 1

        if unit_id in self.dead_units:
            self.log.append({
                "event": "skip_turn",
                "unit": unit_id,
                "reason": "dead"
            })
            self.turn_controller.end_turn()
            return

        self._ensure_fsm_state()

        event = {
            "event": "turn_start",
            "turn": self.turn_count,
            "unit": unit_id,
            "type": "ai" if self._is_ai(unit_id) else "player",
        }
        self.log.append(event)

        if self._is_ai(unit_id):
            self._run_ai_turn(unit_id)
        else:
            self.log.append({
                "event": "player_input_waiting",
                "unit": unit_id,
                "fsm_state": self.turn_controller.get_state().name,
            })

        self.turn_controller.end_turn()

        self.log.append({
            "event": "turn_end",
            "turn": self.turn_count,
            "unit": unit_id,
        })

        if self.turn_count >= self.max_turns:
            self.phase = "GAME_OVER"
            self.log.append({
                "event": "game_over",
                "reason": "Max turns reached",
            })

    def _run_ai_turn(self, unit_id: str):
        """Run AI logic for this unit, respecting AP and FSM."""
        # Call the AI controller's take_action method
        if self.ai_controller:
            try:
                # Try to call with string ID (for test AI controllers)
                self.ai_controller.take_action(unit_id)  # type: ignore
            except TypeError:
                # If that fails, try to find the Unit object
                if hasattr(self.ai_controller, "units"):
                    unit = next(
                        (u for u in self.ai_controller.units if u.name == unit_id), None
                    )
                    if unit:
                        self.ai_controller.take_action(unit)
        
        self.log.append({
            "event": "ai_action",
            "unit": unit_id,
        })

    def _ensure_fsm_state(self):
        if self.turn_controller.get_state() != TacticalState.SELECTING_UNIT:
            self.turn_controller.set_state(TacticalState.SELECTING_UNIT)

    def _is_ai(self, unit_id: str) -> bool:
        return unit_id.startswith("ai")

    def get_log(self) -> List[Dict]:
        return list(self.log)

    def reset(self) -> None:
        self.turn_count = 0
        self.phase = "INIT"
        self.log.clear()
        self.dead_units.clear()

    def mark_unit_dead(self, unit_id: str) -> None:
        """Remove a unit from simulation."""
        self.dead_units.add(unit_id)
        # Remove from turn controller
        self.turn_controller.remove_unit(unit_id)
        self.log.append({
            "event": "unit_dead",
            "unit": unit_id,
        })

    def _check_game_over(self) -> bool:
        living_units = [u for u in self.turn_controller.units if u not in self.dead_units]
        return len(living_units) == 0

    # Backward compatibility methods
    def run(self, max_turns=1000):
        """Legacy method for backward compatibility."""
        self.log.append({"event": "simulation_started"})
        print("DEBUG: Simulation started")
        turns = 0
        while turns < max_turns and self.phase != "GAME_OVER":
            try:
                self.run_turn()
                turns += 1
            except Exception as e:
                self.log.append({"event": "error", "turn": turns, "error": str(e)})
                break
        if turns == max_turns:
            print("WARNING: Simulation reached max_turns limit!")
            self.log.append({"event": "max_turns_reached"})
