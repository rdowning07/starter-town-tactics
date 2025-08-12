import sys
import time

from devtools.scenario_loader import load_scenario
from devtools.scenario_manager import create_scenario_manager
from game.action_point_manager import ActionPointManager
from game.ai_controller import AIController
from game.sim_runner import SimRunner
from game.tactical_state_machine import TacticalState, TacticalStateMachine
from game.turn_controller import TurnController


class DemoAI(AIController):
    """Simple AI controller for demo purposes that works with string IDs."""

    def __init__(self):
        super().__init__([])  # Initialize with empty units list
        self.actions = []

    def take_action(self, unit):
        """Take action for a unit. Handles both Unit objects and string IDs."""
        if isinstance(unit, str):
            # String ID case
            unit_id = unit
            self.actions.append(unit_id)
            print(f"🤖 AI {unit_id} taking action...")
        else:
            # Unit object case (for compatibility with AIController)
            unit_id = unit.name if hasattr(unit, "name") else str(unit)
            self.actions.append(unit_id)
            print(f"🤖 AI {unit_id} taking action...")


def print_ap_state(apm: ActionPointManager):
    print("🔋 Action Points:")
    for unit, ap in apm.get_all_ap().items():
        print(f"  - {unit}: {ap} AP")


def print_fsm_state(fsm: TacticalStateMachine):
    print(f"🎮 Tactical State: {fsm.state.name}")


def print_structured_log(logs):
    print("📜 Structured Log (last 3):")
    for entry in logs[-3:]:
        kind = entry.get("event", "UNKNOWN").upper()
        info = ", ".join(f"{k}={v}" for k, v in entry.items() if k != "event")
        print(f"  [{kind}] {info}")


def handle_player_action(
    choice: str, tc: TurnController, fsm: TacticalStateMachine
) -> bool:
    """Handle a single player action choice. Returns True if turn should end."""
    if choice == "1":  # Move
        if tc.can_act(1):
            fsm.transition_to(TacticalState.PLANNING_MOVE)
            print("🕹️  Moved!")
            tc.spend_ap(1)
            fsm.transition_to(TacticalState.SELECTING_UNIT)
        else:
            print("❌ Not enough AP to move.")
    elif choice == "2":  # Attack
        if tc.can_act(1):
            fsm.transition_to(TacticalState.PLANNING_ATTACK)
            print("💥 Attacked!")
            tc.spend_ap(1)
            fsm.transition_to(TacticalState.SELECTING_UNIT)
        else:
            print("❌ Not enough AP to attack.")
    elif choice == "3":  # Pass
        print("🛑 Passed.")
        return True
    elif choice == "4":  # Undo
        fsm.cancel()
    elif choice == "5":  # End Turn
        print("🔚 Ending turn manually.")
        return True
    else:
        print("❓ Invalid input. Try again.")
    return False


def player_action_menu(runner: SimRunner):
    tc = runner.turn_controller
    apm = tc.action_point_manager
    fsm = tc.tactical_state_machine
    unit = tc.get_current_unit()

    # Check if required components are available
    if apm is None:
        print("❌ Action Point Manager not available")
        return
    if fsm is None:
        print("❌ Tactical State Machine not available")
        return

    while True:
        print(f"\n🎯 Player '{unit}' options:")
        print("  [1] Move (1 AP)")
        print("  [2] Attack (1 AP)")
        print("  [3] Pass")
        print("  [4] Undo (FSM cancel)")
        print("  [5] End Turn")

        print_ap_state(apm)
        print_fsm_state(fsm)

        choice = input("Enter action: ").strip()

        if handle_player_action(choice, tc, fsm):
            break

        if apm.get_ap(unit) == 0:
            print("⚠️ Out of AP — turn must end.")
            break


def run_basic_demo(auto_run: bool = False):
    """Run the basic demo with hardcoded units."""
    print("=== SimRunner CLI Demo with Player Input and Unit Death ===")
    apm = ActionPointManager()
    fsm = TacticalStateMachine()
    tc = TurnController(apm, fsm)

    tc.add_unit("ai_alpha")
    tc.add_unit("p_bravo")
    tc.add_unit("ai_delta")

    ai = DemoAI()
    runner = SimRunner(tc, ai)

    turn_limit = 12
    for _ in range(turn_limit):
        print(f"\n🔄 PHASE: {runner.phase}")

        if runner.phase == "GAME_OVER":
            print("🏁 Game Over — Simulation Complete")
            break

        runner.run_turn()

        # 💀 Simulate death mid-simulation (turn 3)
        if runner.turn_count == 3:
            runner.mark_unit_dead("ai_delta")
            print("💀 ai_delta has died and was removed from the battle.")

        unit_id = tc.get_current_unit()
        if not unit_id.startswith("ai") and not auto_run:
            try:
                player_action_menu(runner)
            except KeyboardInterrupt:
                print("\nDemo interrupted by user.")
                break
        elif not unit_id.startswith("ai") and auto_run:
            print("⏸️  Player turn (auto-advancing in 2 seconds...)")
            time.sleep(2)

        print_structured_log(runner.get_log())
        print("-" * 40)
        time.sleep(0.5)

    print("\n=== Demo Ended ===")
    print(f"🤖 AI Actions taken: {ai.actions}")
    print(f"📊 Total turns completed: {runner.turn_count}")
    print(f"🎮 Final game phase: {runner.phase}")
    print(f"💀 Dead units: {runner.dead_units}")


