import pygame
import os

class Platform:
    chung_image = None
    mystery_image = None
    mystery_used_image = None  # Thêm cache cho mystery box đã dùng

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.used = False  # Thêm thuộc tính used mặc định

        base_path = os.path.dirname(__file__)
        assets_path = os.path.normpath(os.path.join(base_path, "..", "assets", "other"))

        if width == 40 and height == 40:
            # Mystery Box
            if Platform.mystery_image is None:
                path = os.path.join(assets_path, "mystery-box.png")
                img = pygame.image.load(path).convert_alpha()
                Platform.mystery_image = img
            self.image = pygame.transform.scale(Platform.mystery_image, (width, height))

            # Tạo hình mystery box đã dùng (màu xám)
            if Platform.mystery_used_image is None:
                gray_img = Platform.mystery_image.copy()
                arr = pygame.surfarray.pixels3d(gray_img)
                arr[:] = arr.mean(axis=2, keepdims=True)  # Chuyển sang xám
                del arr
                Platform.mystery_used_image = gray_img
            self.used_image = pygame.transform.scale(Platform.mystery_used_image, (width, height))
        else:
            # Chướng ngại
            if Platform.chung_image is None:
                path = os.path.join(assets_path, "ChuongNgai.png")
                img = pygame.image.load(path).convert_alpha()
                Platform.chung_image = img
            self.image = pygame.transform.scale(Platform.chung_image, (width, height))

    def render(self, screen):
        # Nếu là mystery box và đã dùng thì vẽ hình xám
        if self.rect.width == 40 and self.rect.height == 40 and getattr(self, "used", False):
            screen.blit(self.used_image, self.rect.topleft)
        else:
            screen.blit(self.image, self.rect.topleft)
