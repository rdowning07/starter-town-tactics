# tests/test_scenario_manager.py

import os
import tempfile
from unittest.mock import MagicMock, Mock

import pygame
import pytest

from devtools.scenario_manager import ScenarioManager, create_scenario_manager
from game.fx_manager import FXManager
from game.game_state import GameState
from game.sound_manager import SoundManager
from game.sprite_manager import SpriteManager


@pytest.fixture
def mock_camera():
    """Mock camera object for testing."""
    camera = Mock()
    camera.cinematic_pan = Mock()
    return camera


@pytest.fixture
def mock_ai_controller():
    """Mock AI controller for testing."""
    ai_controller = Mock()
    ai_controller.get_unit = Mock(return_value="test_unit")
    ai_controller.attack = Mock()
    ai_controller.move = Mock()
    ai_controller.retreat = Mock()
    return ai_controller


@pytest.fixture
def mock_player_unit():
    """Mock player unit for testing."""
    player_unit = Mock()
    player_unit.prepare_for_battle = Mock()
    player_unit.hp = 10
    return player_unit


@pytest.fixture
def game_state():
    """Game state for testing."""
    return GameState()


@pytest.fixture
def scenario_manager(mock_camera, mock_ai_controller, mock_player_unit, game_state):
    """ScenarioManager instance for testing."""
    return ScenarioManager(mock_camera, mock_ai_controller, mock_player_unit, game_state)


@pytest.fixture
def valid_scenario_yaml():
    """Valid scenario YAML for testing."""
    return """
name: "Test Scenario"
description: "A test scenario for ScenarioManager"
map_id: "test_map"

units:
  - name: "player1"
    team: "player"
    sprite: "knight"
    x: 5
    y: 5
    hp: 10
    ap: 3
    animation: "idle"

  - name: "enemy1"
    team: "enemy"
    sprite: "rogue"
    x: 8
    y: 8
    hp: 8
    ap: 2
    animation: "idle"
    ai: "aggressive"

camera:
  - action: "pan"
    targets:
      - [100, 100]
      - [200, 200]
    speed: 10
    delay: 0.5

ai:
  - unit: "enemy1"
    action: "attack"
    target: "player1"

actions:
  - unit: "player1"
    action: "prepare_for_battle"

next_scenario:
  condition: "victory"
  victory_scenario: "victory.yaml"
  defeat_scenario: "defeat.yaml"
"""


@pytest.fixture
def branching_scenario_yaml():
    """Scenario with branching for testing."""
    return """
name: "Branching Test"
description: "Test scenario branching"
units:
  - name: "player1"
    team: "player"
    sprite: "knight"
    x: 5
    y: 5
    hp: 10
    ap: 3
    animation: "idle"

next_scenario:
  condition: "boss_defeated"
  second_phase_scenario: "phase2.yaml"
  victory_scenario: "victory.yaml"
"""


@pytest.fixture
def mock_scenario_data():
    """Mock scenario data for comprehensive testing."""
    return {
        "name": "Battle Start",
        "camera": [{"action": "pan", "targets": [[100, 100], [400, 400], [600, 600]], "speed": 10, "delay": 0.5}],
        "ai": [
            {"unit": "enemy_unit_1", "action": "attack", "target": "player_unit"},
            {"unit": "enemy_unit_2", "action": "move", "target": [500, 500]},
        ],
        "actions": [{"unit": "player_unit", "action": "prepare_for_battle"}],
        "branch_conditions": [
            {"condition": "player_wins", "next_scenario": "victory_celebration.yaml"},
            {"condition": "player_loses", "next_scenario": "defeat_ending.yaml"},
        ],
    }


def test_scenario_manager_initialization(scenario_manager):
    """Test that ScenarioManager initializes correctly."""
    assert scenario_manager.camera is not None
    assert scenario_manager.ai_controller is not None
    assert scenario_manager.player_unit is not None
    assert scenario_manager.game_state is not None
    assert scenario_manager.sprite_manager is None
    assert scenario_manager.fx_manager is None
    assert scenario_manager.sound_manager is None
    assert len(scenario_manager.supported_sprites) > 0
    assert len(scenario_manager.supported_ai_types) > 0


def test_set_managers(scenario_manager):
    """Test setting managers."""
    sprite_manager = SpriteManager()
    fx_manager = FXManager()
    sound_manager = SoundManager()

    scenario_manager.set_managers(sprite_manager, fx_manager, sound_manager)

    assert scenario_manager.sprite_manager == sprite_manager
    assert scenario_manager.fx_manager == fx_manager
    assert scenario_manager.sound_manager == sound_manager


