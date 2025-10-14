import os
import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, health, move_range=None):
        super().__init__()
        self.rect = pygame.Rect(position[0], position[1], 60, 60)
        self.direction = 1
        self.move_range = move_range
        self.health = health
        self.max_health = health  # Lưu máu tối đa để tính % thanh máu
        
        # Hiển thị sát thương
        self.damage_texts = []  # Danh sách các text sát thương đang hiển thị
        
        # Trạng thái chết
        self.is_dead = False
        self.death_timer = 0
        

        # Vận tốc di chuyển
        self.speed = 2  

        # Load frames
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets", "enemies")
        base_path = os.path.abspath(base_path)

        self.frames_right = [
            pygame.image.load(os.path.join(base_path, "enemy-walk1.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "enemy-walk2.png")).convert_alpha(),
            pygame.image.load(os.path.join(base_path, "enemy-walk3.png")).convert_alpha(),
        ]
        self.frames_right = [pygame.transform.scale(frame, (self.rect.width, self.rect.height)) for frame in self.frames_right]
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]

        # Hoạt ảnh
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.05  # chỉnh nhỏ hơn thì hoạt ảnh chậm hơn

        # Trạng thái bất tử
        self.invincible = False
        self.invincible_timer = 0

        # Knockback
        self.knockback = 0  # Số pixel bị đẩy lùi còn lại
        self.knockback_dir = 0  # Hướng đẩy lùi

        # Physics
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms=None):
        # Kiểm tra trạng thái chết
        if self.health <= 0 and not self.is_dead:
            self.is_dead = True
            self.death_timer = 15  # 15 frame = 0.25 giây để hiển thị damage text
        
        if self.is_dead:
            self.death_timer -= 1
            # Không di chuyển nữa khi chết, chỉ cập nhật damage texts
            for damage_text in self.damage_texts[:]:
                damage_text['timer'] -= 1
                damage_text['y'] -= 1
                if damage_text['timer'] <= 0:
                    self.damage_texts.remove(damage_text)
            return
        
        # Xử lý knockback trước khi di chuyển bình thường
        if self.knockback > 0:
            self.rect.x += self.knockback_dir * 6
            self.knockback -= 1
        else:
            # CHỈ di chuyển ngang và kiểm tra move_range khi đang đứng trên platform
            if self.on_ground:
                self.rect.x += self.direction * self.speed

                if self.move_range:
                    # Nếu vượt ra khỏi move_range thì đảo hướng, KHÔNG ép vị trí
                    if self.rect.left < self.move_range[0]:
                        self.direction = 1
                    elif self.rect.right > self.move_range[1]:
                        self.direction = -1
                else:
                    # Nếu không có move_range, chỉ đảo hướng khi chạm mép màn hình
                    if self.rect.left < 0:
                        self.direction = 1
                    elif self.rect.right > 800:
                        self.direction = -1

        # Áp dụng trọng lực
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.y += int(self.vel_y)
        self.on_ground = False

        # Xác định platform đất chính (y lớn nhất, width >= 800)
        ground_platform = None
        if platforms:
            for plat in platforms:
                if plat.rect.width >= 800:
                    ground_platform = plat
                    break

        # Kiểm tra va chạm với platform
        standing_on_ground = False
        if platforms:
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    if self.vel_y > 0 and self.rect.bottom - plat.rect.top < 20:
                        self.rect.bottom = plat.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        # Nếu đứng trên platform đất chính thì bỏ move_range
                        if ground_platform and plat == ground_platform:
                            standing_on_ground = True
                        break  # Đã đứng trên 1 platform thì không cần kiểm tra tiếp

        # Nếu đang đứng trên đất chính thì bỏ move_range, cho đi tự do
        if standing_on_ground:
            self.move_range = None
        else:
            # Nếu enemy có move_range gốc thì giữ lại, tránh bị mất khi nhảy lên lại platform
            if hasattr(self, "original_move_range"):
                self.move_range = self.original_move_range
            else:
                self.original_move_range = self.move_range

        # Cập nhật hoạt ảnh (chậm, cố định)
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames_right)
        
        # Cập nhật damage texts
        for damage_text in self.damage_texts[:]:
            damage_text['timer'] -= 1
            damage_text['y'] -= 1  # Text bay lên
            if damage_text['timer'] <= 0:
                self.damage_texts.remove(damage_text)
        

    def render(self, screen):
        # Làm mờ enemy khi chết
        alpha = 100 if self.is_dead else 255
        
        if self.direction > 0:
            frame = self.frames_right[self.current_frame].copy()
        else:
            frame = self.frames_left[self.current_frame].copy()
        
        if self.is_dead:
            frame.set_alpha(alpha)
        
        screen.blit(frame, self.rect)
        
        # Hiển thị thanh máu (chỉ khi còn sống)
        if self.health > 0 and not self.is_dead:
            # Thanh máu nền (đỏ)
            health_bar_bg = pygame.Rect(self.rect.x, self.rect.y - 10, self.rect.width, 6)
            pygame.draw.rect(screen, (255, 0, 0), health_bar_bg)
            
            # Thanh máu hiện tại (xanh lá)
            health_percentage = self.health / self.max_health
            health_bar_fg = pygame.Rect(self.rect.x, self.rect.y - 10, self.rect.width * health_percentage, 6)
            pygame.draw.rect(screen, (0, 255, 0), health_bar_fg)
            
            # Viền thanh máu
            pygame.draw.rect(screen, (0, 0, 0), health_bar_bg, 1)
        
        # Hiển thị damage texts
        font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "DejaVuSans.ttf")
        try:
            font = pygame.font.Font(font_path, 20)
        except:
            font = pygame.font.SysFont(None, 20)
            
        for damage_text in self.damage_texts:
            color = (255, 255, 0) if damage_text['amount'] >= 50 else (255, 100, 100)
            text_surface = font.render(f"-{damage_text['amount']}", True, color)
            screen.blit(text_surface, (damage_text['x'], damage_text['y']))

    def take_damage(self, amount, knockback_dir=0):       
        self.health -= amount
        if knockback_dir != 0:
            self.knockback = 8  # số frame bị đẩy lùi, chỉnh tùy ý
            self.knockback_dir = knockback_dir
        
        # Thêm text sát thương
        damage_text = {
            'amount': amount,
            'x': self.rect.centerx - 10,
            'y': self.rect.y - 20,
            'timer': 60  # Hiển thị trong 60 frame (1 giây với 60 FPS)
        }
        self.damage_texts.append(damage_text)
