import yaml

from game.game_state import GameState
from map_loader import load_map


def load_scenario(path: str) -> GameState:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    scenario_name = data.get("name", "Unnamed Scenario")
    units = data.get("units", [])
    metadata = data.get("metadata", {})

    if not isinstance(units, list) or not units:
        raise ValueError("Scenario must include a non-empty 'units' list.")

    game_state = GameState()

    # Handle map_id from both top-level and metadata
    map_id = data.get("map_id") or metadata.get("map", "default_map")

    # Use the new set_metadata method
    game_state.set_metadata(
        name=scenario_name,
        map_id=map_id,
        objective=metadata.get("objective", "Defeat all enemies"),
        max_turns=metadata.get("max_turns", 20),
    )

    # Set additional metadata fields
    game_state.description = data.get("description", "")
    game_state.metadata = metadata

    for unit in units:
        if not all(k in unit for k in ("id", "team", "hp", "ap")):
            raise ValueError(f"Unit definition incomplete: {unit}")

        # Add the unit to the game state
        game_state.add_unit(
            unit_id=unit["id"], team=unit["team"], hp=unit["hp"], ap=unit["ap"]
        )

        # Handle fake death mechanics if present
        if unit.get("fake_death", False):
            game_state.units.mark_as_fake_dead(unit["id"])

        # Store revival HP in metadata for future use
        if "revive_hp" in unit:
            if "revival_data" not in game_state.metadata:
                game_state.metadata["revival_data"] = {}
            game_state.metadata["revival_data"][unit["id"]] = {
                "revive_hp": unit["revive_hp"]
            }

    # Load terrain grid based on map_id
    try:
        game_state.terrain_grid = load_map(game_state.map_id)
    except (FileNotFoundError, ValueError) as e:
        # If terrain loading fails, use empty grid and log warning
        print(f"Warning: Could not load terrain for map '{game_state.map_id}': {e}")
        game_state.terrain_grid = []

    return game_state


def load_scenario_from_file(filepath: str) -> GameState:
    """
    Alternative scenario loading function that uses direct unit registration.
    This is kept for backward compatibility but load_scenario is preferred.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    state = GameState()
    state.name = data.get("name", "Untitled Scenario")
    state.description = data.get("description", "")
    state.map_id = data.get("map_id", "default_map")
    state.objective = data.get("objective", "Defeat all enemies")
    state.max_turns = data.get("max_turns", 20)

    for unit in data.get("units", []):
        uid = unit["id"]
        team = unit["team"]
        hp = unit["hp"]
        ap = unit["ap"]

        # Use the proper add_unit method instead of direct access
        state.add_unit(uid, team, ap=ap, hp=hp)

        if unit.get("fake_death"):
            state.units.mark_as_fake_dead(uid)

    # Load terrain grid based on map_id
    try:
        state.terrain_grid = load_map(state.map_id)
    except (FileNotFoundError, ValueError) as e:
        # If terrain loading fails, use empty grid and log warning
        print(f"Warning: Could not load terrain for map '{state.map_id}': {e}")
        state.terrain_grid = []

    return state
