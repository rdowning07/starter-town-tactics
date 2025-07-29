"""Handles drawing overlays like movement, attack, and threat zones."""

import pygame

from game.grid import Grid
from game.overlay.overlay_state import OverlayState


def draw_movement_range(surface, grid: Grid, overlay_state: OverlayState) -> None:
    for x, y in overlay_state.movement_tiles:
        pygame.draw.rect(surface, (0, 255, 0), grid.get_tile_rect(x, y), 2)


def draw_threat_zone(surface, grid: Grid, overlay_state: OverlayState) -> None:
    for x, y in overlay_state.threat_tiles:
        pygame.draw.rect(surface, (255, 0, 0), grid.get_tile_rect(x, y), 2)


def draw_attack_range(surface, grid: Grid, overlay_state: OverlayState) -> None:
    for x, y in overlay_state.attack_tiles:
        pygame.draw.rect(surface, (255, 255, 0), grid.get_tile_rect(x, y), 2)


def draw_terrain_overlay(surface, grid: Grid, overlay_state: OverlayState) -> None:
    for x, y in overlay_state.terrain_tiles:
        pygame.draw.rect(surface, (0, 0, 255), grid.get_tile_rect(x, y), 2)
