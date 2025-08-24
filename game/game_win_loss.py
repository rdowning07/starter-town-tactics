"""
Game Win/Loss Logic - detects victory/defeat conditions with full architecture integration.
Integrated with GameState, SimRunner, and includes validation and logging.
"""

from typing import Dict

# @api
# @refactor
class GameWinLoss:
    """Detects victory/defeat conditions with full architecture integration."""

    def __init__(self, logger=None):
        self.logger = logger
        self.game_status = "playing"  # playing, victory, defeat, draw
        self.victory_conditions = []
        self.defeat_conditions = []
        self._victory_message = ""
        self._defeat_message = ""

    def check_victory_conditions(self, game_state) -> bool:
        """Check all victory conditions with validation and logging."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return False

        # Get all units
        all_units = game_state.units.units

        # Check if all enemies are dead
        enemies_alive = any(
            unit_data.get("alive", True)
            for unit_data in all_units.values()
            if unit_data.get("team") == "enemy"
        )

        # Check if all players are dead
        players_alive = any(
            unit_data.get("alive", True)
            for unit_data in all_units.values()
            if unit_data.get("team") == "player"
        )

        # Determine game status
        if not enemies_alive and players_alive:
            self._set_victory(game_state, "All enemies defeated")
            return True
        if not players_alive and enemies_alive:
            self._set_defeat(game_state, "All player units defeated")
            return True
        if not enemies_alive and not players_alive:
            self._set_draw(game_state, "All units defeated")
            return True

        return False

    def check_custom_victory_conditions(self, game_state) -> bool:
        """Check custom victory conditions (e.g., reach objective, survive turns)."""
        if not hasattr(game_state, 'sim_runner'):
            return False

        # Check turn-based victory (survive X turns)
        turn_count = getattr(game_state.sim_runner, 'turn_count', 0)
        if hasattr(game_state, 'victory_turns') and turn_count >= game_state.victory_turns:
            self._set_victory(game_state, f"Survived {turn_count} turns")
            return True

        # Check objective-based victory (reach specific tile)
        if hasattr(game_state, 'objective_tile'):
            objective_x, objective_y = game_state.objective_tile
            for unit_data in game_state.units.units.values():
                if (unit_data.get("team") == "player" and
                    unit_data.get("alive", True) and
                    unit_data.get("x") == objective_x and
                    unit_data.get("y") == objective_y):
                    self._set_victory(game_state, f"Reached objective at ({objective_x}, {objective_y})")
                    return True

        return False

    def check_defeat_conditions(self, game_state) -> bool:
        """Check custom defeat conditions."""
        if not hasattr(game_state, 'sim_runner'):
            return False

        # Check turn-based defeat (time limit)
        turn_count = getattr(game_state.sim_runner, 'turn_count', 0)
        if hasattr(game_state, 'defeat_turns') and turn_count >= game_state.defeat_turns:
            self._set_defeat(game_state, f"Time limit exceeded ({turn_count} turns)")
            return True

        return False

    def get_game_status(self) -> str:
        """Get current game status."""
        return self.game_status

    def get_victory_message(self) -> str:
        """Get victory message."""
        return getattr(self, '_victory_message', "Victory!")

    def get_defeat_message(self) -> str:
        """Get defeat message."""
        return getattr(self, '_defeat_message', "Defeat!")

    def reset_game_status(self):
        """Reset game status to playing."""
        self.game_status = "playing"
        self._victory_message = ""
        self._defeat_message = ""

    def _set_victory(self, game_state, message: str):
        """Set victory status with logging."""
        self.game_status = "victory"
        self._victory_message = message

        # Set game state status
        if hasattr(game_state, 'status'):
            game_state.status = "victory"

        # Log victory
        if self.logger:
            self.logger.log_event("game_victory", {
                "message": message,
                "turn_count": getattr(game_state.sim_runner, 'turn_count', 0),
                "player_units": self._count_team_units(game_state, "player"),
                "enemy_units": self._count_team_units(game_state, "enemy")
            })

        print(f"🎉 VICTORY: {message}")

    def _set_defeat(self, game_state, message: str):
        """Set defeat status with logging."""
        self.game_status = "defeat"
        self._defeat_message = message

        # Set game state status
        if hasattr(game_state, 'status'):
            game_state.status = "defeat"

        # Log defeat
        if self.logger:
            self.logger.log_event("game_defeat", {
                "message": message,
                "turn_count": getattr(game_state.sim_runner, 'turn_count', 0),
                "player_units": self._count_team_units(game_state, "player"),
                "enemy_units": self._count_team_units(game_state, "enemy")
            })

        print(f"💀 DEFEAT: {message}")

    def _set_draw(self, game_state, message: str):
        """Set draw status with logging."""
        self.game_status = "draw"

        # Set game state status
        if hasattr(game_state, 'status'):
            game_state.status = "draw"

        # Log draw
        if self.logger:
            self.logger.log_event("game_draw", {
                "message": message,
                "turn_count": getattr(game_state.sim_runner, 'turn_count', 0)
            })

        print(f"🤝 DRAW: {message}")

    def _count_team_units(self, game_state, team: str) -> Dict[str, int]:
        """Count units by team and status."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return {"alive": 0, "dead": 0}

        alive_count = 0
        dead_count = 0

        for unit_data in game_state.units.units.values():
            if unit_data.get("team") == team:
                if unit_data.get("alive", True):
                    alive_count += 1
                else:
                    dead_count += 1

        return {"alive": alive_count, "dead": dead_count}

    def get_game_summary(self, game_state) -> Dict:
        """Get comprehensive game summary."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return {}

        turn_count = getattr(game_state.sim_runner, 'turn_count', 0)
        player_units = self._count_team_units(game_state, "player")
        enemy_units = self._count_team_units(game_state, "enemy")

        return {
            "status": self.game_status,
            "turn_count": turn_count,
            "player_units": player_units,
            "enemy_units": enemy_units,
            "victory_message": self.get_victory_message(),
            "defeat_message": self.get_defeat_message()
        }

# Backward compatibility function
def check_victory(game_state) -> bool:
    """Backward compatibility function for simple victory check."""
    win_loss = GameWinLoss()
    return win_loss.check_victory_conditions(game_state)