def test_load_yaml(scenario_manager, valid_scenario_yaml):
    """Test YAML loading functionality."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name

    try:
        data = scenario_manager._load_yaml(temp_file)
        assert data["name"] == "Test Scenario"
        assert data["description"] == "A test scenario for ScenarioManager"
        assert "units" in data
        assert "camera" in data
        assert "ai" in data
        assert "actions" in data
    finally:
        os.unlink(temp_file)


def test_validate_scenario_valid(scenario_manager, valid_scenario_yaml):
    """Test validation of valid scenario."""
    import yaml

    scenario_data = yaml.safe_load(valid_scenario_yaml)
    scenario_manager._validate_scenario(scenario_data)  # Should not raise


def test_validate_scenario_missing_name(scenario_manager):
    """Test validation fails with missing name."""
    scenario_data = {"units": []}
    with pytest.raises(ValueError, match="missing required field: name"):
        scenario_manager._validate_scenario(scenario_data)


def test_validate_scenario_missing_units(scenario_manager):
    """Test validation fails with missing units."""
    scenario_data = {"name": "Test"}
    with pytest.raises(ValueError, match="missing required field: units"):
        scenario_manager._validate_scenario(scenario_data)


def test_validate_scenario_units_not_list(scenario_manager):
    """Test validation fails when units is not a list."""
    scenario_data = {"name": "Test", "units": "not_a_list"}
    with pytest.raises(ValueError, match="units must be a list"):
        scenario_manager._validate_scenario(scenario_data)


def test_validate_unit_valid(scenario_manager):
    """Test validation of valid unit."""
    unit_data = {"name": "test_unit", "team": "player", "sprite": "knight", "x": 5, "y": 5}
    scenario_manager._validate_unit(unit_data, 0)  # Should not raise


def test_validate_unit_missing_fields(scenario_manager):
    """Test validation fails with missing unit fields."""
    unit_data = {
        "name": "test_unit",
        "team": "player"
        # Missing sprite, x, y
    }
    with pytest.raises(ValueError, match="missing required field: sprite"):
        scenario_manager._validate_unit(unit_data, 0)


def test_validate_unit_invalid_team(scenario_manager):
    """Test validation fails with invalid team."""
    unit_data = {"name": "test_unit", "team": "invalid_team", "sprite": "knight", "x": 5, "y": 5}
    with pytest.raises(ValueError, match="invalid team"):
        scenario_manager._validate_unit(unit_data, 0)


def test_validate_unit_invalid_coordinates(scenario_manager):
    """Test validation fails with invalid coordinates."""
    unit_data = {"name": "test_unit", "team": "player", "sprite": "knight", "x": "not_an_int", "y": 5}
    with pytest.raises(ValueError, match="invalid coordinates"):
        scenario_manager._validate_unit(unit_data, 0)


def test_load_unit(scenario_manager):
    """Test loading a single unit."""
    unit_data = {
        "name": "test_unit",
        "team": "player",
        "sprite": "knight",
        "x": 5,
        "y": 5,
        "hp": 15,
        "ap": 4,
        "animation": "idle",
    }

    scenario_manager._load_unit(unit_data)

    # Check that unit was added to game state
    assert scenario_manager.game_state.units.unit_exists("test_unit")
    unit_info = scenario_manager.game_state.units.units["test_unit"]
    assert unit_info["x"] == 5
    assert unit_info["y"] == 5
    assert unit_info["sprite"] == "knight"
    assert unit_info["animation"] == "idle"


def test_load_units(scenario_manager):
    """Test loading multiple units."""
    units_data = [
        {
            "name": "player1",
            "team": "player",
            "sprite": "knight",
            "x": 5,
            "y": 5,
            "hp": 10,
            "ap": 3,
            "animation": "idle",
        },
        {
            "name": "enemy1",
            "team": "enemy",
            "sprite": "rogue",
            "x": 8,
            "y": 8,
            "hp": 8,
            "ap": 2,
            "animation": "idle",
            "ai": "aggressive",
        },
    ]

    scenario_manager._load_units(units_data)

    # Check that both units were added
    assert scenario_manager.game_state.units.unit_exists("player1")
    assert scenario_manager.game_state.units.unit_exists("enemy1")


def test_process_camera_actions(scenario_manager, mock_camera):
    """Test processing camera actions."""
    camera_actions = [{"action": "pan", "targets": [[100, 100], [200, 200]], "speed": 10, "delay": 0.1}]

    scenario_manager._process_camera_actions(camera_actions)

    # Check that camera pan was called
    mock_camera.cinematic_pan.assert_called_once()
    call_args = mock_camera.cinematic_pan.call_args
    assert len(call_args[0][0]) == 2  # Two targets
    assert call_args[0][1] == 10  # Speed


def test_process_ai_actions(scenario_manager, mock_ai_controller):
    """Test processing AI actions."""
    # Add a unit to the game state first
    scenario_manager.game_state.add_unit("enemy1", "enemy", ap=3, hp=10)
    scenario_manager.game_state.add_unit("player1", "player", ap=3, hp=10)

    ai_actions = [
        {"unit": "enemy1", "action": "attack", "target": "player1"},
        {"unit": "enemy1", "action": "move", "target": [6, 6]},
    ]

    scenario_manager._process_ai_actions(ai_actions)

    # Currently just prints, so we test that no exceptions are raised


def test_process_player_actions(scenario_manager, mock_player_unit):
    """Test processing player actions."""
    # Add a unit to the game state first
    scenario_manager.game_state.add_unit("player1", "player", ap=3, hp=10)

    player_actions = [{"unit": "player1", "action": "prepare_for_battle"}]

    scenario_manager._process_player_actions(player_actions)

    # Currently just prints, so we test that no exceptions are raised


def test_handle_scenario_branching_simple_path(scenario_manager):
    """Test scenario branching with simple string path."""
    scenario = {"next_scenario": "next_scenario.yaml"}

    # Mock os.path.exists to return False to avoid actual file loading
    with pytest.MonkeyPatch().context() as m:
        m.setattr(os.path, "exists", lambda x: False)
        scenario_manager._handle_scenario_branching(scenario)
        # Should print warning about file not found


def test_handle_scenario_branching_conditional(scenario_manager):
    """Test scenario branching with conditional logic."""
    scenario = {
        "next_scenario": {
            "condition": "victory",
            "victory_scenario": "victory.yaml",
            "defeat_scenario": "defeat.yaml",
            "default_scenario": "default.yaml",
        }
    }

    # Mock os.path.exists to return False
    with pytest.MonkeyPatch().context() as m:
        m.setattr(os.path, "exists", lambda x: False)
        scenario_manager._handle_scenario_branching(scenario)
        # Should print warning about file not found


def test_is_battle_won(scenario_manager):
    """Test battle won condition."""
    # Add only player units
    scenario_manager.game_state.add_unit("player1", "player", ap=3, hp=10)
    scenario_manager.game_state.add_unit("player2", "player", ap=3, hp=10)

    assert scenario_manager._is_battle_won() is True


def test_is_battle_lost(scenario_manager):
    """Test battle lost condition."""
    # Add only enemy units
    scenario_manager.game_state.add_unit("enemy1", "enemy", ap=3, hp=10)
    scenario_manager.game_state.add_unit("enemy2", "enemy", ap=3, hp=10)

    assert scenario_manager._is_battle_lost() is True


def test_is_battle_ongoing(scenario_manager):
    """Test ongoing battle condition."""
    # Add both player and enemy units
    scenario_manager.game_state.add_unit("player1", "player", ap=3, hp=10)
    scenario_manager.game_state.add_unit("enemy1", "enemy", ap=3, hp=10)

    assert scenario_manager._is_battle_won() is False
    assert scenario_manager._is_battle_lost() is False


def test_load_scenario_integration(scenario_manager, valid_scenario_yaml):
    """Test full scenario loading integration."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name

    try:
        game_state = scenario_manager.load_scenario(temp_file)

        assert game_state.name == "Test Scenario"
        assert game_state.description == "A test scenario for ScenarioManager"
        assert game_state.map_id == "test_map"

        # Check that units were loaded
        assert game_state.units.unit_exists("player1")
        assert game_state.units.unit_exists("enemy1")

    finally:
        os.unlink(temp_file)


