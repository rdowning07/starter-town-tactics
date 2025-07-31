import yaml
from game.turn_controller import TurnController
from game.action_point_manager import ActionPointManager
from game.tactical_state_machine import TacticalStateMachine


def load_scenario(path: str):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    apm = ActionPointManager()
    fsm = TacticalStateMachine()
    tc = TurnController(apm, fsm)

    for unit in data.get("units", []):
        unit_id = unit["id"]
        tc.add_unit(unit_id)
        apm.register_unit(unit_id, ap=unit.get("ap", 2))
        # Stub: HP/team/etc. could be registered in a future UnitManager

    scenario_info = {
        "name": data.get("name", "Unnamed Scenario"),
        "description": data.get("description", ""),
        "turn_controller": tc,
        "action_point_manager": apm,
        "fsm": fsm,
        "max_turns": data.get("metadata", {}).get("max_turns", 20),
        "metadata": data.get("metadata", {}),
    }

    return scenario_info
