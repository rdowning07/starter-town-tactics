# tests/test_scenario_loader.py

import pytest
import tempfile
import os
from devtools.scenario_loader import ScenarioLoader, load_scenario, trigger_battle_scenario
from game.sprite_manager import SpriteManager
from game.fx_manager import FXManager
from game.sound_manager import SoundManager

@pytest.fixture
def scenario_loader():
    return ScenarioLoader()

@pytest.fixture
def sprite_manager():
    return SpriteManager()

@pytest.fixture
def fx_manager():
    return FXManager()

@pytest.fixture
def sound_manager():
    return SoundManager()

@pytest.fixture
def valid_scenario_yaml():
    return """
name: "Test Scenario"
description: "A test scenario for unit testing"
map_id: "test_map"

units:
  - name: "Test Knight"
    team: player
    sprite: knight
    x: 5
    y: 5
    hp: 10
    ap: 3
    animation: idle

  - name: "Test Enemy"
    team: enemy
    sprite: rogue
    x: 6
    y: 5
    hp: 8
    ap: 2
    animation: idle
    ai: aggressive

camera:
  - action: "pan"
    targets: 
      - [100, 100]
      - [200, 200]
      - [300, 300]
    speed: 10
    delay: 0.5

ai:
  - unit: "Test Enemy"
    action: "attack"
    target: "Test Knight"

actions:
  - unit: "Test Knight"
    action: "prepare_for_battle"
"""

@pytest.fixture
def camera_mock():
    """Mock camera object for testing."""
    class MockCamera:
        def __init__(self):
            self.pan_called = False
            self.pan_targets = None
            self.pan_speed = None
        
        def cinematic_pan(self, targets, speed):
            self.pan_called = True
            self.pan_targets = targets
            self.pan_speed = speed
    
    return MockCamera()

def test_scenario_loader_initialization(scenario_loader):
    """Test that ScenarioLoader initializes correctly."""
    assert scenario_loader is not None
    assert hasattr(scenario_loader, 'supported_sprites')
    assert hasattr(scenario_loader, 'supported_ai_types')
    assert isinstance(scenario_loader.supported_sprites, list)
    assert isinstance(scenario_loader.supported_ai_types, list)

def test_validate_scenario_valid(scenario_loader, valid_scenario_yaml):
    """Test validation of a valid scenario."""
    import yaml
    scenario_data = yaml.safe_load(valid_scenario_yaml)
    
    # Should not raise any exceptions
    scenario_loader._validate_scenario(scenario_data)

def test_validate_scenario_missing_name(scenario_loader):
    """Test validation fails when name is missing."""
    scenario_data = {
        "units": []
    }
    
    with pytest.raises(ValueError, match="Scenario missing required field: name"):
        scenario_loader._validate_scenario(scenario_data)

def test_validate_scenario_missing_units(scenario_loader):
    """Test validation fails when units is missing."""
    scenario_data = {
        "name": "Test"
    }
    
    with pytest.raises(ValueError, match="Scenario missing required field: units"):
        scenario_loader._validate_scenario(scenario_data)

def test_validate_scenario_units_not_list(scenario_loader):
    """Test validation fails when units is not a list."""
    scenario_data = {
        "name": "Test",
        "units": "not a list"
    }
    
    with pytest.raises(ValueError, match="Scenario units must be a list"):
        scenario_loader._validate_scenario(scenario_data)

def test_validate_unit_valid(scenario_loader):
    """Test validation of a valid unit."""
    unit_data = {
        "name": "Test Unit",
        "team": "player",
        "sprite": "knight",
        "x": 5,
        "y": 5,
        "hp": 10,
        "animation": "idle"
    }
    
    # Should not raise any exceptions
    scenario_loader._validate_unit(unit_data, 0)

def test_validate_unit_missing_required_fields(scenario_loader):
    """Test validation fails when required fields are missing."""
    unit_data = {
        "name": "Test Unit",
        "team": "player"
        # Missing sprite, x, y
    }
    
    with pytest.raises(ValueError, match="Unit 0 missing required field: sprite"):
        scenario_loader._validate_unit(unit_data, 0)

def test_validate_unit_invalid_team(scenario_loader):
    """Test validation fails with invalid team."""
    unit_data = {
        "name": "Test Unit",
        "team": "invalid_team",
        "sprite": "knight",
        "x": 5,
        "y": 5
    }
    
    with pytest.raises(ValueError, match="Unit Test Unit has invalid team: invalid_team"):
        scenario_loader._validate_unit(unit_data, 0)