def run_scenario_demo(
    auto_run: bool = False, scenario_path: str = "devtools/scenarios/demo_battle.yaml"
):
    """Run the scenario-based demo."""
    print("=== Scenario-Based SimRunner CLI Demo ===")
    
    # Create mock objects for ScenarioManager
    class MockCamera:
        def cinematic_pan(self, targets, speed):
            print(f"📹 Camera panning to {targets} at speed {speed}")
    
    class MockAIController:
        def get_unit(self, unit_name):
            return unit_name
        def attack(self, unit, target):
            print(f"🤖 {unit} attacks {target}")
        def move(self, unit, position):
            print(f"🤖 {unit} moves to {position}")
    
    class MockPlayerUnit:
        def prepare_for_battle(self):
            print("⚔️ Player unit prepares for battle")
    
    camera = MockCamera()
    ai_controller = MockAIController()
    player_unit = MockPlayerUnit()
    game_state = GameState()
    
    # Create scenario manager and load scenario
    scenario_manager = create_scenario_manager(camera, ai_controller, player_unit, game_state)
    game_state = scenario_manager.load_scenario(scenario_path)

    print(f"📘 Scenario: {game_state.name}")
    print(f"📝 {game_state.description}")

    tc = game_state.turn_controller
    ai = DemoAI()

    runner = SimRunner(tc, ai)
    runner.max_turns = game_state.max_turns

    # Get death configuration from scenario metadata
    death_on_turn = game_state.metadata.get("death_on_turn")
    death_unit = game_state.metadata.get("death_unit")

    for _ in range(runner.max_turns + 1):
        print(f"\n🔄 PHASE: {runner.phase}")
        if runner.phase == "GAME_OVER":
            print("🏁 Game Over — Simulation Complete")
            break

        runner.run_turn()

        # 💀 Simulate death based on scenario configuration
        if death_on_turn and death_unit and runner.turn_count == death_on_turn:
            runner.mark_unit_dead(death_unit)
            print(f"💀 {death_unit} has died and was removed from the battle.")

        unit_id = tc.get_current_unit()
        # Check if unit is AI based on team, not just ID prefix
        is_ai_unit = game_state.units.get_team(unit_id) == "ai"

        if not is_ai_unit and not auto_run:
            try:
                player_action_menu(runner)
            except KeyboardInterrupt:
                print("\nDemo interrupted by user.")
                break
        elif not is_ai_unit and auto_run:
            print("⏸️  Player turn (auto-advancing in 2 seconds...)")
            time.sleep(2)

        print_structured_log(runner.get_log())
        print("-" * 40)
        time.sleep(0.5)

    print("\n=== Demo Ended ===")
    print(f"🤖 AI Actions taken: {ai.actions}")
    print(f"📊 Total turns completed: {runner.turn_count}")
    print(f"🎮 Final game phase: {runner.phase}")
    print(f"💀 Dead units: {runner.dead_units}")


def main():
    # Check for auto-run mode
    auto_run = "--auto" in sys.argv or "-a" in sys.argv

    # Auto-enable auto-run if a scenario file is provided as an argument
    scenario_path = None
    if len(sys.argv) > 1 and not any(arg.startswith("-") for arg in sys.argv[1:]):
        auto_run = True
        scenario_path = sys.argv[1]
        print("🚀 Auto-run mode automatically enabled for scenario file")

    if auto_run:
        print("🚀 Auto-run mode enabled - no user input required")

    # Check for scenario mode
    if "--scenario" in sys.argv or "-s" in sys.argv or scenario_path:
        run_scenario_demo(
            auto_run, scenario_path or "devtools/scenarios/demo_battle.yaml"
        )
    else:
        run_basic_demo(auto_run)


if __name__ == "__main__":
    main()
