# ui/grid_overlay_draw.py

import pygame
from game.grid import Grid
from game.unit import Unit


def draw_movement_range(screen, grid: Grid, unit: Unit, reachable: set, tile_size: int, camera_x: int, camera_y: int):
    color = (0, 0, 255, 100)  # translucent blue

    overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    pygame.draw.rect(overlay, color, overlay.get_rect())

    for x, y in reachable:
        screen_x = (x - camera_x) * tile_size
        screen_y = (y - camera_y) * tile_size
        if 0 <= screen_x < screen.get_width() and 0 <= screen_y < screen.get_height():
            screen.blit(overlay, (screen_x, screen_y))


def draw_terrain_overlay(screen, grid: Grid, tile_size: int, camera_x: int, camera_y: int):
    font = pygame.font.SysFont("Arial", 10)

    for row in grid.tiles:
        for tile in row:
            screen_x = (tile.x - camera_x) * tile_size
            screen_y = (tile.y - camera_y) * tile_size
            if 0 <= screen_x < screen.get_width() and 0 <= screen_y < screen.get_height():
                cost = str(tile.movement_cost)
                label = font.render(cost, True, (255, 255, 255))
                screen.blit(label, (screen_x + 2, screen_y + 2))
