# Standard library imports
import time
from collections import defaultdict
from typing import Dict, List, Optional

# Local imports
from .bt import BTContext, BTNode


class BTProfiler:
    """Profiles Behavior Tree execution for performance and debugging."""

    def __init__(self):
        self.execution_times: Dict[str, List[float]] = defaultdict(list)
        self.node_usage: Dict[str, int] = defaultdict(int)
        self.decision_paths: List[List[str]] = []
        self.total_decisions = 0
        self.start_time: Optional[float] = None

    def start_profiling(self) -> None:
        """Start profiling session."""
        self.start_time = time.time()
        self.execution_times.clear()
        self.node_usage.clear()
        self.decision_paths.clear()
        self.total_decisions = 0

    def record_node_execution(self, node_name: str, execution_time: float) -> None:
        """Record execution time for a specific node."""
        self.execution_times[node_name].append(execution_time)
        self.node_usage[node_name] += 1

    def record_decision_path(self, path: List[str]) -> None:
        """Record the decision path taken."""
        self.decision_paths.append(path)
        self.total_decisions += 1

    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary."""
        if not self.start_time:
            return {"error": "Profiling not started"}

        total_time = time.time() - self.start_time

        # Calculate average execution times
        avg_times = {}
        for node_name, times in self.execution_times.items():
            if times:
                avg_times[node_name] = sum(times) / len(times)

        # Calculate decisions per second
        decisions_per_second = self.total_decisions / total_time if total_time > 0 else 0

        return {
            "total_time": total_time,
            "total_decisions": self.total_decisions,
            "decisions_per_second": decisions_per_second,
            "average_execution_times": avg_times,
            "node_usage": dict(self.node_usage),
            "decision_paths": self.decision_paths[-10:],  # Last 10 paths
            "most_used_nodes": sorted(self.node_usage.items(), key=lambda x: x[1], reverse=True)[:5],
        }

    def print_summary(self) -> None:
        """Print a formatted performance summary."""
        summary = self.get_performance_summary()

        if "error" in summary:
            print("❌ Profiling error:", summary["error"])
            return

        print("📊 Behavior Tree Performance Summary")
        print("=" * 50)
        print(f"⏱️  Total Time: {summary['total_time']:.3f}s")
        print(f"🎯 Total Decisions: {summary['total_decisions']}")
        print(f"⚡ Decisions/Second: {summary['decisions_per_second']:.0f}")
        print()

        print("🏃 Node Performance:")
        for node_name, avg_time in summary["average_execution_times"].items():
            usage_count = summary["node_usage"].get(node_name, 0)
            print(f"  {node_name}: {avg_time*1000:.2f}ms avg ({usage_count} uses)")
        print()

        print("📈 Most Used Nodes:")
        for node_name, count in summary["most_used_nodes"]:
            print(f"  {node_name}: {count} times")
        print()

        print("🛤️  Recent Decision Paths:")
        for i, path in enumerate(summary["decision_paths"][-3:], 1):
            print(f"  {i}. {' → '.join(path)}")

    def profile_execution(self, bt: BTNode, ctx: BTContext, iterations: int = 100) -> None:
        """Profile BT execution over multiple iterations."""
        print(f"🔍 Profiling BT execution over {iterations} iterations...")

        self.start_profiling()

        for i in range(iterations):
            start_time = time.time()
            status = bt.tick(ctx)
            execution_time = time.time() - start_time

            # Record execution time (simplified - in real implementation,
            # you'd track individual node execution)
            self.record_node_execution("total_bt", execution_time)

            # Record decision path (simplified)
            self.record_decision_path([f"BT_{status}"])

            if i % 20 == 0:
                print(f"  Progress: {i+1}/{iterations}")

        print("✅ Profiling complete!")
        self.print_summary()


# Global profiler instance
bt_profiler = BTProfiler()


def profile_bt(bt: BTNode, ctx: BTContext, iterations: int = 100) -> None:
    """Convenience function to profile BT execution."""
    bt_profiler.profile_execution(bt, ctx, iterations)
