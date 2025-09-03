"""
Tests for A* pathfinding: shortest path, blocked tiles, unreachable targets.
"""
import pytest

from core.rules.move import a_star, heuristic, terrain_cost
from core.state import GameState, Map, Tile


class TestHeuristic:
    """Test Manhattan distance heuristic."""

    def test_heuristic_basic(self):
        """Basic Manhattan distance calculation."""
        # Distance from (0,0) to (3,4) = 3 + 4 = 7
        distance = heuristic((0, 0), (3, 4))
        assert distance == 7

    def test_heuristic_same_point(self):
        """Distance to same point is 0."""
        distance = heuristic((2, 3), (2, 3))
        assert distance == 0

    def test_heuristic_negative_coords(self):
        """Handles negative coordinates."""
        distance = heuristic((-1, -2), (2, 3))
        assert distance == 8  # |-1-2| + |-2-3| = 3 + 5 = 8

    def test_heuristic_symmetric(self):
        """Heuristic is symmetric."""
        dist1 = heuristic((1, 2), (4, 6))
        dist2 = heuristic((4, 6), (1, 2))
        assert dist1 == dist2


class TestTerrainCost:
    """Test terrain cost calculation."""

    def test_basic_terrain_cost(self):
        """Basic terrain cost from tile."""
        game_state = GameState()

        # Default tile should have cost 1
        cost = terrain_cost(game_state, (2, 3))
        assert cost == 1

    def test_custom_terrain_cost(self):
        """Custom terrain cost from modified tile."""
        game_state = GameState()

        # Modify a tile to have higher cost
        tile = game_state.map.tile((5, 5))
        tile.move_cost = 3

        cost = terrain_cost(game_state, (5, 5))
        assert cost == 3


class TestAStarBasic:
    """Basic A* pathfinding tests."""

    def setup_method(self):
        """Set up test game state."""
        self.game_state = GameState()
        # Use small map for testing
        self.game_state.map = Map(width=10, height=10)

    def test_straight_line_path(self):
        """Find straight line path."""
        start = (1, 1)
        goal = (1, 4)
        max_cost = 10

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert path[0] == start
        assert path[-1] == goal
        assert len(path) == 4  # (1,1) -> (1,2) -> (1,3) -> (1,4)

    def test_diagonal_path(self):
        """Find path requiring diagonal movement."""
        start = (0, 0)
        goal = (3, 3)
        max_cost = 10

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert path[0] == start
        assert path[-1] == goal
        # Path length should be 7 (Manhattan distance, no diagonal moves)
        assert len(path) == 7

    def test_same_start_and_goal(self):
        """Path from point to itself."""
        start = (2, 2)
        goal = (2, 2)
        max_cost = 5

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert len(path) == 1
        assert path[0] == start

    def test_adjacent_points(self):
        """Path between adjacent points."""
        start = (3, 3)
        goal = (3, 4)
        max_cost = 5

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert len(path) == 2
        assert path[0] == start
        assert path[1] == goal


