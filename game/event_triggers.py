"""
Dynamic Event Triggers - manages environmental events with full architecture integration.
Integrated with GameState, FXManager, and includes validation and logging.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from game.fx_manager import FXManager

# @api
# @refactor
@dataclass
class EventTrigger:
    """Represents a dynamic event trigger."""
    name: str
    condition_func: Callable
    effect_func: Callable
    triggered: bool = False
    description: str = ""
    fx_type: Optional[str] = None
    fx_position: Optional[tuple] = None
    one_time: bool = True
    cooldown: int = 0
    current_cooldown: int = 0

    def check_condition(self, game_state) -> bool:
        """Check if event condition is met."""
        try:
            return self.condition_func(game_state)
        except Exception:
            return False

    def execute_effect(self, game_state, event_manager) -> bool:
        """Execute the event effect."""
        try:
            result = self.effect_func(game_state, event_manager)

            # Trigger FX if specified
            if self.fx_type and hasattr(event_manager, 'fx_manager') and self.fx_position:
                event_manager.fx_manager.trigger_fx(self.fx_type, self.fx_position)

            return result
        except Exception as e:
            if hasattr(event_manager, 'logger'):
                event_manager.logger.log_event("event_effect_error", {
                    "event": self.name,
                    "error": str(e)
                })
            return False

class EventManager:
    """Manages dynamic event triggers with full architecture integration."""

    def __init__(self, fx_manager: Optional[FXManager] = None, logger=None):
        self.fx_manager = fx_manager
        self.logger = logger
        self.events: List[EventTrigger] = []
        self.event_definitions = self._create_event_definitions()

    def _create_event_definitions(self) -> Dict[str, Callable]:
        """Define standard event triggers."""
        return {
            "trap_activation": self._create_trap_event,
            "hazard_trigger": self._create_hazard_event,
            "environmental_change": self._create_environmental_event,
            "unit_death_chain": self._create_death_chain_event,
            "turn_count_milestone": self._create_turn_milestone_event
        }

    def add_event(self, event: EventTrigger) -> bool:
        """Add an event trigger."""
        self.events.append(event)

        if self.logger:
            self.logger.log_event("event_added", {
                "event": event.name,
                "description": event.description
            })

        return True

    def create_event(self, event_name: str, **kwargs) -> Optional[EventTrigger]:
        """Create an event using predefined definitions."""
        if event_name not in self.event_definitions:
            if self.logger:
                self.logger.log_event("event_unknown", {
                    "event": event_name
                })
            return None

        return self.event_definitions[event_name](**kwargs)

    def evaluate_events(self, game_state) -> List[str]:
        """Evaluate all event triggers."""
        triggered_events = []

        for event in self.events:
            # Skip if already triggered and one-time
            if event.triggered and event.one_time:
                continue

            # Check cooldown
            if event.current_cooldown > 0:
                event.current_cooldown -= 1
                continue

            # Check condition
            if event.check_condition(game_state):
                # Execute effect
                if event.execute_effect(game_state, self):
                    triggered_events.append(event.name)
                    event.triggered = True

                    # Set cooldown
                    if event.cooldown > 0:
                        event.current_cooldown = event.cooldown

                    if self.logger:
                        self.logger.log_event("event_triggered", {
                            "event": event.name,
                            "description": event.description
                        })

        return triggered_events

    def reset_events(self):
        """Reset all events to untriggered state."""
        for event in self.events:
            event.triggered = False
            event.current_cooldown = 0

        if self.logger:
            self.logger.log_event("events_reset", {
                "count": len(self.events)
            })

    def get_event_status(self) -> Dict[str, Any]:
        """Get status of all events."""
        event_status = []
        for event in self.events:
            event_status.append({
                "name": event.name,
                "description": event.description,
                "triggered": event.triggered,
                "cooldown_remaining": event.current_cooldown,
                "one_time": event.one_time
            })

        return {
            "total_events": len(self.events),
            "triggered_events": sum(1 for e in self.events if e.triggered),
            "events": event_status
        }

    def remove_event(self, event_name: str) -> bool:
        """Remove an event by name."""
        for i, event in enumerate(self.events):
            if event.name == event_name:
                del self.events[i]

                if self.logger:
                    self.logger.log_event("event_removed", {
                        "event": event_name
                    })
                return True

        return False

    # Event Definition Methods
    def _create_trap_event(self, position: tuple = (0, 0), damage: int = 10, **kwargs) -> EventTrigger:
        """Create a trap activation event."""
        def trap_condition(game_state):
            # Check if any unit is at the trap position
            if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
                return False

            for unit_data in game_state.units.units.values():
                if (unit_data.get("alive", True) and
                    unit_data.get("x") == position[0] and
                    unit_data.get("y") == position[1]):
                    return True
            return False

        def trap_effect(game_state, event_manager):
            # Damage all units at trap position
            if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
                return False

            units_hit = []
            for unit_id, unit_data in game_state.units.units.items():
                if (unit_data.get("alive", True) and
                    unit_data.get("x") == position[0] and
                    unit_data.get("y") == position[1]):
                    old_hp = unit_data.get("hp", 0)
                    unit_data["hp"] = max(0, old_hp - damage)
                    units_hit.append(unit_id)  # Need unit_id for tracking

            return len(units_hit) > 0

        return EventTrigger(
            name="trap_activation",
            condition_func=trap_condition,
            effect_func=trap_effect,
            description=f"Trap deals {damage} damage to units at {position}",
            fx_type="explosion",
            fx_position=position,
            **kwargs
        )

    def _create_hazard_event(self, hazard_type: str = "fire", duration: int = 3, **kwargs) -> EventTrigger:
        """Create a hazard trigger event."""
        def hazard_condition(game_state):
            # Check if hazard should activate (e.g., based on turn count)
            if hasattr(game_state, 'sim_runner'):
                turn_count = getattr(game_state.sim_runner, 'turn_count', 0)
                return turn_count % 5 == 0  # Every 5 turns
            return False

        def hazard_effect(game_state, event_manager):
            # Apply hazard effect to all units
            if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
                return False

            if hasattr(event_manager, 'status_manager'):
                for unit_id, unit_data in game_state.units.units.items():
                    if unit_data.get("alive", True):
                        if hazard_type == "fire":
                            event_manager.status_manager.add_effect(unit_id, "poison", duration, 2)
                        elif hazard_type == "ice":
                            event_manager.status_manager.add_effect(unit_id, "slow", duration, 1)

            return True

        return EventTrigger(
            name="hazard_trigger",
            condition_func=hazard_condition,
            effect_func=hazard_effect,
            description=f"{hazard_type.title()} hazard affects all units",
            fx_type="fire" if hazard_type == "fire" else "ice",
            one_time=False,
            cooldown=5,
            **kwargs
        )

    def _create_environmental_event(self, event_type: str = "weather_change", **kwargs) -> EventTrigger:
        """Create an environmental change event."""
        def env_condition(game_state):
            # Environmental changes based on game state
            if hasattr(game_state, 'sim_runner'):
                turn_count = getattr(game_state.sim_runner, 'turn_count', 0)
                return turn_count == 10  # At turn 10
            return False

        def env_effect(game_state, event_manager):
            # Apply environmental effect
            if event_type == "weather_change":
                # Change weather affects movement
                if hasattr(game_state, 'units') and hasattr(game_state.units, 'units'):
                    for unit_data in game_state.units.units.values():
                        if unit_data.get("alive", True):
                            unit_data["movement_penalty"] = 1

            return True

        return EventTrigger(
            name="environmental_change",
            condition_func=env_condition,
            effect_func=env_effect,
            description=f"Environmental {event_type} affects gameplay",
            fx_type="magic",
            **kwargs
        )

    def _create_death_chain_event(self, chain_length: int = 3, **kwargs) -> EventTrigger:
        """Create a unit death chain reaction event."""
        def death_condition(game_state):
            # Check if multiple units died recently
            if not hasattr(game_state, 'units') or not hasattr(game_state.units, 'units'):
                return False

            dead_count = sum(1 for unit_data in game_state.units.units.values()
                           if not unit_data.get("alive", True))
            return dead_count >= chain_length

        def death_effect(game_state, event_manager):
            # Chain reaction effect
            if hasattr(event_manager, 'fx_manager'):
                # Trigger chain reaction FX
                event_manager.fx_manager.trigger_explosion_fx((400, 300), 30)

            return True

        return EventTrigger(
            name="unit_death_chain",
            condition_func=death_condition,
            effect_func=death_effect,
            description=f"Chain reaction after {chain_length} unit deaths",
            fx_type="explosion",
            one_time=False,
            cooldown=10,
            **kwargs
        )

    def _create_turn_milestone_event(self, milestone: int = 20, **kwargs) -> EventTrigger:
        """Create a turn count milestone event."""
        def milestone_condition(game_state):
            if hasattr(game_state, 'sim_runner'):
                turn_count = getattr(game_state.sim_runner, 'turn_count', 0)
                return turn_count == milestone
            return False

        def milestone_effect(game_state, event_manager):
            # Milestone reached effect
            if hasattr(event_manager, 'fx_manager'):
                event_manager.fx_manager.trigger_magic_fx((400, 300), "arcane")

            return True

        return EventTrigger(
            name="turn_count_milestone",
            condition_func=milestone_condition,
            effect_func=milestone_effect,
            description=f"Milestone reached at turn {milestone}",
            fx_type="magic",
            **kwargs
        )
