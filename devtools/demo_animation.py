# devtools/demo_animation.py

import sys

import pygame

from game.grid import Grid
from game.overlay.overlay_state import OverlayState
from game.renderer import Renderer
from game.sprite_manager import SpriteManager
from game.tile import Tile
from game.unit_manager import UnitManager

# Note: Unit import temporarily disabled due to syntax issues
# from game.unit import Unit

SCREEN_WIDTH, SCREEN_HEIGHT = 160, 160
TILE_SIZE = 32
GRID_WIDTH, GRID_HEIGHT = 5, 5


def load_dummy_animation(color1, color2, color3):
    frames = []
    for color in [color1, color2, color3]:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(color)
        frames.append(surf)
    return frames


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Animation Demo")
    clock = pygame.time.Clock()

    # Grid setup
    grid = Grid(GRID_WIDTH, GRID_HEIGHT)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            grid.tiles[y][x] = Tile(x=x, y=y, terrain="grass")

    # Unit setup - temporarily disabled due to import issues
    # unit = Unit("knight", 2, 2, "player", health=10)
    # unit.set_animation("attack", duration=30)
    # grid.place_unit(unit)

    # Create a dummy unit for testing
    class DummyUnit:
        """Dummy unit class for animation demo."""

        def __init__(self, name, x, y, team, health=10):
            self.name = name
            self.x = x
            self.y = y
            self.team = team
            self.health = health
            self.hp = health
            self.current_animation = "idle"
            self.animation_timer = 0

        def set_animation(self, name, duration=10):
            """Set animation state."""
            self.current_animation = name
            self.animation_timer = duration

        def update_animation(self):
            """Update animation timer."""
            if self.animation_timer > 0:
                self.animation_timer -= 1
            if self.animation_timer == 0:
                self.current_animation = "idle"

    unit = DummyUnit("knight", 2, 2, "player", 10)
    unit.set_animation("attack", 30)

    # Unit manager setup
    unit_manager = UnitManager()
    unit_manager.register_unit("knight", "player", hp=10)

    # Overlay setup
    overlay_state = OverlayState()
    overlay_state.movement_tiles.add((2, 2))
    overlay_state.threat_tiles.add((3, 3))

    # SpriteManager setup
    sprite_manager = SpriteManager()
    green_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
    green_tile.fill((0, 200, 0))
    sprite_manager.load_terrain_sprite("grass", green_tile)

    animation_frames = load_dummy_animation((255, 0, 0), (255, 100, 0), (255, 200, 0))
    sprite_manager.load_unit_animation("knight", "attack", animation_frames)
    sprite_manager.load_unit_animation("knight", "idle", [animation_frames[0]])

    # Renderer
    renderer = Renderer(screen, sprite_manager)

    # Main loop
    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simulate animation ticking
        unit.update_animation()

        class DummyGameState:
            """Dummy game state for demo."""

            def __init__(self):
                self.terrain_grid = [
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"],
                    ["grass", "grass", "grass", "grass", "grass"],
                ]
                self.units = unit_manager

        renderer.render(DummyGameState(), overlay_state)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
