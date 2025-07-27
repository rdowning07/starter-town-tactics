# game/overlay/grid_overlay.py

from game.grid import Grid
from game.unit import Unit
from game.ui.grid_overlay_draw import draw_movement_range, draw_terrain_overlay


class GridOverlay:
    def __init__(self, game):
        self.game = game

    def draw(self, screen, tile_size, camera_x, camera_y):
        if self.game and self.game.units:
            for unit in self.game.units:
                if unit.team == "Red":  # Example condition for overlay filtering
                    reachable = self.movement_range(self.game.grid, unit, 3)
                    draw_movement_range(screen, self.game.grid, unit, reachable, tile_size, camera_x, camera_y)

        draw_terrain_overlay(screen, self.game.grid, tile_size, camera_x, camera_y)

    @staticmethod
    def movement_range(grid: Grid, unit: Unit, max_steps: int):
        reachable = set()
        frontier = {(unit.x, unit.y, 0)}
        while frontier:
            x, y, dist = frontier.pop()
            if dist > max_steps:
                continue
            reachable.add((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if grid.is_within_bounds(nx, ny):
                    tile = grid.get_tile(nx, ny)
                    if tile and tile.is_walkable() or (nx, ny) == (unit.x, unit.y):
                        if (nx, ny) not in reachable:
                            frontier.add((nx, ny, dist + tile.movement_cost))
        return reachable

    @staticmethod
    def terrain_heatmap(grid: Grid):
        return {(tile.x, tile.y): tile.movement_cost for row in grid.tiles for tile in row}
