# @api
from game.action_point_manager import ActionPointManager
from game.ai_controller import AIController
from game.fx_manager import FXManager
from game.sim_runner import SimRunner
from game.tactical_state_machine import TacticalStateMachine
from game.turn_controller import TurnController
from game.unit_manager import UnitManager


class GameState:  # pylint: disable=too-many-instance-attributes
    """
    Dependency hub and global context for all game systems.
    Owns and wires: FSM, TurnController, AP, AI, Units, SimRunner
    """

    def __init__(self) -> None:
        self.units = UnitManager()
        self.ap_manager = ActionPointManager()
        self.fsm = TacticalStateMachine()
        self.turn_controller = TurnController(self.ap_manager, self.fsm)
        self.ai_controller = AIController([])
        self.sim_runner = SimRunner(self.turn_controller, self.ai_controller)
        self.fx_manager = FXManager()

        # Scenario metadata (set by loader)
        self.name: str = ""
        self.description: str = ""
        self.map_id: str = "default_map"
        self.objective: str = "Defeat all enemies"
        self.max_turns: int = 20
        self.metadata: dict = {}

        # Terrain data (loaded via map_loader)
        self.terrain_grid: list[list[str]] = []

    def set_metadata(
        self, name: str, map_id: str, objective: str, max_turns: int
    ) -> None:
        self.name = name
        self.map_id = map_id
        self.objective = objective
        self.max_turns = max_turns

    def add_unit(self, unit_id: str, team: str, ap: int = 2, hp: int = 10) -> None:
        self.units.register_unit(unit_id, team, hp=hp)
        self.turn_controller.add_unit(unit_id)
        self.ap_manager.register_unit(unit_id, ap=ap)

    def get_current_unit(self) -> str:
        return self.turn_controller.get_current_unit()

    def is_ai_turn(self) -> bool:
        uid = self.get_current_unit()
        return self.units.get_team(uid) == "ai"

    def is_game_over(self) -> bool:
        return self.sim_runner.phase == "GAME_OVER"

    def damage_unit(self, unit_id: str, dmg: int) -> bool:
        """Damage a unit and handle death logic. Returns True if unit was damaged."""
        if not self.units.damage_unit(unit_id, dmg):
            return False  # Unit doesn't exist

        if not self.units.is_alive(unit_id):
            self.turn_controller.remove_unit(unit_id)
            self.sim_runner.mark_unit_dead(unit_id)

        return True

    def heal_unit(self, unit_id: str, heal: int) -> bool:
        """Heal a unit. Returns True if unit was healed."""
        return self.units.heal_unit(unit_id, heal)

    def has_won(self) -> bool:
        """Determine if the player has won the scenario."""
        # Basic win condition: all AI units defeated (including fake dead)
        return not self.units.any_effectively_alive("ai")

    def has_lost(self) -> bool:
        """Determine if the player has lost the scenario."""
        # Basic loss condition: all player units defeated or turns exceeded
        player_dead = not self.units.any_effectively_alive("player")
        turns_exceeded = self.turn_controller.current_turn > self.max_turns
        return player_dead or turns_exceeded

    def trigger_fx(self, fx_type: str, position: tuple[int, int], 
                   duration: float = 0.5, intensity: float = 1.0,
                   color: tuple[int, int, int] = (255, 255, 255),
                   size: int = 10) -> None:
        """Trigger a visual effect."""
        self.fx_manager.trigger_fx(fx_type, position, duration, intensity, color, size)

    def trigger_flash(self, position: tuple[int, int], 
                     color: tuple[int, int, int] = (255, 255, 255),
                     duration: float = 0.3, intensity: float = 1.0) -> None:
        """Trigger a flash effect."""
        self.fx_manager.trigger_flash(position, color, duration, intensity)

    def trigger_screen_shake(self, intensity: float = 5.0, duration: float = 0.5) -> None:
        """Trigger screen shake effect."""
        self.fx_manager.trigger_screen_shake(intensity, duration)

    def trigger_particle(self, position: tuple[int, int], 
                        particle_type: str = "sparkle",
                        count: int = 5, duration: float = 1.0) -> None:
        """Trigger particle effect."""
        self.fx_manager.trigger_particle(position, particle_type, count, duration)

    def update_fx(self) -> None:
        """Update all visual effects."""
        self.fx_manager.update()

    def draw_fx(self, screen) -> None:
        """Draw all visual effects."""
        self.fx_manager.draw_fx(screen)

    def clear_fx(self) -> None:
        """Clear all visual effects."""
        self.fx_manager.clear_effects()
