"""
AI Scheduler for managing AI unit actions with staggering.

This module provides a scheduler that manages AI unit actions with
configurable timing and staggering to prevent frame hitching.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AITask:
    """Represents an AI task to be executed."""

    unit_id: str
    action: Callable
    period_s: float
    offset_s: float
    last_execution: float = 0.0


class AIScheduler:
    """Scheduler for managing AI unit actions with staggering."""

    def __init__(self):
        """Initialize the AI scheduler."""
        self.tasks: Dict[str, AITask] = {}
        self.start_time = time.time()

    def register(
        self,
        unit_id: str,
        action: Callable,
        period_s: float = 2.0,
        offset_s: float = 0.0,
    ) -> None:
        """Register an AI unit for scheduling.

        Args:
            unit_id: Unique identifier for the unit
            action: Function to call for AI decisions
            period_s: Time between AI actions in seconds
            offset_s: Offset from start time in seconds
        """
        self.tasks[unit_id] = AITask(
            unit_id=unit_id,
            action=action,
            period_s=period_s,
            offset_s=offset_s,
            last_execution=0.0,
        )

    def unregister(self, unit_id: str) -> None:
        """Unregister an AI unit from scheduling.

        Args:
            unit_id: Unit identifier to remove
        """
        if unit_id in self.tasks:
            del self.tasks[unit_id]

    def update(self, dt_seconds: float) -> None:
        """Update the scheduler and execute due tasks.

        Args:
            dt_seconds: Delta time in seconds
        """
        current_time = time.time()

        for task in self.tasks.values():
            # Calculate when this task should execute next
            next_execution = task.last_execution + task.period_s

            # Check if it's time to execute
            if current_time >= next_execution:
                try:
                    # Execute the AI action
                    task.action()
                    task.last_execution = current_time
                except Exception as e:
                    print(f"AI Scheduler: Error executing task for {task.unit_id}: {e}")

    def get_next_execution_time(self, unit_id: str) -> Optional[float]:
        """Get the next execution time for a unit.

        Args:
            unit_id: Unit identifier

        Returns:
            Next execution time in seconds, or None if not registered
        """
        if unit_id not in self.tasks:
            return None

        task = self.tasks[unit_id]
        return task.last_execution + task.period_s

    def get_task_count(self) -> int:
        """Get the number of registered tasks.

        Returns:
            Number of registered AI tasks
        """
        return len(self.tasks)

    def clear(self) -> None:
        """Clear all registered tasks."""
        self.tasks.clear()

    def get_task_info(self) -> List[Dict[str, Any]]:
        """Get information about all registered tasks.

        Returns:
            List of task information dictionaries
        """
        current_time = time.time()
        task_info = []

        for task in self.tasks.values():
            next_execution = task.last_execution + task.period_s
            time_until_next = max(0, next_execution - current_time)

            task_info.append(
                {
                    "unit_id": task.unit_id,
                    "period_s": task.period_s,
                    "offset_s": task.offset_s,
                    "last_execution": task.last_execution,
                    "next_execution": next_execution,
                    "time_until_next": time_until_next,
                }
            )

        return task_info
