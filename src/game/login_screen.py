import pygame
import sys
import os
from game.auth_manager import AuthManager

class LoginScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.auth_manager = AuthManager()
        
        # Background image (optional)
        self._bg_image = None           # original image surface
        self._bg_scaled = None          # scaled to cover window
        self._bg_cache_size = None      # cache size to avoid re-scale every frame
        self._load_background()
        
        # Màu sắc
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 100, 200)
        self.GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        
        # Font (đường dẫn tuyệt đối tới assets/fonts)
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            font_path = os.path.join(base_dir, "assets", "fonts", "DejaVuSans.ttf")
            self.font_large = pygame.font.Font(font_path, 36)
            self.font_medium = pygame.font.Font(font_path, 24)
            self.font_small = pygame.font.Font(font_path, 18)
            # Font nhỏ hơn dành riêng cho hướng dẫn cuối màn hình
            self.font_tiny = pygame.font.Font(font_path, 14)
        except:
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
            self.font_tiny = pygame.font.Font(None, 14)
        
        # Trạng thái
        self.mode = "login"  # "login" hoặc "register"
        self.username_input = ""
        self.password_input = ""
        self.email_input = ""
        self.active_field = "username"
        self.message = ""
        self.message_color = self.BLACK
        
        # Cursor blinking
        self.cursor_timer = 0
        self.cursor_visible = True
        
        # Buttons
        self.login_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 100, 200, 50)
        self.register_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 160, 200, 50)
        self.switch_mode_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 220, 200, 30)
        
        # Input boxes
        self.username_box = pygame.Rect(screen_width//2 - 150, screen_height//2 - 60, 300, 40)
        self.password_box = pygame.Rect(screen_width//2 - 150, screen_height//2 - 10, 300, 40)
        self.email_box = pygame.Rect(screen_width//2 - 150, screen_height//2 + 40, 300, 40)
    
    def _load_background(self):
        """Attempt to load a background image from assets/other.
        Tries a few common filenames and caches the original surface.
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            other_dir = os.path.join(base_dir, "assets", "other")
            candidates = [
                "login_bg.jpg", "login_bg.png",
                "background.jpg", "background.png"
            ]
            for name in candidates:
                path = os.path.join(other_dir, name)
                if os.path.exists(path):
                    self._bg_image = pygame.image.load(path).convert()  # drop alpha for faster blit
                    self._bg_scaled = None
                    self._bg_cache_size = None
                    break
        except Exception:
            # Background is optional; ignore any failures.
            self._bg_image = None
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                # Chuyển đổi giữa các field
                if self.mode == "login":
                    self.active_field = "password" if self.active_field == "username" else "username"
                else:  # register mode
                    fields = ["username", "password", "email"]
                    current_index = fields.index(self.active_field)
                    self.active_field = fields[(current_index + 1) % len(fields)]
            
            elif event.key == pygame.K_RETURN:
                # Enter để đăng nhập/đăng ký
                if self.mode == "login":
                    self.login()
                else:
                    self.register()
            
            elif event.key == pygame.K_BACKSPACE:
                # Xóa ký tự
                if self.active_field == "username":
                    self.username_input = self.username_input[:-1]
                elif self.active_field == "password":
                    self.password_input = self.password_input[:-1]
                elif self.active_field == "email":
                    self.email_input = self.email_input[:-1]
            
            else:
                # Nhập ký tự
                char = event.unicode
                if char.isprintable():
                    if self.active_field == "username":
                        if len(self.username_input) < 20:
                            self.username_input += char
                    elif self.active_field == "password":
                        if len(self.password_input) < 20:
                            self.password_input += char
                    elif self.active_field == "email":
                        if len(self.email_input) < 30:
                            self.email_input += char
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Kiểm tra click vào input boxes
            if self.username_box.collidepoint(mouse_pos):
                self.active_field = "username"
            elif self.password_box.collidepoint(mouse_pos):
                self.active_field = "password"
            elif self.email_box.collidepoint(mouse_pos) and self.mode == "register":
                self.active_field = "email"
            
            # Kiểm tra click vào buttons
            elif self.login_button.collidepoint(mouse_pos) and self.mode == "login":
                self.login()
            elif self.register_button.collidepoint(mouse_pos) and self.mode == "register":
                self.register()
            elif self.switch_mode_button.collidepoint(mouse_pos):
                self.switch_mode()
    
    def login(self):
        if not self.username_input or not self.password_input:
            self.message = "Vui lòng nhập đầy đủ thông tin!"
            self.message_color = self.RED
            return False
        
        success, message = self.auth_manager.login(self.username_input, self.password_input)
        self.message = message
        self.message_color = self.GREEN if success else self.RED
        
        return success
    
    def register(self):
        if not self.username_input or not self.password_input:
            self.message = "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!"
            self.message_color = self.RED
            return False
        
        success, message = self.auth_manager.register(self.username_input, self.password_input, self.email_input)
        self.message = message
        self.message_color = self.GREEN if success else self.RED
        
        if success:
            # Tự động chuyển sang chế độ đăng nhập
            self.mode = "login"
            self.password_input = ""  # Xóa mật khẩu
        
        return False  # Không tự động đăng nhập sau khi đăng ký
    
    def switch_mode(self):
        self.mode = "register" if self.mode == "login" else "login"
        self.message = ""
        self.active_field = "username"
        # Không xóa input để user không phải nhập lại
    
    def _ensure_scaled_background(self):
        """Ensure self._bg_scaled covers the window, recomputing if needed."""
        if not self._bg_image:
            return None
        if self._bg_cache_size == (self.screen_width, self.screen_height) and self._bg_scaled:
            return self._bg_scaled
        # Compute cover scaling
        img_w, img_h = self._bg_image.get_width(), self._bg_image.get_height()
        if img_w == 0 or img_h == 0:
            return None
        scale = max(self.screen_width / img_w, self.screen_height / img_h)
        new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
        self._bg_scaled = pygame.transform.smoothscale(self._bg_image, new_size)
        self._bg_cache_size = (self.screen_width, self.screen_height)
        return self._bg_scaled

    def draw(self, screen):
        # Background: cover-fit image with subtle dark overlay for readability
        bg = self._ensure_scaled_background()
        if bg:
            x = (self.screen_width - bg.get_width()) // 2
            y = (self.screen_height - bg.get_height()) // 2
            screen.blit(bg, (x, y))
            # Overlay (transparent black)
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 60))  # ~24% opacity (brighter background)
            screen.blit(overlay, (0, 0))
        else:
            # Fallback solid background if no image found
            screen.fill((240, 248, 255))  # Alice Blue
        
        # Update cursor blinking
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # 30 frames = 0.5 seconds at 60 FPS
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # Title
        title_text = "ĐĂNG NHẬP" if self.mode == "login" else "ĐĂNG KỲ TÀI KHOẢN"
        # Slight shadow for title for contrast on bright backgrounds
        title_surface = self.font_large.render(title_text, True, self.BLUE)
        title_rect = title_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 150))
        screen.blit(title_surface, title_rect)
        
        # Input boxes + placeholders (text mờ bên trong ô, tự ẩn khi có nhập liệu)
        placeholder_color = (150, 150, 150)
        # Username
        username_color = self.BLUE if self.active_field == "username" else self.GRAY
        border_width = 3 if self.active_field == "username" else 2
        pygame.draw.rect(screen, username_color, self.username_box, border_width)
        inner_color = (255, 255, 255) if self.active_field != "username" else (250, 250, 255)
        pygame.draw.rect(screen, inner_color, (self.username_box.x + border_width, self.username_box.y + border_width, 
                                           self.username_box.width - border_width*2, self.username_box.height - border_width*2))
        
        if self.username_input:
            username_display = self.username_input + ("|" if self.active_field == "username" and self.cursor_visible else "")
            username_surface = self.font_medium.render(username_display, True, self.BLACK)
        else:
            username_surface = self.font_medium.render("Tên đăng nhập", True, placeholder_color)
        screen.blit(username_surface, (self.username_box.x + 5, self.username_box.y + 10))
        
        # Password
        password_color = self.BLUE if self.active_field == "password" else self.GRAY
        border_width = 3 if self.active_field == "password" else 2
        pygame.draw.rect(screen, password_color, self.password_box, border_width)
        inner_color = (255, 255, 255) if self.active_field != "password" else (250, 250, 255)
        pygame.draw.rect(screen, inner_color, (self.password_box.x + border_width, self.password_box.y + border_width,
                                           self.password_box.width - border_width*2, self.password_box.height - border_width*2))
        
        # Hiển thị mật khẩu dạng dấu * hoặc placeholder khi trống
        if self.password_input:
            password_display = "*" * len(self.password_input)
            if self.active_field == "password" and self.cursor_visible:
                password_display += "|"
            password_surface = self.font_medium.render(password_display, True, self.BLACK)
        else:
            password_surface = self.font_medium.render("Mật khẩu", True, placeholder_color)
        screen.blit(password_surface, (self.password_box.x + 5, self.password_box.y + 10))
        
        # Email (chỉ hiện khi đăng ký)
        if self.mode == "register":
            email_color = self.BLUE if self.active_field == "email" else self.GRAY
            border_width = 3 if self.active_field == "email" else 2
            pygame.draw.rect(screen, email_color, self.email_box, border_width)
            inner_color = (255, 255, 255) if self.active_field != "email" else (250, 250, 255)
            pygame.draw.rect(screen, inner_color, (self.email_box.x + border_width, self.email_box.y + border_width,
                                               self.email_box.width - border_width*2, self.email_box.height - border_width*2))
            
            if self.email_input:
                email_display = self.email_input + ("|" if self.active_field == "email" and self.cursor_visible else "")
                email_surface = self.font_medium.render(email_display, True, self.BLACK)
            else:
                email_surface = self.font_medium.render("Email (tùy chọn)", True, placeholder_color)
            screen.blit(email_surface, (self.email_box.x + 5, self.email_box.y + 10))
        
        # Buttons
        if self.mode == "login":
            pygame.draw.rect(screen, self.BLUE, self.login_button)
            login_text = self.font_medium.render("ĐĂNG NHẬP", True, self.WHITE)
            login_rect = login_text.get_rect(center=self.login_button.center)
            screen.blit(login_text, login_rect)
        else:
            pygame.draw.rect(screen, self.BLUE, self.register_button)
            register_text = self.font_medium.render("ĐĂNG KÝ", True, self.WHITE)
            register_rect = register_text.get_rect(center=self.register_button.center)
            screen.blit(register_text, register_rect)
        
        # Switch mode button
        pygame.draw.rect(screen, self.GRAY, self.switch_mode_button)
        switch_text = "Chưa có tài khoản?" if self.mode == "login" else "Đã có tài khoản?"
        switch_surface = self.font_small.render(switch_text, True, self.BLACK)
        switch_rect = switch_surface.get_rect(center=self.switch_mode_button.center)
        screen.blit(switch_surface, switch_rect)
        
        # Message
        if self.message:
            message_surface = self.font_small.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 + 280))
            screen.blit(message_surface, message_rect)
        
        # Instructions
        instructions = [
            "Nhấn TAB để chuyển field",
            "Nhấn ENTER để đăng nhập/đăng ký",
            "ESC để thoát"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.font_tiny.render(instruction, True, self.GRAY)
            screen.blit(inst_surface, (20, self.screen_height - 80 + i * 20))
    
    def get_auth_manager(self):
        return self.auth_manager