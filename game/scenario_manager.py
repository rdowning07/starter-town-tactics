"""
Scenario Manager - manages scenario progression with full architecture integration.
Integrated with GameState, EnemyAI, EventManager, and includes validation and logging.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from game.ai.enemy_ai import AIBehaviorType, EnemyAI
from game.event_triggers import EventManager, EventTrigger


# @api
# @refactor
class ScenarioStep:
    """Represents a single step in a scenario."""

    def __init__(self, step_data: Dict[str, Any]):
        self.name = step_data.get("name", "unnamed_step")
        self.description = step_data.get("description", "")
        self.objectives = step_data.get("objectives", [])
        self.enemies = step_data.get("enemies", [])
        self.events = step_data.get("events", [])
        self.escalation = step_data.get("escalation", {})
        self.conditions = step_data.get("conditions", {})
        self.rewards = step_data.get("rewards", {})
        self.timeout = step_data.get("timeout", 0)
        self.completed = False


class ScenarioManager:
    """Manages scenario progression with full architecture integration."""

    def __init__(self, scenario_file: Union[str, Path], event_manager: Optional[EventManager] = None, logger=None):
        self.scenario_file = Path(scenario_file)
        self.event_manager = event_manager
        self.logger = logger
        self.scenario_data = {}
        self.steps = []
        self.current_step_index = 0
        self.scenario_state = {}
        self.active_ais = {}
        self.escalation_level = 1.0
        self.scenario_start_time = 0

        # Load scenario
        self._load_scenario()

    def _load_scenario(self):
        """Load scenario from YAML file."""
        try:
            if not self.scenario_file.exists():
                if self.logger:
                    self.logger.log_event("scenario_file_missing", {"file": str(self.scenario_file)})
                self._create_default_scenario()
                return

            with open(self.scenario_file, "r") as f:
                self.scenario_data = yaml.safe_load(f)

            # Parse steps
            self.steps = [ScenarioStep(step_data) for step_data in self.scenario_data.get("steps", [])]

            # Initialize scenario state
            self.scenario_state = {
                "name": self.scenario_data.get("name", "Unknown Scenario"),
                "description": self.scenario_data.get("description", ""),
                "difficulty": self.scenario_data.get("difficulty", "normal"),
                "max_turns": self.scenario_data.get("max_turns", 50),
                "victory_conditions": self.scenario_data.get("victory_conditions", []),
                "defeat_conditions": self.scenario_data.get("defeat_conditions", []),
            }

            if self.logger:
                self.logger.log_event(
                    "scenario_loaded",
                    {
                        "scenario": self.scenario_state["name"],
                        "steps": len(self.steps),
                        "difficulty": self.scenario_state["difficulty"],
                    },
                )

        except Exception as e:
            if self.logger:
                self.logger.log_event("scenario_load_error", {"file": str(self.scenario_file), "error": str(e)})
            self._create_default_scenario()

    def _create_default_scenario(self):
        """Create a default scenario if file is missing or invalid."""
        self.scenario_data = {
            "name": "Default Demo Scenario",
            "description": "Basic scenario for testing",
            "difficulty": "easy",
            "max_turns": 30,
            "victory_conditions": ["eliminate_all_enemies"],
            "defeat_conditions": ["all_players_dead"],
            "steps": [
                {
                    "name": "Initial Encounter",
                    "description": "First wave of enemies",
                    "enemies": [
                        {"type": "goblin", "position": [7, 7], "behavior": "aggressive"},
                        {"type": "goblin", "position": [8, 7], "behavior": "patrol"},
                    ],
                    "objectives": ["Defeat all enemies"],
                    "escalation": {"enemy_hp_multiplier": 1.0, "enemy_damage_multiplier": 1.0},
                },
                {
                    "name": "Reinforcements",
                    "description": "Additional enemies arrive",
                    "enemies": [
                        {"type": "goblin", "position": [9, 8], "behavior": "aggressive"},
                        {"type": "orc", "position": [8, 9], "behavior": "defensive"},
                    ],
                    "objectives": ["Survive the reinforcements"],
                    "escalation": {"enemy_hp_multiplier": 1.2, "enemy_damage_multiplier": 1.1},
                },
            ],
        }

        self.steps = [ScenarioStep(step_data) for step_data in self.scenario_data["steps"]]
        self.scenario_state = {
            "name": self.scenario_data["name"],
            "description": self.scenario_data["description"],
            "difficulty": self.scenario_data["difficulty"],
            "max_turns": self.scenario_data["max_turns"],
            "victory_conditions": self.scenario_data["victory_conditions"],
            "defeat_conditions": self.scenario_data["defeat_conditions"],
        }

    def start_scenario(self, game_state) -> bool:
        """Start the scenario."""
        if not self.steps:
            if self.logger:
                self.logger.log_event("scenario_start_failed", {"reason": "no_steps"})
            return False

        self.current_step_index = 0
        self.escalation_level = 1.0
        self.scenario_start_time = 0  # Could be set to actual time if needed

        # Reset all steps
        for step in self.steps:
            step.completed = False

        if self.logger:
            self.logger.log_event(
                "scenario_started", {"scenario": self.scenario_state["name"], "total_steps": len(self.steps)}
            )

        return True

    def run_step(self, game_state) -> Dict[str, Any]:
        """Run the current scenario step."""
        if self.current_step_index >= len(self.steps):
            return {"success": False, "reason": "scenario_complete"}

        current_step = self.steps[self.current_step_index]

        if current_step.completed:
            return {"success": False, "reason": "step_already_completed"}

        # Execute step
        step_result = self._execute_step(current_step, game_state)

        if self.logger:
            self.logger.log_event(
                "scenario_step_executed",
                {"step_index": self.current_step_index, "step_name": current_step.name, "result": step_result},
            )

        return step_result

    def _execute_step(self, step: ScenarioStep, game_state) -> Dict[str, Any]:
        """Execute a scenario step."""
        executed_actions = []

        # Spawn enemies
        for enemy_data in step.enemies:
            enemy_result = self._spawn_enemy(enemy_data, game_state)
            if enemy_result:
                executed_actions.append(f"spawned_{enemy_data.get('type', 'unknown')}")

        # Trigger events
        if self.event_manager:
            for event_data in step.events:
                event_result = self._create_scenario_event(event_data, game_state)
                if event_result:
                    executed_actions.append(f"event_{event_data.get('type', 'unknown')}")

        # Apply escalation
        if step.escalation:
            self._apply_escalation(step.escalation, game_state)
            executed_actions.append("escalation_applied")

        step.completed = True

        return {"success": True, "step_name": step.name, "actions": executed_actions, "objectives": step.objectives}

    def _spawn_enemy(self, enemy_data: Dict[str, Any], game_state) -> bool:
        """Spawn an enemy unit."""
        if not hasattr(game_state, "units") or not hasattr(game_state.units, "units"):
            return False

        # Generate unique enemy ID
        enemy_type = enemy_data.get("type", "enemy")
        enemy_id = f"{enemy_type}_{len([u for u in game_state.units.units.keys() if u.startswith(enemy_type)]) + 1}"

        # Create enemy unit data
        position = enemy_data.get("position", [5, 5])
        enemy_unit = {
            "unit_id": enemy_id,
            "x": position[0],
            "y": position[1],
            "hp": enemy_data.get("hp", 15),
            "max_hp": enemy_data.get("max_hp", 15),
            "team": "enemy",
            "alive": True,
            "type": enemy_type,
            "attack_range": enemy_data.get("attack_range", 1),
            "detection_range": enemy_data.get("detection_range", 3),
            "support_range": enemy_data.get("support_range", 2),
            "level": enemy_data.get("level", 1),
        }

        # Apply escalation to enemy stats
        enemy_unit["hp"] = int(enemy_unit["hp"] * self.escalation_level)
        enemy_unit["max_hp"] = int(enemy_unit["max_hp"] * self.escalation_level)

        # Add to game state
        game_state.units.units[enemy_id] = enemy_unit

        # Create AI for enemy
        behavior_name = enemy_data.get("behavior", "aggressive")
        try:
            behavior_type = AIBehaviorType(behavior_name)
        except ValueError:
            behavior_type = AIBehaviorType.AGGRESSIVE

        enemy_ai = EnemyAI(enemy_id, behavior_type, self.logger)
        self.active_ais[enemy_id] = enemy_ai

        if self.logger:
            self.logger.log_event(
                "enemy_spawned",
                {
                    "enemy_id": enemy_id,
                    "type": enemy_type,
                    "position": position,
                    "behavior": behavior_name,
                    "hp": enemy_unit["hp"],
                },
            )

        return True

    def _create_scenario_event(self, event_data: Dict[str, Any], game_state) -> bool:
        """Create and add a scenario event."""
        if not self.event_manager:
            return False

        event_type = event_data.get("type", "trap_activation")
        event_params = event_data.get("params", {})

        try:
            event = self.event_manager.create_event(event_type, **event_params)
            if event:
                self.event_manager.add_event(event)
                return True
        except Exception as e:
            if self.logger:
                self.logger.log_event("scenario_event_error", {"event_type": event_type, "error": str(e)})

        return False

    def _apply_escalation(self, escalation_data: Dict[str, Any], game_state):
        """Apply escalation modifiers."""
        # Update escalation level
        hp_multiplier = escalation_data.get("enemy_hp_multiplier", 1.0)
        damage_multiplier = escalation_data.get("enemy_damage_multiplier", 1.0)

        self.escalation_level *= max(hp_multiplier, damage_multiplier)

        # Apply to existing enemies
        if hasattr(game_state, "units") and hasattr(game_state.units, "units"):
            for unit_id, unit_data in game_state.units.units.items():
                if unit_data.get("team") == "enemy" and unit_data.get("alive", True):
                    if hp_multiplier != 1.0:
                        unit_data["max_hp"] = int(unit_data["max_hp"] * hp_multiplier)
                        unit_data["hp"] = int(unit_data["hp"] * hp_multiplier)

        # Update AI aggression
        aggression_modifier = escalation_data.get("aggression_modifier", 1.0)
        for ai in self.active_ais.values():
            ai.aggression_level *= aggression_modifier

        if self.logger:
            self.logger.log_event(
                "escalation_applied",
                {
                    "hp_multiplier": hp_multiplier,
                    "damage_multiplier": damage_multiplier,
                    "new_escalation_level": self.escalation_level,
                },
            )

    def advance_step(self) -> bool:
        """Advance to the next step."""
        if self.current_step_index >= len(self.steps) - 1:
            return False  # Already at last step

        self.current_step_index += 1

        if self.logger:
            self.logger.log_event(
                "scenario_step_advanced",
                {
                    "new_step_index": self.current_step_index,
                    "step_name": self.steps[self.current_step_index].name
                    if self.current_step_index < len(self.steps)
                    else "complete",
                },
            )

        return True

    def check_step_completion(self, game_state) -> bool:
        """Check if current step is complete."""
        if self.current_step_index >= len(self.steps):
            return True

        current_step = self.steps[self.current_step_index]

        # Check completion conditions
        if current_step.conditions:
            return self._evaluate_conditions(current_step.conditions, game_state)

        # Default: step is complete if all enemies are dead
        if hasattr(game_state, "units") and hasattr(game_state.units, "units"):
            enemy_count = sum(
                1 for unit in game_state.units.units.values() if unit.get("team") == "enemy" and unit.get("alive", True)
            )
            return enemy_count == 0

        return False

    def _evaluate_conditions(self, conditions: Dict[str, Any], game_state) -> bool:
        """Evaluate step completion conditions."""
        condition_type = conditions.get("type", "enemies_defeated")

        if condition_type == "enemies_defeated":
            target_count = conditions.get("count", 0)
            if hasattr(game_state, "units") and hasattr(game_state.units, "units"):
                defeated_enemies = sum(
                    1
                    for unit in game_state.units.units.values()
                    if unit.get("team") == "enemy" and not unit.get("alive", True)
                )
                return defeated_enemies >= target_count

        elif condition_type == "turns_survived":
            target_turns = conditions.get("turns", 10)
            current_turns = getattr(game_state, "turn_count", 0)
            return current_turns >= target_turns

        elif condition_type == "area_reached":
            target_pos = conditions.get("position", [0, 0])
            if hasattr(game_state, "units") and hasattr(game_state.units, "units"):
                for unit in game_state.units.units.values():
                    if unit.get("team") == "player" and unit.get("alive", True):
                        if (unit["x"], unit["y"]) == tuple(target_pos):
                            return True

        return False

    def process_ai_turns(self, game_state) -> List[Dict[str, Any]]:
        """Process AI turns for all active enemies."""
        ai_actions = []

        for unit_id, ai in list(self.active_ais.items()):
            # Check if unit is still alive
            if hasattr(game_state, "units") and hasattr(game_state.units, "units"):
                unit_data = game_state.units.units.get(unit_id)
                if not unit_data or not unit_data.get("alive", True):
                    # Remove dead AI
                    del self.active_ais[unit_id]
                    continue

            # Get AI decision
            action_result = ai.decide_action(game_state)
            if action_result.get("action") != "none":
                ai_actions.append({"unit_id": unit_id, "action": action_result})

                # Execute the action
                self._execute_ai_action(unit_id, action_result, game_state)

        return ai_actions

    def _execute_ai_action(self, unit_id: str, action_result: Dict[str, Any], game_state):
        """Execute an AI action."""
        action = action_result.get("action")

        if action == "move":
            target_pos = action_result.get("target_pos")
            if target_pos and hasattr(game_state, "units") and hasattr(game_state.units, "units"):
                unit_data = game_state.units.units.get(unit_id)
                if unit_data:
                    unit_data["x"] = target_pos[0]
                    unit_data["y"] = target_pos[1]

        elif action == "attack":
            target = action_result.get("target")
            if target and hasattr(game_state, "units") and hasattr(game_state.units, "units"):
                # Simple attack: reduce target HP
                damage = 5  # Base damage
                target["hp"] = max(0, target["hp"] - damage)
                if target["hp"] <= 0:
                    target["alive"] = False

        # Update AI behavior history
        ai = self.active_ais.get(unit_id)
        if ai:
            success = action_result.get("reason") != "cannot_move_to_target"
            ai.update_behavior_history(action_result, success)

    def get_scenario_status(self) -> Dict[str, Any]:
        """Get comprehensive scenario status."""
        current_step = self.steps[self.current_step_index] if self.current_step_index < len(self.steps) else None

        return {
            "scenario_name": self.scenario_state["name"],
            "current_step_index": self.current_step_index,
            "total_steps": len(self.steps),
            "current_step_name": current_step.name if current_step else "Complete",
            "escalation_level": self.escalation_level,
            "active_ais": len(self.active_ais),
            "scenario_complete": self.current_step_index >= len(self.steps),
            "difficulty": self.scenario_state["difficulty"],
        }

    def is_scenario_complete(self) -> bool:
        """Check if scenario is complete."""
        return self.current_step_index >= len(self.steps)

    def reset_scenario(self):
        """Reset scenario to beginning."""
        self.current_step_index = 0
        self.escalation_level = 1.0
        self.active_ais.clear()

        for step in self.steps:
            step.completed = False

        if self.logger:
            self.logger.log_event("scenario_reset", {"scenario": self.scenario_state["name"]})

    def save_scenario_state(self, filename: str) -> bool:
        """Save current scenario state to file."""
        try:
            state_data = {
                "scenario_name": self.scenario_state["name"],
                "current_step_index": self.current_step_index,
                "escalation_level": self.escalation_level,
                "step_completion": [step.completed for step in self.steps],
                "active_ai_count": len(self.active_ais),
            }

            with open(filename, "w") as f:
                json.dump(state_data, f, indent=2)

            if self.logger:
                self.logger.log_event("scenario_state_saved", {"filename": filename})

            return True
        except Exception as e:
            if self.logger:
                self.logger.log_event("scenario_state_save_error", {"filename": filename, "error": str(e)})
            return False
