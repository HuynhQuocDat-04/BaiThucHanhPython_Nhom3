import pygame
import sys
from game.player import Player
from game.enemies import Enemy
from game.levels import Level
from game.item import Item
from game.projectile import Projectile
from game.coin import Coin  
from game.dialogue import DialogueSystem
from game.npc import NPC
from game.login_screen import LoginScreen
from game.auth_manager import AuthManager
from game.config import GAME_SETTINGS
from game.boss import Boss
from game.weapon_shop import WeaponShop
import os

# Initialize Pygame
pygame.init()

# Testing helper: set to True to skip the login screen for faster testing.
# You can also control this via environment variable SKIP_LOGIN=1 if preferred.
# Restore default behavior: do not skip login screen.
SKIP_LOGIN = False

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dũng Sĩ Đầu Nấm")

# Load background clouds
base_path = os.path.join(os.path.dirname(__file__), "assets", "other")
cloud1_img = pygame.image.load(os.path.join(base_path, "cloud1.png")).convert_alpha()
cloud2_img = pygame.image.load(os.path.join(base_path, "cloud2.png")).convert_alpha()

cloud1_img = pygame.transform.scale(cloud1_img, (100, 60))
cloud2_img = pygame.transform.scale(cloud2_img, (120, 70))

clouds = [
    {"x": 100, "y": 100, "speed": 0.3, "img": cloud1_img},
    {"x": 500, "y": 80, "speed": 0.2, "img": cloud2_img},
    {"x": 200, "y": 250, "speed": 0.25, "img": cloud2_img},
    {"x": 550, "y": 300, "speed": 0.35, "img": cloud1_img},
]

# Toggle to draw boss firebreath hitbox overlay for debugging (semi-transparent)
SHOW_HITBOX = True

clock = pygame.time.Clock()
last_dt_ms = 16

level_data_list = [
    [
        {'type': 'platform', 'x': 0, 'y': 550, 'width': 800, 'height': 50},
    {'type': 'platform', 'x': 200, 'y': 450, 'width': 180, 'height': 20},
        {'type': 'platform', 'x': 400, 'y': 350, 'width': 400, 'height': 20},
        {'type': 'platform', 'x': 600, 'y': 250, 'width': 500, 'height': 20},
    ],
    [
        {'type': 'platform', 'x': 0, 'y': 550, 'width': 800, 'height': 50},
        {'type': 'platform', 'x': 100, 'y': 450, 'width': 120, 'height': 20},
        {'type': 'platform', 'x': 300, 'y': 400, 'width': 100, 'height': 20},
        {'type': 'platform', 'x': 500, 'y': 350, 'width': 180, 'height': 20},
        {'type': 'platform', 'x': 650, 'y': 250, 'width': 100, 'height': 20},
        {'type': 'platform', 'x': 250, 'y': 200, 'width': 120, 'height': 60},
        {'type': 'platform', 'x': 450, 'y': 180, 'width': 120, 'height': 30},
        {'type': 'platform', 'x': 250, 'y': 95, 'width': 40, 'height': 40},
        {'type': 'platform', 'x': 290, 'y': 95, 'width': 40, 'height': 40},
    ],
    [
        # Level 3: Chỉ có mặt đất, không có chướng ngại vật hay quái vật
        {'type': 'platform', 'x': 0, 'y': 550, 'width': 800, 'height': 50},
    ]
]
current_level = 0
level = Level(level_data_list[current_level])

items_per_level = [[] for _ in range(len(level_data_list))]
items = items_per_level[current_level]

box_used_per_level = [[] for _ in range(len(level_data_list))]

def reset_enemies_for_level(level_idx):
    if level_idx == 0:
        return [
            Enemy((200, 490), 100),
            Enemy((300, 490), 100),
            Enemy((500, 290), 100, move_range=(400, 800))
        ]
    elif level_idx == 1:
        return [
            Enemy((120, 390), 100, move_range=(100, 220)),
            Enemy((550, 290), 100, move_range=(500, 680))
        ]
    elif level_idx == 2:
        # Level 3: không có quái vật
        return []
    return []

def get_enemies_for_level(level_idx):
    """Tạo enemies cho màn nhưng loại bỏ những con đã chết"""
    all_enemies = reset_enemies_for_level(level_idx)
    killed_set = killed_enemies_per_level[level_idx]
    
    # Lọc ra những enemy chưa bị giết (dựa trên index)
    alive_enemies = []
    for i, enemy in enumerate(all_enemies):
        if i not in killed_set:
            enemy.original_index = i  # Lưu index gốc của enemy
            alive_enemies.append(enemy)
    
    return alive_enemies


# Xác định platform nhỏ (platform thứ hai trong level đầu tiên)
small_platform = level_data_list[0][1]
player_x = small_platform['x'] + 10  # 10px cách mép trái platform
player_y = small_platform['y'] - 55  # 55 là height player
player = Player(player_x, player_y)

