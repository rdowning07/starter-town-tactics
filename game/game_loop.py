"""Enhanced game loop implementation using integrated GameState methods."""

import time
from typing import Optional
from unittest.mock import Mock

from devtools.scenario_manager import create_scenario_manager
from game.game_state import GameState


def game_loop(game_state: GameState, max_turns: Optional[int] = None) -> None:
    """
    Enhanced game loop using integrated GameState methods.

    Args:
        game_state: The GameState instance to run the game loop with
        max_turns: Optional maximum number of turns (for testing/demo purposes)
    """
    print("🎮 Starting enhanced game loop...")

    turn_count = 0
    while not game_state.is_game_over():
        # Check for maximum turns (for testing/demo)
        if max_turns and turn_count >= max_turns:
            print(f"🛑 Game loop stopped after {max_turns} turns (demo mode)")
            break

        turn_count += 1
        print(f"\n🔄 Turn {turn_count}")

        # Process player input (if any)
        process_player_input(game_state)

        # Advance turn (automatically handles events and objectives)
        game_state.advance_turn()

        # Get current state information
        current_objective = game_state.get_current_objective()
        current_turn = game_state.get_turn_count()
        triggered_events = game_state.get_triggered_events()

        # Display current state
        print(f"🎯 Objective: {current_objective}")
        print(f"📊 Turn: {current_turn}")

        # Handle any newly triggered events
        handle_triggered_events(game_state, triggered_events)

        # Render the game state
        render_game_state(game_state)

        # Optional: Add delay for turn-based gameplay
        time.sleep(0.1)  # 100ms delay between turns

    # Game over
    print(f"\n🏁 Game Over! Final turn: {turn_count}")
    print(f"🎯 Final objective: {game_state.get_current_objective()}")

    if game_state.has_won():
        print("🎉 Victory! The player has won!")
    elif game_state.has_lost():
        print("💀 Defeat! The player has lost!")
    else:
        print("🤔 Game ended without clear victory/defeat condition")


def process_player_input(game_state: GameState) -> None:
    """
    Process player input for current turn.

    Args:
        game_state: The current game state
    """
    # Implementation depends on your input system
    # For now, this is a placeholder that can be extended
    print("👤 Processing player input...")
    # Add player input processing here


def handle_triggered_events(game_state: GameState, triggered_events: list[str]) -> None:
    """
    Handle any newly triggered events.

    Args:
        game_state: The current game state
        triggered_events: List of events that have been triggered
    """
    for event in triggered_events:
        if event == "reinforcements":
            handle_reinforcement_effects(game_state)
        elif event == "storm":
            handle_storm_effects(game_state)
        elif event == "boss_phase":
            handle_boss_phase_effects(game_state)


def handle_reinforcement_effects(game_state: GameState) -> None:
    """Handle reinforcement event effects."""
    print("🎉 Reinforcements have arrived! New units join the battle.")
    # Add any additional reinforcement logic here
    # The actual unit creation is handled by EventManager


def handle_storm_effects(game_state: GameState) -> None:
    """Handle storm event effects."""
    print("⛈️ Storm reduces visibility and movement!")
    # Add storm-specific game mechanics here
    # Could affect unit movement, attack accuracy, etc.


def handle_boss_phase_effects(game_state: GameState) -> None:
    """Handle boss phase event effects."""
    print("👹 Boss phase activated! Enemies become more aggressive!")
    # Add boss phase mechanics here
    # Could affect AI behavior, unit stats, etc.


def render_game_state(game_state: GameState) -> None:
    """
    Render the current game state.

    Args:
        game_state: The current game state to render
    """
    # Display basic game information
    print("📊 Game State:")
    print(f"   - Units: {len(game_state.units.get_all_units())}")
    print(f"   - Events: {game_state.get_triggered_events()}")

    # Display unit information
    all_units = game_state.units.get_all_units()
    if all_units:
        print("   - Living Units:")
        for unit_id, unit_data in all_units.items():
            if game_state.units.is_alive(unit_id):
                team = unit_data.get("team", "unknown")
                hp = unit_data.get("hp", 0)
                print(f"     • {unit_id} ({team}): {hp} HP")


def demo_game_loop(scenario_path: str, max_turns: int = 10) -> None:
    """
    Demo function to run a game loop with a specific scenario.

    Args:
        scenario_path: Path to the scenario file to load
        max_turns: Maximum number of turns to run
    """

    print(f"🎬 Demo: Loading scenario from {scenario_path}")

    # Create mock components for demo
    camera = Mock()
    ai_controller = Mock()
    player_unit = Mock()
    game_state = GameState()

    # Create scenario manager and load scenario
    scenario_manager = create_scenario_manager(camera, ai_controller, player_unit, game_state)

    try:
        # Load the scenario
        loaded_game_state = scenario_manager.load_scenario(scenario_path)
        print(f"✅ Scenario loaded: {loaded_game_state.name}")

        # Run the game loop
        game_loop(loaded_game_state, max_turns=max_turns)

    except FileNotFoundError:
        print(f"❌ Scenario file not found: {scenario_path}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"❌ Error loading scenario: {e}")


if __name__ == "__main__":
    # Example usage
    print("🎮 Enhanced Game Loop Demo")
    print("=" * 40)

    # Demo with a scenario
    demo_game_loop("devtools/scenarios/demo_battle.yaml", max_turns=8)
