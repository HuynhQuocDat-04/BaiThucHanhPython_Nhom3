import pygame
import os

class Fireball:
    def __init__(self, x, y, direction):
        effect_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "effect")
        sheet_path = os.path.join(effect_dir, "chuong-caulua.png")
        self.frames = []
        fireball_size = 100  # giống với fireball.py
        if os.path.exists(sheet_path):
            sheet = pygame.image.load(sheet_path).convert_alpha()
            num_frames = 4
            frame_w = sheet.get_width() // num_frames
            frame_h = sheet.get_height()
            for i in range(num_frames):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
                frame = pygame.transform.scale(frame, (fireball_size, fireball_size))  # To hơn
                self.frames.append(frame)
        else:
            for i in range(4):
                dummy = pygame.Surface((fireball_size, fireball_size), pygame.SRCALPHA)
                dummy.fill((255, 100, 0, 180))
                self.frames.append(dummy)
        self.frame_idx = 0
        self.frame_counter = 0
        self.frame_speed = 5
        self.rect = pygame.Rect(x, y, fireball_size, fireball_size)
        self.direction = direction
        self.speed = 5 * direction  # Bay chậm lại
        self.active = True
        self.spawn_delay = 10  # Số frame đầu không gây va chạm

    def update(self):
        self.rect.x += self.speed
        self.frame_counter += 1
        if self.frame_counter >= self.frame_speed:
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
            self.frame_counter = 0
        # Nếu ra khỏi màn hình thì tắt
        if self.rect.right < 0 or self.rect.left > 800:
            self.active = False
        if self.spawn_delay > 0:
            self.spawn_delay -= 1

    def render(self, screen):
        img = self.frames[self.frame_idx]
        if self.direction == -1:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, self.rect.topleft)

