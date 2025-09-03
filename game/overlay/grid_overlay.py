from game.grid import Grid
from game.unit import Unit


class GridOverlay:
    def __init__(self, game):
        self.game = game

    def movement_range(self, grid: Grid, unit: Unit, max_steps: int):
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
                    if tile and tile.is_walkable() and (nx, ny) not in reachable:
                        frontier.add((nx, ny, dist + 1))
        return reachable

    def attack_range(self, grid: Grid, unit: Unit, radius: int = 1):
        in_range = set()
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) <= radius:
                    tx, ty = unit.x + dx, unit.y + dy
                    if grid.is_within_bounds(tx, ty):
                        in_range.add((tx, ty))
        return in_range

    def threat_zone(self, grid: Grid, unit: Unit, move_range: int = 3, attack_range: int = 1):
        reachable = self.movement_range(grid, unit, move_range)
        threat = set()
        for x, y in reachable:
            for dx in range(-attack_range, attack_range + 1):
                for dy in range(-attack_range, attack_range + 1):
                    if abs(dx) + abs(dy) <= attack_range:
                        tx, ty = x + dx, y + dy
                        if grid.is_within_bounds(tx, ty):
                            threat.add((tx, ty))
        return threat
