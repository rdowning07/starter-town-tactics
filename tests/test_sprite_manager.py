from game.sprite_manager import SpriteManager


def test_sprite_storage():
    sm = SpriteManager()
    sm.add_sprite("hero", "sprite_object")
    assert sm.get_sprite("hero") == "sprite_object"


def test_get_cursor_sprite_returns_cursor():
    sm = SpriteManager()
    dummy_sprite = object()
    sm.add_sprite("cursor", dummy_sprite)
    assert sm.get_cursor_sprite() is dummy_sprite
