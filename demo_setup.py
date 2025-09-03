"""
Demo setup script using the new architecture.

This script demonstrates the Factory spawn, AI Scheduler, and Victory Service
integration for the 4v4 tactical combat system.
"""

import time
from typing import Any, Dict, Optional

import pygame

from game.ai.scheduler import AIScheduler
from game.factories import EntityFactory, TeamConfig
from game.services import GameOutcome, VictoryService


class DemoGameState:
    """Simplified game state for the demo."""

    def __init__(self):
        self.units: Dict[str, Dict[str, Any]] = {}
        self.teams: Dict[int, TeamConfig] = {}
        self.victory_service: Optional[VictoryService] = None
        self.ai_scheduler: Optional[AIScheduler] = None

    def add_unit(self, unit_id: str, unit_data: Dict[str, Any]) -> None:
        """Add a unit to the game state."""
        self.units[unit_id] = unit_data

    def get_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """Get a unit from the game state."""
        return self.units.get(unit_id)

    def update_unit_hp(self, unit_id: str, new_hp: int) -> None:
        """Update a unit's HP."""
        if unit_id in self.units:
            self.units[unit_id]["hp"] = new_hp
            if new_hp <= 0:
                team_id = self.units[unit_id]["team"]
                if self.victory_service:
                    self.victory_service.on_unit_defeated(team_id)


def create_demo_teams() -> tuple[TeamConfig, TeamConfig]:
    """Create demo teams using the Entity Factory."""
    factory = EntityFactory()
    allies, bandits = factory.create_demo_teams()

    print("🏭 Factory: Spawned Allies & Bandits")
    print(f"   Allies: {len(allies.units)} units")
    print(f"   Bandits: {len(bandits.units)} units")

    return allies, bandits


def setup_ai_scheduler(game_state: DemoGameState, allies: TeamConfig, bandits: TeamConfig) -> AIScheduler:
    """Set up the AI scheduler with staggered timing."""
    scheduler = AIScheduler()

    # Register AI units with staggered timing
    ai_units = []

    # Add ally AI units (skip player unit)
    for unit in allies.units[1:]:  # Skip first unit (player)
        ai_units.append(unit)

    # Add all bandit units
    for unit in bandits.units:
        ai_units.append(unit)

    # Register with staggered timing
    for i, unit in enumerate(ai_units):

        def create_ai_action(unit_id: str):
            def ai_action():
                print(f"🤖 AI: {unit_id} making decision")
                # Simulate AI decision making
                time.sleep(0.1)  # Simulate processing time

            return ai_action

        scheduler.register(
            unit_id=unit.name,
            action=create_ai_action(unit.name),
            period_s=2.0,
            offset_s=i * 0.25,  # 250ms staggering
        )

    print("⏰ Scheduler: AI units registered with 250ms staggering")
    print(f"   Registered {scheduler.get_task_count()} AI units")

    return scheduler


def setup_victory_service(allies: TeamConfig, bandits: TeamConfig) -> VictoryService:
    """Set up the victory service."""
    victory_service = VictoryService(
        player_team_id=allies.team_id,
        enemy_team_ids={bandits.team_id},
        alive_by_team={
            allies.team_id: len(allies.units),
            bandits.team_id: len(bandits.units),
        },
    )

    # Subscribe to victory events
    def on_victory(outcome: GameOutcome):
        if outcome == GameOutcome.VICTORY:
            print("🎉 VICTORY! All enemies defeated!")
        elif outcome == GameOutcome.DEFEAT:
            print("💀 DEFEAT! Player team defeated!")
        elif outcome == GameOutcome.DRAW:
            print("🤝 DRAW! Game ended in a tie!")

    victory_service.subscribe(on_victory)

    print("🏆 Victory Service: Configured with win/lose conditions")
    print(f"   Player team: {allies.team_id} ({len(allies.units)} units)")
    print(f"   Enemy teams: {list(victory_service.enemy_team_ids)} ({len(bandits.units)} units)")

    return victory_service


def simulate_combat(game_state: DemoGameState, scheduler: AIScheduler, victory_service: VictoryService) -> None:
    """Simulate combat with the new architecture."""
    print("\n⚔️ Starting combat simulation...")

    # Simulate some combat
    for turn in range(10):
        print(f"\n--- Turn {turn + 1} ---")

        # Update AI scheduler
        scheduler.update(0.1)  # 100ms delta time

        # Simulate some damage
        if turn == 3:
            print("💥 Bandit 1 takes damage!")
            game_state.update_unit_hp("bandit_1", 0)  # Defeat a bandit

        if turn == 6:
            print("💥 Fighter takes damage!")
            game_state.update_unit_hp("fighter", 0)  # Defeat the player

        # Check if game is over
        if victory_service.is_game_over():
            print(f"🏁 Game Over: {victory_service.get_outcome().value}")
            break

        time.sleep(0.5)  # Pause between turns

    print("\n📊 Final Results:")
    print(f"   Game Over: {victory_service.is_game_over()}")
    print(f"   Outcome: {victory_service.get_outcome().value}")
    print(f"   Alive Counts: {victory_service.get_current_alive_counts()}")


def main():
    """Main demo function."""
    print("🚀 Demo Setup: 4v4 Tactical Combat Architecture")
    print("=" * 50)

    # Initialize pygame (required for some imports)
    pygame.init()

    # 1. Factory Spawn
    print("\n1️⃣ Factory Spawn")
    allies, bandits = create_demo_teams()

    # 2. Set up game state
    game_state = DemoGameState()
    game_state.teams[allies.team_id] = allies
    game_state.teams[bandits.team_id] = bandits

    # Add units to game state
    for unit in allies.units + bandits.units:
        game_state.add_unit(
            unit.name,
            {
                "name": unit.name,
                "team": unit.team,
                "sprite": unit.sprite,
                "x": unit.x,
                "y": unit.y,
                "hp": unit.hp,
                "ap": unit.ap,
                "attack_range": unit.attack_range,
                "is_player": unit.is_player,
            },
        )

    # 3. AI Scheduler
    print("\n2️⃣ AI Scheduler")
    scheduler = setup_ai_scheduler(game_state, allies, bandits)
    game_state.ai_scheduler = scheduler

    # 4. Victory Service
    print("\n3️⃣ Victory Service")
    victory_service = setup_victory_service(allies, bandits)
    game_state.victory_service = victory_service

    # 5. Pattern Pulses
    print("\n4️⃣ Pattern Pulses")
    print("🏭 Factory: Spawned Allies & Bandits")
    print("⏰ Scheduler: AI units registered with 250ms staggering")
    print("🏆 Victory Service: Configured with win/lose conditions")
    print("👁️ Observer: UnitDefeated → VictoryService")

    # 6. Simulate combat
    print("\n5️⃣ Combat Simulation")
    simulate_combat(game_state, scheduler, victory_service)

    print("\n✅ Demo Complete!")
    print("Architecture patterns demonstrated:")
    print("  - Factory: Team spawning")
    print("  - Scheduler: AI timing")
    print("  - Service: Victory conditions")
    print("  - Observer: Event notifications")


if __name__ == "__main__":
    main()
