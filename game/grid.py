# game/grid.py

"""Grid module for handling the game board logic."""


class Grid:
    """Represents a 2D grid of tiles for the game."""

    def __init__(self, width, height):
        """
        Initialize the grid with the specified width and height.

        Args:
            width (int): Number of columns in the grid.
            height (int): Number of rows in the grid.
        """
        self.width = width
        self.height = height
        self.tiles = [[None for _ in range(width)] for _ in range(height)]
