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
        
        # Load run frames từ các file riêng biệt (dragon_knight_run1.png, run2.png, ...)
        self.frames_run = []
        boss_dir = os.path.join(base_dir, "assets", "Boss")
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
        
        # Đồng bộ width cho run frames
        if self.frames_run:
            max_w = max(f.get_width() for f in self.frames_run)
            uniform_run = []
            for f in self.frames_run:
                canvas = pygame.Surface((max_w, target_height), pygame.SRCALPHA)
                off_x = (max_w - f.get_width()) // 2
                canvas.blit(f, (off_x, 0))
                uniform_run.append(canvas)
            self.frames_run = uniform_run
        
        
        # Load attack frames từ spritesheet
        attack1_sheet_path = os.path.join(boss_dir, "dragon_knight_attack_11.png")
        if not os.path.exists(attack1_sheet_path):
            attack1_sheet_path = None

        self.baseline_offset = baseline_offset
        # Load attack frames (firebreath từ các file riêng)
        self.frames_attack1 = []
        if attack1_sheet_path:
            self.frames_attack1 = self._load_frames(
                attack1_sheet_path,
                target_height,
                attack_frame_count,
                trim_alpha_threshold,
                drop_indices=list(attack_drop_frames) if attack_drop_frames else None,
            )
        
        # Thử load firebreath từ các file riêng biệt (dragon_knight_firebreath1.png đến 11.png)
        if not self.frames_attack1:
            for i in range(1, attack_frame_count + 1):
                if attack_drop_frames and (i-1) in attack_drop_frames:
                    continue
                fb_path = os.path.join(boss_dir, f"dragon_knight_firebreath{i}.png")
                if os.path.exists(fb_path):
                    try:
                        img = pygame.image.load(fb_path).convert_alpha()
                        scale_ratio = target_height / img.get_height()
                        new_w = max(1, int(img.get_width() * scale_ratio))
                        scaled = pygame.transform.smoothscale(img, (new_w, target_height))
                        self.frames_attack1.append(scaled)
                    except Exception:
                        pass
        
        # Fallback: dùng run nếu không có attack
        if not self.frames_attack1:
            self.frames_attack1 = self.frames_run
        
        # Đồng bộ width cho attack frames
        if self.frames_attack1:
            max_w_atk = max(f.get_width() for f in self.frames_attack1)
            uniform_atk = []
            for f in self.frames_attack1:
                canvas = pygame.Surface((max_w_atk, target_height), pygame.SRCALPHA)
                off_x = (max_w_atk - f.get_width()) // 2
                canvas.blit(f, (off_x, 0))
                uniform_atk.append(canvas)
            self.frames_attack1 = uniform_atk

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

        # Attack logic
        self.next_attack_timer = random.randint(3000, 5000)
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False
        self._attack_started = False
        
        # Firebreath skill: gây sát thương ở frame 5-8 (index 4-7)
        self.skill_hit_frames = tuple(range(4, 8)) if len(self.frames_attack1) >= 8 else tuple(range(2, min(6, len(self.frames_attack1))))
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
        self.state = "attack1"
        self.frames = self.frames_attack1
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 80
        self._attack_started = True
        self.attack_hitbox = None
        self.attack_hitbox_timer = 0
        self.attack_hitbox_did_damage = False

    def _end_attack1(self):
        self.state = "run"
        self.frames = self.frames_run
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 90
        self.next_attack_timer = random.randint(3000, 5000)
        self._attack_started = False
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

        # Firebreath attack hitbox logic (frames 5-8, index 4-7)
        if self.state == "attack1":
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

            # End attack when loop completes
            if frame_advanced and self.frame_index == 0 and self._attack_started:
                self._end_attack1()

    def render(self, screen, debug=False):
        if self.is_dead:
            return
        screen.blit(self.image, self.rect.topleft)
        
        # Debug: Hiển thị hitbox firebreath
        if debug and self.attack_hitbox:
            pygame.draw.rect(screen, (255, 100, 0, 128), self.attack_hitbox, 2)
            # Vẽ điểm center của boss để tham khảo
            pygame.draw.circle(screen, (0, 255, 0), self.rect.center, 3)

    def render_healthbar(self, screen):
        bar_w, bar_h = 300, 18
        x = (screen.get_width() - bar_w) // 2
        y = 20
        pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(x, y, bar_w, bar_h), border_radius=6)
        ratio = 0 if self.max_health == 0 else self.health / self.max_health
        pygame.draw.rect(screen, (200, 30, 30), pygame.Rect(x + 2, y + 2, int((bar_w - 4) * ratio), bar_h - 4), border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(x, y, bar_w, bar_h), 2, border_radius=6)

