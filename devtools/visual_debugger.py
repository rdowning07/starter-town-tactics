# devtools/visual_debugger.py

import pygame
from game.renderer import Renderer
from game.sprite_manager import SpriteManager
from game.overlay.overlay_state import OverlayState
from game.grid import Grid
from game.tile import Tile
from game.unit_manager import UnitManager
from game.unit import Unit

def main():
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    clock = pygame.time.Clock()

    # Grid setup
    grid = Grid(5, 5)
    for x in range(5):
        for y in range(5):
            grid.tiles[y][x] = Tile(x=x, y=y, terrain="grass")

    # Unit setup
    unit_manager = UnitManager()
    unit_manager.register_unit("knight", "player", hp=10)

    # Create and place unit on grid
    knight = Unit("knight", 2, 2, "player", health=10)
    grid.place_unit(knight)

    # Overlay setup
    overlay_state = OverlayState()
    overlay_state.movement_tiles.add((1, 1))
    overlay_state.movement_tiles.add((2, 2))
    overlay_state.threat_tiles.add((3, 3))

    # Sprite manager with dummy data
    sprite_manager = SpriteManager()
    dummy_tile = pygame.Surface((32, 32))
    dummy_tile.fill((50, 180, 50))
    dummy_unit = pygame.Surface((32, 32))
    dummy_unit.fill((180, 50, 50))
    sprite_manager.load_terrain_sprite("grass", dummy_tile)
    sprite_manager.load_unit_sprite("knight", "idle", dummy_unit)

    renderer = Renderer(screen, sprite_manager)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        class DummyGameState:
            def __init__(self):
                self.terrain_grid = [
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"]
                ]
                self.units = unit_manager

        renderer.render(DummyGameState(), overlay_state)
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