def test_validate_unit_invalid_coordinates(scenario_loader):
    """Test validation fails with invalid coordinates."""
    unit_data = {
        "name": "Test Unit",
        "team": "player",
        "sprite": "knight",
        "x": "not an int",
        "y": 5
    }
    
    with pytest.raises(ValueError, match="Unit Test Unit has invalid coordinates"):
        scenario_loader._validate_unit(unit_data, 0)

def test_load_scenario_from_file(scenario_loader, sprite_manager, fx_manager, sound_manager, valid_scenario_yaml):
    """Test loading a scenario from a temporary file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name
    
    try:
        game_state = scenario_loader.load_scenario(temp_file, sprite_manager, fx_manager, sound_manager)
        
        assert game_state.name == "Test Scenario"
        assert game_state.description == "A test scenario for unit testing"
        assert game_state.map_id == "test_map"
        
        # Check that units were loaded
        assert hasattr(game_state, 'units')
        
    finally:
        os.unlink(temp_file)

def test_load_scenario_file_not_found(scenario_loader, sprite_manager, fx_manager, sound_manager):
    """Test loading a non-existent scenario file."""
    with pytest.raises(FileNotFoundError):
        scenario_loader.load_scenario("nonexistent_file.yaml", sprite_manager, fx_manager, sound_manager)

def test_load_scenario_convenience_function(sprite_manager, fx_manager, sound_manager, valid_scenario_yaml):
    """Test the convenience load_scenario function."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name
    
    try:
        game_state = load_scenario(temp_file, sprite_manager, fx_manager, sound_manager)
        
        assert game_state.name == "Test Scenario"
        assert game_state.description == "A test scenario for unit testing"
        assert game_state.map_id == "test_map"
        
    finally:
        os.unlink(temp_file)

def test_supported_sprites_and_ai_types(scenario_loader):
    """Test that supported sprites and AI types are reasonable."""
    # Check that we have some supported sprites
    assert len(scenario_loader.supported_sprites) > 0
    assert "knight" in scenario_loader.supported_sprites
    
    # Check that we have some supported AI types
    assert len(scenario_loader.supported_ai_types) > 0
    assert "aggressive" in scenario_loader.supported_ai_types

def test_camera_integration(scenario_loader, sprite_manager, fx_manager, sound_manager, camera_mock, valid_scenario_yaml):
    """Test camera integration in scenario loading."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name
    
    try:
        game_state = scenario_loader.load_scenario(temp_file, sprite_manager, fx_manager, sound_manager, camera_mock)
        
        # Check that camera pan was called
        assert camera_mock.pan_called
        assert camera_mock.pan_targets is not None
        assert camera_mock.pan_speed == 10
        
        # Check that we have the expected number of targets
        assert len(camera_mock.pan_targets) == 3
        
    finally:
        os.unlink(temp_file)

def test_ai_actions_processing(scenario_loader, sprite_manager, fx_manager, sound_manager, valid_scenario_yaml):
    """Test AI actions processing from YAML."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name
    
    try:
        game_state = scenario_loader.load_scenario(temp_file, sprite_manager, fx_manager, sound_manager)
        
        # The AI actions should be processed (currently just prints)
        # This test ensures no exceptions are raised during processing
        
    finally:
        os.unlink(temp_file)

def test_actions_processing(scenario_loader, sprite_manager, fx_manager, sound_manager, valid_scenario_yaml):
    """Test general actions processing from YAML."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name
    
    try:
        game_state = scenario_loader.load_scenario(temp_file, sprite_manager, fx_manager, sound_manager)
        
        # The actions should be processed (currently just prints)
        # This test ensures no exceptions are raised during processing
        
    finally:
        os.unlink(temp_file)

def test_trigger_battle_scenario(sprite_manager, fx_manager, sound_manager, camera_mock, valid_scenario_yaml):
    """Test the trigger_battle_scenario function."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name
    
    try:
        game_state = trigger_battle_scenario(temp_file, sprite_manager, fx_manager, sound_manager, camera_mock)
        
        assert game_state.name == "Test Scenario"
        assert game_state.description == "A test scenario for unit testing"
        assert camera_mock.pan_called
        
    finally:
        os.unlink(temp_file)

def test_load_scenario_without_camera(scenario_loader, sprite_manager, fx_manager, sound_manager, valid_scenario_yaml):
    """Test loading scenario without camera (should not fail)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(valid_scenario_yaml)
        temp_file = f.name
    
    try:
        game_state = scenario_loader.load_scenario(temp_file, sprite_manager, fx_manager, sound_manager)
        
        assert game_state.name == "Test Scenario"
        # Should not fail even without camera
        
    finally:
        os.unlink(temp_file)
