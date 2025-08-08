import pygame

from game.ai_controller import AIController
from game.game import Game
from game.gamepad_controller import GamepadController
from game.input_state import InputState
from game.keyboard_controller import KeyboardController
from game.overlay.grid_overlay import GridOverlay
from game.overlay.overlay_state import OverlayState
from game.sprite_manager import SpriteManager
from game.turn_controller import TurnController
from game.ui.debug_overlay import draw_debug_info
from game.unit import Unit
from CameraController import CameraController

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # Increased for better visibility
TILE_SIZE = 32
VISIBLE_COLS = SCREEN_WIDTH // TILE_SIZE
VISIBLE_ROWS = SCREEN_HEIGHT // TILE_SIZE


def create_outline(color):
    """Create an outline surface for highlighting."""
    surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, surface.get_rect(), 2)
    return surface


def init_game():
    """Initialize the game with units."""
    game = Game(20, 20)  # Larger map
    # Add units using the new sprite system
    game.add_unit(Unit("Recruit", 2, 2, team="blue"))
    game.add_unit(Unit("PhoenixBinder", 1, 1, team="blue"))
    game.add_unit(Unit("CrystalArchon", 3, 3, team="blue"))
    return game


def init_ui():
    """Initialize UI elements."""
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 14)
    return (
        font,
        create_outline((255, 255, 0)),
        create_outline((0, 255, 255)),
        create_outline((0, 255, 0)),
    )


def handle_mouse_click(event, game, input_state, turn_controller, camera):
    """Handle mouse click events."""
    # Simplified mouse handling for now
    mx, my = event.pos
    # Adjust for camera position
    world_x = mx + camera.position.x
    world_y = my + camera.position.y
    tx = world_x // TILE_SIZE
    ty = world_y // TILE_SIZE
    input_state.cursor_x = tx
    input_state.cursor_y = ty
    input_state.confirm_selection()
    if input_state.state == "idle":
        turn_controller.next_turn()


def init_gamepads(input_state):
    """Initialize gamepad controllers."""
    pygame.joystick.init()
    controllers = []
    for i in range(pygame.joystick.get_count()):
        controller = GamepadController(input_state)
        controller.joystick = pygame.joystick.Joystick(i)
        controller.joystick.init()
        controllers.append(controller)
    return controllers


