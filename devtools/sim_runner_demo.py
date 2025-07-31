import time
import sys
from game.turn_controller import TurnController
from game.tactical_state_machine import TacticalStateMachine, TacticalState
from game.action_point_manager import ActionPointManager
from game.sim_runner import SimRunner
from game.ai_controller import AIController
from devtools.scenario_loader import load_scenario


class DemoAI:
    """Simple AI controller for demo purposes that works with string IDs."""

    def __init__(self):
        self.actions = []

    def take_action(self, unit_id: str):
        """Take action for a unit identified by string ID."""
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

        if choice == "1":
            if tc.can_act(1):
                fsm.transition_to(TacticalState.PLANNING_MOVE)
                print("🕹️  Moved!")
                tc.spend_ap(1)
                fsm.transition_to(TacticalState.SELECTING_UNIT)
            else:
                print("❌ Not enough AP to move.")
        elif choice == "2":
            if tc.can_act(1):
                fsm.transition_to(TacticalState.PLANNING_ATTACK)
                print("💥 Attacked!")
                tc.spend_ap(1)
                fsm.transition_to(TacticalState.SELECTING_UNIT)
            else:
                print("❌ Not enough AP to attack.")
        elif choice == "3":
            print("🛑 Passed.")
            break
        elif choice == "4":
            fsm.cancel()
        elif choice == "5":
            print("🔚 Ending turn manually.")
            break
        else:
            print("❓ Invalid input. Try again.")

        if apm.get_ap(unit) == 0:
            print("⚠️ Out of AP — turn must end.")
            break


def run_basic_demo():
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
    for turn_num in range(turn_limit):
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


def run_scenario_demo():
    """Run the scenario-based demo."""
    print("=== Scenario-Based SimRunner CLI Demo ===")
    scenario = load_scenario("devtools/scenarios/demo_battle.yaml")

    print(f"📘 Scenario: {scenario['name']}")
    print(f"📝 {scenario['description']}")

    tc = scenario["turn_controller"]
    apm = scenario["action_point_manager"]
    fsm = scenario["fsm"]
    ai = DemoAI()

    runner = SimRunner(tc, ai)
    runner.max_turns = scenario["max_turns"]

    # Get death configuration from scenario
    death_on_turn = scenario["metadata"].get("death_on_turn")
    death_unit = scenario["metadata"].get("death_unit")

    for turn_num in range(runner.max_turns + 1):
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


def main():
    # Check for auto-run mode
    global auto_run
    auto_run = "--auto" in sys.argv or "-a" in sys.argv
    if auto_run:
        print("🚀 Auto-run mode enabled - no user input required")

    # Check for scenario mode
    if "--scenario" in sys.argv or "-s" in sys.argv:
        run_scenario_demo()
    else:
        run_basic_demo()


if __name__ == "__main__":
    main()
