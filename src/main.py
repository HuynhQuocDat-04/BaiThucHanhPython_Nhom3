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
import os

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dũng Sĩ Diệt Rồng")

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

clock = pygame.time.Clock()

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

weapon_types = [
    {"name": "Martial", "img": pygame.image.load(os.path.join(base_path, "type-martial.png")).convert_alpha()},
    {"name": "Shield", "img": pygame.image.load(os.path.join(base_path, "type-shield.png")).convert_alpha()},
    {"name": "Machate", "img": pygame.image.load(os.path.join(base_path, "type-machate.png")).convert_alpha()},
    {"name": "Magic", "img": pygame.image.load(os.path.join(base_path, "type-magic.png")).convert_alpha()},
]   
selected_weapon = 0

def draw_game_over(screen, show_weapon_select):
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
            border_color = (255, 0, 0) if i == selected_weapon else (180, 180, 180)
            pygame.draw.rect(screen, border_color, rect, 4)
            screen.blit(img, rect.topleft)
            weapon_rects.append(rect)
    return retry_rect, btn_rect, weapon_rects

def draw_start_screen(screen, show_weapon_select):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Sử dụng font Unicode cho tiêu đề tiếng Việt
    font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
    font_big = pygame.font.Font(font_path, 70)
    font_small = pygame.font.Font(font_path, 48)
    text_title = font_big.render("DŨNG SĨ DIỆT RỒNG", True, (255, 255, 0))
    text_play = font_small.render("Chơi", True, (255, 255, 255))

    screen.blit(text_title, (screen.get_width()//2 - text_title.get_width()//2, 180))
    play_rect = text_play.get_rect(center=(screen.get_width()//2, 300))
    screen.blit(text_play, play_rect)

    # Weapon select button
    font_btn = pygame.font.Font(font_path, 32)
    text_btn = font_btn.render("Chọn Vũ Khí", True, (0, 0, 0))
    btn_rect = pygame.Rect(screen.get_width()//2 - 100, 360, 200, 50)
    pygame.draw.rect(screen, (255, 255, 0), btn_rect, border_radius=8)
    screen.blit(text_btn, text_btn.get_rect(center=btn_rect.center))

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
            border_color = (255, 0, 0) if i == selected_weapon else (180, 180, 180)
            pygame.draw.rect(screen, border_color, rect, 4)
            screen.blit(img, rect.topleft)
            weapon_rects.append(rect)
    return play_rect, btn_rect, weapon_rects

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

def main():
    global current_level, level, enemies, player, items, coin_count, selected_weapon, killed_enemies_per_level
    attack_cooldown = 0
    coin_count = 0
    game_over = False
    retry_rect = None
    weapon_rects = []
    show_weapon_select = False
    btn_rect = None
    show_start_screen = True
    play_rect = None
    

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
                            selected_weapon = i
                            show_weapon_select = False
                # Khi bảng chọn vũ khí hiện, không xử lý các nút khác!
                continue

            if show_start_screen:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_rect and play_rect.collidepoint(mouse_pos):
                        show_start_screen = False
                        player.weapon_type = weapon_types[selected_weapon]["name"]
                        # Bắt đầu hội thoại của NPC và cho NPC xuất hiện
                        npc_visible = True
                        dialogue_system.start_dialogue(npc_intro_dialogue, npc.rect)
                        started_npc_dialogue = True
                    elif btn_rect and btn_rect.collidepoint(mouse_pos):
                        show_weapon_select = not show_weapon_select
            elif game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if retry_rect and retry_rect.collidepoint(mouse_pos):
                        current_level = 0
                        level = Level(level_data_list[current_level])
                        player = Player(100, 400)
                        player.weapon_type = weapon_types[selected_weapon]["name"]
                        # Reset danh sách enemies đã chết
                        killed_enemies_per_level = [set() for _ in range(len(level_data_list))]
                        enemies = get_enemies_for_level(current_level)
                        game_over = False
                        for i in range(len(box_used_per_level)):
                            box_used_per_level[i] = [False for plat in level_data_list[i] if plat['width'] == 40 and plat['height'] == 40]
                            items_per_level[i] = []
                        restore_box_used(level, current_level)
                        items = items_per_level[current_level]
                        show_weapon_select = False
                        # NPC sẽ biến mất hoàn toàn khi chơi lại
                        npc_visible = False
                        started_npc_dialogue = False
                    elif btn_rect and btn_rect.collidepoint(mouse_pos):
                        show_weapon_select = not show_weapon_select
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                    player.attack()
                    player.attack_key_held = True
                if event.type == pygame.KEYUP and event.key == pygame.K_z:
                    player.attack_key_held = False

        if show_start_screen:
            screen.fill((135, 206, 235))
            for cloud in clouds:
                screen.blit(cloud["img"], (cloud["x"], cloud["y"]))
            play_rect, btn_rect, weapon_rects = draw_start_screen(screen, show_weapon_select)
            pygame.display.flip()
            clock.tick(60)
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
                                    enemy.take_damage(20, knockback_dir)
                                    hit_dict[enemy_id].add(stage)
                            # Nếu đã trúng ở stage này thì bỏ qua
                        else:
                            # Martial, Shield: giữ logic cũ
                            if id(enemy) not in player.already_hit_enemies and not enemy.invincible:
                                knockback_dir = 1 if player.facing_right else -1
                                enemy.take_damage(20, knockback_dir)
                                player.already_hit_enemies.add(id(enemy))
                        continue
                    # Nếu player đang tấn công bằng Shield thì không nhận sát thương từ enemy
                    if player.is_attacking and player.weapon_type == "Shield":
                        continue
                    # Không nhận damage từ enemy đã chết
                    if not enemy.is_dead and player.rect.colliderect(enemy.rect):
                        player.take_damage(20)

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
                            if hasattr(proj, "speed"):
                                enemy.take_damage(100)
                            else:
                                enemy.take_damage(10)
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
        player.render(screen)
        if npc_visible:
            npc.render(screen)

        items = items_per_level[current_level]
        for item in items:
            item.render(screen)
            if item.active and player.rect.colliderect(item.rect) and not item.rising:
                if hasattr(item, "sheet"):
                    coin_count += 1
                    item.active = False
                else:
                    player.health = min(player.health + 50, 100)
                    item.active = False

        font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "DejaVuSans.ttf")
        font = pygame.font.Font(font_path, 32)
        coin_text = font.render(f"Xu: {coin_count}", True, (255, 215, 0))
        screen.blit(coin_text, (700, 20))

        retry_rect = None
        btn_rect = None
        play_rect = None
        if player.health <= 0:
            game_over = True
            retry_rect, btn_rect, weapon_rects = draw_game_over(screen, show_weapon_select)
        elif show_start_screen:
            play_rect, btn_rect, weapon_rects = draw_start_screen(screen, show_weapon_select)

        # Luôn render dialogue system trên cùng
        dialogue_system.render(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()