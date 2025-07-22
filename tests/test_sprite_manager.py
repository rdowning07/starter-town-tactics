import pygame
import pytest

from game.sprite_manager import SpriteManager


@pytest.fixture(scope="module", autouse=True)
def pygame_setup():
    pygame.init()
    pygame.display.set_mode((1, 1))  # 🧠 Headless surface to enable convert_alpha
    yield
    pygame.quit()


def test_sprite_loading():
    sm = SpriteManager()
    sm.load_assets()

    # Tile sprites
    assert sm.get_sprite("tile", "grass") is not None
    assert sm.get_sprite("tile", "wall") is not None
    assert sm.get_sprite("tile", "water") is not None

    # Unit sprites
    assert sm.get_sprite("unit", "knight") is not None
    assert sm.get_sprite("unit", "goblin") is not None

    # UI sprites
    assert sm.get_sprite("ui", "cursor") is not None
    assert sm.get_sprite("ui", "healthbar") is not None
