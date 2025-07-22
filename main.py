"""Main entry point to run a sample game session with sprite rendering, camera panning, unit selection, click-to-move, tile outlines, move preview, and debug overlay."""

import pygame

from game.game import Game
from game.sprite_manager import SpriteManager
from game.unit import Unit

SCREEN_WIDTH, SCREEN_HEIGHT = 320, 240
TILE_SIZE = 32
VISIBLE_COLS = SCREEN_WIDTH // TILE_SIZE
VISIBLE_ROWS = SCREEN_HEIGHT // TILE_SIZE


def main():
    # Initialize pygame and window
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Starter Town Tactics")
    clock = pygame.time.Clock()

    # Load sprites
    sprites = SpriteManager()
    sprites.load_assets()

    # Create game logic layer
    game = Game(10, 10)  # Bigger grid to support scrolling
    hero = Unit("Knight", 2, 2, team="Red")
    enemy = Unit("Goblin", 1, 1, team="Blue")
    game.add_unit(hero)
    game.add_unit(enemy)

    # Create overlays
    highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    highlight_surface.fill((255, 255, 0, 100))  # yellow semi-transparent overlay

    outline_hover = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(outline_hover, (255, 255, 0), outline_hover.get_rect(), 2)

    outline_selected = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(outline_selected, (0, 255, 255), outline_selected.get_rect(), 2)

    move_preview = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(move_preview, (0, 255, 0), move_preview.get_rect(), 2)

    selected_unit = None  # Holds reference to the selected unit

    # Initialize font for debug overlay
    pygame.font.init()
    debug_font = pygame.font.SysFont("Arial", 14)

    def draw_debug_text(surface, text, x, y):
        label = debug_font.render(text, True, (255, 255, 255))
        surface.blit(label, (x, y))

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.pan_camera(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.pan_camera(1, 0)
                elif event.key == pygame.K_UP:
                    game.pan_camera(0, -1)
                elif event.key == pygame.K_DOWN:
                    game.pan_camera(0, 1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                tile_x = (mouse_x // TILE_SIZE) + game.camera_x
                tile_y = (mouse_y // TILE_SIZE) + game.camera_y

                if selected_unit:
                    if 0 <= tile_x < game.width and 0 <= tile_y < game.height:
                        selected_unit.move_to(tile_x, tile_y)
                        game.next_turn()
                        selected_unit = None
                else:
                    for unit in game.units:
                        if unit.x == tile_x and unit.y == tile_y:
                            selected_unit = unit
                            break

        screen.fill((0, 0, 0))  # Clear the screen

        # Draw visible portion of the tile grid
        for y in range(VISIBLE_ROWS):
            for x in range(VISIBLE_COLS):
                world_x = x + game.camera_x
                world_y = y + game.camera_y
                if 0 <= world_x < game.width and 0 <= world_y < game.height:
                    screen.blit(
                        sprites.get_sprite("tile", "grass"),
                        (x * TILE_SIZE, y * TILE_SIZE),
                    )

        # Draw units in view
        for unit in game.units:
            draw_x = unit.x - game.camera_x
            draw_y = unit.y - game.camera_y
            if 0 <= draw_x < VISIBLE_COLS and 0 <= draw_y < VISIBLE_ROWS:
                sprite = sprites.get_sprite("unit", unit.name.lower())
                screen.blit(sprite, (draw_x * TILE_SIZE, draw_y * TILE_SIZE))

        # Mouse hover tile highlight (adjusted for camera)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_x = mouse_x // TILE_SIZE
        hover_y = mouse_y // TILE_SIZE
        world_hover_x = hover_x + game.camera_x
        world_hover_y = hover_y + game.camera_y

        if 0 <= hover_x < VISIBLE_COLS and 0 <= hover_y < VISIBLE_ROWS:
            screen.blit(highlight_surface, (hover_x * TILE_SIZE, hover_y * TILE_SIZE))
            screen.blit(outline_hover, (hover_x * TILE_SIZE, hover_y * TILE_SIZE))

        # Draw outline on selected unit
        if selected_unit:
            draw_x = selected_unit.x - game.camera_x
            draw_y = selected_unit.y - game.camera_y
            if 0 <= draw_x < VISIBLE_COLS and 0 <= draw_y < VISIBLE_ROWS:
                cursor = sprites.get_sprite("ui", "cursor")
                screen.blit(cursor, (draw_x * TILE_SIZE, draw_y * TILE_SIZE))
                screen.blit(outline_selected, (draw_x * TILE_SIZE, draw_y * TILE_SIZE))

            # Preview move destination if hover is valid
            if 0 <= world_hover_x < game.width and 0 <= world_hover_y < game.height:
                screen.blit(move_preview, (hover_x * TILE_SIZE, hover_y * TILE_SIZE))

        # === DEBUG TEXT ===
        draw_debug_text(screen, f"Turn: {game.current_turn}", 5, 5)
        draw_debug_text(screen, f"Camera: ({game.camera_x}, {game.camera_y})", 5, 20)
        draw_debug_text(screen, f"Hover: ({world_hover_x}, {world_hover_y})", 5, 35)

        if selected_unit:
            draw_debug_text(
                screen, f"Selected: {selected_unit.name} ({selected_unit.team})", 5, 50
            )
            draw_debug_text(screen, f"HP: {selected_unit.health}", 5, 65)
            draw_debug_text(
                screen, f"Pos: ({selected_unit.x}, {selected_unit.y})", 5, 80
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
