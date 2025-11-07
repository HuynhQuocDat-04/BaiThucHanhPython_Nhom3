"""
Màn hình chọn vũ khí - Weapon Shop
"""
import pygame
import os


class WeaponShop:
    """Màn hình chọn và mua vũ khí"""
    
    # Danh sách vũ khí (id, name, description)
    WEAPONS = [
        (0, "Tay không", "Vũ khí mặc định:   10 dame"),
        (1, "Khiên", "Phòng thủ tốt:   chặn dame"),
        (2, "Kiếm", "Vũ khí cận chiến:   20 dame"),
        (3, "Phép thuật", "Tấn công phép:   100 dame"),
    ]
    
    def __init__(self, screen, auth_manager):
        self.screen = screen
        self.auth_manager = auth_manager
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Load font Unicode để hiển thị tiếng Việt
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "DejaVuSans.ttf")
        
        # Fonts
        self.title_font = pygame.font.Font(font_path, 60)
        self.font = pygame.font.Font(font_path, 36)
        self.small_font = pygame.font.Font(font_path, 24)
        self.tiny_font = pygame.font.Font(font_path, 18)  # Font nhỏ hơn cho description
        
        # Colors
        self.bg_color = (20, 20, 40)
        self.panel_color = (40, 40, 70)
        self.selected_color = (80, 120, 200)
        self.locked_color = (80, 80, 80)
        self.text_color = (255, 255, 255)
        self.coin_color = (255, 215, 0)
        
        # Layout
        self.panel_width = 180
        self.panel_height = 220
        self.panel_spacing = 20
        self.start_x = (self.width - (len(self.WEAPONS) * (self.panel_width + self.panel_spacing))) // 2
        self.start_y = 180
        
        # Selected weapon
        self.selected_index = 0
        
        # Load coin icon (tạm thời dùng text, bạn có thể thay bằng hình ảnh)
        self.coin_text = "XU"
        
        # Back button (bên trái)
        self.back_button = pygame.Rect(50, self.height - 80, 150, 50)
        
        # Buy button (bên phải, song song với nút Quay lại)
        self.buy_button = pygame.Rect(self.width - 200, self.height - 80, 150, 50)
        
        # Load weapon icons from assets/other to reuse the same style as weapon menu
        # Path relative to src/game -> src/assets/other
        other_assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "other")
        try:
            self.weapon_icons = [
                pygame.image.load(os.path.join(other_assets_path, "type-martial.png")).convert_alpha(),
                pygame.image.load(os.path.join(other_assets_path, "type-shield.png")).convert_alpha(),
                pygame.image.load(os.path.join(other_assets_path, "type-machate.png")).convert_alpha(),
                pygame.image.load(os.path.join(other_assets_path, "type-magic.png")).convert_alpha(),
            ]
        except Exception:
            # Fallback to empty list if icons not found; rendering will keep gray boxes
            self.weapon_icons = []
        
    def handle_event(self, event):
        """Xử lý sự kiện"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check back button
            if self.back_button.collidepoint(mouse_pos):
                return "back"
            
            # Check buy button
            if self.buy_button.collidepoint(mouse_pos):
                # Mua vũ khí đang được chọn
                weapon_id = self.WEAPONS[self.selected_index][0]
                if not self.auth_manager.is_weapon_unlocked(weapon_id):
                    success, message = self.auth_manager.unlock_weapon(weapon_id)
                    if success:
                        self.auth_manager.select_weapon(weapon_id)
                    # Có thể thêm thông báo lỗi nếu không đủ XU
                return None
            
            # Check weapon panels - chỉ để chọn
            for i, weapon in enumerate(self.WEAPONS):
                weapon_id = weapon[0]
                panel_x = self.start_x + i * (self.panel_width + self.panel_spacing)
                panel_y = self.start_y
                panel_rect = pygame.Rect(panel_x, panel_y, self.panel_width, self.panel_height)
                
                if panel_rect.collidepoint(mouse_pos):
                    # Chọn vũ khí này
                    self.selected_index = i
                    # Nếu đã mở khóa thì set làm vũ khí hiện tại
                    if self.auth_manager.is_weapon_unlocked(weapon_id):
                        self.auth_manager.select_weapon(weapon_id)
                    break
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key == pygame.K_LEFT:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = min(len(self.WEAPONS) - 1, self.selected_index + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Mua/chọn vũ khí bằng phím
                weapon_id = self.WEAPONS[self.selected_index][0]
                if self.auth_manager.is_weapon_unlocked(weapon_id):
                    self.auth_manager.select_weapon(weapon_id)
                else:
                    success, message = self.auth_manager.unlock_weapon(weapon_id)
                    if success:
                        self.auth_manager.select_weapon(weapon_id)
        
        return None
    
    def render(self):
        """Vẽ màn hình"""
        # Background
        self.screen.fill(self.bg_color)
        
        # Title
        title_surf = self.title_font.render("MUA VŨ KHÍ", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Hiển thị số XU hiện tại
        user_data = self.auth_manager.get_user_data()
        coins = user_data.get("coins", 0) if user_data else 0
        coin_surf = self.font.render(f"XU: {coins}", True, self.coin_color)
        coin_rect = coin_surf.get_rect(topright=(self.width - 50, 50))
        self.screen.blit(coin_surf, coin_rect)
        
        # Vũ khí đang chọn
        selected_weapon_id = self.auth_manager.get_selected_weapon()
        
        # Weapon panels
        for i, weapon in enumerate(self.WEAPONS):
            weapon_id, weapon_name, weapon_desc = weapon
            panel_x = self.start_x + i * (self.panel_width + self.panel_spacing)
            panel_y = self.start_y
            
            is_unlocked = self.auth_manager.is_weapon_unlocked(weapon_id)
            is_selected = weapon_id == selected_weapon_id
            is_highlighted = i == self.selected_index  # Vũ khí đang được chọn để mua
            
            # Panel color and border
            if is_highlighted:
                # Viền vàng cho vũ khí đang được chọn
                border_color = (255, 215, 0)
                border_width = 4
            else:
                # Viền trắng cho tất cả vũ khí còn lại
                border_color = self.text_color
                border_width = 3
            
            # Màu nền panel
            if is_selected:
                color = self.selected_color
            elif is_unlocked:
                # Màu xanh dương cho vũ khí đã mở khóa (giống Tay không)
                color = (80, 120, 200)
            else:
                # Màu xám cho vũ khí bị khóa
                color = self.locked_color
            
            # Draw panel
            panel_rect = pygame.Rect(panel_x, panel_y, self.panel_width, self.panel_height)
            pygame.draw.rect(self.screen, color, panel_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, panel_rect, border_width, border_radius=10)
            
            # Weapon icon (use actual images loaded from assets/other)
            icon_size = 80
            icon_rect = pygame.Rect(panel_x + (self.panel_width - icon_size) // 2,
                                    panel_y + 20, icon_size, icon_size)
            if hasattr(self, "weapon_icons") and len(self.weapon_icons) > i and self.weapon_icons[i] is not None:
                icon_img = pygame.transform.smoothscale(self.weapon_icons[i], (icon_size, icon_size))
                self.screen.blit(icon_img, icon_rect.topleft)
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), icon_rect, border_radius=5)
            
            # Nếu chưa mở khóa, làm mờ icon và hiển thị giá
            if not is_unlocked:
                # Làm mờ icon bằng overlay tối để thể hiện đang bị khóa
                dim_overlay = pygame.Surface((icon_rect.width, icon_rect.height), pygame.SRCALPHA)
                dim_overlay.fill((0, 0, 0, 140))
                self.screen.blit(dim_overlay, icon_rect.topleft)
                
                # Vẽ giá ở góc dưới phải
                price_text = "1"
                price_surf = self.small_font.render(price_text, True, self.coin_color)
                coin_icon_surf = self.small_font.render(self.coin_text, True, self.coin_color)
                
                price_x = panel_x + self.panel_width - price_surf.get_width() - coin_icon_surf.get_width() - 15
                price_y = panel_y + self.panel_height - 35
                
                self.screen.blit(price_surf, (price_x, price_y))
                self.screen.blit(coin_icon_surf, (price_x + price_surf.get_width() + 3, price_y))
                
            elif is_selected:
                # Vẽ dấu check nếu đang được chọn
                check_surf = self.font.render("✓", True, (0, 255, 0))
                check_rect = check_surf.get_rect(center=icon_rect.center)
                self.screen.blit(check_surf, check_rect)
            
            # Weapon name
            name_surf = self.small_font.render(weapon_name, True, self.text_color)
            name_rect = name_surf.get_rect(center=(panel_x + self.panel_width // 2, panel_y + 130))
            self.screen.blit(name_surf, name_rect)
            
            # Weapon description (wrap text)
            desc_lines = self._wrap_text(weapon_desc, self.panel_width - 20)
            for j, line in enumerate(desc_lines):
                desc_surf = self.tiny_font.render(line, True, (200, 200, 200))
                desc_rect = desc_surf.get_rect(center=(panel_x + self.panel_width // 2, panel_y + 160 + j * 18))
                self.screen.blit(desc_surf, desc_rect)
        
        # Back button (trái)
        pygame.draw.rect(self.screen, (100, 100, 150), self.back_button, border_radius=8)
        pygame.draw.rect(self.screen, self.text_color, self.back_button, 2, border_radius=8)
        back_surf = self.font.render("Quay lại", True, self.text_color)
        back_rect = back_surf.get_rect(center=self.back_button.center)
        self.screen.blit(back_surf, back_rect)
        
        # Buy button (phải) - chỉ hiện khi vũ khí được chọn chưa mở khóa
        selected_weapon = self.WEAPONS[self.selected_index]
        selected_weapon_id = selected_weapon[0]
        is_selected_unlocked = self.auth_manager.is_weapon_unlocked(selected_weapon_id)

        # Nút MUA (hiện khi vũ khí đang highlight chưa mở khóa)
        if not is_selected_unlocked:
            buy_color = (50, 200, 50) if coins >= 1 else (100, 100, 100)
            pygame.draw.rect(self.screen, buy_color, self.buy_button, border_radius=8)
            pygame.draw.rect(self.screen, self.text_color, self.buy_button, 2, border_radius=8)
            buy_surf = self.font.render("MUA", True, self.text_color)
            buy_rect = buy_surf.get_rect(center=self.buy_button.center)
            self.screen.blit(buy_surf, buy_rect)
        else:
            # Nếu đã mở khóa: vẫn vẽ nền nút mờ để bố cục không thay đổi (tuỳ chọn)
            disabled_color = (70, 70, 90)
            pygame.draw.rect(self.screen, disabled_color, self.buy_button, border_radius=8)
            pygame.draw.rect(self.screen, self.text_color, self.buy_button, 2, border_radius=8)

            label = "ĐÃ MỞ KHÓA"  # Label khi đã sở hữu vũ khí
            # Thu nhỏ font nếu chữ bị tràn ra khỏi nút
            font_candidates = [self.font, self.small_font, self.tiny_font]
            chosen_font = self.font
            for fnt in font_candidates:
                if fnt.render(label, True, (0,0,0)).get_width() <= self.buy_button.width - 20:  # padding 10 mỗi bên
                    chosen_font = fnt
                    break

            buy_surf = chosen_font.render(label, True, (160,160,160))
            buy_rect = buy_surf.get_rect(center=self.buy_button.center)
            self.screen.blit(buy_surf, buy_rect)

        # Hướng dẫn (đặt phía trên hàng nút để không đè lên)
        inst_text = "Nhấn MUA để mở khóa" if not is_selected_unlocked else "Click để chọn vũ khí"
        inst_surf = self.small_font.render(inst_text, True, (150, 150, 150))
        inst_y = max(0, self.back_button.top - 12)
        inst_rect = inst_surf.get_rect(center=(self.width // 2, inst_y))
        self.screen.blit(inst_surf, inst_rect)
    
    def _wrap_text(self, text, max_width):
        """Chia text thành nhiều dòng"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_surf = self.tiny_font.render(test_line, True, (0, 0, 0))
            if test_surf.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines[:2]  # Giới hạn 2 dòng