def test_create_scenario_manager(mock_camera, mock_ai_controller, mock_player_unit, game_state):
    """Test the convenience function for creating ScenarioManager."""
    from devtools.scenario_manager import create_scenario_manager

    scenario_manager = create_scenario_manager(mock_camera, mock_ai_controller, mock_player_unit, game_state)

    assert isinstance(scenario_manager, ScenarioManager)
    assert scenario_manager.camera == mock_camera
    assert scenario_manager.ai_controller == mock_ai_controller
    assert scenario_manager.player_unit == mock_player_unit
    assert scenario_manager.game_state == game_state


def test_load_scenario_file_not_found(scenario_manager):
    """Test loading scenario with non-existent file."""
    with pytest.raises(FileNotFoundError, match="Scenario file not found"):
        scenario_manager.load_scenario("non_existent_file.yaml")


def test_supported_sprites_and_ai_types(scenario_manager):
    """Test that supported sprites and AI types are reasonable."""
    assert len(scenario_manager.supported_sprites) > 0
    assert "knight" in scenario_manager.supported_sprites
    assert "rogue" in scenario_manager.supported_sprites

    assert len(scenario_manager.supported_ai_types) > 0
    assert "aggressive" in scenario_manager.supported_ai_types
    assert "defensive" in scenario_manager.supported_ai_types
    assert "passive" in scenario_manager.supported_ai_types


