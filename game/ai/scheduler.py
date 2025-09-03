"""
AI Scheduler - Staggers Behavior Tree ticks to prevent frame bursts.
"""

from __future__ import annotations

import time
from typing import Callable, Dict, Optional


class AIScheduler:
    """Schedules AI updates with staggered timing to prevent frame hitching."""

    def __init__(self):
        self.scheduled_units: Dict[str, Dict] = {}
        self.last_update = time.time()

    def register(
        self,
        unit_id: str,
        tick_func: Callable,
        period_s: float = 2.0,
        offset_s: float = 0.0,
    ):
        """Register a unit for periodic AI updates."""
        self.scheduled_units[unit_id] = {
            "tick_func": tick_func,
            "period_s": period_s,
            "offset_s": offset_s,
            "last_tick": time.time() + offset_s,
        }

    def unregister(self, unit_id: str):
        """Remove a unit from AI scheduling."""
        if unit_id in self.scheduled_units:
            del self.scheduled_units[unit_id]

    def update(self, dt_seconds: float):
        """Update all scheduled AI units."""
        current_time = time.time()

        for unit_id, schedule in self.scheduled_units.items():
            if current_time - schedule["last_tick"] >= schedule["period_s"]:
                try:
                    schedule["tick_func"]()
                    schedule["last_tick"] = current_time
                except Exception as e:
                    print(f"AI tick failed for {unit_id}: {e}")

    def get_active_count(self) -> int:
        """Get number of actively scheduled AI units."""
        return len(self.scheduled_units)

    def clear(self):
        """Clear all scheduled units."""
        self.scheduled_units.clear()