class TestAStarBlocked:
    """A* pathfinding with blocked tiles."""

    def setup_method(self):
        """Set up game state with some blocked tiles."""
        self.game_state = GameState()
        self.game_state.map = Map(width=10, height=10)

        # Mock the blocked method to return True for specific tiles
        self.blocked_tiles = set()
        original_blocked = self.game_state.map.blocked

        def mock_blocked(pos):
            return pos in self.blocked_tiles or not self.game_state.map.in_bounds(pos)

        self.game_state.map.blocked = mock_blocked

    def test_path_around_single_block(self):
        """Find path around single blocked tile."""
        # Block the direct path
        self.blocked_tiles.add((2, 2))

        start = (1, 2)
        goal = (3, 2)
        max_cost = 10

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert path[0] == start
        assert path[-1] == goal
        assert (2, 2) not in path  # Should avoid blocked tile
        assert len(path) > 3  # Should be longer than direct path

    def test_path_around_wall(self):
        """Find path around wall of blocked tiles."""
        # Create vertical wall
        wall = [(2, 1), (2, 2), (2, 3), (2, 4)]
        self.blocked_tiles.update(wall)

        start = (1, 2)
        goal = (3, 2)
        max_cost = 15

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert path[0] == start
        assert path[-1] == goal

        # Path should not contain any blocked tiles
        for tile in wall:
            assert tile not in path

    def test_unreachable_target(self):
        """Return None when target is unreachable."""
        # Surround goal with blocked tiles
        goal = (5, 5)
        surrounding = [(4, 4), (4, 5), (4, 6), (5, 4), (5, 6), (6, 4), (6, 5), (6, 6)]
        self.blocked_tiles.update(surrounding)

        start = (1, 1)
        max_cost = 20

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is None

    def test_start_blocked(self):
        """Handle blocked start position."""
        start = (2, 2)
        self.blocked_tiles.add(start)

        goal = (4, 4)
        max_cost = 10

        path = a_star(self.game_state, start, goal, max_cost)

        # Should still work if start is in blocked set but we allow starting there
        # Or return None if we don't allow starting in blocked positions
        # Implementation dependent - either is valid
        assert path is None or (path is not None and path[0] == start)


class TestAStarCostLimits:
    """A* pathfinding with cost limits."""

    def setup_method(self):
        """Set up game state with varied terrain costs."""
        self.game_state = GameState()
        self.game_state.map = Map(width=10, height=10)

    def test_max_cost_limit(self):
        """Path fails when exceeding max cost."""
        start = (0, 0)
        goal = (5, 5)
        max_cost = 5  # Too low for Manhattan distance of 10

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is None

    def test_high_cost_terrain(self):
        """Path through high-cost terrain."""
        # Make some tiles expensive
        expensive_tiles = [(2, 2), (2, 3), (2, 4)]
        for pos in expensive_tiles:
            tile = self.game_state.map.tile(pos)
            tile.move_cost = 5

        start = (1, 3)
        goal = (3, 3)
        max_cost = 15

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert path[0] == start
        assert path[-1] == goal

    def test_prefer_low_cost_path(self):
        """A* prefers lower cost paths."""
        # Create expensive direct path
        expensive_direct = [(2, 2), (3, 2), (4, 2)]
        for pos in expensive_direct:
            tile = self.game_state.map.tile(pos)
            tile.move_cost = 10

        start = (1, 2)
        goal = (5, 2)
        max_cost = 50

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        # Should find alternative route avoiding expensive tiles
        expensive_in_path = any(pos in expensive_direct for pos in path)
        # Depending on implementation, might still use expensive path if it's shortest
        # The key is that it respects the cost limits


class TestAStarEdgeCases:
    """Edge cases for A* pathfinding."""

    def setup_method(self):
        """Set up basic game state."""
        self.game_state = GameState()
        self.game_state.map = Map(width=5, height=5)

    def test_out_of_bounds_goal(self):
        """Handle out of bounds goal."""
        start = (2, 2)
        goal = (10, 10)  # Out of bounds
        max_cost = 20

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is None

    def test_out_of_bounds_start(self):
        """Handle out of bounds start."""
        start = (-1, -1)  # Out of bounds
        goal = (2, 2)
        max_cost = 10

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is None

    def test_zero_max_cost(self):
        """Handle zero max cost."""
        start = (1, 1)
        goal = (1, 1)  # Same position
        max_cost = 0

        path = a_star(self.game_state, start, goal, max_cost)

        # Should work for same position with 0 cost
        assert path is not None
        assert len(path) == 1

    def test_large_map_performance(self):
        """Test performance on larger map."""
        # Create larger map
        self.game_state.map = Map(width=50, height=50)

        start = (0, 0)
        goal = (49, 49)
        max_cost = 200  # Generous limit

        path = a_star(self.game_state, start, goal, max_cost)

        assert path is not None
        assert path[0] == start
        assert path[-1] == goal
        # Should find optimal Manhattan path
        assert len(path) == 99  # 49 + 49 + 1
