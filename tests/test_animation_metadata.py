# tests/test_animation_metadata.py

import json
import os

import pytest

# Test both the old global metadata and new unit-specific metadata
GLOBAL_METADATA_PATH = "assets/animations/animation_metadata.json"
UNIT_METADATA_PATH = "assets/units/knight/animation_metadata.json"


def test_unit_metadata_format_valid():
    """Test that unit-specific animation metadata exists and is valid."""
    assert os.path.exists(UNIT_METADATA_PATH), f"Unit metadata file missing: {UNIT_METADATA_PATH}"
    with open(UNIT_METADATA_PATH) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert len(data) > 0, "Unit metadata should contain at least one animation"


def test_unit_metadata_required_fields():
    """Test that unit metadata has required fields."""
    with open(UNIT_METADATA_PATH) as f:
        data = json.load(f)

    for name, entry in data.items():
        assert "frame_count" in entry, f"{name} missing frame_count"
        assert "frame_duration" in entry, f"{name} missing frame_duration"
        assert "loop" in entry, f"{name} missing loop field"

        # Test optional fields
        if "fx_at" in entry:
            for frame in entry["fx_at"]:
                assert isinstance(frame, int), f"{name} fx_at contains non-integer: {frame}"
        if "sound_at" in entry:
            for frame in entry["sound_at"]:
                assert isinstance(frame, int), f"{name} sound_at contains non-integer: {frame}"
        if "fx_type" in entry:
            assert isinstance(entry["fx_type"], str), f"{name} fx_type should be string"


def test_animation_types_present():
    """Test that all expected animation types are present."""
    with open(UNIT_METADATA_PATH) as f:
        data = json.load(f)

    expected_animations = ["idle", "attack", "hurt", "die", "stun"]
    for anim_type in expected_animations:
        assert anim_type in data, f"Missing animation type: {anim_type}"


def test_damage_transition_logic():
    """Test that damage transitions work correctly."""
    from game.unit import Unit

    # Test light damage -> hurt
    unit = Unit(name="Test", x=0, y=0, team="player")
    unit.hp = 5
    unit.take_damage(1)
    assert unit.current_animation == "hurt"

    # Test heavy damage -> stun
    unit = Unit(name="Test2", x=0, y=0, team="player")
    unit.hp = 5
    unit.take_damage(3)
    assert unit.current_animation == "stun"

    # Test lethal damage -> die
    unit = Unit(name="Test3", x=0, y=0, team="player")
    unit.hp = 2
    unit.take_damage(5)
    assert unit.current_animation == "die"


def test_global_metadata_backward_compatibility():
    """Test global metadata for backward compatibility (if it exists)."""
    if os.path.exists(GLOBAL_METADATA_PATH):
        with open(GLOBAL_METADATA_PATH) as f:
            data = json.load(f)
        assert isinstance(data, dict)
    else:
        # Global metadata is optional now
        pytest.skip("Global metadata file not found - this is optional")
