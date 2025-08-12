"""Event management system for turn-based game events."""

from __future__ import annotations

from typing import Dict, List, Optional


class EventManager:
    """Manages turn-based events and their triggers."""

    def __init__(self, game_state):
        self.game_state = game_state
        self.turn_count = 0
        self.triggered_events: List[str] = []
        self.event_history: List[Dict] = []

    def advance_turn(self) -> None:
        """Advances the game turn and triggers events based on turn count."""
        self.turn_count += 1
        print(f"🔄 Turn {self.turn_count} advanced")
        
        # Check for turn-based events
        if self.turn_count == 5:
            self.trigger_reinforcements()
        if self.turn_count == 10:
            self.trigger_storm()
        if self.turn_count == 15:
            self.trigger_boss_phase()

    def trigger_reinforcements(self) -> None:
        """Trigger reinforcements after 5 turns."""
        if "reinforcements" not in self.triggered_events:
            print("🆘 Reinforcements have arrived!")
            self.triggered_events.append("reinforcements")
            
            # Add new units to game state
            self.game_state.add_unit("reinforcement_1", "player", ap=3, hp=15)
            self.game_state.add_unit("reinforcement_2", "player", ap=3, hp=15)
            
            # Log the event
            self.event_history.append({
                "turn": self.turn_count,
                "event": "reinforcements",
                "description": "Player reinforcements arrived"
            })

    def trigger_storm(self) -> None:
        """Trigger a storm after 10 turns."""
        if "storm" not in self.triggered_events:
            print("⛈️ A storm has arrived! All units' vision is reduced.")
            self.triggered_events.append("storm")
            
            # Apply weather effect through FX system
            self.game_state.trigger_fx("weather_storm", (0, 0), duration=5.0, intensity=0.8)
            
            # Log the event
            self.event_history.append({
                "turn": self.turn_count,
                "event": "storm",
                "description": "Weather storm reduced visibility"
            })

    def trigger_boss_phase(self) -> None:
        """Trigger boss phase after 15 turns."""
        if "boss_phase" not in self.triggered_events:
            print("👹 Boss phase activated! Enemy units become more aggressive.")
            self.triggered_events.append("boss_phase")
            
            # Apply boss phase effects
            self.game_state.trigger_fx("boss_aura", (400, 300), duration=3.0, intensity=1.0, color=(255, 0, 0))
            
            # Log the event
            self.event_history.append({
                "turn": self.turn_count,
                "event": "boss_phase",
                "description": "Boss phase activated"
            })

    def get_turn_count(self) -> int:
        """Get the current turn count."""
        return self.turn_count

    def get_triggered_events(self) -> List[str]:
        """Get list of events that have been triggered."""
        return list(self.triggered_events)

    def get_event_history(self) -> List[Dict]:
        """Get the history of all events."""
        return list(self.event_history)

    def reset(self) -> None:
        """Reset the event manager to initial state."""
        self.turn_count = 0
        self.triggered_events.clear()
        self.event_history.clear()

    def has_event_triggered(self, event_name: str) -> bool:
        """Check if a specific event has been triggered."""
        return event_name in self.triggered_events
