from game.platform import Platform

class Level:
    def __init__(self, data):
        self.platforms = []
        for obj in data:
            if obj['type'] == 'platform':
                plat = Platform(obj['x'], obj['y'], obj['width'], obj['height'])
                self.platforms.append(plat)

    def update(self):
        pass

    def render(self, screen):
        for plat in self.platforms:
            plat.render(screen)
