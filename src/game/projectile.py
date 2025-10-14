import pygame

class Projectile:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 20, 10)
        self.color = (255, 100, 0)
        self.speed = 10 * direction  # direction: 1 (phải), -1 (trái)
        self.active = True

    def update(self):
        self.rect.x += self.speed
        # Nếu ra khỏi màn hình thì biến mất
        if self.rect.right < 0 or self.rect.left > 800:
            self.active = False

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)