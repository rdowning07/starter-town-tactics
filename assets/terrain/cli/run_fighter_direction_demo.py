# Standard library imports
from pathlib import Path

# Third-party imports
import pygame

# Local imports
from src.units.AnimationCatalog import AnimationCatalog
from src.units.UnitRendererShim import UnitRendererShim


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Fighter Direction Demo (idle/walk per facing)")
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    catalog = AnimationCatalog(Path("assets/units/_metadata/animation_metadata.json"))
    renderer = UnitRendererShim(catalog, tile_size=(32, 32))

    pos = (5, 5)  # grid
    cam = (0, 0)
    facing = "down"  # 'up'|'down'|'left'|'right'
    walking = False

    running = True
    while running:
        dt = clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        walking = False
        if keys[pygame.K_LEFT]:
            facing = "left"
            walking = True
        elif keys[pygame.K_RIGHT]:
            facing = "right"
            walking = True
        elif keys[pygame.K_UP]:
            facing = "up"
            walking = True
        elif keys[pygame.K_DOWN]:
            facing = "down"
            walking = True

        screen.fill((10, 10, 12))

        state = f"walk_{facing}" if walking else f"idle_{facing}"
        elapsed = pygame.time.get_ticks()
        renderer.draw_unit(
            surface=screen,
            unit_sprite="fighter",  # the unit name you imported
            state=state,
            grid_xy=pos,
            camera_px=cam,
            elapsed_ms=elapsed,
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