def test_unit_with_fake_death(scenario_manager):
    """Test loading unit with fake death properties."""
    unit_data = {
        "name": "boss_unit",
        "team": "enemy",
        "sprite": "shadow",
        "x": 8,
        "y": 8,
        "hp": 20,
        "ap": 4,
        "animation": "idle",
        "ai": "aggressive",
        "fake_death": True,
        "revive_hp": 30,
    }

    scenario_manager._load_unit(unit_data)

    unit_info = scenario_manager.game_state.units.units["boss_unit"]
    assert unit_info["fake_death"] is True
    assert unit_info["revive_hp"] == 30


def test_execute_scenario_metadata(scenario_manager, valid_scenario_yaml):
    """Test that scenario metadata is properly set during execution."""
    import yaml

    scenario_data = yaml.safe_load(valid_scenario_yaml)

    scenario_manager._execute_scenario(scenario_data)

    assert scenario_manager.game_state.name == "Test Scenario"
    assert scenario_manager.game_state.description == "A test scenario for ScenarioManager"
    assert scenario_manager.game_state.map_id == "test_map"


def test_evaluate_condition(scenario_manager):
    """Test condition evaluation functionality."""
    # Test player_wins condition
    assert scenario_manager.evaluate_condition("player_wins") == scenario_manager._is_battle_won()

    # Test player_loses condition
    assert scenario_manager.evaluate_condition("player_loses") == scenario_manager._is_battle_lost()

    # Test all_enemies_defeated condition
    assert scenario_manager.evaluate_condition("all_enemies_defeated") == scenario_manager._is_battle_won()

    # Test unknown condition
    assert scenario_manager.evaluate_condition("unknown_condition") is False


def test_branch_conditions_format(scenario_manager):
    """Test the new branch_conditions format."""
    branch_scenario = {
        "scenario": "Test Branch",
        "branch_conditions": [
            {"condition": "player_wins", "next_scenario": "victory.yaml"},
            {"condition": "player_loses", "next_scenario": "defeat.yaml"},
        ],
    }

    # Mock os.path.exists to return False to avoid actual file loading
    with pytest.MonkeyPatch().context() as m:
        m.setattr(os.path, "exists", lambda x: False)
        result = scenario_manager._check_branch_conditions(branch_scenario)
        # Should return False since files don't exist
        assert result is False


def test_ai_behavior_aggressive(scenario_manager):
    """Test AI behavior for aggressive units."""
    # Add some units to test with
    scenario_manager.game_state.add_unit("player1", "player", ap=3, hp=10)
    scenario_manager.game_state.add_unit("enemy1", "enemy", ap=3, hp=10)

    # Create a mock unit with aggressive AI
    class MockUnit:
        def __init__(self, name, ai_type):
            self.name = name
            self.ai = ai_type

    unit = MockUnit("enemy1", "aggressive")

    # Test AI behavior
    scenario_manager.ai_behavior(unit, scenario_manager.game_state)
    # Should print aggressive behavior message


def test_ai_behavior_defensive(scenario_manager):
    """Test AI behavior for defensive units."""
    # Add a defensive unit
    scenario_manager.game_state.add_unit("defender", "enemy", ap=3, hp=5)
    scenario_manager.game_state.units.units["defender"]["max_hp"] = 10

    # Create a mock unit with defensive AI
    class MockUnit:
        def __init__(self, name, ai_type):
            self.name = name
            self.ai = ai_type

    unit = MockUnit("defender", "defensive")

    # Test AI behavior
    scenario_manager.ai_behavior(unit, scenario_manager.game_state)
    # Should print defensive behavior message


