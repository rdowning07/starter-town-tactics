"""
Enhanced AI Behavior for Starter Town Tactics.

Provides more dynamic and engaging AI behavior patterns.
"""

import math
import random
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class AIBehaviorType(Enum):
    """Types of AI behavior patterns."""

    AGGRESSIVE = "aggressive"  # Direct attack, high risk
    TACTICAL = "tactical"  # Strategic positioning
    DEFENSIVE = "defensive"  # Protect allies, low risk
    MOBILE = "mobile"  # Constant movement, hit-and-run
    PACK_HUNTER = "pack_hunter"  # Coordinate with other units


class EnhancedAIBehavior:
    """Enhanced AI behavior system for dynamic unit actions."""

    def __init__(self):
        """Initialize enhanced AI behavior."""
        self.behavior_types: Dict[str, AIBehaviorType] = {}
        self.last_positions: Dict[str, Tuple[int, int]] = {}
        self.movement_history: Dict[str, List[Tuple[int, int]]] = {}
        self.target_priorities: Dict[str, str] = {}
        self.formation_positions: Dict[str, Tuple[int, int]] = {}

        # Behavior parameters
        self.aggression_level = 0.7  # 0.0 = passive, 1.0 = very aggressive
        self.mobility_level = 0.6  # 0.0 = stationary, 1.0 = very mobile
        self.coordination_level = 0.5  # 0.0 = individual, 1.0 = coordinated

        print("🤖 Enhanced AI Behavior initialized")

    def assign_behavior(self, unit_id: str, behavior: AIBehaviorType) -> None:
        """Assign a behavior type to a unit.

        Args:
            unit_id: ID of the unit
            behavior: Behavior type to assign
        """
        self.behavior_types[unit_id] = behavior
        self.movement_history[unit_id] = []
        print(f"🤖 Unit {unit_id} assigned {behavior.value} behavior")

    def get_enhanced_action(self, unit_id: str, unit_data: Dict, all_units: Dict, game_state: Any) -> Optional[Dict]:
        """Get enhanced AI action based on behavior type.

        Args:
            unit_id: ID of the unit
            unit_data: Unit data dictionary
            all_units: All units in the game
            game_state: Current game state

        Returns:
            Action dictionary or None
        """
        behavior = self.behavior_types.get(unit_id, AIBehaviorType.TACTICAL)

        if behavior == AIBehaviorType.AGGRESSIVE:
            return self._aggressive_action(unit_id, unit_data, all_units)
        elif behavior == AIBehaviorType.TACTICAL:
            return self._tactical_action(unit_id, unit_data, all_units)
        elif behavior == AIBehaviorType.DEFENSIVE:
            return self._defensive_action(unit_id, unit_data, all_units)
        elif behavior == AIBehaviorType.MOBILE:
            return self._mobile_action(unit_id, unit_data, all_units)
        elif behavior == AIBehaviorType.PACK_HUNTER:
            return self._pack_hunter_action(unit_id, unit_data, all_units)

        return None

    def _aggressive_action(self, unit_id: str, unit_data: Dict, all_units: Dict) -> Optional[Dict]:
        """Aggressive behavior: direct attack, high risk."""
        current_pos = (unit_data.get("x", 0), unit_data.get("y", 0))

        # Find nearest enemy
        team = unit_data.get("team")
        if not isinstance(team, str):
            return None
        nearest_enemy = self._find_nearest_enemy(current_pos, all_units, team)
        if not nearest_enemy:
            return None

        enemy_pos = (nearest_enemy.get("x", 0), nearest_enemy.get("y", 0))
        distance = self._calculate_distance(current_pos, enemy_pos)

        # If in range, attack
        if distance <= 2:  # Attack range
            return {
                "action": "attack",
                "target": nearest_enemy.get("id", ""),
                "reason": "aggressive_attack",
            }

        # Move directly toward enemy
        direction = self._get_direction_toward(current_pos, enemy_pos)
        new_pos = self._apply_movement(current_pos, direction)

        return {
            "action": "move",
            "x": new_pos[0],
            "y": new_pos[1],
            "reason": "aggressive_advance",
        }

    def _tactical_action(self, unit_id: str, unit_data: Dict, all_units: Dict) -> Optional[Dict]:
        """Tactical behavior: strategic positioning."""
        current_pos = (unit_data.get("x", 0), unit_data.get("y", 0))

        # Find best tactical position
        team = unit_data.get("team")
        if not isinstance(team, str):
            return None
        tactical_pos = self._find_tactical_position(current_pos, all_units, team)
        if tactical_pos and tactical_pos != current_pos:
            return {
                "action": "move",
                "x": tactical_pos[0],
                "y": tactical_pos[1],
                "reason": "tactical_positioning",
            }

        # If in good position, attack if possible
        team = unit_data.get("team")
        if not isinstance(team, str):
            return None
        nearest_enemy = self._find_nearest_enemy(current_pos, all_units, team)
        if nearest_enemy:
            enemy_pos = (nearest_enemy.get("x", 0), nearest_enemy.get("y", 0))
            distance = self._calculate_distance(current_pos, enemy_pos)

            if distance <= 2:
                return {
                    "action": "attack",
                    "target": nearest_enemy.get("id", ""),
                    "reason": "tactical_attack",
                }

        return None

    def _defensive_action(self, unit_id: str, unit_data: Dict, all_units: Dict) -> Optional[Dict]:
        """Defensive behavior: protect allies, low risk."""
        current_pos = (unit_data.get("x", 0), unit_data.get("y", 0))

        # Find nearest ally in danger
        team = unit_data.get("team")
        if not isinstance(team, str):
            return None
        ally_in_danger = self._find_ally_in_danger(current_pos, all_units, team)
        if ally_in_danger:
            # Move to protect ally
            ally_pos = (ally_in_danger.get("x", 0), ally_in_danger.get("y", 0))
            direction = self._get_direction_toward(current_pos, ally_pos)
            new_pos = self._apply_movement(current_pos, direction)

            return {
                "action": "move",
                "x": new_pos[0],
                "y": new_pos[1],
                "reason": "defensive_protection",
            }

        # If no allies in danger, maintain defensive position
        return None

    def _mobile_action(self, unit_id: str, unit_data: Dict, all_units: Dict) -> Optional[Dict]:
        """Mobile behavior: constant movement, hit-and-run."""
        current_pos = (unit_data.get("x", 0), unit_data.get("y", 0))

        # Add to movement history
        if unit_id not in self.movement_history:
            self.movement_history[unit_id] = []
        self.movement_history[unit_id].append(current_pos)

        # Keep only recent history
        if len(self.movement_history[unit_id]) > 5:
            self.movement_history[unit_id] = self.movement_history[unit_id][-5:]

        # Avoid recent positions
        recent_positions = set(self.movement_history[unit_id][-3:])

        # Find new position that's not recent
        for _ in range(10):  # Try up to 10 random positions
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
            new_pos = self._apply_movement(current_pos, direction)

            if new_pos not in recent_positions:
                return {
                    "action": "move",
                    "x": new_pos[0],
                    "y": new_pos[1],
                    "reason": "mobile_movement",
                }

        # If can't find new position, attack if possible
        team = unit_data.get("team")
        if not isinstance(team, str):
            return None
        nearest_enemy = self._find_nearest_enemy(current_pos, all_units, team)
        if nearest_enemy:
            enemy_pos = (nearest_enemy.get("x", 0), nearest_enemy.get("y", 0))
            distance = self._calculate_distance(current_pos, enemy_pos)

            if distance <= 2:
                return {
                    "action": "attack",
                    "target": nearest_enemy.get("id", ""),
                    "reason": "mobile_attack",
                }

        return None

    def _pack_hunter_action(self, unit_id: str, unit_data: Dict, all_units: Dict) -> Optional[Dict]:
        """Pack hunter behavior: coordinate with other units."""
        current_pos = (unit_data.get("x", 0), unit_data.get("y", 0))

        # Find other units of same team
        allies = [u for u in all_units.values() if u.get("team") == unit_data.get("team") and u.get("id") != unit_id]

        if allies:
            # Find formation position
            formation_pos = self._calculate_formation_position(current_pos, allies)
            if formation_pos and formation_pos != current_pos:
                return {
                    "action": "move",
                    "x": formation_pos[0],
                    "y": formation_pos[1],
                    "reason": "pack_formation",
                }

        # If in formation, attack together
        team = unit_data.get("team")
        if not isinstance(team, str):
            return None
        nearest_enemy = self._find_nearest_enemy(current_pos, all_units, team)
        if nearest_enemy:
            enemy_pos = (nearest_enemy.get("x", 0), nearest_enemy.get("y", 0))
            distance = self._calculate_distance(current_pos, enemy_pos)

            if distance <= 2:
                return {
                    "action": "attack",
                    "target": nearest_enemy.get("id", ""),
                    "reason": "pack_attack",
                }

        return None

    def _find_nearest_enemy(self, current_pos: Tuple[int, int], all_units: Dict, team: str) -> Optional[Dict]:
        """Find the nearest enemy unit."""
        enemies = [u for u in all_units.values() if u.get("team") != team and u.get("alive", True)]
        if not enemies:
            return None

        nearest = None
        min_distance = float("inf")

        for enemy in enemies:
            enemy_pos = (enemy.get("x", 0), enemy.get("y", 0))
            distance = self._calculate_distance(current_pos, enemy_pos)
            if distance < min_distance:
                min_distance = distance
                nearest = enemy

        return nearest

    def _find_ally_in_danger(self, current_pos: Tuple[int, int], all_units: Dict, team: str) -> Optional[Dict]:
        """Find an ally that's in danger (low health or surrounded)."""
        allies = [u for u in all_units.values() if u.get("team") == team and u.get("alive", True)]

        for ally in allies:
            # Check if ally has low health
            if ally.get("hp", 10) <= 5:
                return ally

            # Check if ally is surrounded by enemies
            ally_pos = (ally.get("x", 0), ally.get("y", 0))
            nearby_enemies = 0
            for enemy in all_units.values():
                if enemy.get("team") != team and enemy.get("alive", True):
                    enemy_pos = (enemy.get("x", 0), enemy.get("y", 0))
                    if self._calculate_distance(ally_pos, enemy_pos) <= 2:
                        nearby_enemies += 1

            if nearby_enemies >= 2:
                return ally

        return None

    def _find_tactical_position(
        self, current_pos: Tuple[int, int], all_units: Dict, team: str
    ) -> Optional[Tuple[int, int]]:
        """Find a good tactical position."""
        # Look for positions that provide good coverage
        candidates = []

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                new_pos = (current_pos[0] + dx, current_pos[1] + dy)
                if new_pos != current_pos:
                    score = self._evaluate_position(new_pos, all_units, team)
                    candidates.append((new_pos, score))

        if candidates:
            # Return position with highest score
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return None

    def _evaluate_position(self, pos: Tuple[int, int], all_units: Dict, team: str) -> float:
        """Evaluate how good a position is tactically."""
        score = 0.0

        # Prefer positions near allies
        allies = [u for u in all_units.values() if u.get("team") == team and u.get("alive", True)]
        for ally in allies:
            ally_pos = (ally.get("x", 0), ally.get("y", 0))
            distance = self._calculate_distance(pos, ally_pos)
            if distance <= 3:
                score += 1.0 / (distance + 1)

        # Prefer positions that can attack enemies
        enemies = [u for u in all_units.values() if u.get("team") != team and u.get("alive", True)]
        for enemy in enemies:
            enemy_pos = (enemy.get("x", 0), enemy.get("y", 0))
            distance = self._calculate_distance(pos, enemy_pos)
            if distance <= 2:
                score += 2.0 / (distance + 1)

        # Prefer center positions
        center_distance = self._calculate_distance(pos, (5, 5))
        score += 1.0 / (center_distance + 1)

        return score

    def _calculate_formation_position(
        self, current_pos: Tuple[int, int], allies: List[Dict]
    ) -> Optional[Tuple[int, int]]:
        """Calculate formation position relative to allies."""
        if not allies:
            return None

        # Find center of ally formation
        ally_positions = [(ally.get("x", 0), ally.get("y", 0)) for ally in allies]
        center_x = sum(pos[0] for pos in ally_positions) / len(ally_positions)
        center_y = sum(pos[1] for pos in ally_positions) / len(ally_positions)

        # Position to the side of the formation
        direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        formation_pos = (
            int(center_x + direction[0] * 2),
            int(center_y + direction[1] * 2),
        )

        return formation_pos

    def _get_direction_toward(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Get direction vector toward target position."""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]

        # Normalize to unit direction
        if dx != 0:
            dx = 1 if dx > 0 else -1
        if dy != 0:
            dy = 1 if dy > 0 else -1

        return (dx, dy)

    def _apply_movement(self, current_pos: Tuple[int, int], direction: Tuple[int, int]) -> Tuple[int, int]:
        """Apply movement in a direction."""
        new_x = max(0, min(14, current_pos[0] + direction[0]))
        new_y = max(0, min(14, current_pos[1] + direction[1]))
        return (new_x, new_y)

    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between two positions."""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
