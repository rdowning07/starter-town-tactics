# test_map_loader.py
import os
import tempfile

import pytest

from map_loader import get_map_dimensions, load_map, validate_map


def test_load_basic_map(tmp_path):
    """Test loading a basic map file."""
    content = """
G G G
W W G
F F G
"""
    maps_dir = tmp_path / "maps"
    maps_dir.mkdir()
    (maps_dir / "testmap.map").write_text(content.strip())

    result = load_map("testmap", str(maps_dir))

    assert result == [
        ["G", "G", "G"],
        ["W", "W", "G"],
        ["F", "F", "G"],
    ]


def test_load_map_with_empty_lines(tmp_path):
    """Test loading a map file with empty lines."""
    content = """
G G G

W W G

F F G
"""
    maps_dir = tmp_path / "maps"
    maps_dir.mkdir()
    (maps_dir / "testmap.map").write_text(content.strip())

    result = load_map("testmap", str(maps_dir))

    assert result == [
        ["G", "G", "G"],
        ["W", "W", "G"],
        ["F", "F", "G"],
    ]


def test_load_map_fails_on_missing_file(tmp_path):
    """Test that loading fails when the map file doesn't exist."""
    maps_dir = tmp_path / "maps"
    maps_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        load_map("nonexistent", str(maps_dir))


def test_load_map_fails_on_empty_file(tmp_path):
    """Test that loading fails when the map file is empty."""
    maps_dir = tmp_path / "maps"
    maps_dir.mkdir()
    (maps_dir / "empty.map").write_text("")

    with pytest.raises(ValueError, match="Map file is empty"):
        load_map("empty", str(maps_dir))


def test_load_map_fails_on_inconsistent_rows(tmp_path):
    """Test that loading fails when rows have different lengths."""
    content = """
G G G
W W
F F F F
"""
    maps_dir = tmp_path / "maps"
    maps_dir.mkdir()
    (maps_dir / "badmap.map").write_text(content.strip())

    with pytest.raises(ValueError, match="inconsistent row lengths"):
        load_map("badmap", str(maps_dir))


def test_validate_map_valid():
    """Test map validation with valid terrain grid."""
    valid_map = [
        ["G", "G", "G"],
        ["W", "W", "G"],
        ["F", "F", "G"],
    ]

    assert validate_map(valid_map) is True


def test_validate_map_empty():
    """Test map validation with empty terrain grid."""
    assert validate_map([]) is False


def test_validate_map_inconsistent_rows():
    """Test map validation with inconsistent row lengths."""
    invalid_map = [
        ["G", "G", "G"],
        ["W", "W"],
        ["F", "F", "F", "F"],
    ]

    assert validate_map(invalid_map) is False


def test_validate_map_non_string_cells():
    """Test map validation with non-string cells."""
    invalid_map = [
        ["G", "G", "G"],
        ["W", 123, "G"],  # Non-string cell
        ["F", "F", "G"],
    ]

    assert validate_map(invalid_map) is False


def test_get_map_dimensions():
    """Test getting map dimensions."""
    terrain_grid = [
        ["G", "G", "G", "G"],
        ["W", "W", "G", "G"],
        ["F", "F", "G", "G"],
    ]

    width, height = get_map_dimensions(terrain_grid)
    assert width == 4
    assert height == 3


def test_get_map_dimensions_empty():
    """Test getting dimensions of empty map."""
    width, height = get_map_dimensions([])
    assert width == 0
    assert height == 0


def test_load_map_with_whitespace(tmp_path):
    """Test loading a map file with extra whitespace."""
    content = """
  G   G   G
  W   W   G
  F   F   G
"""
    maps_dir = tmp_path / "maps"
    maps_dir.mkdir()
    (maps_dir / "whitespace.map").write_text(content.strip())

    result = load_map("whitespace", str(maps_dir))

    assert result == [
        ["G", "G", "G"],
        ["W", "W", "G"],
        ["F", "F", "G"],
    ]
