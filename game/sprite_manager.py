class SpriteManager:
    def __init__(self):
        self.sprites = {}

    def add_sprite(self, name, sprite):
        self.sprites[name] = sprite

    def get_sprite(self, name):
        return self.sprites.get(name)
