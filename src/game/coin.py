import pygame
import os

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.active = True
        self.rising = True
        self.rise_speed = 2
        self.target_y = y - 40

        # Load sprite sheet
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "other")
        sheet_path = os.path.join(assets_path, "coin.png")
        self.sheet = pygame.image.load(sheet_path).convert_alpha()
        self.frame_width = self.sheet.get_height()  # coin.png là frame ngang, vuông
        self.frame_count = self.sheet.get_width() // self.frame_width
        self.frame = 0
        self.anim_timer = 0

    def update(self):
        if self.rising:
            self.rect.y -= self.rise_speed
            if self.rect.y <= self.target_y:
                self.rect.y = self.target_y
                self.rising = False
        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 5:
            self.frame = (self.frame + 1) % self.frame_count
            self.anim_timer = 0

    def render(self, screen):
        if self.active:
            frame_rect = pygame.Rect(self.frame * self.frame_width, 0, self.frame_width, self.frame_width)
            img = self.sheet.subsurface(frame_rect)
            img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
            screen.blit(img, self.rect)