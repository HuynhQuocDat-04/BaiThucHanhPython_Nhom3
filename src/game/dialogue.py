import pygame

class DialogueSystem:
    def __init__(self):
        self.active = False
        self.current_dialogue = []
        self.current_index = 0
        self.speaker_rect = None  # Rect của nhân vật đang nói
        
    def start_dialogue(self, dialogue_list, speaker_rect):
        """Bắt đầu hội thoại"""
        self.active = True
        self.current_dialogue = dialogue_list
        self.current_index = 0
        self.speaker_rect = speaker_rect
        
    def next_dialogue(self):
        """Chuyển sang câu tiếp theo"""
        if self.current_index < len(self.current_dialogue) - 1:
            self.current_index += 1
            return True
        else:
            # Hết hội thoại
            self.end_dialogue()
            return False
            
    def end_dialogue(self):
        """Kết thúc hội thoại"""
        self.active = False
        self.current_dialogue = []
        self.current_index = 0
        self.speaker_rect = None
        
    def get_current_text(self):
        """Lấy text hiện tại"""
        if self.active and self.current_index < len(self.current_dialogue):
            return self.current_dialogue[self.current_index]
        return ""
        
    def render(self, screen):
        """Vẽ speech bubble"""
        if not self.active or not self.speaker_rect:
            return
            
        current_text = self.get_current_text()
        if not current_text:
            return
            
        # Tạo font Unicode hỗ trợ tiếng Việt
        import os
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "DejaVuSans.ttf")
        if os.path.exists(font_path):
            font = pygame.font.Font(font_path, 18)
        else:
            font = pygame.font.SysFont("Arial", 16, bold=True)
        text_surface = font.render(current_text, True, (0, 0, 0))
        
        # Tính toán kích thước bubble
        padding = 10
        bubble_width = text_surface.get_width() + padding * 2
        bubble_height = text_surface.get_height() + padding * 2
        
        # Vị trí bubble (trên đầu nhân vật)
        bubble_x = self.speaker_rect.centerx - bubble_width // 2
        bubble_y = self.speaker_rect.top - bubble_height - 15  # Cách đầu 15px
        
        # Đảm bảo bubble không ra ngoài màn hình
        screen_width = screen.get_width()
        if bubble_x < 5:
            bubble_x = 5
        elif bubble_x + bubble_width > screen_width - 5:
            bubble_x = screen_width - bubble_width - 5
            
        if bubble_y < 5:
            bubble_y = 5
            
        # Vẽ bubble (hình chữ nhật bo góc)
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # Vẽ shadow
        shadow_rect = bubble_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=8)
        
        # Vẽ bubble chính
        pygame.draw.rect(screen, (255, 255, 255), bubble_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 2, border_radius=8)
        
        # Vẽ đuôi bubble (tam giác nhọn xuống)
        tail_tip_x = self.speaker_rect.centerx
        tail_tip_y = bubble_rect.bottom + 10
        tail_left_x = bubble_rect.centerx - 10
        tail_right_x = bubble_rect.centerx + 10
        tail_base_y = bubble_rect.bottom
        
        # Vẽ shadow cho đuôi
        shadow_points = [
            (tail_tip_x + 2, tail_tip_y + 2),
            (tail_left_x + 2, tail_base_y + 2),
            (tail_right_x + 2, tail_base_y + 2)
        ]
        pygame.draw.polygon(screen, (100, 100, 100), shadow_points)
        
        # Vẽ đuôi chính
        tail_points = [
            (tail_tip_x, tail_tip_y),
            (tail_left_x, tail_base_y),
            (tail_right_x, tail_base_y)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), tail_points)
        pygame.draw.polygon(screen, (0, 0, 0), tail_points, 2)
        
        # Vẽ text
        text_x = bubble_x + padding
        text_y = bubble_y + padding
        screen.blit(text_surface, (text_x, text_y))
        
        # Không vẽ dòng hướng dẫn SPACE