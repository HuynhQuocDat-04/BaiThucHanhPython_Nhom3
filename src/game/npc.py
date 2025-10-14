import pygame
import os

class NPC:
    def __init__(self, x, y):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "Character")
        img = pygame.image.load(os.path.join(assets_dir, '16x16 knight 4 v3.png')).convert_alpha()
        # Scale NPC đúng bằng chiều cao player (55px), giữ tỉ lệ gốc
        target_height = 70
        scale_ratio = target_height / img.get_height()
        new_width = int(img.get_width() * scale_ratio)
        img = pygame.transform.scale(img, (new_width, target_height))
        img = pygame.transform.flip(img, True, False)
        self.image = img
        self.rect = self.image.get_rect()

    def render(self, screen):
        screen.blit(self.image, self.rect.topleft)