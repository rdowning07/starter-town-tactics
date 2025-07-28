from game.sprite_manager import SpriteManager


def test_sprite_storage():
    sm = SpriteManager()
    sm.add_sprite("hero", "sprite_object")
    assert sm.get_sprite("hero") == "sprite_object"