def draw_terrain(screen, sprites, camera):
    """Draw terrain tiles."""
    for y in range(VISIBLE_ROWS):
        for x in range(VISIBLE_COLS):
            wx, wy = x + int(camera.position.x // TILE_SIZE), y + int(camera.position.y // TILE_SIZE)
            if 0 <= wx < 20 and 0 <= wy < 20:  # Use game.grid.width/height if available
                # Use terrain tileset
                terrain_sprite = sprites.get_terrain_sprite("terrain")
                if terrain_sprite:
                    try:
                        terrain_image = pygame.image.load(terrain_sprite)
                        screen.blit(terrain_image, (x * TILE_SIZE, y * TILE_SIZE))
                    except (pygame.error, OSError):
                        # Fallback to colored rectangle
                        pygame.draw.rect(
                            screen,
                            (100, 150, 100),
                            (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                        )


def draw_units(screen, game, sprites, camera):
    """Draw units on screen."""
    for unit in game.units:
        dx = unit.x - int(camera.position.x // TILE_SIZE)
        dy = unit.y - int(camera.position.y // TILE_SIZE)
        if 0 <= dx < VISIBLE_COLS and 0 <= dy < VISIBLE_ROWS:
            # Try to get unit sprite with animation frame 0
            unit_sprite = sprites.get_unit_sprite(unit.name, "blue", 0)
            if unit_sprite:
                try:
                    unit_image = pygame.image.load(unit_sprite)
                    screen.blit(unit_image, (dx * TILE_SIZE, dy * TILE_SIZE))
                except (pygame.error, OSError):
                    # Fallback to colored rectangle
                    color = (0, 0, 255) if unit.team == "blue" else (255, 0, 0)
                    pygame.draw.rect(
                        screen,
                        color,
                        (dx * TILE_SIZE, dy * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                    )
            else:
                # Fallback to colored rectangle
                color = (0, 0, 255) if unit.team == "blue" else (255, 0, 0)
                pygame.draw.rect(
                    screen,
                    color,
                    (dx * TILE_SIZE, dy * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                )


def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Starter Town Tactics")
    clock = pygame.time.Clock()

    # Initialize sprite manager with new asset system
    sprites = SpriteManager()
    sprites.load_assets()
    font, hover_outline, selected_outline, move_preview = init_ui()

    game = init_game()
    input_state = InputState(game)
    keyboard_controller = KeyboardController(input_state)
    gamepad_controllers = init_gamepads(input_state)
    turn_controller = TurnController(game)
    ai_controller = AIController(game)
    overlay_state = OverlayState()
    overlay = GridOverlay(game)

    # Initialize camera controller
    camera = CameraController(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keyboard_controller.handle_key_event(event)
                overlay_state.handle_key_event(event)

                # Camera controls
                if event.key == pygame.K_SPACE:
                    # Trigger cinematic pan for testing
                    cinematic_targets = [
                        pygame.Vector2(200, 200),
                        pygame.Vector2(400, 400),
                        pygame.Vector2(600, 600)
                    ]
                    camera.cinematic_pan(cinematic_targets, speed=10)

                if input_state.state == "idle":
                    turn_controller.next_turn()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(event, game, input_state, turn_controller, camera)
            elif event.type in [pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION]:
                for controller in gamepad_controllers:
                    controller.handle_event(event)
                    if input_state.state == "idle":
                        turn_controller.next_turn()

        for controller in gamepad_controllers:
            controller.update()

        # AI turn handling
        if turn_controller.is_ai_turn():
            ai_controller.take_turn()
            turn_controller.next_turn()

        # Update camera
        camera.update()

        screen.fill((0, 0, 0))

        # Draw terrain using new tileset system with camera offset
        draw_terrain(screen, sprites, camera)

        # Draw overlays with camera offset
        overlay.draw(screen, TILE_SIZE, int(camera.position.x // TILE_SIZE), int(camera.position.y // TILE_SIZE))

        # Draw units using new sprite system with camera offset
        draw_units(screen, game, sprites, camera)

        # Mouse hover with camera offset
        mx, my = pygame.mouse.get_pos()
        hx, hy = mx // TILE_SIZE, my // TILE_SIZE
        whx = hx + int(camera.position.x // TILE_SIZE)
        why = hy + int(camera.position.y // TILE_SIZE)
        if 0 <= hx < VISIBLE_COLS and 0 <= hy < VISIBLE_ROWS:
            screen.blit(hover_outline, (hx * TILE_SIZE, hy * TILE_SIZE))

        # Selected unit with camera offset
        if input_state.state == "selected" and input_state.selected_unit:
            dx = input_state.selected_unit.x - int(camera.position.x // TILE_SIZE)
            dy = input_state.selected_unit.y - int(camera.position.y // TILE_SIZE)
            if 0 <= dx < VISIBLE_COLS and 0 <= dy < VISIBLE_ROWS:
                screen.blit(selected_outline, (dx * TILE_SIZE, dy * TILE_SIZE))
            if 0 <= whx < 20 and 0 <= why < 20:  # Use game.grid.width/height if available
                screen.blit(move_preview, (hx * TILE_SIZE, hy * TILE_SIZE))

        # Draw cursor with camera offset
        input_state.draw_cursor(
            screen, TILE_SIZE, int(camera.position.x // TILE_SIZE), int(camera.position.y // TILE_SIZE), sprites
        )

        # Debug info
        draw_debug_info(
            screen,
            font,
            [
                f"Game: {game}",
                f"InputState: {input_state.state}",
                f"Turn: {turn_controller.current_turn}",
                f"Current Unit: {turn_controller.get_current_unit() if turn_controller.units else 'None'}",
                f"AI Turn: {turn_controller.is_ai_turn()}",
                f"Camera Position: ({camera.position.x:.1f}, {camera.position.y:.1f})",
                f"Camera Panning: {camera.panning}",
                f"Available Tilesets: {len(sprites.list_available_tilesets())}",
                f"Available Units: {len(sprites.list_available_units())}",
            ],
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
