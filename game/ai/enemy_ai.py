"""
Enemy AI System - manages AI behaviors with full architecture integration.
Integrated with GameState, UnitManager, StatusEffects, and includes validation and logging.
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import random
import math
from game.status_effects import StatusEffectManager
from game.fx_manager import FXManager

# @api
# @refactor
class AIBehaviorType(Enum):
    """Types of AI behaviors."""
    PATROL = "patrol"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    ADAPTIVE = "adaptive"
    SUPPORT = "support"

class EnemyAI:
    """Manages AI behaviors with full architecture integration."""

    def __init__(self, unit_id: str, behavior_type: AIBehaviorType = AIBehaviorType.AGGRESSIVE,
                 logger=None):
        self.unit_id = unit_id
        self.behavior_type = behavior_type
        self.logger = logger
        self.last_known_player_positions = {}
        self.patrol_path = []
        self.current_patrol_index = 0
        self.aggression_level = 1.0
        self.defensive_threshold = 0.3  # HP percentage to switch to defensive
        self.behavior_history = []

    def decide_action(self, game_state) -> Dict[str, Any]:
        """Decide AI action based on behavior type and game state."""
        if not self._validate_game_state(game_state):
            return {"action": "none", "reason": "invalid_game_state"}

        unit_data = self._get_unit_data(game_state)
        if not unit_data or not unit_data.get("alive", True):
            return {"action": "none", "reason": "unit_dead"}

        # Update player position tracking
        self._update_player_tracking(game_state)

        # Determine behavior based on type and current state
        action_result = self._execute_behavior(game_state, unit_data)

        # Log action
        if self.logger:
            self.logger.log_event("ai_action_decided", {
                "unit": self.unit_id,
                "behavior": self.behavior_type.value,
                "action": action_result.get("action", "none"),
                "reason": action_result.get("reason", ""),
                "aggression_level": self.aggression_level
            })

        return action_result

    def _execute_behavior(self, game_state, unit_data: Dict) -> Dict[str, Any]:
        """Execute behavior based on AI type."""
        if self.behavior_type == AIBehaviorType.AGGRESSIVE:
            return self._aggressive_behavior(game_state, unit_data)
        elif self.behavior_type == AIBehaviorType.DEFENSIVE:
            return self._defensive_behavior(game_state, unit_data)
        elif self.behavior_type == AIBehaviorType.PATROL:
            return self._patrol_behavior(game_state, unit_data)
        elif self.behavior_type == AIBehaviorType.ADAPTIVE:
            return self._adaptive_behavior(game_state, unit_data)
        elif self.behavior_type == AIBehaviorType.SUPPORT:
            return self._support_behavior(game_state, unit_data)
        else:
            return {"action": "wait", "reason": "unknown_behavior"}

    def _aggressive_behavior(self, game_state, unit_data: Dict) -> Dict[str, Any]:
        """Aggressive AI: prioritize attacking nearest player."""
        player_units = self._get_player_units(game_state)
        if not player_units:
            return {"action": "wait", "reason": "no_targets"}

        # Find nearest player
        nearest_target = self._find_nearest_unit(unit_data, player_units)
        if not nearest_target:
            return {"action": "wait", "reason": "no_valid_targets"}

        target_pos = (nearest_target["x"], nearest_target["y"])
        unit_pos = (unit_data["x"], unit_data["y"])
        distance = self._calculate_distance(unit_pos, target_pos)

        # Check if in attack range
        attack_range = unit_data.get("attack_range", 1)
        if distance <= attack_range:
            return {
                "action": "attack",
                "target": nearest_target,
                "target_pos": target_pos,
                "reason": "target_in_range"
            }
        else:
            # Move towards target
            move_pos = self._get_move_towards_target(unit_pos, target_pos, game_state)
            if move_pos:
                return {
                    "action": "move",
                    "target_pos": move_pos,
                    "reason": "moving_to_target"
                }
            else:
                return {"action": "wait", "reason": "cannot_move_to_target"}

    def _defensive_behavior(self, game_state, unit_data: Dict) -> Dict[str, Any]:
        """Defensive AI: prioritize survival and support."""
        current_hp_ratio = unit_data.get("hp", 0) / max(unit_data.get("max_hp", 1), 1)

        # If low HP, try to retreat
        if current_hp_ratio < self.defensive_threshold:
            retreat_pos = self._find_retreat_position(unit_data, game_state)
            if retreat_pos:
                return {
                    "action": "move",
                    "target_pos": retreat_pos,
                    "reason": "retreating_low_hp"
                }

        # Look for support opportunities
        ally_units = self._get_ally_units(game_state)
        for ally in ally_units:
            if ally["hp"] < ally.get("max_hp", ally["hp"]) * 0.5:
                # Try to help wounded ally
                return self._support_ally(unit_data, ally, game_state)

        # Default to defensive positioning
        return {"action": "wait", "reason": "defensive_position"}

    def _patrol_behavior(self, game_state, unit_data: Dict) -> Dict[str, Any]:
        """Patrol AI: follow patrol path, engage if players nearby."""
        # Check for nearby players first
        player_units = self._get_player_units(game_state)
        for player in player_units:
            player_pos = (player["x"], player["y"])
            unit_pos = (unit_data["x"], unit_data["y"])
            distance = self._calculate_distance(unit_pos, player_pos)

            # If player is within detection range, switch to aggressive
            detection_range = unit_data.get("detection_range", 3)
            if distance <= detection_range:
                return self._aggressive_behavior(game_state, unit_data)

        # Continue patrol
        if not self.patrol_path:
            self._generate_patrol_path(unit_data)

        if self.patrol_path:
            target_pos = self.patrol_path[self.current_patrol_index]
            unit_pos = (unit_data["x"], unit_data["y"])

            if unit_pos == target_pos:
                # Reached patrol point, move to next
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                target_pos = self.patrol_path[self.current_patrol_index]

            return {
                "action": "move",
                "target_pos": target_pos,
                "reason": "patrolling"
            }

        return {"action": "wait", "reason": "no_patrol_path"}

    def _adaptive_behavior(self, game_state, unit_data: Dict) -> Dict[str, Any]:
        """Adaptive AI: changes behavior based on game state."""
        # Analyze recent behavior effectiveness
        recent_actions = self.behavior_history[-5:] if len(self.behavior_history) >= 5 else self.behavior_history

        # Check player threat level
        player_units = self._get_player_units(game_state)
        threat_level = self._assess_threat_level(unit_data, player_units)

        # Adapt behavior based on threat and effectiveness
        if threat_level > 0.7:
            # High threat: be defensive
            return self._defensive_behavior(game_state, unit_data)
        elif threat_level > 0.3:
            # Medium threat: be aggressive
            return self._aggressive_behavior(game_state, unit_data)
        else:
            # Low threat: patrol or support
            if random.random() < 0.5:
                return self._patrol_behavior(game_state, unit_data)
            else:
                return self._support_behavior(game_state, unit_data)

    def _support_behavior(self, game_state, unit_data: Dict) -> Dict[str, Any]:
        """Support AI: help allies and provide buffs."""
        ally_units = self._get_ally_units(game_state)

        # Find ally that needs support
        for ally in ally_units:
            if ally["hp"] < ally.get("max_hp", ally["hp"]) * 0.7:
                return self._support_ally(unit_data, ally, game_state)

        # No allies need support, default to defensive
        return self._defensive_behavior(game_state, unit_data)

    def _support_ally(self, unit_data: Dict, ally_data: Dict, game_state) -> Dict[str, Any]:
        """Provide support to an ally."""
        ally_pos = (ally_data["x"], ally_data["y"])
        unit_pos = (unit_data["x"], unit_data["y"])
        distance = self._calculate_distance(unit_pos, ally_pos)

        # If close enough, could cast support spell/ability
        support_range = unit_data.get("support_range", 2)
        if distance <= support_range:
            return {
                "action": "support",
                "target": ally_data,
                "reason": "supporting_ally"
            }
        else:
            # Move closer to ally
            move_pos = self._get_move_towards_target(unit_pos, ally_pos, game_state)
            if move_pos:
                return {
                    "action": "move",
                    "target_pos": move_pos,
                    "reason": "moving_to_support"
                }

        return {"action": "wait", "reason": "cannot_support"}

    def _find_nearest_unit(self, unit_data: Dict, target_units: List[Dict]) -> Optional[Dict]:
        """Find the nearest unit from a list of targets."""
        if not target_units:
            return None

        unit_pos = (unit_data["x"], unit_data["y"])
        nearest_unit = None
        min_distance = float('inf')

        for target in target_units:
            if not target.get("alive", True):
                continue

            target_pos = (target["x"], target["y"])
            distance = self._calculate_distance(unit_pos, target_pos)

            if distance < min_distance:
                min_distance = distance
                nearest_unit = target

        return nearest_unit

    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _get_move_towards_target(self, current_pos: Tuple[int, int],
                                target_pos: Tuple[int, int], game_state) -> Optional[Tuple[int, int]]:
        """Get next move position towards target."""
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]

        # Simple pathfinding: move one step towards target
        next_x = current_pos[0]
        next_y = current_pos[1]

        if abs(dx) > abs(dy):
            next_x += 1 if dx > 0 else -1
        else:
            next_y += 1 if dy > 0 else -1

        next_pos = (next_x, next_y)

        # Check if position is valid and not occupied
        if self._is_valid_position(next_pos, game_state):
            return next_pos

        # Try alternative moves
        alternatives = [
            (current_pos[0] + 1, current_pos[1]),
            (current_pos[0] - 1, current_pos[1]),
            (current_pos[0], current_pos[1] + 1),
            (current_pos[0], current_pos[1] - 1)
        ]

        for alt_pos in alternatives:
            if self._is_valid_position(alt_pos, game_state):
                return alt_pos

        return None

    def _is_valid_position(self, pos: Tuple[int, int], game_state) -> bool:
        """Check if position is valid for movement."""
        # Basic bounds checking (assuming 10x10 grid for now)
        if pos[0] < 0 or pos[0] >= 10 or pos[1] < 0 or pos[1] >= 10:
            return False

        # Check if position is occupied
        if hasattr(game_state, 'units') and hasattr(game_state.units, 'units'):
            for unit_data in game_state.units.units.values():
                if unit_data.get("alive", True) and (unit_data["x"], unit_data["y"]) == pos:
                    return False

        return True

    def _find_retreat_position(self, unit_data: Dict, game_state) -> Optional[Tuple[int, int]]:
        """Find a safe position to retreat to."""
        current_pos = (unit_data["x"], unit_data["y"])
        player_units = self._get_player_units(game_state)

        # Find position furthest from all players
        best_pos = None
        max_min_distance = 0

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0:
                    continue

                candidate_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if not self._is_valid_position(candidate_pos, game_state):
                    continue

                # Calculate minimum distance to any player
                min_distance = float('inf')
                for player in player_units:
                    player_pos = (player["x"], player["y"])
                    distance = self._calculate_distance(candidate_pos, player_pos)
                    min_distance = min(min_distance, distance)

                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_pos = candidate_pos

        return best_pos

    def _generate_patrol_path(self, unit_data: Dict):
        """Generate a patrol path around the unit's starting position."""
        start_pos = (unit_data["x"], unit_data["y"])

        # Simple square patrol pattern
        patrol_radius = 2
        self.patrol_path = [
            (start_pos[0] + patrol_radius, start_pos[1]),
            (start_pos[0] + patrol_radius, start_pos[1] + patrol_radius),
            (start_pos[0], start_pos[1] + patrol_radius),
            (start_pos[0] - patrol_radius, start_pos[1] + patrol_radius),
            (start_pos[0] - patrol_radius, start_pos[1]),
            (start_pos[0] - patrol_radius, start_pos[1] - patrol_radius),
            (start_pos[0], start_pos[1] - patrol_radius),
            (start_pos[0] + patrol_radius, start_pos[1] - patrol_radius),
        ]

        # Filter out invalid positions
        self.patrol_path = [pos for pos in self.patrol_path if 0 <= pos[0] < 10 and 0 <= pos[1] < 10]

        if not self.patrol_path:
            self.patrol_path = [start_pos]

    def _assess_threat_level(self, unit_data: Dict, player_units: List[Dict]) -> float:
        """Assess threat level from player units (0.0 to 1.0)."""
        if not player_units:
            return 0.0

        unit_pos = (unit_data["x"], unit_data["y"])
        total_threat = 0.0

        for player in player_units:
            if not player.get("alive", True):
                continue

            player_pos = (player["x"], player["y"])
            distance = self._calculate_distance(unit_pos, player_pos)

            # Closer players are more threatening
            if distance == 0:
                threat = 1.0
            else:
                threat = 1.0 / distance

            # Player level/stats could modify threat
            player_level = player.get("level", 1)
            threat *= (player_level / 10.0 + 0.5)

            total_threat += threat

        # Normalize to 0.0-1.0 range
        return min(total_threat / len(player_units), 1.0)

    def _get_player_units(self, game_state) -> List[Dict]:
        """Get all player units from game state."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return []

        return [unit for unit in game_state.units.units.values()
                if unit.get("team") == "player" and unit.get("alive", True)]

    def _get_ally_units(self, game_state) -> List[Dict]:
        """Get all ally units from game state."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return []

        return [unit for unit in game_state.units.units.values()
                if unit.get("team") == "enemy" and unit.get("alive", True)
                and unit.get("unit_id") != self.unit_id]

    def _get_unit_data(self, game_state) -> Optional[Dict]:
        """Get this unit's data from game state."""
        if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
            return None

        return game_state.units.units.get(self.unit_id)

    def _update_player_tracking(self, game_state):
        """Update tracking of player positions."""
        player_units = self._get_player_units(game_state)
        for player in player_units:
            unit_id = player.get("unit_id", "unknown")
            self.last_known_player_positions[unit_id] = (player["x"], player["y"])

    def _validate_game_state(self, game_state) -> bool:
        """Validate game state has required components."""
        return (hasattr(game_state, 'units') and
                hasattr(game_state.units, 'units') and
                isinstance(game_state.units.units, dict))

    def update_behavior_history(self, action_result: Dict[str, Any], success: bool):
        """Update behavior history for adaptive learning."""
        self.behavior_history.append({
            "action": action_result.get("action", "none"),
            "behavior": self.behavior_type.value,
            "success": success,
            "aggression_level": self.aggression_level
        })

        # Keep only recent history
        if len(self.behavior_history) > 20:
            self.behavior_history = self.behavior_history[-20:]

        # Adjust aggression based on success
        if success:
            self.aggression_level = min(self.aggression_level * 1.1, 2.0)
        else:
            self.aggression_level = max(self.aggression_level * 0.9, 0.5)

    def set_behavior_type(self, behavior_type: AIBehaviorType):
        """Change AI behavior type."""
        old_behavior = self.behavior_type
        self.behavior_type = behavior_type

        if self.logger:
            self.logger.log_event("ai_behavior_changed", {
                "unit": self.unit_id,
                "old_behavior": old_behavior.value,
                "new_behavior": behavior_type.value
            })

    def get_ai_status(self) -> Dict[str, Any]:
        """Get comprehensive AI status."""
        return {
            "unit_id": self.unit_id,
            "behavior_type": self.behavior_type.value,
            "aggression_level": self.aggression_level,
            "patrol_path_length": len(self.patrol_path),
            "current_patrol_index": self.current_patrol_index,
            "behavior_history_length": len(self.behavior_history),
            "known_player_positions": len(self.last_known_player_positions)
        }