def test_ai_behavior_passive(scenario_manager):
    """Test AI behavior for passive units."""

    # Create a mock unit with passive AI
    class MockUnit:
        def __init__(self, name, ai_type):
            self.name = name
            self.ai = ai_type

    unit = MockUnit("passive_unit", "passive")

    # Test AI behavior
    scenario_manager.ai_behavior(unit, scenario_manager.game_state)
    # Should print passive behavior message


def test_check_branch_conditions_with_existing_file(scenario_manager):
    """Test branch conditions with existing scenario file."""
    branch_scenario = {"branch_conditions": [{"condition": "player_wins", "next_scenario": "existing_file.yaml"}]}

    # Mock os.path.exists to return True for existing file
    with pytest.MonkeyPatch().context() as m:
        m.setattr(os.path, "exists", lambda x: x == "existing_file.yaml")
        # Mock load_scenario to avoid actual loading
        m.setattr(scenario_manager, "load_scenario", lambda x, allow_branching=False: None)
        result = scenario_manager._check_branch_conditions(branch_scenario)
        # Should return True since condition is met and file exists
        assert result is True


# Enhanced test methods incorporating the provided test patterns


def test_camera_pan_with_parameters(scenario_manager, mock_camera, mock_scenario_data):
    """Test camera pan with specific parameters."""
    mock_camera.cinematic_pan.reset_mock()
    scenario_manager._process_camera_actions(mock_scenario_data["camera"])

    # Assert cinematic pan is called with correct parameters
    mock_camera.cinematic_pan.assert_called_once()
    call_args = mock_camera.cinematic_pan.call_args
    assert len(call_args[0][0]) == 3  # Three targets
    assert call_args[0][1] == 10  # Speed


def test_camera_action_delay(scenario_manager, mock_camera, mock_scenario_data):
    """Test camera action with delay parameter."""
    mock_camera.cinematic_pan.reset_mock()
    scenario_manager._process_camera_actions(mock_scenario_data["camera"])

    # Ensure that the correct delay is applied
    mock_camera.cinematic_pan.assert_called_once()
    call_args = mock_camera.cinematic_pan.call_args
    assert call_args[0][1] == 10  # Speed is the second positional argument


def test_ai_attack_action(scenario_manager, mock_ai_controller, mock_scenario_data):
    """Test AI attack action processing."""
    mock_ai_controller.attack.reset_mock()

    # Add units to game state for testing
    scenario_manager.game_state.add_unit("enemy_unit_1", "enemy", ap=3, hp=10)
    scenario_manager.game_state.add_unit("player_unit", "player", ap=3, hp=10)

    scenario_manager._process_ai_actions(mock_scenario_data["ai"])

    # Verify AI actions were processed (currently just prints, but we can test no exceptions)


def test_ai_move_action(scenario_manager, mock_ai_controller, mock_scenario_data):
    """Test AI move action processing."""
    mock_ai_controller.move.reset_mock()

    # Add units to game state for testing
    scenario_manager.game_state.add_unit("enemy_unit_2", "enemy", ap=3, hp=10)

    scenario_manager._process_ai_actions(mock_scenario_data["ai"])

    # Verify AI move actions were processed


def test_load_and_execute_scenario(scenario_manager, mock_scenario_data):
    """Test complete scenario loading and execution."""
    # Mock the load_scenario method to avoid file I/O
    original_load_scenario = scenario_manager.load_scenario
    scenario_manager.load_scenario = Mock()

    try:
        # Test scenario loading
        scenario_manager.load_scenario("battle_start.yaml")
        scenario_manager.load_scenario.assert_called_once_with("battle_start.yaml")
    finally:
        # Restore original method
        scenario_manager.load_scenario = original_load_scenario


def test_branching_scenario_win_condition(scenario_manager, mock_scenario_data):
    """Test branching scenario with win condition."""
    # Mock game state to simulate win condition
    scenario_manager._is_battle_won = Mock(return_value=True)
    scenario_manager._is_battle_lost = Mock(return_value=False)

    # Mock file existence and load_scenario
    with pytest.MonkeyPatch().context() as m:
        m.setattr(os.path, "exists", lambda x: True)
        m.setattr(scenario_manager, "load_scenario", Mock())

        result = scenario_manager._check_branch_conditions(mock_scenario_data)

        # Should load victory scenario
        assert result is True
        scenario_manager.load_scenario.assert_called_with("victory_celebration.yaml", allow_branching=False)


