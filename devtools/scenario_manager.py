# devtools/scenario_manager.py

import os
import time
from typing import Any, Dict, Optional

import pygame
import yaml

from game.fx_manager import FXManager
from game.game_state import GameState
from game.sound_manager import SoundManager
from game.sprite_manager import SpriteManager
from game.unit import Unit


class ScenarioManager:
    """Manages scenario execution with integrated camera, AI, and player controls."""

    def __init__(self, camera, ai_controller, player_unit, game_state: GameState):
        self.camera = camera
        self.ai_controller = ai_controller
        self.player_unit = player_unit
        self.game_state = game_state
        self.sprite_manager: Optional[SpriteManager] = None
        self.fx_manager: Optional[FXManager] = None
        self.sound_manager: Optional[SoundManager] = None
        self.supported_sprites = ["knight", "rogue", "mage", "archer", "paladin", "shadow", "berserker"]
        self.supported_ai_types = ["aggressive", "defensive", "passive"]

    def set_managers(self, sprite_manager: SpriteManager, fx_manager: FXManager, sound_manager: SoundManager):
        """Set the required managers for scenario execution."""
        self.sprite_manager = sprite_manager
        self.fx_manager = fx_manager
        self.sound_manager = sound_manager

    def load_scenario(self, scenario_path: str, allow_branching: bool = True) -> GameState:
        """Load and execute a scenario based on its path."""
        if not os.path.exists(scenario_path):
            raise FileNotFoundError(f"Scenario file not found: {scenario_path}")

        scenario_data = self._load_yaml(scenario_path)
        self._validate_scenario(scenario_data)

        # Load units into game state (only for legacy format)
        if "units" in scenario_data:
            self._load_units(scenario_data.get("units", []))
        else:
            # New format: units are defined elsewhere or loaded separately
            print(f"📋 New format scenario detected - units must be loaded separately")

        # Execute scenario actions
        self._execute_scenario(scenario_data, allow_branching)

        return self.game_state

    def _load_yaml(self, scenario_path: str) -> Dict[str, Any]:
        """Load a YAML scenario file."""
        with open(scenario_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def _validate_scenario(self, scenario_data: Dict[str, Any]) -> None:
        """Validate scenario data structure."""
        # Check for new simplified format first
        if "scenario" in scenario_data:
            # New format: simplified structure without units section
            if not isinstance(scenario_data["scenario"], str):
                raise ValueError("Scenario name must be a string")
            return

        # Legacy format: requires name and units
        required_fields = ["name", "units"]
        for field in required_fields:
            if field not in scenario_data:
                raise ValueError(f"Scenario missing required field: {field}")

        if not isinstance(scenario_data["units"], list):
            raise ValueError("Scenario units must be a list")

        # Validate each unit
        for i, unit_data in enumerate(scenario_data["units"]):
            self._validate_unit(unit_data, i)

    def _validate_unit(self, unit_data: Dict[str, Any], unit_index: int) -> None:
        """Validate unit data structure."""
        required_fields = ["name", "team", "sprite", "x", "y"]
        for field in required_fields:
            if field not in unit_data:
                raise ValueError(f"Unit {unit_index} missing required field: {field}")

        # Validate sprite
        sprite = unit_data["sprite"]
        if sprite not in self.supported_sprites:
            print(f"⚠️  Warning: Unit {unit_data['name']} uses unsupported sprite '{sprite}'")

        # Validate team
        team = unit_data["team"]
        if team not in ["player", "enemy", "neutral"]:
            raise ValueError(f"Unit {unit_data['name']} has invalid team: {team}")

        # Validate coordinates
        x, y = unit_data["x"], unit_data["y"]
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"Unit {unit_data['name']} has invalid coordinates: ({x}, {y})")

        # Validate AI type if present
        if "ai" in unit_data:
            ai_type = unit_data["ai"]
            if ai_type not in self.supported_ai_types:
                print(f"⚠️  Warning: Unit {unit_data['name']} uses unsupported AI type '{ai_type}'")

    def _load_units(self, units_data: list) -> None:
        """Load units from scenario data into game state."""
        for unit_data in units_data:
            self._load_unit(unit_data)

    def _load_unit(self, unit_data: Dict[str, Any]) -> None:
        """Load a single unit from scenario data."""
        # Create unit
        unit = Unit(
            name=unit_data["name"],
            x=unit_data["x"],
            y=unit_data["y"],
            team=unit_data["team"],
            health=unit_data.get("hp", 10),
        )

        # Set HP
        unit.hp = unit_data.get("hp", unit.health)

        # Set initial animation
        initial_animation = unit_data.get("animation", "idle")
        unit.set_animation(initial_animation)

        # Add unit to game state with additional data
        self.game_state.add_unit(unit.name, unit.team, ap=unit_data.get("ap", 3), hp=unit.hp)

        # Store additional unit data in the unit manager
        unit_info = self.game_state.units.units[unit.name]
        unit_info.update(
            {
                "x": unit_data["x"],
                "y": unit_data["y"],
                "sprite": unit_data["sprite"],
                "animation": unit_data.get("animation", "idle"),
                "ai": unit_data.get("ai", None),
                "fake_death": unit_data.get("fake_death", False),
                "revive_hp": unit_data.get("revive_hp", 0),
            }
        )

        # Set AI behavior if specified
        if "ai" in unit_data:
            ai_type = unit_data["ai"]
            print(f"📋 Unit {unit.name} has AI behavior: {ai_type}")

        print(f"✅ Loaded unit: {unit.name} ({unit.team}) at ({unit.x}, {unit.y}) with {unit.hp} HP")

    def _execute_scenario(self, scenario: Dict[str, Any], allow_branching: bool = True) -> None:
        """Execute a scenario including camera, AI, and player actions."""
        # Set scenario metadata - handle both formats
        if "scenario" in scenario:
            # New simplified format
            self.game_state.name = scenario.get("scenario", "Unknown Scenario")
            self.game_state.description = scenario.get("description", "")
            self.game_state.map_id = scenario.get("map_id", "default")
        else:
            # Legacy format
            self.game_state.name = scenario.get("name", "Unknown Scenario")
            self.game_state.description = scenario.get("description", "")
            self.game_state.map_id = scenario.get("map_id", "default")

        # Process Camera Actions
        if "camera" in scenario:
            self._process_camera_actions(scenario["camera"])

        # Process AI Actions
        if "ai" in scenario:
            self._process_ai_actions(scenario["ai"])

        # Process Player Actions
        if "actions" in scenario:
            self._process_player_actions(scenario["actions"])

        # Handle scenario branching only if allowed
        if allow_branching:
            if "branch_conditions" in scenario:
                # New branch_conditions format
                self._check_branch_conditions(scenario)
            elif "next_scenario" in scenario:
                # Legacy next_scenario format
                self._handle_scenario_branching(scenario)

    def _process_camera_actions(self, camera_actions: list) -> None:
        """Execute camera actions based on scenario YAML."""
        for action in camera_actions:
            if action["action"] == "pan":
                targets = action["targets"]
                speed = action.get("speed", 5)
                delay = action.get("delay", 0)

                # Convert targets to Vector2 objects
                vector_targets = []
                for target in targets:
                    if isinstance(target, list) and len(target) == 2:
                        vector_targets.append(pygame.Vector2(target[0], target[1]))

                if vector_targets and self.camera:
                    self.camera.cinematic_pan(vector_targets, speed)
                    if delay > 0:
                        time.sleep(delay)

    def _process_ai_actions(self, ai_actions: list) -> None:
        """Execute AI actions based on scenario YAML."""
        for action in ai_actions:
            unit_name = action["unit"]
            ai_action = action["action"]
            target = action.get("target", None)

            # Check if the AI unit exists in game state
            if self.game_state.units.unit_exists(unit_name):
                # Get unit data for AI behavior
                unit_data = self.game_state.units.units[unit_name]

                if ai_action == "attack":
                    # Check if target unit exists
                    if self.game_state.units.unit_exists(target):
                        print(f"🤖 AI unit {unit_name} attacks {target}")
                        # Apply AI behavior based on unit type
                        if unit_data.get("ai"):
                            self.ai_behavior(unit_data, self.game_state)
                        # TODO: Implement actual attack logic through AI controller
                    else:
                        print(f"⚠️ Target unit {target} not found for AI attack")
                elif ai_action == "move":
                    if isinstance(target, list) and len(target) == 2:
                        print(f"🤖 AI unit {unit_name} moves to {target}")
                        # Apply AI behavior based on unit type
                        if unit_data.get("ai"):
                            self.ai_behavior(unit_data, self.game_state)
                        # TODO: Implement actual move logic through AI controller
            else:
                print(f"⚠️ AI unit {unit_name} not found in game state")

    def _process_player_actions(self, player_actions: list) -> None:
        """Execute player actions based on scenario YAML."""
        for action in player_actions:
            unit_name = action["unit"]
            action_type = action["action"]

            if self.game_state.units.unit_exists(unit_name):
                if action_type == "prepare_for_battle":
                    print(f"⚔️ Unit {unit_name} prepares for battle")
                    # TODO: Implement actual prepare for battle logic
            else:
                print(f"⚠️ Unit {unit_name} not found for action {action_type}")

    def _handle_scenario_branching(self, scenario: Dict[str, Any]) -> None:
        """Check the game state and determine which scenario to load next."""
        next_scenario_config = scenario["next_scenario"]

        # For demo purposes, we'll only branch if explicitly requested
        # In a real game, this would be called during gameplay when conditions are met
        should_branch = scenario.get("metadata", {}).get("auto_branch", False)

        if not should_branch:
            print(f"📋 Scenario branching configured but not auto-triggered")
            return

        # Check conditions for branching
        if isinstance(next_scenario_config, dict):
            # Complex branching with conditions
            condition = next_scenario_config.get("condition", "default")
            if condition == "victory" and self._is_battle_won():
                next_path = next_scenario_config.get("victory_scenario")
            elif condition == "defeat" and self._is_battle_lost():
                next_path = next_scenario_config.get("defeat_scenario")
            else:
                next_path = next_scenario_config.get("default_scenario")
        else:
            # Simple string path (new format)
            next_path = next_scenario_config

        if next_path and os.path.exists(next_path):
            print(f"🔄 Loading next scenario: {next_path}")
            self.load_scenario(next_path, allow_branching=False)
        else:
            print(f"⚠️ Next scenario not found: {next_path}")

    def _is_battle_won(self) -> bool:
        """Check if the player has won the battle."""
        # Check if all enemy units are defeated
        enemy_units = [
            name for name, data in self.game_state.units.get_all_units().items() if data.get("team") == "enemy"
        ]
        return len(enemy_units) == 0

    def _is_battle_lost(self) -> bool:
        """Check if the player has lost the battle."""
        # Check if all player units are defeated
        player_units = [
            name for name, data in self.game_state.units.get_all_units().items() if data.get("team") == "player"
        ]
        return len(player_units) == 0

    def check_and_trigger_branching(self, scenario_data: Dict[str, Any]) -> bool:
        """Check if branching conditions are met and trigger if so. Returns True if branching occurred."""
        # Check for new branch_conditions format first
        if "branch_conditions" in scenario_data:
            return self._check_branch_conditions(scenario_data)

        # Legacy next_scenario format
        if "next_scenario" not in scenario_data:
            return False

        next_scenario_config = scenario_data["next_scenario"]

        # Check conditions for branching
        if isinstance(next_scenario_config, dict):
            # Complex branching with conditions
            condition = next_scenario_config.get("condition", "default")
            if condition == "victory" and self._is_battle_won():
                next_path = next_scenario_config.get("victory_scenario")
            elif condition == "defeat" and self._is_battle_lost():
                next_path = next_scenario_config.get("defeat_scenario")
            else:
                next_path = next_scenario_config.get("default_scenario")
        else:
            # Simple string path (new format)
            next_path = next_scenario_config

        if next_path and os.path.exists(next_path):
            print(f"🔄 Loading next scenario: {next_path}")
            self.load_scenario(next_path, allow_branching=False)
            return True
        else:
            print(f"⚠️ Next scenario not found: {next_path}")
            return False

    def evaluate_condition(self, condition: str) -> bool:
        """Evaluates dynamic conditions based on the game state."""
        if condition == "player_wins":
            return self._is_battle_won()
        elif condition == "player_loses":
            return self._is_battle_lost()
        elif condition == "all_enemies_defeated":
            return self._is_battle_won()  # Same as player_wins for now
        elif condition == "victory":
            return self._is_battle_won()
        elif condition == "defeat":
            return self._is_battle_lost()
        else:
            print(f"⚠️ Unknown condition: {condition}")
            return False

    def _check_branch_conditions(self, scenario_data: Dict[str, Any]) -> bool:
        """Check branch_conditions format and trigger appropriate branching."""
        branch_conditions = scenario_data.get("branch_conditions", [])

        for branch in branch_conditions:
            condition = branch.get("condition")
            next_scenario = branch.get("next_scenario")

            if condition and next_scenario:
                if self.evaluate_condition(condition):
                    print(f"🔄 Condition '{condition}' met, loading: {next_scenario}")
                    if os.path.exists(next_scenario):
                        self.load_scenario(next_scenario, allow_branching=False)
                        return True
                    else:
                        print(f"⚠️ Next scenario not found: {next_scenario}")

        return False

    def ai_behavior(self, unit, game_state):
        """Defines AI behavior based on unit type and game state."""
        if not hasattr(unit, "ai"):
            return

        if unit.ai == "aggressive":
            # Move towards player and attack
            player_units = [
                name for name, data in game_state.units.get_all_units().items() if data.get("team") == "player"
            ]
            if player_units:
                target_name = player_units[0]  # Attack first player unit
                print(f"🤖 {unit.name} (aggressive) attacks {target_name}")
                # TODO: Implement actual attack logic
        elif unit.ai == "defensive":
            # Check for low health and retreat if necessary
            unit_data = game_state.units.units.get(unit.name, {})
            current_hp = unit_data.get("hp", 10)
            max_hp = unit_data.get("max_hp", 10)

            if current_hp < max_hp / 2:
                print(f"🤖 {unit.name} (defensive) retreats due to low health")
                # TODO: Implement retreat logic
            else:
                print(f"🤖 {unit.name} (defensive) heals or defends")
                # TODO: Implement heal/defend logic
        elif unit.ai == "passive":
            # Do nothing unless provoked
            print(f"🤖 {unit.name} (passive) waits")
            pass


def create_scenario_manager(camera, ai_controller, player_unit, game_state: GameState) -> ScenarioManager:
    """Convenience function to create a ScenarioManager."""
    return ScenarioManager(camera, ai_controller, player_unit, game_state)
