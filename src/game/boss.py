import os
import random
import pygame


class Boss:
    """Boss cơ bản với chạy + tấn công 1 (đòn giáo/lửa), giống phương pháp crop như Player.

    - Cắt spritesheet: chia theo frame_count (một hàng) rồi crop mask bounding box để bỏ viền trong suốt
    - Scale về target_height rồi đóng gói canvas cùng chiều cao, căn giữa ngang, giữ đáy
    - State: run / attack1
    - Attack1 xuất hiện ngẫu nhiên mỗi 3–5s, hitbox ở frame thứ 3 (index 2)
    """

    def __init__(
        self,
        x: int,
        y: int,
        patrol_range=(100, 700),
        target_height: int = 120,
        frame_count: int = 4,
        attack_frame_count: int = 6,
        trim_alpha_threshold: int = 16,
        baseline_offset: int = 1,
        attack_drop_frames: tuple[int, ...] = (),
    ):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        boss_dir = os.path.join(base_dir, "assets", "Boss")
        
        # Load run frames từ các file riêng biệt (dragon_knight_run1.png, run2.png, ...)
        self.frames_run = []
        for i in range(1, frame_count + 1):
            run_path = os.path.join(boss_dir, f"dragon_knight_run{i}.png")
            if os.path.exists(run_path):
                try:
                    img = pygame.image.load(run_path).convert_alpha()
                    # Scale về target_height
                    scale_ratio = target_height / img.get_height()
                    new_w = max(1, int(img.get_width() * scale_ratio))
                    scaled = pygame.transform.smoothscale(img, (new_w, target_height))
                    self.frames_run.append(scaled)
                except Exception:
                    pass
        
        # Fallback nếu không load được
        if not self.frames_run:
            # Thử load từ spritesheet cũ
            run_sheet_path = os.path.join(boss_dir, "dragon_knight_run1.png")
            if os.path.exists(run_sheet_path):
                self.frames_run = self._load_frames(
                    run_sheet_path,
                    target_height,
                    frame_count,
                    trim_alpha_threshold,
                    drop_indices=None,
                )
            else:
                raise FileNotFoundError(f"Không tìm thấy run frames: {boss_dir}")
        
        # Load attack1 frames từ các file riêng biệt (6 frames)
        # Tên file: dragon_knight_attack_1_1.png đến dragon_knight_attack_1_6.png
        self.frames_attack1 = []
        for i in range(1, 7):  # 6 frames attack1
            atk_path = os.path.join(boss_dir, f"dragon_knight_attack_1_{i}.png")
            if os.path.exists(atk_path):
                try:
                    img = pygame.image.load(atk_path).convert_alpha()
                    # Scale về target_height, giữ nguyên tỉ lệ
                    scale_ratio = target_height / img.get_height()
                    new_w = max(1, int(img.get_width() * scale_ratio))
                    scaled = pygame.transform.smoothscale(img, (new_w, target_height))
                    self.frames_attack1.append(scaled)
                except Exception as e:
                    print(f"Error loading attack1 frame {i}: {e}")
            else:
                print(f"Warning: File not found: {atk_path}")
        
        # Fallback cuối: dùng run nếu không có attack1
        if not self.frames_attack1:
            print("Warning: No attack1 frames found, using run frames as fallback")
            self.frames_attack1 = self.frames_run
        
        # Load attack2 frames từ các file riêng biệt (6 frames)
        # Tên file: dragon_knight_attack_2_1.png đến dragon_knight_attack_2_6.png
        self.frames_attack2 = []
        for i in range(1, 7):  # 6 frames attack2
            atk2_path = os.path.join(boss_dir, f"dragon_knight_attack_2_{i}.png")
            if os.path.exists(atk2_path):
                try:
                    img = pygame.image.load(atk2_path).convert_alpha()
                    # Scale về target_height, giữ nguyên tỉ lệ
                    scale_ratio = target_height / img.get_height()
                    new_w = max(1, int(img.get_width() * scale_ratio))
                    scaled = pygame.transform.smoothscale(img, (new_w, target_height))
                    self.frames_attack2.append(scaled)
                except Exception as e:
                    print(f"Error loading attack2 frame {i}: {e}")
            else:
                print(f"Warning: File not found: {atk2_path}")
        
        # Fallback: dùng attack1 nếu không có attack2
        if not self.frames_attack2:
            print("Warning: No attack2 frames found, using attack1 frames as fallback")
            self.frames_attack2 = self.frames_attack1
        
        # Load attack3 frames từ các file riêng biệt (8 frames)
        # Tên file: dragon_knight_attack_3_1.png đến dragon_knight_attack_3_8.png
        self.frames_attack3 = []
        for i in range(1, 9):  # 8 frames attack3
            atk3_path = os.path.join(boss_dir, f"dragon_knight_attack_3_{i}.png")
            if os.path.exists(atk3_path):
                try:
                    img = pygame.image.load(atk3_path).convert_alpha()
                    # Scale về target_height, giữ nguyên tỉ lệ
                    scale_ratio = target_height / img.get_height()
                    new_w = max(1, int(img.get_width() * scale_ratio))
                    scaled = pygame.transform.smoothscale(img, (new_w, target_height))
                    self.frames_attack3.append(scaled)
                except Exception as e:
                    print(f"Error loading attack3 frame {i}: {e}")
            else:
                print(f"Warning: File not found: {atk3_path}")
        
        # Fallback: dùng attack2 nếu không có attack3
        if not self.frames_attack3:
            print("Warning: No attack3 frames found, using attack2 frames as fallback")
            self.frames_attack3 = self.frames_attack2
        
        # Load firebreath frames từ các file riêng biệt
        self.frames_firebreath = []
        for i in range(1, attack_frame_count + 1):
            fb_path = os.path.join(boss_dir, f"dragon_knight_firebreath{i}.png")
            if os.path.exists(fb_path):
                try:
                    img = pygame.image.load(fb_path).convert_alpha()
                    scale_ratio = target_height / img.get_height()
                    new_w = max(1, int(img.get_width() * scale_ratio))
                    scaled = pygame.transform.smoothscale(img, (new_w, target_height))
                    self.frames_firebreath.append(scaled)
                except Exception:
                    pass
        
        # Fallback: dùng attack1 nếu không có firebreath
        if not self.frames_firebreath:
            self.frames_firebreath = self.frames_attack1
        
        # Đồng bộ attack1, attack2, attack3 và firebreath có CÙNG width (vì đã crop cùng kích thước)
        # Run frames giữ width riêng của nó
        if self.frames_attack1 and self.frames_attack2 and self.frames_attack3 and self.frames_firebreath:
            # Tìm width chung cho attack1, attack2, attack3 và firebreath
            atk_fb_frames = self.frames_attack1 + self.frames_attack2 + self.frames_attack3 + self.frames_firebreath
            max_w_atk_fb = max(f.get_width() for f in atk_fb_frames)
            
            # Chuẩn hóa attack1 - căn giữa ngang, căn đáy
            uniform_atk = []
            for f in self.frames_attack1:
                canvas = pygame.Surface((max_w_atk_fb, target_height), pygame.SRCALPHA)
                off_x = (max_w_atk_fb - f.get_width()) // 2
                off_y = target_height - f.get_height()
                canvas.blit(f, (off_x, off_y))
                uniform_atk.append(canvas)
            self.frames_attack1 = uniform_atk
            
            # Chuẩn hóa attack2 - căn giữa ngang, căn đáy
            uniform_atk2 = []
            for f in self.frames_attack2:
                canvas = pygame.Surface((max_w_atk_fb, target_height), pygame.SRCALPHA)
                off_x = (max_w_atk_fb - f.get_width()) // 2
                off_y = target_height - f.get_height()
                canvas.blit(f, (off_x, off_y))
                uniform_atk2.append(canvas)
            self.frames_attack2 = uniform_atk2
            
            # Chuẩn hóa attack3 - căn giữa ngang, căn đáy
            uniform_atk3 = []
            for f in self.frames_attack3:
                canvas = pygame.Surface((max_w_atk_fb, target_height), pygame.SRCALPHA)
                off_x = (max_w_atk_fb - f.get_width()) // 2
                off_y = target_height - f.get_height()
                canvas.blit(f, (off_x, off_y))
                uniform_atk3.append(canvas)
            self.frames_attack3 = uniform_atk3
            
            # Chuẩn hóa firebreath - căn giữa ngang, căn đáy
            uniform_fb = []
            for f in self.frames_firebreath:
                canvas = pygame.Surface((max_w_atk_fb, target_height), pygame.SRCALPHA)
                off_x = (max_w_atk_fb - f.get_width()) // 2
                off_y = target_height - f.get_height()
                canvas.blit(f, (off_x, off_y))
                uniform_fb.append(canvas)
            self.frames_firebreath = uniform_fb
        
        # Chuẩn hóa run frames (giữ width riêng)
        if self.frames_run:
            max_w_run = max(f.get_width() for f in self.frames_run)
            uniform_run = []
            for f in self.frames_run:
                canvas = pygame.Surface((max_w_run, target_height), pygame.SRCALPHA)
                off_x = (max_w_run - f.get_width()) // 2
                canvas.blit(f, (off_x, 0))
                uniform_run.append(canvas)
            self.frames_run = uniform_run

        self.baseline_offset = baseline_offset

        # Animation state
        self.state = "run"
        self.frames = self.frames_run
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 90

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Patrol
        self.speed = 2
        self.facing_right = True
        self.patrol_min, self.patrol_max = patrol_range

        # Physics
        self.vel_y = 0
        self.on_ground = False

        # Combat / health
        self.max_health = 500
        self.health = self.max_health
        self.is_dead = False
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 250

        # Attack logic - combo liên tiếp attack1 → attack2 → attack3 → firebreath
        self.next_attack_timer = random.randint(3000, 5000)
        self.in_combo = False  # Đang trong combo hay không
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False
        self._attack_started = False
        
        # Attack1 (đòn đánh 1 - 6 frames): gây sát thương ở frame 3 (index 2)
        self.attack1_hit_frame = 2
        self.attack1_damage = 20
        
        # Attack2 (đòn đánh 2 - 6 frames): gây sát thương ở frame 3 (index 2)
        self.attack2_hit_frame = 2
        self.attack2_damage = 25
        
        # Attack3 (đòn đánh 3 - 8 frames): gây sát thương ở frame 4 (index 3)
        self.attack3_hit_frame = 3
        self.attack3_damage = 30
        
        # Firebreath skill: gây sát thương ở frame 5-8 (index 4-7)
        self.skill_hit_frames = tuple(range(4, 8)) if len(self.frames_firebreath) >= 8 else tuple(range(2, min(6, len(self.frames_firebreath))))
        self.skill_damage = 50

    def _load_frames(
        self,
        sheet_path: str,
        target_height: int,
        frame_count: int,
        trim_alpha_threshold: int,
        drop_indices: list[int] | None = None,
    ) -> list[pygame.Surface]:
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_h = sheet.get_height()
        sheet_w = sheet.get_width()
        frame_count = max(1, int(frame_count))
        frame_w = sheet_w // frame_count if frame_count > 0 else sheet_w
        if frame_w <= 0:
            frame_w = sheet_w
            frame_count = 1

        processed = []
        for i in range(frame_count):
            if drop_indices and i in drop_indices:
                continue
            x = i * frame_w
            if x + frame_w > sheet_w:
                break
            # Lấy frame gốc từ sheet (KHÔNG crop để giữ kích thước lớn)
            raw = sheet.subsurface(pygame.Rect(x, 0, frame_w, sheet_h)).copy()
            
            # Kiểm tra frame rỗng
            mask = pygame.mask.from_surface(raw)
            try:
                nonzero = mask.count()
            except Exception:
                nonzero = 1
            if nonzero == 0:
                continue
            
            # Scale trực tiếp từ raw frame (giữ nguyên tỉ lệ gốc)
            scale_ratio = target_height / raw.get_height()
            new_w = max(1, int(raw.get_width() * scale_ratio))
            scaled = pygame.transform.smoothscale(raw, (new_w, target_height))
            processed.append(scaled)

        if not processed:
            raw = sheet.subsurface(pygame.Rect(0, 0, frame_w, sheet_h)).copy()
            scale_ratio = target_height / raw.get_height()
            new_w = int(raw.get_width() * scale_ratio)
            processed = [pygame.transform.smoothscale(raw, (new_w, target_height))]

        # Đồng bộ width giữa các frame
        max_w = max(f.get_width() for f in processed)
        uniform = []
        for f in processed:
            canvas = pygame.Surface((max_w, target_height), pygame.SRCALPHA)
            off_x = (max_w - f.get_width()) // 2
            canvas.blit(f, (off_x, 0))
            uniform.append(canvas)
        return uniform

    def place_on_ground(self, platforms):
        if not platforms:
            return
        candidate = None
        for p in platforms:
            if self.rect.right > p.rect.left and self.rect.left < p.rect.right:
                if candidate is None or p.rect.top < candidate.rect.top:
                    candidate = p
        if candidate is None:
            candidate = max(platforms, key=lambda pl: pl.rect.top)
        self.rect.bottom = candidate.rect.top
        self.vel_y = 0
        self.on_ground = True

    def take_damage(self, amount: int, knockback_dir: int = 0):
        if self.is_dead or self.invincible:
            return
        self.health -= max(0, amount)
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
        else:
            self.invincible = True
            self.invincible_timer = self.invincible_duration
            if knockback_dir != 0:
                self.rect.x += 6 * knockback_dir

    def _start_attack1(self):
        """Bắt đầu đòn đánh 1 - phần đầu của combo"""
        self.state = "attack1"
        self.frames = self.frames_attack1
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 80
        self._attack_started = True
        self.in_combo = True  # Đánh dấu đang trong combo
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False

    def _start_attack2(self):
        """Bắt đầu đòn đánh 2 - phần thứ 2 của combo"""
        self.state = "attack2"
        self.frames = self.frames_attack2
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 80
        self._attack_started = True
        # in_combo vẫn = True
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False

    def _start_attack3(self):
        """Bắt đầu đòn đánh 3 - phần thứ 3 của combo"""
        self.state = "attack3"
        self.frames = self.frames_attack3
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 80
        self._attack_started = True
        # in_combo vẫn = True
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False

    def _start_firebreath(self):
        """Bắt đầu skill phun lửa - phần thứ 4 của combo"""
        self.state = "firebreath"
        self.frames = self.frames_firebreath
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 150
        self._attack_started = True
        # in_combo vẫn = True
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False

    def _end_combo(self):
        """Kết thúc combo và quay về run"""
        self.state = "run"
        self.frames = self.frames_run
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 90
        self.next_attack_timer = random.randint(3000, 5000)
        self._attack_started = False
        self.in_combo = False
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False

    def update(self, platforms, dt_ms: int = 16):
        if self.is_dead:
            return

        # Invincibility timer
        if self.invincible:
            self.invincible_timer -= dt_ms
            if self.invincible_timer <= 0:
                self.invincible = False

        # Attack cooldown (only while running)
        if self.state == "run":
            self.next_attack_timer -= dt_ms
            if self.next_attack_timer <= 0:
                # Bắt đầu combo: attack1 trước
                self._start_attack1()

        # Animation advance
        self.anim_timer += dt_ms
        frame_advanced = False
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            frame_advanced = True

        # Preserve position when frame size changes
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx
        self.image = self.frames[self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.centerx = old_centerx
        self.rect.bottom = old_bottom

        # Patrol movement (disabled during attack)
        if self.state == "run":
            dx = self.speed if self.facing_right else -self.speed
            self.rect.x += dx
            if self.rect.left <= self.patrol_min:
                self.rect.left = self.patrol_min
                self.facing_right = True
            elif self.rect.right >= self.patrol_max:
                self.rect.right = self.patrol_max
                self.facing_right = False

        # Gravity and ground collision
        self.vel_y += 1
        self.rect.y += self.vel_y
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect) and self.vel_y >= 0:
                if self.rect.bottom > p.rect.top and self.rect.centery < p.rect.centery:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    break

        # Attack1 hitbox logic (đòn đánh thường - frame 3, index 2)
        if self.state == "attack1":
            if frame_advanced and self.frame_index == self.attack1_hit_frame and not self.attack_hitbox:
                # Hitbox nằm trong vùng lửa/năng lượng của animation
                width = 158
                height = 73
                
                if self.facing_right:
                    # Hitbox bắt đầu từ giữa boss và kéo dài ra phía trước
                    offset_x = -30  # Bắt đầu hơi trước boss một chút
                    offset_y = 30  # Hạ xuống thấp hơn
                    hb_x = self.rect.centerx + offset_x
                    hb_y = self.rect.centery - height // 2 + offset_y
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                else:
                    # Hitbox cho hướng trái
                    offset_x = -30
                    offset_y = 30  # Hạ xuống thấp hơn
                    hb_x = self.rect.centerx - width - offset_x
                    hb_y = self.rect.centery - height // 2 + offset_y
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                
                self.attack_hitbox = rect
                self.attack_hitbox_timer = 200
                self.attack_hitbox_did_damage = False

            if self.attack_hitbox_timer > 0:
                self.attack_hitbox_timer -= dt_ms
                if self.attack_hitbox_timer <= 0:
                    self.attack_hitbox = None
                    self.attack_hitbox_did_damage = False

            # End attack1 → chuyển sang attack2 NGAY LẬP TỨC
            if frame_advanced and self.frame_index == 0 and self._attack_started:
                self._start_attack2()  # Combo: attack1 → attack2
        
        # Attack2 hitbox logic (đòn đánh 2 - frame 3, index 2)
        elif self.state == "attack2":
            if frame_advanced and self.frame_index == self.attack2_hit_frame and not self.attack_hitbox:
                # Hitbox nằm trong vùng lửa/năng lượng của animation
                width = 158
                height = 73
                
                if self.facing_right:
                    # Hitbox bắt đầu từ giữa boss và kéo dài ra phía trước
                    offset_x = -30
                    offset_y = 30
                    hb_x = self.rect.centerx + offset_x
                    hb_y = self.rect.centery - height // 2 + offset_y
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                else:
                    # Hitbox cho hướng trái
                    offset_x = -30
                    offset_y = 30
                    hb_x = self.rect.centerx - width - offset_x
                    hb_y = self.rect.centery - height // 2 + offset_y
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                
                self.attack_hitbox = rect
                self.attack_hitbox_timer = 200
                self.attack_hitbox_did_damage = False

            if self.attack_hitbox_timer > 0:
                self.attack_hitbox_timer -= dt_ms
                if self.attack_hitbox_timer <= 0:
                    self.attack_hitbox = None
                    self.attack_hitbox_did_damage = False

            # End attack2 → chuyển sang attack3 NGAY LẬP TỨC
            if frame_advanced and self.frame_index == 0 and self._attack_started:
                self._start_attack3()  # Combo: attack2 → attack3
        
        # Attack3 hitbox logic (đòn đánh 3 - frame 4, index 3) - HITBOX RỘNG HƠN
        elif self.state == "attack3":
            if frame_advanced and self.frame_index == self.attack3_hit_frame and not self.attack_hitbox:
                # Hitbox rộng hơn attack 1 và 2
                width = 200  # Rộng hơn (158 → 200)
                height = 85   # Cao hơn (73 → 85)
                
                if self.facing_right:
                    # Hitbox bắt đầu từ giữa boss và kéo dài ra phía trước
                    offset_x = -30
                    offset_y = 30
                    hb_x = self.rect.centerx + offset_x
                    hb_y = self.rect.centery - height // 2 + offset_y
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                else:
                    # Hitbox cho hướng trái
                    offset_x = -30
                    offset_y = 30
                    hb_x = self.rect.centerx - width - offset_x
                    hb_y = self.rect.centery - height // 2 + offset_y
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                
                self.attack_hitbox = rect
                self.attack_hitbox_timer = 200
                self.attack_hitbox_did_damage = False

            if self.attack_hitbox_timer > 0:
                self.attack_hitbox_timer -= dt_ms
                if self.attack_hitbox_timer <= 0:
                    self.attack_hitbox = None
                    self.attack_hitbox_did_damage = False

            # End attack3 → chuyển sang firebreath NGAY LẬP TỨC
            if frame_advanced and self.frame_index == 0 and self._attack_started:
                self._start_firebreath()  # Combo: attack3 → firebreath
        
        # Firebreath hitbox logic (frames 5-8, index 4-7)
        elif self.state == "firebreath":
            # Create/update hitbox on firebreath damage frames
            if self.frame_index in self.skill_hit_frames:
                # Hitbox đồng bộ chính xác với vị trí lửa trong sprite
                width = 140
                height = 60
                
                # Lửa phun ra gần sát boss hơn
                if self.facing_right:
                    # Lửa phun về phía bên phải từ vị trí miệng boss
                    hb_x = self.rect.centerx  # Bắt đầu ngay từ center boss
                    hb_y = self.rect.centery + 10  # Hơi thấp hơn center một chút
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                else:
                    # Lửa phun về phía bên trái
                    hb_x = self.rect.centerx - width  # Bắt đầu ngay từ center sang trái
                    hb_y = self.rect.centery + 10  # Hơi thấp hơn center một chút
                    rect = pygame.Rect(hb_x, hb_y, width, height)
                
                self.attack_hitbox = rect
                self.attack_hitbox_timer = self.anim_speed + 10
                if frame_advanced:
                    self.attack_hitbox_did_damage = False  # Reset mỗi frame mới

            # Clear hitbox if not on damage frames
            if self.frame_index not in self.skill_hit_frames:
                if self.attack_hitbox:
                    self.attack_hitbox = None
                    self.attack_hitbox_did_damage = False

            if self.attack_hitbox_timer > 0:
                self.attack_hitbox_timer -= dt_ms
                if self.attack_hitbox_timer <= 0:
                    self.attack_hitbox = None

            # End firebreath → kết thúc combo
            if frame_advanced and self.frame_index == 0 and self._attack_started:
                self._end_combo()

    def render(self, screen):
        if self.is_dead:
            return
        # Vẽ sprite của boss
        screen.blit(self.image, self.rect.topleft)
        # (Đã gỡ bỏ vẽ hitbox debug theo yêu cầu)

    def render_healthbar(self, screen):
        bar_w, bar_h = 300, 18
        x = (screen.get_width() - bar_w) // 2
        y = 40  # đẩy thanh máu xuống thấp hơn một chút
        # Name label above the health bar
        try:
            font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "DejaVuSans.ttf")
            name_font = pygame.font.Font(font_path, 28)
        except Exception:
            name_font = pygame.font.SysFont(None, 28)
        name_text = "QUỶ LỬA"
        name_surf = name_font.render(name_text, True, (255, 180, 60))
        name_rect = name_surf.get_rect(center=(screen.get_width() // 2, y - 18))
        # Optional background box for readability
        pad_x, pad_y = 14, 6
        box_rect = pygame.Rect(name_rect.left - pad_x//2, name_rect.top - pad_y//2,
                                name_rect.width + pad_x, name_rect.height + pad_y)
        box_surf = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        box_surf.fill((30, 30, 30, 160))
        pygame.draw.rect(box_surf, (255, 140, 40), box_surf.get_rect(), 2, border_radius=6)
        screen.blit(box_surf, box_rect.topleft)
        screen.blit(name_surf, name_rect)
        pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(x, y, bar_w, bar_h), border_radius=6)
        ratio = 0 if self.max_health == 0 else self.health / self.max_health
        pygame.draw.rect(screen, (200, 30, 30), pygame.Rect(x + 2, y + 2, int((bar_w - 4) * ratio), bar_h - 4), border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(x, y, bar_w, bar_h), 2, border_radius=6)

