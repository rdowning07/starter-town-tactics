# map_loader.py
import os
from typing import List


def load_map(map_id: str, maps_dir: str = "maps") -> List[List[str]]:
    """
    Load a .map file into a 2D terrain array.

    Args:
        map_id: The name of the map file (without .map extension)
        maps_dir: Directory containing map files

    Returns:
        A 2D list representing the terrain grid

    Raises:
        FileNotFoundError: If the map file doesn't exist
        ValueError: If the map file is empty or malformed
    """
    filepath = os.path.join(maps_dir, f"{map_id}.map")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Map file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        raise ValueError(f"Map file is empty: {filepath}")

    lines = content.splitlines()
    if not lines:
        raise ValueError(f"Map file has no valid lines: {filepath}")

    terrain_grid = []
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines

        row = line.split()
        if not row:
            continue  # Skip lines with only whitespace

        terrain_grid.append(row)

    if not terrain_grid:
        raise ValueError(f"Map file contains no valid terrain data: {filepath}")

    # Validate that all rows have the same length
    row_lengths = [len(row) for row in terrain_grid]
    if len(set(row_lengths)) > 1:
        raise ValueError(f"Map file has inconsistent row lengths: {row_lengths}")

    return terrain_grid


def validate_map(terrain_grid: List[List[str]]) -> bool:
    """
    Validate that a terrain grid is properly formatted.

    Args:
        terrain_grid: 2D list representing the terrain

    Returns:
        True if the map is valid, False otherwise
    """
    if not terrain_grid:
        return False

    if not all(isinstance(row, list) for row in terrain_grid):
        return False

    # Check that all rows have the same length
    row_lengths = [len(row) for row in terrain_grid]
    if len(set(row_lengths)) > 1:
        return False

    # Check that all cells contain strings
    for row in terrain_grid:
        if not all(isinstance(cell, str) for cell in row):
            return False

    return True


def get_map_dimensions(terrain_grid: List[List[str]]) -> tuple[int, int]:
    """
    Get the dimensions of a terrain grid.

    Args:
        terrain_grid: 2D list representing the terrain

    Returns:
        Tuple of (width, height)
    """
    if not terrain_grid:
        return (0, 0)

    height = len(terrain_grid)
    width = len(terrain_grid[0]) if terrain_grid[0] else 0

    return (width, height)
