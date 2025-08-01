import pytest
import tempfile
import os
import yaml
from devtools.scenario_loader import load_scenario


# === Fixtures ===

def write_yaml(temp_path: str, data: dict) -> str:
    """Helper function to write YAML data to a temporary file."""
    with open(temp_path, "w") as f:
        yaml.dump(data, f)
    return temp_path


# === Happy Path ===

def test_load_valid_scenario_creates_gamestate():
    """Test that a valid scenario creates a properly configured GameState."""
    scenario_data = {
        "name": "Demo Battle",
        "description": "Test scenario",
        "metadata": {
            "objective": "Survive 5 turns",
            "map": "demo_map",
            "max_turns": 5,
        },
        "units": [
            {"id": "u1", "team": "player", "hp": 10, "ap": 2},
            {"id": "u2", "team": "ai", "hp": 8, "ap": 3},
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, scenario_data)

    game_state = load_scenario(path)
    os.remove(path)

    # Test basic metadata
    assert game_state.name == "Demo Battle"
    assert game_state.description == "Test scenario"
    assert game_state.objective == "Survive 5 turns"
    assert game_state.map_id == "demo_map"
    assert game_state.max_turns == 5
    
    # Test unit registration
    assert game_state.units.get_team("u1") == "player"
    assert game_state.units.get_team("u2") == "ai"
    assert game_state.units.get_hp("u1") == 10
    assert game_state.units.get_hp("u2") == 8
    
    # Test action points
    assert game_state.ap_manager.get_ap("u1") == 2
    assert game_state.ap_manager.get_ap("u2") == 3


def test_default_values_when_fields_missing():
    """Test that default values are applied when optional fields are missing."""
    minimal_data = {
        "units": [
            {"id": "u1", "team": "player", "hp": 10, "ap": 2},
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, minimal_data)

    game_state = load_scenario(path)
    os.remove(path)

    # Test default values
    assert game_state.name == "Unnamed Scenario"
    assert game_state.description == ""
    assert game_state.objective == "Defeat all enemies"
    assert game_state.map_id == "default_map"
    assert game_state.max_turns == 20
    assert game_state.metadata == {}


def test_loaded_gamestate_works_with_turn_controller():
    """Test that the loaded GameState works correctly with turn controller."""
    scenario_data = {
        "units": [
            {"id": "u1", "team": "player", "hp": 10, "ap": 2},
            {"id": "u2", "team": "ai", "hp": 8, "ap": 3},
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, scenario_data)

    game_state = load_scenario(path)
    os.remove(path)

    # Test turn controller integration
    current_unit = game_state.get_current_unit()
    assert current_unit in ["u1", "u2"]
    
    # Test that units are in turn order
    assert "u1" in game_state.turn_controller.units
    assert "u2" in game_state.turn_controller.units


def test_loaded_gamestate_works_with_action_points():
    """Test that action points are properly configured and accessible."""
    scenario_data = {
        "units": [
            {"id": "u1", "team": "player", "hp": 10, "ap": 2},
            {"id": "u2", "team": "ai", "hp": 8, "ap": 3},
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, scenario_data)

    game_state = load_scenario(path)
    os.remove(path)

    # Test action point manager integration
    assert game_state.ap_manager.get_ap("u1") == 2
    assert game_state.ap_manager.get_ap("u2") == 3
    
    # Test that AP can be spent
    assert game_state.turn_controller.can_act(1)  # Should have enough AP for 1 action


def test_fake_death_functionality():
    """Test that fake death mechanics are properly loaded from scenario files."""
    scenario_data = {
        "name": "Boss Test",
        "description": "A fake-out death boss.",
        "metadata": {
            "map": "arena",
            "objective": "Defeat boss twice",
            "max_turns": 12,
        },
        "units": [
            {"id": "hero", "team": "player", "hp": 10, "ap": 3},
            {"id": "boss", "team": "ai", "hp": 10, "ap": 3, "fake_death": True, "revive_hp": 20},
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, scenario_data)

    game_state = load_scenario(path)
    os.remove(path)

    # Test basic scenario data
    assert game_state.name == "Boss Test"
    assert game_state.map_id == "arena"
    assert game_state.max_turns == 12
    
    # Test unit registration
    assert game_state.units.get_hp("hero") == 10
    assert game_state.units.is_alive("boss")
    
    # Test fake death functionality
    assert "boss" in game_state.units.fake_dead_units
    assert game_state.units.is_effectively_alive("boss")
    
    # Test revival data storage
    assert "revival_data" in game_state.metadata
    assert "boss" in game_state.metadata["revival_data"]
    assert game_state.metadata["revival_data"]["boss"]["revive_hp"] == 20
    
    # Test win/loss conditions
    assert not game_state.has_won()
    assert not game_state.has_lost()


# === Error Cases ===

def test_load_fails_on_missing_units():
    """Test that loading fails when units list is empty."""
    bad_data = {
        "name": "Bad Scenario",
        "metadata": {"map": "m1", "objective": "None"},
        "units": [],  # Invalid
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_data)

    with pytest.raises(ValueError, match="non-empty 'units'"):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_unit_missing_fields():
    """Test that loading fails when unit definitions are incomplete."""
    bad_unit_data = {
        "name": "Bad Units",
        "units": [
            {"id": "u1", "team": "player"},  # Missing hp, ap
        ]
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_unit_data)

    with pytest.raises(ValueError, match="Unit definition incomplete"):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_missing_file():
    """Test that loading fails when the scenario file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        load_scenario("nonexistent.yaml")


def test_load_fails_on_malformed_yaml():
    """Test that loading fails when YAML syntax is invalid."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        tf.write(b"invalid: yaml: [syntax: {")
        tf.flush()
        path = tf.name

    with pytest.raises(yaml.YAMLError):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_units_not_list():
    """Test that loading fails when units is not a list."""
    bad_data = {
        "units": "not a list",  # Should be a list
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_data)

    with pytest.raises(ValueError, match="non-empty 'units'"):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_units_none():
    """Test that loading fails when units is None."""
    bad_data = {
        "units": None,  # Should be a list
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_data)

    with pytest.raises(ValueError, match="non-empty 'units'"):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_unit_missing_id():
    """Test that loading fails when a unit is missing the id field."""
    bad_unit_data = {
        "units": [
            {"team": "player", "hp": 10, "ap": 2},  # Missing id
        ]
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_unit_data)

    with pytest.raises(ValueError, match="Unit definition incomplete"):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_unit_missing_team():
    """Test that loading fails when a unit is missing the team field."""
    bad_unit_data = {
        "units": [
            {"id": "u1", "hp": 10, "ap": 2},  # Missing team
        ]
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_unit_data)

    with pytest.raises(ValueError, match="Unit definition incomplete"):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_unit_missing_hp():
    """Test that loading fails when a unit is missing the hp field."""
    bad_unit_data = {
        "units": [
            {"id": "u1", "team": "player", "ap": 2},  # Missing hp
        ]
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_unit_data)

    with pytest.raises(ValueError, match="Unit definition incomplete"):
        load_scenario(path)

    os.remove(path)


def test_load_fails_on_unit_missing_ap():
    """Test that loading fails when a unit is missing the ap field."""
    bad_unit_data = {
        "units": [
            {"id": "u1", "team": "player", "hp": 10},  # Missing ap
        ]
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, bad_unit_data)

    with pytest.raises(ValueError, match="Unit definition incomplete"):
        load_scenario(path)

    os.remove(path)


# === Edge Cases ===

def test_metadata_preservation():
    """Test that metadata is properly preserved in the GameState."""
    scenario_data = {
        "metadata": {
            "custom_field": "custom_value",
            "nested": {"key": "value"},
            "numbers": [1, 2, 3],
        },
        "units": [
            {"id": "u1", "team": "player", "hp": 10, "ap": 2},
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, scenario_data)

    game_state = load_scenario(path)
    os.remove(path)

    # Test that metadata is preserved
    assert game_state.metadata["custom_field"] == "custom_value"
    assert game_state.metadata["nested"]["key"] == "value"
    assert game_state.metadata["numbers"] == [1, 2, 3]


def test_multiple_units_with_same_team():
    """Test that multiple units with the same team are handled correctly."""
    scenario_data = {
        "units": [
            {"id": "u1", "team": "player", "hp": 10, "ap": 2},
            {"id": "u2", "team": "player", "hp": 8, "ap": 3},
            {"id": "u3", "team": "ai", "hp": 12, "ap": 1},
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tf:
        path = write_yaml(tf.name, scenario_data)

    game_state = load_scenario(path)
    os.remove(path)

    # Test that all units are registered
    assert game_state.units.get_team("u1") == "player"
    assert game_state.units.get_team("u2") == "player"
    assert game_state.units.get_team("u3") == "ai"
    
    # Test that all units are in turn controller
    assert "u1" in game_state.turn_controller.units
    assert "u2" in game_state.turn_controller.units
    assert "u3" in game_state.turn_controller.units
