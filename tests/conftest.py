import pytest
from game.grid import Grid


@pytest.fixture
def grid():
    return Grid(width=5, height=5)
