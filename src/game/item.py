import pygame
import os

class Item:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.color = (255, 215, 0)
        self.active = True
        self.rising = True
        self.rise_speed = 2
        self.target_y = y - 40

    def update(self):
        if self.rising:
            self.rect.y -= self.rise_speed
            if self.rect.y <= self.target_y:
                self.rect.y = self.target_y
                self.rising = False

    def render(self, screen):
        if self.active:
            pygame.draw.ellipse(screen, self.color, self.rect)
            # Dùng font Unicode để ổn định hiển thị
            font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "DejaVuSans.ttf")
            try:
                font = pygame.font.Font(font_path, 24)
            except:
                font = pygame.font.SysFont(None, 24)
            text = font.render('+', True, (255, 0, 0))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)