# Thêm NPC đứng bên phải platform nhỏ, căn chân sát mặt platform bằng midbottom
# NPC scale đúng bằng player (55px)
npc_height = 55
img = pygame.image.load(os.path.join(os.path.dirname(__file__), "assets", "Character", "16x16 knight 4 v3.png")).convert_alpha()
scale_ratio = npc_height / img.get_height()
npc_width = int(img.get_width() * scale_ratio)
del img
# Tính midbottom cho NPC sát midtop platform
npc_midbottom_x = small_platform['x'] + small_platform['width'] - npc_width // 2 - 10
npc_midbottom_y = small_platform['y']
npc = NPC(0, 0)
npc.rect = npc.image.get_rect(midbottom=(npc_midbottom_x, npc_midbottom_y))

# Lưu trạng thái quái vật đã chết cho mỗi màn
killed_enemies_per_level = [set() for _ in range(len(level_data_list))]

current_level = 0
enemies = get_enemies_for_level(current_level)
boss = None

weapon_types = [
    {"name": "Martial", "img": pygame.image.load(os.path.join(base_path, "type-martial.png")).convert_alpha()},
    {"name": "Shield", "img": pygame.image.load(os.path.join(base_path, "type-shield.png")).convert_alpha()},
    {"name": "Machate", "img": pygame.image.load(os.path.join(base_path, "type-machate.png")).convert_alpha()},
    {"name": "Magic", "img": pygame.image.load(os.path.join(base_path, "type-magic.png")).convert_alpha()},
]   
selected_weapon = 0