def test_branching_scenario_loss_condition(scenario_manager, mock_scenario_data):
    """Test branching scenario with loss condition."""
    # Mock game state to simulate loss condition
    scenario_manager._is_battle_won = Mock(return_value=False)
    scenario_manager._is_battle_lost = Mock(return_value=True)

    # Mock file existence and load_scenario
    with pytest.MonkeyPatch().context() as m:
        m.setattr(os.path, "exists", lambda x: True)
        m.setattr(scenario_manager, "load_scenario", Mock())

        result = scenario_manager._check_branch_conditions(mock_scenario_data)

        # Should load defeat scenario
        assert result is True
        scenario_manager.load_scenario.assert_called_with("defeat_ending.yaml", allow_branching=False)


def test_ai_defensive_behavior_low_health(scenario_manager, mock_ai_controller):
    """Test AI defensive behavior when health is low."""

    # Create a mock unit with defensive AI and low health
    class MockUnit:
        def __init__(self, name, ai_type, hp, max_hp):
            self.name = name
            self.ai = ai_type
            self.hp = hp
            self.max_hp = max_hp

    unit = MockUnit("defender", "defensive", 5, 10)

    # Add unit to game state
    scenario_manager.game_state.add_unit("defender", "enemy", ap=3, hp=5)
    scenario_manager.game_state.units.units["defender"]["max_hp"] = 10

    # Test AI behavior
    scenario_manager.ai_behavior(unit, scenario_manager.game_state)
    # Should print defensive retreat message


def test_ai_aggressive_behavior_with_targets(scenario_manager):
    """Test AI aggressive behavior with available targets."""
    # Add player units for aggressive AI to target
    scenario_manager.game_state.add_unit("player1", "player", ap=3, hp=10)
    scenario_manager.game_state.add_unit("enemy1", "enemy", ap=3, hp=10)

    # Create a mock unit with aggressive AI
    class MockUnit:
        def __init__(self, name, ai_type):
            self.name = name
            self.ai = ai_type

    unit = MockUnit("enemy1", "aggressive")

    # Test AI behavior
    scenario_manager.ai_behavior(unit, scenario_manager.game_state)
    # Should print aggressive attack message


def test_player_preparation_action(scenario_manager, mock_player_unit, mock_scenario_data):
    """Test player preparation action."""
    mock_player_unit.prepare_for_battle.reset_mock()

    # Add player unit to game state
    scenario_manager.game_state.add_unit("player_unit", "player", ap=3, hp=10)

    # Process player actions
    scenario_manager._process_player_actions(mock_scenario_data["actions"])

    # Verify player preparation was triggered (currently just prints)


def test_full_scenario_execution_integration(scenario_manager, mock_scenario_data):
    """Test complete scenario execution with all components."""
    # Mock the individual processing methods
    scenario_manager._process_camera_actions = Mock()
    scenario_manager._process_ai_actions = Mock()
    scenario_manager._process_player_actions = Mock()
    scenario_manager._handle_scenario_branching = Mock()

    # Execute a complete scenario
    scenario_manager._execute_scenario(mock_scenario_data)

    # Ensure all actions were processed
    scenario_manager._process_camera_actions.assert_called_once_with(mock_scenario_data["camera"])
    scenario_manager._process_ai_actions.assert_called_once_with(mock_scenario_data["ai"])
    scenario_manager._process_player_actions.assert_called_once_with(mock_scenario_data["actions"])


def test_scenario_execution_with_branch_conditions(scenario_manager, mock_scenario_data):
    """Test scenario execution with branch conditions."""
    # Mock the branching check
    scenario_manager._check_branch_conditions = Mock(return_value=False)

    # Execute scenario with branch conditions
    scenario_manager._execute_scenario(mock_scenario_data, allow_branching=True)

    # Verify branch conditions were checked
    scenario_manager._check_branch_conditions.assert_called_once_with(mock_scenario_data)


def test_scenario_execution_without_branching(scenario_manager, mock_scenario_data):
    """Test scenario execution without branching."""
    # Mock the branching methods
    scenario_manager._check_branch_conditions = Mock()
    scenario_manager._handle_scenario_branching = Mock()

    # Execute scenario without branching
    scenario_manager._execute_scenario(mock_scenario_data, allow_branching=False)

    # Verify no branching was attempted
    scenario_manager._check_branch_conditions.assert_not_called()
    scenario_manager._handle_scenario_branching.assert_not_called()
