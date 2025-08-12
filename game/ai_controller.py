"""AI behavior logic."""

from __future__ import annotations

from game.grid import Grid
from game.unit import Unit


class AIController:
    def __init__(self, units: list[Unit]):
        self.units = units
        self.game_state = None  # Will be set by GameState

    def set_game_state(self, game_state):
        """Set the game state reference for enhanced AI behavior."""
        self.game_state = game_state

    def update(self, grid: Grid):
        for unit in self.units:
            if unit.hp <= 0:
                continue
            new_x, new_y = unit.x, min(grid.height - 1, unit.y + 1)
            unit.move(new_x, new_y, grid)

    def take_action(self, unit: Unit):
        """Take action for the given unit."""
        print(f"DEBUG: AIController.take_action called for {unit.name}")

        # Set attack animation
        unit.set_animation("attack")

        # Enhanced AI behavior based on unit type
        if hasattr(unit, 'ai') and unit.ai:
            self.decide_action(unit)
        else:
            # Fallback to simple behavior
            grid = unit.grid if hasattr(unit, "grid") else None
            if grid:
                new_x, new_y = unit.x, min(grid.height - 1, unit.y + 1)
                unit.move(new_x, new_y, grid)

    def attack(self, ai_unit, target_unit):
        """AI attacks a target unit."""
        if hasattr(ai_unit, 'can_attack') and ai_unit.can_attack(target_unit):
            ai_unit.attack(target_unit)
            print(f"{ai_unit.name} attacks {target_unit.name}")
        else:
            print(f"{ai_unit.name} cannot attack {target_unit.name}")

    def retreat(self, ai_unit):
        """AI retreats to a safe spot."""
        safe_position = self.find_safe_position(ai_unit)
        if hasattr(ai_unit, 'move_to'):
            ai_unit.move_to(safe_position)
        print(f"{ai_unit.name} retreats to {safe_position}")

    def heal(self, ai_unit):
        """AI heals itself."""
        if hasattr(ai_unit, 'heal'):
            ai_unit.heal(10)  # Example healing amount
            print(f"{ai_unit.name} heals itself")
        else:
            print(f"{ai_unit.name} cannot heal")

    def move(self, ai_unit, target_position):
        """AI moves towards a target position."""
        if hasattr(ai_unit, 'move_to'):
            ai_unit.move_to(target_position)
            print(f"{ai_unit.name} moves to {target_position}")
        else:
            print(f"{ai_unit.name} cannot move")

    def decide_action(self, ai_unit):
        """Decides what action to take based on AI behavior and health."""
        if not hasattr(ai_unit, 'ai'):
            return
            
        # Check if health is low
        current_hp = getattr(ai_unit, 'hp', 10)
        max_hp = getattr(ai_unit, 'max_hp', 10)
        
        if current_hp < max_hp / 2:  # If health is low
            if ai_unit.ai == "defensive":
                self.retreat(ai_unit)  # Defensive AI retreats
            else:
                self.heal(ai_unit)  # Heal if health is below 50%
        else:
            if ai_unit.ai == "aggressive":
                # Find a target to attack
                if self.game_state:
                    player_units = self.game_state.units.get_unit_ids_by_team("player")
                    if player_units:
                        target_name = player_units[0]  # Attack first player unit
                        print(f"{ai_unit.name} (aggressive) targets {target_name}")
                        # TODO: Implement actual attack logic
            elif ai_unit.ai == "passive":
                print(f"{ai_unit.name} is passive and waiting.")

    def find_safe_position(self, ai_unit):
        """Find a safe position for retreating."""
        # Simple implementation - move away from center
        current_x = getattr(ai_unit, 'x', 0)
        current_y = getattr(ai_unit, 'y', 0)
        return (max(0, current_x - 2), max(0, current_y - 2))