def draw_game_over(screen, show_weapon_select, auth_manager=None):
    # Overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # GAME OVER text
    font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
    font_big = pygame.font.SysFont(None, 80)
    font_small = pygame.font.Font(font_path, 48)
    text_game_over = font_big.render("GAME OVER", True, (255, 0, 0))
    text_retry = font_small.render("Chơi Lại", True, (255, 255, 255))
    screen.blit(text_game_over, (screen.get_width()//2 - text_game_over.get_width()//2, 180))
    retry_rect = text_retry.get_rect(center=(screen.get_width()//2, 300))
    screen.blit(text_retry, retry_rect)

    # Weapon select button
    font_btn = pygame.font.Font(font_path, 32)
    text_btn = font_btn.render("Chọn Vũ Khí", True, (0, 0, 0))
    btn_rect = pygame.Rect(screen.get_width()//2 - 100, 360, 200, 50)
    pygame.draw.rect(screen, (255, 255, 0), btn_rect, border_radius=8)
    screen.blit(text_btn, text_btn.get_rect(center=btn_rect.center))

    # Leaderboard button (dùng font nhỏ hơn để vừa trong nút)
    font_btn_small = pygame.font.Font(font_path, 24)
    text_leaderboard = font_btn_small.render("Bảng Xếp Hạng", True, (0, 0, 0))
    leaderboard_btn_rect = pygame.Rect(screen.get_width()//2 - 100, 420, 200, 50)
    pygame.draw.rect(screen, (100, 200, 255), leaderboard_btn_rect, border_radius=8)
    screen.blit(text_leaderboard, text_leaderboard.get_rect(center=leaderboard_btn_rect.center))

    weapon_rects = []
    if show_weapon_select:
        # Large overlay for weapon selection
        panel_overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        panel_overlay.fill((0, 0, 0, 200))
        screen.blit(panel_overlay, (0, 0))

        # Centered, large panel
        panel_width = 400
        panel_height = 220
        panel_rect = pygame.Rect(
            (screen.get_width() - panel_width) // 2,
            (screen.get_height() - panel_height) // 2,
            panel_width,
            panel_height
        )
        pygame.draw.rect(screen, (240, 240, 240), panel_rect, border_radius=16)
        pygame.draw.rect(screen, (180, 180, 180), panel_rect, 4, border_radius=16)

        font_weapon = pygame.font.Font(font_path, 32)
        text_weapon = font_weapon.render("Chọn vũ khí của bạn:", True, (0, 0, 0))
        screen.blit(text_weapon, (panel_rect.x + 30, panel_rect.y + 20))

        # Draw weapon icons centered horizontally
        total_width = len(weapon_types) * 70
        start_x = panel_rect.x + (panel_width - total_width) // 2
        y = panel_rect.y + 80
        for i, w in enumerate(weapon_types):
            rect = pygame.Rect(start_x + i*70, y, 60, 60)
            img = pygame.transform.scale(w["img"], (60, 60))
            
            # Kiểm tra vũ khí đã mở khóa chưa
            is_unlocked = True
            if auth_manager:
                is_unlocked = auth_manager.is_weapon_unlocked(i)
            
            # Nếu chưa mở khóa, vẽ overlay tối (không hiển thị biểu tượng khóa)
            if not is_unlocked:
                # Vẽ overlay tối lên vũ khí
                gray_overlay = pygame.Surface((60, 60), pygame.SRCALPHA)
                gray_overlay.fill((0, 0, 0, 180))
                screen.blit(img, rect.topleft)
                screen.blit(gray_overlay, rect.topleft)
                
                # Viền xám cho vũ khí bị khóa
                border_color = (100, 100, 100)
            else:
                screen.blit(img, rect.topleft)
                border_color = (255, 0, 0) if i == selected_weapon else (180, 180, 180)
            
            pygame.draw.rect(screen, border_color, rect, 4)
            weapon_rects.append(rect)
    return retry_rect, btn_rect, weapon_rects, leaderboard_btn_rect

def draw_victory_overlay(screen):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
    font_title = pygame.font.Font(font_path, 56)
    font_btn = pygame.font.Font(font_path, 32)

    text_title = font_title.render("CHIẾN THẮNG!", True, (255, 215, 0))
    screen.blit(text_title, (screen.get_width()//2 - text_title.get_width()//2, 180))

    btn_rect = pygame.Rect(screen.get_width()//2 - 140, 320, 280, 60)
    pygame.draw.rect(screen, (90, 200, 120), btn_rect, border_radius=10)
    text_btn = font_btn.render("Về màn chính", True, (0, 0, 0))
    screen.blit(text_btn, text_btn.get_rect(center=btn_rect.center))
    return btn_rect

def draw_start_screen(screen, show_weapon_select, auth_manager=None):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Sử dụng font Unicode cho tiêu đề tiếng Việt
    font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
    font_big = pygame.font.Font(font_path, 70)
    font_small = pygame.font.Font(font_path, 48)
    text_title = font_big.render("DŨNG SĨ ĐẦU NẤM", True, (255, 255, 0))
    text_play = font_small.render("Chơi", True, (255, 255, 255))

    screen.blit(text_title, (screen.get_width()//2 - text_title.get_width()//2, 180))
    play_rect = text_play.get_rect(center=(screen.get_width()//2, 300))
    screen.blit(text_play, play_rect)

    # Weapon select button
    font_btn = pygame.font.Font(font_path, 25)
    text_btn = font_btn.render("Chọn Vũ Khí", True, (0, 0, 0))
    btn_rect = pygame.Rect(screen.get_width()//2 - 100, 360, 200, 50)
    pygame.draw.rect(screen, (255, 255, 0), btn_rect, border_radius=8)
    screen.blit(text_btn, text_btn.get_rect(center=btn_rect.center))

    # Weapon shop button
    font_btn_shop = pygame.font.Font(font_path, 23)
    text_shop = font_btn_shop.render("Cửa Hàng Vũ Khí", True, (0, 0, 0))
    weapon_shop_btn_rect = pygame.Rect(screen.get_width()//2 - 100, 420, 200, 50)
    pygame.draw.rect(screen, (255, 200, 100), weapon_shop_btn_rect, border_radius=8)
    screen.blit(text_shop, text_shop.get_rect(center=weapon_shop_btn_rect.center))

    # Leaderboard button (dùng font nhỏ hơn để vừa trong nút)
    font_btn_small = pygame.font.Font(font_path, 24)
    text_leaderboard = font_btn_small.render("Bảng Xếp Hạng", True, (0, 0, 0))
    leaderboard_btn_rect = pygame.Rect(screen.get_width()//2 - 100, 480, 200, 50)
    pygame.draw.rect(screen, (100, 200, 255), leaderboard_btn_rect, border_radius=8)
    screen.blit(text_leaderboard, text_leaderboard.get_rect(center=leaderboard_btn_rect.center))

    weapon_rects = []
    if show_weapon_select:
        panel_overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        panel_overlay.fill((0, 0, 0, 200))
        screen.blit(panel_overlay, (0, 0))

        panel_width = 400
        panel_height = 220
        panel_rect = pygame.Rect(
            (screen.get_width() - panel_width) // 2,
            (screen.get_height() - panel_height) // 2,
            panel_width,
            panel_height
        )
        pygame.draw.rect(screen, (240, 240, 240), panel_rect, border_radius=16)
        pygame.draw.rect(screen, (180, 180, 180), panel_rect, 4, border_radius=16)

        font_weapon = pygame.font.Font(font_path, 32)
        text_weapon = font_weapon.render("Chọn vũ khí của bạn:", True, (0, 0, 0))
        screen.blit(text_weapon, (panel_rect.x + 30, panel_rect.y + 20))

        total_width = len(weapon_types) * 70
        start_x = panel_rect.x + (panel_width - total_width) // 2
        y = panel_rect.y + 80
        for i, w in enumerate(weapon_types):
            rect = pygame.Rect(start_x + i*70, y, 60, 60)
            img = pygame.transform.scale(w["img"], (60, 60))
            
            # Kiểm tra vũ khí đã mở khóa chưa
            is_unlocked = True
            if auth_manager:
                is_unlocked = auth_manager.is_weapon_unlocked(i)
            
            # Nếu chưa mở khóa, vẽ overlay tối (không hiển thị biểu tượng khóa)
            if not is_unlocked:
                # Vẽ overlay tối lên vũ khí
                gray_overlay = pygame.Surface((60, 60), pygame.SRCALPHA)
                gray_overlay.fill((0, 0, 0, 180))
                screen.blit(img, rect.topleft)
                screen.blit(gray_overlay, rect.topleft)
                
                # Viền xám cho vũ khí bị khóa
                border_color = (100, 100, 100)
            else:
                screen.blit(img, rect.topleft)
                border_color = (255, 0, 0) if i == selected_weapon else (180, 180, 180)
            
            pygame.draw.rect(screen, border_color, rect, 4)
            weapon_rects.append(rect)
    return play_rect, btn_rect, weapon_rects, leaderboard_btn_rect, weapon_shop_btn_rect

def draw_leaderboard(screen, auth_manager):
    """Vẽ bảng xếp hạng với danh sách người chơi theo điểm số từ cao đến thấp"""
    # Overlay tối
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))
    
    font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
    
    # Panel chính
    panel_width = 500
    panel_height = 450
    panel_rect = pygame.Rect(
        (screen.get_width() - panel_width) // 2,
        (screen.get_height() - panel_height) // 2,
        panel_width,
        panel_height
    )
    pygame.draw.rect(screen, (240, 240, 250), panel_rect, border_radius=16)
    pygame.draw.rect(screen, (100, 100, 150), panel_rect, 4, border_radius=16)
    
    # Tiêu đề
    font_title = pygame.font.Font(font_path, 48)
    text_title = font_title.render("BẢNG XẾP HẠNG", True, (50, 50, 150))
    screen.blit(text_title, (panel_rect.centerx - text_title.get_width()//2, panel_rect.y + 20))
    
    # Lấy danh sách người chơi từ auth_manager
    leaderboard = auth_manager.get_leaderboard(limit=10)
    
    # Hiển thị danh sách
    font_list = pygame.font.Font(font_path, 24)
    font_rank = pygame.font.Font(font_path, 28)
    start_y = panel_rect.y + 90
    line_height = 32
    
    for i, user in enumerate(leaderboard):
        rank = i + 1
        username = user.get("username", "Unknown")
        score = user.get("score", 0)
        
        # Màu cho top 3
        if rank == 1:
            rank_color = (255, 215, 0)  # Vàng
        elif rank == 2:
            rank_color = (192, 192, 192)  # Bạc
        elif rank == 3:
            rank_color = (205, 127, 50)  # Đồng
        else:
            rank_color = (80, 80, 80)
        
        # Render hạng
        text_rank = font_rank.render(f"#{rank}", True, rank_color)
        screen.blit(text_rank, (panel_rect.x + 30, start_y + i * line_height))
        
        # Render username
        text_username = font_list.render(username, True, (0, 0, 0))
        screen.blit(text_username, (panel_rect.x + 100, start_y + i * line_height + 2))
        
        # Render score
        text_score = font_list.render(f"{score}", True, (0, 100, 0))
        screen.blit(text_score, (panel_rect.x + panel_width - 100, start_y + i * line_height + 2))
    
    # Nút đóng
    font_btn = pygame.font.Font(font_path, 28)
    text_close = font_btn.render("Đóng (ESC)", True, (255, 255, 255))
    close_rect = text_close.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 30))
    screen.blit(text_close, close_rect)
    
    return close_rect

def save_box_used(level, current_level):
    # Lưu trạng thái các box đã dùng (ví dụ: các hộp đã lấy item)
    box_used_per_level[current_level] = []
    for plat in level.platforms:
        if plat.rect.width == 40 and plat.rect.height == 40:
            box_used_per_level[current_level].append(getattr(plat, "used", False))

def restore_box_used(level, current_level):
    # Khôi phục trạng thái các box đã dùng
    idx = 0
    for plat in level.platforms:
        if plat.rect.width == 40 and plat.rect.height == 40:
            if idx < len(box_used_per_level[current_level]):
                plat.used = box_used_per_level[current_level][idx]
                idx += 1

def init_game():
    """Khởi tạo game sau khi đăng nhập thành công"""
    global current_level, level, enemies, player, items, coin_count, player_score, selected_weapon, killed_enemies_per_level, boss
    
    # Reset game state
    current_level = 0
    coin_count = 0
    player_score = 0
    # Giữ selected_weapon là chỉ số (int) tương ứng với weapon_types
    selected_weapon = 0
    
    # Khởi tạo lại player
    small_platform = level_data_list[0][1]
    player_x = small_platform['x'] + 10
    player_y = small_platform['y'] - 55
    player = Player(player_x, player_y)
    
    # Khởi tạo lại level và enemies
    level = Level(level_data_list[current_level])
    enemies = get_enemies_for_level(current_level)
    items = []
    boss = None
    
    # Reset killed enemies
    killed_enemies_per_level = [set() for _ in range(len(level_data_list))]

def main():
    global current_level, level, enemies, player, items, coin_count, player_score, selected_weapon, killed_enemies_per_level, boss, last_dt_ms
    
    # Khởi tạo màn hình đăng nhập
    login_screen = LoginScreen(screen_width, screen_height)
    # Show login by default unless SKIP_LOGIN is set for testing
    show_login = not SKIP_LOGIN
    
    # Khởi tạo weapon shop
    weapon_shop = None
    show_weapon_shop = False
    
    attack_cooldown = 0
    coin_count = 0
    player_score = 0
    game_over = False
    retry_rect = None
    weapon_rects = []
    show_weapon_select = False
    btn_rect = None
    show_start_screen = True
    # Nếu SKIP_LOGIN bật, nhảy thẳng vào gameplay (bỏ qua màn Start)
    if SKIP_LOGIN:
        show_start_screen = False
    play_rect = None
    show_leaderboard = False
    leaderboard_btn_rect = None
    show_victory = False
    victory_btn_rect = None
    weapon_shop_btn_rect = None  # Nút mở weapon shop

    # Tạo dialogue system
    dialogue_system = DialogueSystem()

    # Dialogue intro cho NPC nói trước
    npc_intro_dialogue = [
        "Thế giới này đang bị quái vật xâm chiếm",
        "Chỉ có ngươi mới cứu được thế giới này ",
        "Ngươi có đồng ý giúp ta không ?"
    ]


    # Khi bắt đầu game, cho NPC nói trước
    started_npc_dialogue = False

    player_choice_mode = False
    npc_visible = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Xử lý màn hình đăng nhập (ƯU TIÊN CAO NHẤT)
            if show_login:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                login_screen.handle_event(event)

            # (ĐÃ DI CHUYỂN) Vẽ màn hình đăng nhập ra ngoài event loop để render mỗi frame

            # Xử lý weapon shop (ƯU TIÊN CAO SAU LOGIN)
            if show_weapon_shop and weapon_shop:
                result = weapon_shop.handle_event(event)
                if result == "back":
                    show_weapon_shop = False
                continue

            # Xử lý lựa chọn của player sau khi NPC hỏi xong (ƯU TIÊN NHẤT)
            if player_choice_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        # Đồng ý: tiếp tục game, NPC biến mất
                        player_choice_mode = False
                        npc_visible = False
                        dialogue_system.end_dialogue()
                    elif event.key == pygame.K_f:
                        # Từ chối: game over (giống như bị chết)
                        player_choice_mode = False
                        dialogue_system.end_dialogue()
                        player.health = 0
                    elif event.key == pygame.K_z:
                        # Cho phép nhấn Z (tấn công) để chấp nhận nhanh và tiếp tục game
                        player_choice_mode = False
                        npc_visible = False
                        dialogue_system.end_dialogue()
                # KHÔNG continue ở đây, để các event khác vẫn được xử lý (chỉ dừng update game logic bên dưới)

            # Ưu tiên xử lý dialogue nếu đang active
            if dialogue_system.active:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    dialogue_system.next_dialogue()
                    # Nếu vừa kết thúc hội thoại NPC thì chuyển sang lựa chọn cho player
                    if not dialogue_system.active and started_npc_dialogue:
                        player_choice_mode = True
                        dialogue_system.start_dialogue(["D: Đồng ý        F: Từ chối"], player.rect)
                # Khi dialogue đang active, block input khác
                continue

            # Ưu tiên xử lý bảng chọn vũ khí nếu đang hiện
            if show_weapon_select:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(weapon_rects):
                        if rect.collidepoint(mouse_pos):
                            # Kiểm tra vũ khí đã mở khóa chưa
                            if login_screen.auth_manager.is_weapon_unlocked(i):
                                selected_weapon = i
                                show_weapon_select = False
                                player.weapon_type = weapon_types[selected_weapon]["name"]
                            # Nếu chưa mở khóa, không làm gì (không cho chọn)
                # Khi bảng chọn vũ khí hiện, không xử lý các nút khác!
                continue

            # Xử lý bảng xếp hạng: ESC hoặc click chuột sẽ đóng overlay, ưu tiên cao
            if show_leaderboard:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    show_leaderboard = False
                    continue
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    show_leaderboard = False
                    continue

            # Xử lý màn Victory (ưu tiên cao)
            if show_victory:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Trở về màn chính
                    init_game()
                    show_start_screen = True
                    show_victory = False
                    continue
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if victory_btn_rect and victory_btn_rect.collidepoint(mouse_pos):
                        init_game()
                        show_start_screen = True
                        show_victory = False
                # Khi đang victory, không xử lý gameplay khác
                continue

            # Xử lý click ở màn hình Start
            if show_start_screen:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_rect and play_rect.collidepoint(mouse_pos):
                        show_start_screen = False
                        # Tắt mọi overlay có thể còn treo
                        show_weapon_select = False
                        show_leaderboard = False
                        # Bảo vệ selected_weapon nếu bị lệch state
                        if not isinstance(selected_weapon, int) or not (0 <= selected_weapon < len(weapon_types)):
                            selected_weapon = 0
                        player.weapon_type = weapon_types[selected_weapon]["name"]
                        # Reset trạng thái tấn công
                        player.is_attacking = False
                        player.attack_stage = 0
                        player.machate_attack_stage = 0
                        player.attack_key_held = False
                        # Bắt đầu hội thoại NPC
                        npc_visible = True
                        dialogue_system.start_dialogue(npc_intro_dialogue, npc.rect)
                        started_npc_dialogue = True
                    elif btn_rect and btn_rect.collidepoint(mouse_pos):
                        show_weapon_select = not show_weapon_select
                    elif weapon_shop_btn_rect and weapon_shop_btn_rect.collidepoint(mouse_pos):
                        show_weapon_shop = True
                        if weapon_shop is None:
                            weapon_shop = WeaponShop(screen, login_screen.auth_manager)
                    elif leaderboard_btn_rect and leaderboard_btn_rect.collidepoint(mouse_pos):
                        show_leaderboard = True
                # Khi đang ở start screen, không xử lý gameplay input
                continue

            # Xử lý click ở màn hình Game Over
            if game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if retry_rect and retry_rect.collidepoint(mouse_pos):
                        current_level = 0
                        level = Level(level_data_list[current_level])
                        player = Player(100, 400)
                        if not isinstance(selected_weapon, int) or not (0 <= selected_weapon < len(weapon_types)):
                            selected_weapon = 0
                        player.weapon_type = weapon_types[selected_weapon]["name"]
                        # Tắt mọi overlay có thể còn treo
                        show_weapon_select = False
                        show_leaderboard = False
                        # Reset trạng thái tấn công
                        player.is_attacking = False
                        player.attack_stage = 0
                        player.machate_attack_stage = 0
                        player.attack_key_held = False
                        # Reset enemies/boxes/items
                        killed_enemies_per_level = [set() for _ in range(len(level_data_list))]
                        enemies = get_enemies_for_level(current_level)
                        game_over = False
                        for i in range(len(box_used_per_level)):
                            box_used_per_level[i] = [False for plat in level_data_list[i] if plat['width'] == 40 and plat['height'] == 40]
                            items_per_level[i] = []
                        restore_box_used(level, current_level)
                        items = items_per_level[current_level]
                        show_weapon_select = False
                        npc_visible = False
                        started_npc_dialogue = False
                    elif btn_rect and btn_rect.collidepoint(mouse_pos):
                        show_weapon_select = not show_weapon_select
                        if not show_weapon_select:
                            player.weapon_type = weapon_types[selected_weapon]["name"]
                            player.is_attacking = False
                            player.attack_stage = 0
                            player.machate_attack_stage = 0
                            player.attack_key_held = False
                    elif weapon_shop_btn_rect and weapon_shop_btn_rect.collidepoint(mouse_pos):
                        show_weapon_shop = True
                        if weapon_shop is None:
                            weapon_shop = WeaponShop(screen, login_screen.auth_manager)
                    elif leaderboard_btn_rect and leaderboard_btn_rect.collidepoint(mouse_pos):
                        show_leaderboard = True
                # Khi đang ở game over, không xử lý gameplay input
                continue

            # Gameplay: xử lý phím tấn công Z
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                player.attack()
                player.attack_key_held = True
            if event.type == pygame.KEYUP and event.key == pygame.K_z:
                player.attack_key_held = False


        # (đã chuyển xử lý leaderboard vào trong event loop ở trên)

        # (đã chuyển xử lý click start/game over và phím Z vào trong vòng lặp sự kiện ở trên)

        # Vẽ màn hình đăng nhập NGOÀI event loop (render mỗi frame, không phụ thuộc event)
        if show_login:
            if login_screen.auth_manager.is_logged_in():
                show_login = False
                init_game()  # Đảm bảo reset toàn bộ trạng thái game
                # KHÔNG dùng continue ở đây để chuyển sang game ngay
            else:
                login_screen.draw(screen)
                pygame.display.flip()
                clock.tick(GAME_SETTINGS["FPS"])
                continue

        # Vẽ weapon shop nếu đang mở
        if show_weapon_shop and weapon_shop:
            weapon_shop.render()
            pygame.display.flip()
            clock.tick(GAME_SETTINGS["FPS"])
            continue

        if show_start_screen:
            screen.fill((135, 206, 235))
            for cloud in clouds:
                screen.blit(cloud["img"], (cloud["x"], cloud["y"]))
            play_rect, btn_rect, weapon_rects, leaderboard_btn_rect, weapon_shop_btn_rect = draw_start_screen(screen, show_weapon_select, login_screen.auth_manager)
            if show_leaderboard:
                draw_leaderboard(screen, login_screen.auth_manager)
            pygame.display.flip()
            clock.tick(GAME_SETTINGS["FPS"])
            continue

        if not game_over:
            # Nếu đang ở chế độ lựa chọn (player_choice_mode) thì không update game logic, chỉ render
            if not player_choice_mode:
                # Chỉ update player khi không có dialogue
                if not dialogue_system.active:
                    player.update(level.platforms)

                for cloud in clouds:
                    cloud["x"] += cloud["speed"]
                    if cloud["x"] > screen_width:
                        cloud["x"] = -cloud["img"].get_width()

                if not dialogue_system.active and player.hit_head and player.last_head_platform:
                    plat = player.last_head_platform
                    if plat.rect.width == 40 and plat.rect.height == 40:
                        items = items_per_level[current_level]
                        save_box_used(level, current_level)
                        if not hasattr(plat, "used") or not plat.used:
                            if plat.rect.x == 290 and plat.rect.y == 95:
                                items.append(Coin(plat.rect.centerx - 15, plat.rect.top + 10))
                            else:
                                items.append(Item(plat.rect.centerx - 15, plat.rect.top + 10))
                            plat.used = True
                            save_box_used(level, current_level)

                items = items_per_level[current_level]
                for item in items:
                    item.update()

                for enemy in enemies[:]:
                    enemy.update(level.platforms)
                    
                    # Xóa enemy sau khi death_timer hết
                    if enemy.is_dead and enemy.death_timer <= 0:
                        # Lưu index của enemy đã chết
                        if hasattr(enemy, 'original_index'):
                            killed_enemies_per_level[current_level].add(enemy.original_index)
                        # Cộng điểm khi hạ gục enemy
                        player_score += 50
                        # Lưu điểm ngay vào tài khoản (nếu đã đăng nhập)
                        if login_screen.auth_manager.is_logged_in():
                            login_screen.auth_manager.add_score(50)
                        enemies.remove(enemy)
                        continue
                    # Nếu player đang tấn công bằng Shield, enemy không thể đi xuyên player
                    if player.is_attacking and player.weapon_type == "Shield":
                        if enemy.rect.colliderect(player.rect):
                            # Đẩy enemy ra ngoài player, giống xử lý va chạm platform
                            if enemy.rect.centerx < player.rect.centerx:
                                enemy.rect.right = player.rect.left
                            else:
                                enemy.rect.left = player.rect.right
                            # Nếu enemy vẫn overlap (do tốc độ lớn), lặp lại cho chắc chắn
                            if enemy.rect.colliderect(player.rect):
                                if enemy.rect.centerx < player.rect.centerx:
                                    enemy.rect.right = player.rect.left
                                else:
                                    enemy.rect.left = player.rect.right
                    # BỎ QUA xử lý cận chiến nếu đang dùng Magic và đang special_active
                    skip_melee = player.weapon_type == "Magic" and player.special_active
                    if not skip_melee and player.is_attacking and player.attack_hitbox and enemy.rect.colliderect(player.attack_hitbox):
                        if player.weapon_type == "Machate":
                            # Mỗi enemy có thể bị trúng ở từng stage combo
                            stage = player.machate_attack_stage
                            if stage > 0:
                                hit_dict = player.already_hit_enemies
                                enemy_id = id(enemy)
                                if enemy_id not in hit_dict:
                                    hit_dict[enemy_id] = set()
                                if stage not in hit_dict[enemy_id] and not enemy.invincible:
                                    knockback_dir = 1 if player.facing_right else -1
                                    # Kiếm: 20 dame
                                    enemy.take_damage(20, knockback_dir)
                                    hit_dict[enemy_id].add(stage)
                            # Nếu đã trúng ở stage này thì bỏ qua
                        else:
                            # Martial (tay không) 10 dame, Shield 0 dame
                            if id(enemy) not in player.already_hit_enemies and not enemy.invincible:
                                knockback_dir = 1 if player.facing_right else -1
                                damage = 10 if player.weapon_type == "Martial" else 0
                                if damage > 0:
                                    enemy.take_damage(damage, knockback_dir)
                                player.already_hit_enemies.add(id(enemy))
                        continue
                    # Nếu player đang tấn công bằng Shield thì không nhận sát thương từ enemy
                    if player.is_attacking and player.weapon_type == "Shield":
                        continue
                    # Không nhận damage từ enemy đã chết
                    if not enemy.is_dead and player.rect.colliderect(enemy.rect):
                        player.take_damage(20)

                # Boss spawn/update tại Level 3 (index 2)
                if current_level == 2:
                    if boss is None:
                        # Spawn boss: run 4f, attack 11f; tăng kích thước lên 180px (to hơn player 55px)
                        boss = Boss(
                            x=400,
                            y=0,
                            patrol_range=(150, 750),
                            frame_count=4,
                            attack_frame_count=11,
                            target_height=180,
                            baseline_offset=0,
                            attack_drop_frames=()
                        )
                        boss.place_on_ground(level.platforms)
                    else:
                        boss.update(level.platforms, dt_ms=last_dt_ms)

                    # Boss attack damage to player
                    if boss and boss.attack_hitbox and not boss.attack_hitbox_did_damage:
                        # Shield blocks
                        if not (player.is_attacking and player.weapon_type == "Shield"):
                            if player.rect.colliderect(boss.attack_hitbox):
                                # Damage phụ thuộc vào skill đang dùng
                                if boss.state == "firebreath" and boss.frame_index in boss.skill_hit_frames:
                                    player.take_damage(boss.skill_damage)  # 50 damage
                                    boss.attack_hitbox_did_damage = True
                                elif boss.state == "attack1" and boss.frame_index == boss.attack1_hit_frame:
                                    player.take_damage(boss.attack1_damage)  # 20 damage
                                    boss.attack_hitbox_did_damage = True

                    # Va chạm cận chiến với boss
                    skip_melee_boss = player.weapon_type == "Magic" and player.special_active
                    if boss and not boss.is_dead and not skip_melee_boss and player.is_attacking and player.attack_hitbox and boss.rect.colliderect(player.attack_hitbox):
                        if player.weapon_type == "Machate":
                            stage = player.machate_attack_stage
                            if stage > 0:
                                hit_dict = player.already_hit_enemies
                                boss_id = id(boss)
                                if boss_id not in hit_dict:
                                    hit_dict[boss_id] = set()
                                if stage not in hit_dict[boss_id] and not boss.invincible:
                                    knockback_dir = 1 if player.facing_right else -1
                                    # Kiếm: 20 dame
                                    boss.take_damage(20, knockback_dir)
                                    hit_dict[boss_id].add(stage)
                        else:
                            if id(boss) not in player.already_hit_enemies and not boss.invincible:
                                knockback_dir = 1 if player.facing_right else -1
                                # Tay không: 10 dame, Shield: 0 dame
                                damage = 10 if player.weapon_type == "Martial" else 0
                                if damage > 0:
                                    boss.take_damage(damage, knockback_dir)
                                player.already_hit_enemies.add(id(boss))

                    # Va chạm đạn với boss
                    for proj in player.projectiles:
                        if boss and not boss.is_dead and proj.active and boss.rect.colliderect(proj.rect) and getattr(proj, "spawn_delay", 0) == 0:
                            proj.active = False
                            # Magic hoặc projectile có thuộc tính speed (fireball) gây 100 dame, còn lại 10
                            damage = 100 if (player.weapon_type == "Magic" or hasattr(proj, "speed")) else 10
                            boss.take_damage(damage)

                    # Physical collision with boss does NOT deal damage here; only the firebreath hitbox should.

                    # Boss chết -> hiển thị Victory, cộng điểm
                    if boss and boss.is_dead and not show_victory:
                        player_score += 500
                        if login_screen.auth_manager.is_logged_in():
                            login_screen.auth_manager.add_score(500)
                        show_victory = True

                level.update()

                if player.rect.right > screen_width:
                    save_box_used(level, current_level)
                    current_level += 1
                    if current_level >= len(level_data_list):
                        current_level = 0
                    level = Level(level_data_list[current_level])
                    restore_box_used(level, current_level)
                    player.rect.x = 0
                    # Tạo enemies cho màn mới (loại bỏ những con đã chết)
                    enemies = get_enemies_for_level(current_level)
                    items = items_per_level[current_level]

                elif player.rect.left < 0 and current_level != 0:
                    save_box_used(level, current_level)
                    current_level -= 1
                    if current_level < 0:
                        current_level = len(level_data_list) - 1
                    level = Level(level_data_list[current_level])
                    restore_box_used(level, current_level)
                    player.rect.x = screen_width - player.rect.width
                    # Tạo enemies cho màn mới (loại bỏ những con đã chết)
                    enemies = get_enemies_for_level(current_level)
                    items = items_per_level[current_level]
                if current_level == 0 and player.rect.left < 0:
                    player.rect.left = 0

                for proj in player.projectiles:
                    proj.update()
                player.projectiles = [p for p in player.projectiles if p.active]

                for proj in player.projectiles:
                    for enemy in enemies:
                        # Thêm điều kiện spawn_delay
                        if proj.active and enemy.rect.colliderect(proj.rect) and getattr(proj, "spawn_delay", 0) == 0:
                            proj.active = False
                            # Nếu là Fireball thì gây sát thương lớn hơn
                            damage = 100 if (player.weapon_type == "Magic" or hasattr(proj, "speed")) else 10
                            enemy.take_damage(damage)
                            break
                keys = pygame.key.get_pressed()
                if keys[pygame.K_c] and player.energy >= 100 and not player.is_charging_energy and not player.special_active:
                    player.special_attack()
               
            
        screen.fill((135, 206, 235))

        for cloud in clouds:
            screen.blit(cloud["img"], (cloud["x"], cloud["y"]))

        level.render(screen)
        for enemy in enemies:
            enemy.render(screen)
        # Vẽ boss (nếu đang ở Level 3)
        if current_level == 2 and boss and not boss.is_dead:
            boss.render(screen)
            boss.render_healthbar(screen)
        player.render(screen)
        if npc_visible:
            npc.render(screen)

        items = items_per_level[current_level]
        for item in items:
            item.render(screen)
            if item.active and player.rect.colliderect(item.rect) and not item.rising:
                if hasattr(item, "sheet"):
                    coin_count += 1
                    # Cộng điểm trực tiếp theo quy tắc hiện tại (100 điểm mỗi coin)
                    player_score += 100
                    if login_screen.auth_manager.is_logged_in():
                        login_screen.auth_manager.add_score(100)
                        # Cập nhật xu cho tài khoản ngay khi nhặt coin
                        login_screen.auth_manager.add_coins(1)
                    item.active = False
                else:
                    player.health = min(player.health + 50, 100)
                    item.active = False

        font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
        font = pygame.font.Font(font_path, 32)
        coin_text = font.render(f"Xu: {coin_count}", True, (255, 215, 0))
        screen.blit(coin_text, (700, 20))
        # Hiển thị điểm ngay cạnh Xu
        score_text = font.render(f"Điểm: {player_score}", True, (255, 255, 255))
        # Đặt bên trái coin_text một chút
        score_x = 700 - score_text.get_width() - 20
        screen.blit(score_text, (score_x, 20))

        retry_rect = None
        btn_rect = None
        play_rect = None
        if player.health <= 0:
            game_over = True
            # Cập nhật điểm/xu cho user (không dùng level nữa)
            if login_screen.auth_manager.is_logged_in():
                current_score = player_score + coin_count * 100
                login_screen.auth_manager.update_user_progress(
                    score=current_score
                )
            retry_rect, btn_rect, weapon_rects, leaderboard_btn_rect = draw_game_over(screen, show_weapon_select, login_screen.auth_manager)
            if show_leaderboard:
                draw_leaderboard(screen, login_screen.auth_manager)
        elif show_start_screen:
            play_rect, btn_rect, weapon_rects, leaderboard_btn_rect, weapon_shop_btn_rect = draw_start_screen(screen, show_weapon_select, login_screen.auth_manager)

        # Luôn render dialogue system trên cùng
        dialogue_system.render(screen)

        # Victory overlay
        if show_victory:
            victory_btn_rect = draw_victory_overlay(screen)

        pygame.display.flip()
        clock.tick(GAME_SETTINGS["FPS"])
        last_dt_ms = clock.get_time()

if __name__ == "__main__":
    main()