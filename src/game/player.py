import pygame
import os
import time
from game.fireball import Fireball
from game.config import GAME_SETTINGS
from game.config import GAME_SETTINGS


class Player:
    def __init__(self, x, y):
        self.width = 48
        self.height = 55
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.facing_right = True

        self.vel_y = 0
        self.on_ground = False
        self.health = 100
        self.invincible = False
        self.invincible_start = 0
        self.hit_head = False
        self.last_head_platform = None
        self.direction = 1
        self.projectiles = []
        self.energy = 0
        self.special_active = False
        self.special_timer = 0
        self.special_direction = 1
        
        # Input timing để tránh nhập nhảy
        self.last_jump_time = 0
        self.jump_cooldown = GAME_SETTINGS["JUMP_COOLDOWN"]
        self.movement_speed = GAME_SETTINGS["MOVEMENT_SPEED"]
        self.jump_speed = GAME_SETTINGS["JUMP_SPEED"]

        self.sprites_walk = []
        self.sprites_stand = []
        self.bboxes_walk = []
        self.bboxes_stand = []
        self.frame_offsets_walk = []
        self.frame_offsets_stand = []
        self.sprite_jump = None
        self.sprite_fall = None
        self.bbox_jump = None
        self.bbox_fall = None
        self.frame_offset_jump = (0, 0)
        self.frame_offset_fall = (0, 0)
        self.sprites_attack1 = []
        self.bboxes_attack1 = []
        self.frame_offsets_attack1 = []
        self.sprites_attack2 = []
        self.bboxes_attack2 = []
        self.frame_offsets_attack2 = []
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_timer = 0
        self.attack_hitbox = None
        self.attack_stage = 0
        self.attack_wait_timer = 0
        self.attack_frame_speed = 6
        self.attack_first_frame_speed = 18
        self.attack_anim_counter = 0
        self.attack1_effect_frames = []
        self.attack2_effect_frames = []
        self.attack1_effect_index = 0
        self.attack2_effect_index = 0
        self.attack1_effect_timer = 1
        self.attack2_effect_timer = 2
        self.weapon_type = "Martial"

        self.machate_sprites = [[] for _ in range(4)]
        self.machate_bboxes = [[] for _ in range(4)]
        self.machate_offsets = [[] for _ in range(4)]
        self.machate_attack_frame = 0
        self.machate_attack_stage = 0
        self.machate_attack_timer = 0
        self.machate_attack_anim_counter = 0
        self.machate_attack_queued = [False]*4
        self.machate_hitbox_timer = 0

        self.sprites_charge_magic = []
        self.bboxes_charge_magic = []
        self.frame_offsets_charge_magic = []
        self.charge_magic_frame = 0
        self.charge_magic_counter = 0
        self.charge_magic_speed = 7

        self.no_effect_frames = []
        self.no_effect_frame = 0
        self.no_effect_counter = 0
        self.no_effect_speed = 4

        self.true_midbottom = self.rect.midbottom

        self.load_sprites()
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_speed = 6
        self.is_walking = False
        self.is_jumping = False
        self.is_falling = False

        self.image = self.sprites_stand[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hitbox = self.rect.copy()
        self.attack_queued = False
        self.already_hit_enemies = set()
        self.attack_key_held = False
        self.is_charging_energy = False
        self.charge_start_time = 0
        self.max_energy = 100


    def load_sprites(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "Character")
        walk_path = os.path.join(assets_dir, "Characters-walk.png")
        walk_sheet = pygame.image.load(walk_path).convert_alpha()
        stand_path = os.path.join(assets_dir, "Characters-stand.png")
        stand_sheet = pygame.image.load(stand_path).convert_alpha()
        jump_path = os.path.join(assets_dir, "Characters-jump.png")
        jump_img = pygame.image.load(jump_path).convert_alpha()
        fall_path = os.path.join(assets_dir, "Characters-fall.png")
        fall_img = pygame.image.load(fall_path).convert_alpha()
        martial1_path = os.path.join(assets_dir, "Characters-martial1.png")
        martial1_sheet = pygame.image.load(martial1_path).convert_alpha()
        martial2_path = os.path.join(assets_dir, "Characters-martial2.png")
        martial2_sheet = pygame.image.load(martial2_path).convert_alpha()
        shield_path = os.path.join(assets_dir, "Characters-shield.png")
        self.shield_sheet = pygame.image.load(shield_path).convert_alpha()

        self.machate_sheets = []
        for i in range(1, 5):
            path = os.path.join(assets_dir, f"Characters-machete{i}.png")
            self.machate_sheets.append(pygame.image.load(path).convert_alpha())

        num_frames_walk = 6
        num_frames_stand = 6
        num_frames_attack = 6
        frame_width_walk = walk_sheet.get_width() // num_frames_walk
        frame_height_walk = walk_sheet.get_height()
        frame_width_stand = stand_sheet.get_width() // num_frames_stand
        frame_height_stand = stand_sheet.get_height()
        frame_width_attack = martial1_sheet.get_width() // num_frames_attack
        frame_height_attack = martial1_sheet.get_height()

        target_height = 55
        for i in range(num_frames_walk):
            crop_width = frame_width_walk - 20
            frame = walk_sheet.subsurface((i * frame_width_walk, 0, crop_width, frame_height_walk))
            mask = pygame.mask.from_surface(frame)
            rects = mask.get_bounding_rects()
            bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
            cropped_frame = frame.subsurface(bbox)
            scale_ratio = target_height / cropped_frame.get_height()
            new_width = int(cropped_frame.get_width() * scale_ratio)
            scaled_frame = pygame.transform.scale(cropped_frame, (new_width, target_height))
            self.sprites_walk.append(scaled_frame)
            scaled_bbox = pygame.Rect(0, 0, new_width, target_height)
            self.bboxes_walk.append(scaled_bbox)
            offset_x = (self.width - new_width) // 2
            offset_y = 0
            self.frame_offsets_walk.append((offset_x, offset_y))
        for i in range(num_frames_stand):
            crop_width = frame_width_stand - 20
            frame = stand_sheet.subsurface((i * frame_width_stand, 0, crop_width, frame_height_stand))
            mask = pygame.mask.from_surface(frame)
            rects = mask.get_bounding_rects()
            bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
            cropped_frame = frame.subsurface(bbox)
            scale_ratio = target_height / cropped_frame.get_height()
            new_width = int(cropped_frame.get_width() * scale_ratio)
            scaled_frame = pygame.transform.scale(cropped_frame, (new_width, target_height))
            self.sprites_stand.append(scaled_frame)
            scaled_bbox = pygame.Rect(0, 0, new_width, target_height)
            self.bboxes_stand.append(scaled_bbox)
            offset_x = (self.width - new_width) // 2
            offset_y = 0
            self.frame_offsets_stand.append((offset_x, offset_y))
        frame = martial1_sheet
        mask = pygame.mask.from_surface(frame)
        rects = mask.get_bounding_rects()
        bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
        cropped_frame = frame.subsurface(bbox)
        scale_ratio = 55 / cropped_frame.get_height()
        new_width = int(cropped_frame.get_width() * scale_ratio)
        scaled_frame = pygame.transform.scale(cropped_frame, (new_width, 55))
        self.sprites_attack1 = [scaled_frame]
        self.bboxes_attack1 = [pygame.Rect(0, 0, new_width, 55)]
        offset_x = (self.width - new_width) // 2
        offset_y = 0
        self.frame_offsets_attack1 = [(offset_x, offset_y)]
        frame_width_attack2 = martial2_sheet.get_width() // num_frames_attack
        frame_height_attack2 = martial2_sheet.get_height()
        for i in range(num_frames_attack):
            crop_width = frame_width_attack2
            frame = martial2_sheet.subsurface((i * frame_width_attack2, 0, crop_width, frame_height_attack2))
            mask = pygame.mask.from_surface(frame)
            rects = mask.get_bounding_rects()
            bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
            cropped_frame = frame.subsurface(bbox)
            scale_ratio = 55 / cropped_frame.get_height()
            new_width = int(cropped_frame.get_width() * scale_ratio)
            scaled_frame = pygame.transform.scale(cropped_frame, (new_width, 55))
            self.sprites_attack2.append(scaled_frame)
            scaled_bbox = pygame.Rect(0, 0, new_width, 55)
            self.bboxes_attack2.append(scaled_bbox)
            offset_x = (self.width - new_width) // 2
            offset_y = 0
            self.frame_offsets_attack2.append((offset_x, offset_y))
        num_frames_shield = 4
        frame_width_shield = self.shield_sheet.get_width() // num_frames_shield
        frame_height_shield = self.shield_sheet.get_height()
        self.sprites_shield_attack = []
        self.bboxes_shield_attack = []
        self.frame_offsets_shield_attack = []
        for i in range(num_frames_shield):
            crop_width = frame_width_shield
            frame = self.shield_sheet.subsurface((i * frame_width_shield, 0, crop_width, frame_height_shield))
            mask = pygame.mask.from_surface(frame)
            rects = mask.get_bounding_rects()
            bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
            cropped_frame = frame.subsurface(bbox)
            scale_ratio = 55 / cropped_frame.get_height()
            new_width = int(cropped_frame.get_width() * scale_ratio)
            scaled_frame = pygame.transform.scale(cropped_frame, (new_width, 55))
            self.sprites_shield_attack.append(scaled_frame)
            scaled_bbox = pygame.Rect(0, 0, new_width, 55)
            self.bboxes_shield_attack.append(scaled_bbox)
            offset_x = (self.width - new_width) // 2
            offset_y = 0
            self.frame_offsets_shield_attack.append((offset_x, offset_y))

        mask = pygame.mask.from_surface(jump_img)
        rects = mask.get_bounding_rects()
        bbox = rects[0] if rects else pygame.Rect(0, 0, jump_img.get_width(), jump_img.get_height())
        cropped = jump_img.subsurface(bbox)
        scale_ratio = 55 / cropped.get_height()
        new_width = int(cropped.get_width() * scale_ratio)
        self.sprite_jump = pygame.transform.scale(cropped, (new_width, 55))
        self.bbox_jump = pygame.Rect(0, 0, new_width, 55)
        self.frame_offset_jump = ((self.width - new_width) // 2, 0)
        mask = pygame.mask.from_surface(fall_img)
        rects = mask.get_bounding_rects()
        bbox = rects[0] if rects else pygame.Rect(0, 0, fall_img.get_width(), fall_img.get_height())
        cropped = fall_img.subsurface(bbox)
        scale_ratio = 55 / cropped.get_height()
        new_width = int(cropped.get_width() * scale_ratio)
        self.sprite_fall = pygame.transform.scale(cropped, (new_width, 55))
        self.bbox_fall = pygame.Rect(0, 0, new_width, 55)
        self.frame_offset_fall = ((self.width - new_width) // 2, 0)

        self.image = self.sprites_stand[0]
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.width = self.image.get_width()
        self.height = target_height
        self.bbox = self.bboxes_stand[0]
        self.hitbox = self.rect.copy()

        machate_frames = [5, 5, 5, 7]
        target_height = 55
        for idx, sheet in enumerate(self.machate_sheets):
            num_frames = machate_frames[idx]
            frame_width = sheet.get_width() // num_frames
            frame_height = sheet.get_height()
            for i in range(num_frames):
                frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                mask = pygame.mask.from_surface(frame)
                rects = mask.get_bounding_rects()
                bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
                cropped_frame = frame.subsurface(bbox)
                if idx == 2:
                    if i in [0, 1]:
                        scale_ratio = 70 / cropped_frame.get_height()
                        new_height = 70
                    elif i == 2:
                        scale_ratio = 95 / cropped_frame.get_height()
                        new_height = 95
                    elif i in [3, 4]:
                        scale_ratio = 58 / cropped_frame.get_height()
                        new_height = 58
                    else:
                        scale_ratio = target_height / cropped_frame.get_height()
                        new_height = target_height
                elif idx == 1 and i in [0, 1]:
                    scale_ratio = 55 / cropped_frame.get_height()
                    new_height = 55
                elif idx == 1 and i == 2:
                    scale_ratio = 78 / cropped_frame.get_height()
                    new_height = 78
                elif idx in [1, 2]:
                    scale_ratio = (target_height + 10) / cropped_frame.get_height()
                    new_height = target_height + 10
                else:
                    scale_ratio = target_height / cropped_frame.get_height()
                    new_height = target_height
                new_width = int(cropped_frame.get_width() * scale_ratio)
                scaled_frame = pygame.transform.scale(cropped_frame, (new_width, new_height))
                self.machate_sprites[idx].append(scaled_frame)
                scaled_bbox = pygame.Rect(0, 0, new_width, new_height)
                self.machate_bboxes[idx].append(scaled_bbox)
                offset_x = (self.width - new_width) // 2
                if idx == 2:
                    offset_y = -(new_height - target_height)
                elif idx == 1 and i in [0, 1]:
                    offset_y = -(new_height - target_height)
                elif idx == 1 and i == 2:
                    offset_y = -(new_height - target_height)
                elif idx in [1, 2]:
                    offset_y = -(new_height - target_height)
                else:
                    offset_y = 0
                self.machate_offsets[idx].append((offset_x, offset_y))

        # Load magic charge animation (Characters-magic1.png)
        magic_charge_path = os.path.join(assets_dir, "Characters-magic1.png")
        if os.path.exists(magic_charge_path):
            magic_charge_sheet = pygame.image.load(magic_charge_path).convert_alpha()
            num_frames_charge = 4
            frame_width_charge = magic_charge_sheet.get_width() // num_frames_charge
            frame_height_charge = magic_charge_sheet.get_height()
            target_height = 55
            for i in range(num_frames_charge):
                frame = magic_charge_sheet.subsurface((i * frame_width_charge, 0, frame_width_charge, frame_height_charge))
                mask = pygame.mask.from_surface(frame)
                rects = mask.get_bounding_rects()
                bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
                cropped_frame = frame.subsurface(bbox)
                scale_ratio = target_height / cropped_frame.get_height()
                new_width = int(cropped_frame.get_width() * scale_ratio)
                scaled_frame = pygame.transform.scale(cropped_frame, (new_width, target_height))
                self.sprites_charge_magic.append(scaled_frame)
                scaled_bbox = pygame.Rect(0, 0, new_width, target_height)
                self.bboxes_charge_magic.append(scaled_bbox)
                offset_x = (self.width - new_width) // 2
                offset_y = 0
                self.frame_offsets_charge_magic.append((offset_x, offset_y))
        else:
            # Nếu file không tồn tại, tạo frame mặc định để tránh lỗi
            for i in range(4):
                dummy = pygame.Surface((48, 55), pygame.SRCALPHA)
                dummy.fill((0, 0, 255, 128))
                self.sprites_charge_magic.append(dummy)
                self.bboxes_charge_magic.append(pygame.Rect(0, 0, 48, 55))
                self.frame_offsets_charge_magic.append((0, 0))

        # Load magic2 animation (Characters-magic2.png)
        magic2_path = os.path.join(assets_dir, "Characters-magic2.png")
        self.sprites_magic2 = []
        self.magic2_frame = 0
        self.magic2_counter = 0
        self.magic2_speed = 20
        if os.path.exists(magic2_path):
            magic2_sheet = pygame.image.load(magic2_path).convert_alpha()
            num_frames_magic2 = 5
            frame_width_magic2 = magic2_sheet.get_width() // num_frames_magic2
            frame_height_magic2 = magic2_sheet.get_height()
            target_height = 55
            for i in range(num_frames_magic2):
                frame = magic2_sheet.subsurface((i * frame_width_magic2, 0, frame_width_magic2, frame_height_magic2))
                mask = pygame.mask.from_surface(frame)
                rects = mask.get_bounding_rects()
                bbox = rects[0] if rects else pygame.Rect(0, 0, frame.get_width(), frame.get_height())
                cropped_frame = frame.subsurface(bbox)
                scale_ratio = target_height / cropped_frame.get_height()
                new_width = int(cropped_frame.get_width() * scale_ratio)
                scaled_frame = pygame.transform.scale(cropped_frame, (new_width, target_height))
                self.sprites_magic2.append(scaled_frame)
        else:
            for i in range(5):
                dummy = pygame.Surface((48, 55), pygame.SRCALPHA)
                dummy.fill((255, 0, 255, 128))
                self.sprites_magic2.append(dummy)

        effect_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "effect")
        no_path = os.path.join(effect_dir, "no.png")
        if os.path.exists(no_path):
            no_sheet = pygame.image.load(no_path).convert_alpha()
            num_no_frames = 4
            no_w = no_sheet.get_width() // num_no_frames
            no_h = no_sheet.get_height()
            for i in range(num_no_frames):
                frame = no_sheet.subsurface((i * no_w, 0, no_w, no_h))
                scale_h = 80
                scale_w = int(frame.get_width() * (scale_h / frame.get_height()))
                frame = pygame.transform.scale(frame, (scale_w, scale_h))
                self.no_effect_frames.append(frame)
        else:
            for i in range(4):
                dummy = pygame.Surface((80, 80), pygame.SRCALPHA)
                dummy.fill((0, 255, 255, 80))
                self.no_effect_frames.append(dummy)

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.hitbox = self.rect.copy()

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        moving = False

        # --- Magic charge logic ---
        if self.weapon_type == "Magic":
            # Chỉ cho gồng khi đang đứng trên mặt đất
            if keys[pygame.K_x] and self.on_ground:
                if not self.is_charging_energy:
                    self.is_charging_energy = True
                    self.charge_start_time = time.time()
                    self.charge_magic_frame = 0
                    self.charge_magic_counter = 0
            else:
                if self.is_charging_energy:
                    self.is_charging_energy = False

            if self.is_charging_energy:
                # Animation gồng nộ
                self.charge_magic_counter += 1
                if self.charge_magic_counter >= self.charge_magic_speed:
                    self.charge_magic_frame = (self.charge_magic_frame + 1) % len(self.sprites_charge_magic)
                    self.charge_magic_counter = 0

                self.energy = min(self.max_energy, self.energy + 0.4)
                self.is_walking = False
                self.is_jumping = False
                self.is_falling = False
                self.is_attacking = False
                self.attack_stage = 0
                self.attack_queued = False
                self.vel_y = 0
                # Đặt frame gồng nộ
                self.image = self.sprites_charge_magic[self.charge_magic_frame]
                self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
                self.bbox = self.bboxes_charge_magic[self.charge_magic_frame]
                self.hitbox = self.rect.copy()
                # Hiệu ứng nộ
                self.no_effect_counter += 1
                if self.no_effect_counter >= self.no_effect_speed:
                    self.no_effect_frame = (self.no_effect_frame + 1) % len(self.no_effect_frames)
                    self.no_effect_counter = 0
                return
        # --- End Magic charge logic ---

        if self.is_attacking and self.weapon_type == "Shield":
            self.attack_anim_counter += 1
            if self.attack_anim_counter >= self.attack_frame_speed:
                if self.attack_frame < len(self.sprites_shield_attack) - 1:
                    self.attack_frame += 1
                    self.attack_anim_counter = 0
                    self.update_attack_hitbox()
            if self.attack_frame >= len(self.sprites_shield_attack) - 1:
                if not self.attack_key_held:
                    self.is_attacking = False
                    self.attack_hitbox = None
                    self.attack_stage = 0
            else:
                self.attack_timer -= 1

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            old_y = self.rect.y
            self.rect.y += self.vel_y

            self.on_ground = False
            self.hit_head = False
            self.last_head_platform = None

            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    if self.vel_y > 0 and old_y + self.rect.height <= plat.rect.top + 5:
                        self.rect.bottom = plat.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0 and old_y >= plat.rect.bottom - 5:
                        self.rect.top = plat.rect.bottom
                        self.vel_y = 0
                        self.hit_head = True
                        self.last_head_platform = plat

            if self.invincible and (time.time() - self.invincible_start > 1):
                self.invincible = False

            self.is_jumping = self.vel_y < 0 and not self.on_ground
            self.is_falling = self.vel_y > 0 and not self.on_ground

            return

        if keys[pygame.K_LEFT]:
            dx -= self.movement_speed
            moving = True
            self.facing_right = False
            self.direction = -1

        if keys[pygame.K_RIGHT]:
            dx += self.movement_speed
            moving = True
            self.facing_right = True
            self.direction = 1

        # Nhảy với cooldown để tránh nhập nhảy
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and self.on_ground and current_time - self.last_jump_time > self.jump_cooldown:
            self.vel_y = self.jump_speed
            self.on_ground = False
            self.last_jump_time = current_time



        if self.special_active:
            self.special_timer -= 1
            if self.special_timer <= 0:
                self.special_active = False

        if self.special_active:
            self.special_timer -= 1
            if self.special_timer <= 0:
                self.special_active = False
            # Update magic2 animation frame
            self.magic2_counter += 1
            if self.magic2_counter >= self.magic2_speed:
                self.magic2_frame = (self.magic2_frame + 1) % len(self.sprites_magic2)
                self.magic2_counter = 0

        self.rect.x += dx
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if dx > 0:
                    self.rect.right = plat.rect.left
                elif dx < 0:
                    self.rect.left = plat.rect.right

        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        old_y = self.rect.y
        self.rect.y += self.vel_y

        self.on_ground = False
        self.hit_head = False
        self.last_head_platform = None

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0 and old_y + self.rect.height <= plat.rect.top + 5:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0 and old_y >= plat.rect.bottom - 5:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0
                    self.hit_head = True
                    self.last_head_platform = plat

        if self.invincible and (time.time() - self.invincible_start > 1):
            self.invincible = False

        moving = dx != 0
        self.is_walking = moving
        if moving:
            self.frame_speed = 6
            self.frame_counter += 1
            if self.frame_counter >= self.frame_speed:
                self.current_frame = (self.current_frame + 1) % len(self.sprites_walk)
                self.frame_counter = 0
        elif not (self.is_attacking or self.is_jumping or self.is_falling):
            self.frame_speed = 7
            self.frame_counter += 1
            if self.frame_counter >= self.frame_speed:
                self.current_frame = (self.current_frame + 1) % len(self.sprites_stand)
                self.frame_counter = 0

        self.is_jumping = self.vel_y < 0 and not self.on_ground
        self.is_falling = self.vel_y > 0 and not self.on_ground

        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        old_midbottom = self.rect.midbottom
        if self.is_jumping:
            self.image = self.sprite_jump
            self.bbox = self.bbox_jump
            offset_x, offset_y = self.frame_offset_jump
        elif self.is_falling:
            self.image = self.sprite_fall
            self.bbox = self.bbox_fall
            offset_x, offset_y = self.frame_offset_fall
        elif self.is_walking:
            self.image = self.sprites_walk[self.current_frame]
            self.bbox = self.bboxes_walk[self.current_frame]
            offset_x, offset_y = self.frame_offsets_walk[self.current_frame]
        else:
            self.image = self.sprites_stand[self.current_frame]
            self.bbox = self.bboxes_stand[self.current_frame]
            offset_x, offset_y = self.frame_offsets_stand[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_midbottom

        hitbox_x = self.rect.x + offset_x
        hitbox_y = self.rect.y + offset_y

        self.hitbox = pygame.Rect(
            hitbox_x,
            hitbox_y,
            self.bbox.width,
            self.bbox.height
        )

        if self.is_attacking:
            if self.weapon_type == "Shield":
                self.attack_anim_counter += 1
                if self.attack_anim_counter >= self.attack_frame_speed:
                    self.attack_frame += 1
                    self.attack_anim_counter = 0
                    if self.attack_frame >= len(self.sprites_shield_attack):
                        self.is_attacking = False
                        self.attack_hitbox = None
                        self.attack_stage = 0
            elif self.weapon_type == "Machate":
                self.machate_attack_anim_counter += 1
                if self.machate_attack_anim_counter >= 9:
                    self.machate_attack_frame += 1
                    self.machate_attack_anim_counter = 0
                    if self.machate_attack_frame < len(self.machate_sprites[self.machate_attack_stage-1]):
                        self.update_attack_hitbox()
                        self.machate_hitbox_timer = 18
                self.machate_attack_timer -= 1

                if self.machate_hitbox_timer > 0:
                    self.machate_hitbox_timer -= 1
                else:
                    self.attack_hitbox = None

                if self.machate_attack_timer <= 0 or self.machate_attack_frame >= len(self.machate_sprites[self.machate_attack_stage-1]):
                    if self.machate_attack_stage < 4 and self.machate_attack_queued[self.machate_attack_stage]:
                        self.machate_attack_stage += 1
                        self.machate_attack_frame = 0
                        self.machate_attack_anim_counter = 0
                        self.machate_attack_timer = 20
                        self.update_attack_hitbox()
                        self.machate_hitbox_timer = 18
                    elif self.machate_attack_stage == 4 and self.machate_attack_frame < len(self.machate_sprites[3]):
                        pass
                    else:
                        self.is_attacking = False
                        self.attack_hitbox = None
                        self.machate_attack_stage = 0
                        self.machate_attack_queued = [False]*4
            elif self.weapon_type == "Martial":
                if self.attack_stage == 1:
                    self.attack_anim_counter += 1
                    if self.attack_anim_counter >= self.attack_first_frame_speed:
                        self.attack_frame += 1
                        self.attack_anim_counter = 0
                        if self.attack_frame >= len(self.sprites_attack1):
                            self.is_attacking = False
                            self.attack_hitbox = None
                elif self.attack_stage == 2:
                    self.attack_anim_counter += 1
                    if self.attack_anim_counter >= self.attack_frame_speed:
                        self.attack_frame += 1
                        self.attack_anim_counter = 0
                        if self.attack_frame >= len(self.sprites_attack2):
                            self.is_attacking = False
                            self.attack_hitbox = None
                            self.attack_stage = 0
                            self.attack_wait_timer = 0
        else:
            if self.attack_stage == 1 and self.attack_wait_timer > 0:
                self.attack_wait_timer -= 1
                if self.attack_queued:
                    self.is_attacking = True
                    self.attack_stage = 2
                    self.attack_frame = 0
                    self.attack_anim_counter = 0
                    self.attack_timer = len(self.sprites_attack2) * self.attack_frame_speed
                    self.update_attack_hitbox()
                    self.attack_queued = False
                elif self.attack_wait_timer == 0:
                    self.attack_stage = 0
            else:
                self.attack_queued = False

        if self.is_attacking:
            if self.attack_stage == 1 and self.attack1_effect_timer > 0:
                self.attack1_effect_timer -= 1
                if self.attack1_effect_timer % 2 == 0:
                    self.attack1_effect_index = min(self.attack1_effect_index + 1, 2)
            if self.attack_stage == 2 and self.attack2_effect_timer > 0:
                self.attack2_effect_timer -= 1
                if self.attack2_effect_timer % 2 == 0:
                    self.attack2_effect_index = min(self.attack2_effect_index + 1, 2)
        else:
            self.attack1_effect_index = 0
            self.attack2_effect_index = 0
            self.attack1_effect_timer = 0
            self.attack2_effect_timer = 0

    def take_damage(self, amount):
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_start = time.time()

    def attack(self):
        if self.weapon_type == "Shield":
            if not self.is_attacking and self.attack_stage == 0:
                self.is_attacking = True
                self.attack_frame = 0
                self.attack_anim_counter = 0
                self.attack_timer = len(self.sprites_shield_attack) * self.attack_frame_speed
                self.attack_stage = 1
                self.attack_wait_timer = 0
                self.update_attack_hitbox()
                self.already_hit_enemies = set()
        elif self.weapon_type == "Machate":
            if not self.is_attacking and self.machate_attack_stage == 0:
                self.is_attacking = True
                self.machate_attack_stage = 1
                self.machate_attack_frame = 0
                self.machate_attack_anim_counter = 0
                self.machate_attack_timer = 20
                self.update_attack_hitbox()
                self.machate_hitbox_timer = 1
                self.already_hit_enemies = {}
            elif 1 <= self.machate_attack_stage < 4 and self.machate_attack_timer > 0:
                self.machate_attack_queued[self.machate_attack_stage] = True
        elif self.weapon_type == "Martial":
            if not self.is_attacking and self.attack_stage == 0:
                self.is_attacking = True
                self.attack_frame = 1
                self.attack_anim_counter = 0
                self.attack_timer = self.attack_first_frame_speed
                self.attack_stage = 1
                self.attack_wait_timer = 15
                self.update_attack_hitbox()
                self.already_hit_enemies = set()
                self.attack1_effect_index = 0
                self.attack1_effect_timer = 6
            elif self.attack_stage == 1 and self.attack_wait_timer > 0 and not self.is_attacking:
                self.attack_queued = True
                self.already_hit_enemies = set()
                self.attack2_effect_index = 0
                self.attack2_effect_timer = 6

    def update_attack_hitbox(self):
        if self.weapon_type == "Shield":
            self.attack_hitbox = None
            return
        direction = 1 if self.facing_right else -1
        width = 28
        height = 30
        if direction == 1:
            x = self.rect.right
        else:
            x = self.rect.left - width
        y = self.rect.centery - height // 2
        self.attack_hitbox = pygame.Rect(x, y, width, height)

        if self.weapon_type == "Machate" and self.is_attacking and self.machate_attack_stage > 0:
            direction = 1 if self.facing_right else -1
            width = 40
            height = 36
            if direction == 1:
                x = self.rect.right
            else:
                x = self.rect.left - width
            y = self.rect.centery - height // 2
            self.attack_hitbox = pygame.Rect(x, y, width, height)
            return

    def special_attack(self):
        if self.weapon_type == "Magic":
            self.energy = 0
            self.special_active = True
            self.special_timer = 50
            self.special_direction = self.direction
            fireball_size = 100  # Phải giống với fireball.py
            offset = 170
            # Tạo quả cầu lửa sát nhân vật
            if self.facing_right:
                fireball_x = self.rect.right - fireball_size // 6 - offset # Sát mép phải
            else:
                fireball_x = self.rect.left - fireball_size + fireball_size // 6  # Sát mép trái
            fireball_y = self.rect.centery - fireball_size // 2
            direction = 1 if self.facing_right else -1
            self.projectiles.append(Fireball(fireball_x, fireball_y, direction))

    def render(self, screen):
        visible = True
        if self.invincible:
            if int((time.time() - self.invincible_start) * 10) % 2 == 0:
                visible = False

        if visible:
            # Nếu đang chưởng lực thì chỉ vẽ animation magic2 giống magic1
            if self.special_active:
                img = self.sprites_magic2[self.magic2_frame]
                offset_x = 0
                offset_y = 0
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
                return  # Không vẽ các trạng thái khác nữa

            # --- Render animation gồng nộ Magic ---
            if self.weapon_type == "Magic" and self.is_charging_energy:
                scale_factor = 1.5  # Thêm dòng này để tránh lỗi
                eff_img = self.no_effect_frames[self.no_effect_frame]
                eff_img_big = pygame.transform.scale(
                    eff_img,
                    (int(eff_img.get_width() * scale_factor), int(eff_img.get_height() * scale_factor))
                )
                eff_rect = eff_img_big.get_rect(midbottom=self.rect.midbottom)
                eff_rect.x -= int((eff_img_big.get_width() - self.rect.width) // 2)
                eff_rect.x += 30
                screen.blit(eff_img_big, eff_rect)
                img = self.sprites_charge_magic[self.charge_magic_frame]
                offset_x, offset_y = self.frame_offsets_charge_magic[self.charge_magic_frame]
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
            # --- Các trạng thái khác ---
            elif self.is_attacking:
                if self.weapon_type == "Shield":
                    img = self.sprites_shield_attack[min(self.attack_frame, len(self.sprites_shield_attack)-1)]
                    offset_x, offset_y = self.frame_offsets_shield_attack[min(self.attack_frame, len(self.frame_offsets_shield_attack)-1)]
                elif self.weapon_type == "Machate" and self.machate_attack_stage > 0:
                    idx = self.machate_attack_stage - 1
                    frame = min(self.machate_attack_frame, len(self.machate_sprites[idx])-1)
                    img = self.machate_sprites[idx][frame]
                    offset_x, offset_y = self.machate_offsets[idx][frame]
                    if self.facing_right:
                        screen.blit(img, (self.rect.x + offset_x, self.rect.y + offset_y))
                    else:
                        img_flip = pygame.transform.flip(img, True, False)
                        screen.blit(img_flip, (self.rect.x + offset_x, self.rect.y + offset_y))
                elif self.weapon_type == "Martial":
                    if self.attack_stage == 1:
                        img = self.sprites_attack1[min(self.attack_frame, len(self.sprites_attack1)-1)]
                        offset_x, offset_y = self.frame_offsets_attack1[min(self.attack_frame, len(self.frame_offsets_attack1)-1)]
                    elif self.attack_stage == 2:
                        img = self.sprites_attack2[min(self.attack_frame, len(self.sprites_attack2)-1)]
                        offset_x, offset_y = self.frame_offsets_attack2[min(self.attack_frame, len(self.frame_offsets_attack2)-1)]
                    else:
                        img = self.sprites_stand[self.current_frame]
                        offset_x, offset_y = self.frame_offsets_stand[self.current_frame]
                else:
                    img = self.sprites_stand[self.current_frame]
                    offset_x, offset_y = self.frame_offsets_stand[self.current_frame]
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
            elif self.is_jumping:
                img = self.sprite_jump
                offset_x, offset_y = self.frame_offset_jump
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
            elif self.is_falling:
                img = self.sprite_fall
                offset_x, offset_y = self.frame_offset_fall
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
            elif self.is_walking:
                img = self.sprites_walk[self.current_frame]
                offset_x, offset_y = self.frame_offsets_walk[self.current_frame]
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
            else:
                img = self.sprites_stand[self.current_frame]
                offset_x, offset_y = self.frame_offsets_stand[self.current_frame]
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))

        font = pygame.font.SysFont(None, 32)
        health_text = font.render(f'HP: {self.health}', True, (255, 255, 255))
        screen.blit(health_text, (10, 10))

        for proj in self.projectiles:
            proj.render(screen)

        if self.weapon_type == "Magic":
            pygame.draw.rect(screen, (50, 50, 50), (10, 50, 100, 12))
            pygame.draw.rect(screen, (0, 200, 255), (10, 50, int(self.energy), 12))
            font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "DejaVuSans.ttf")
            font = pygame.font.Font(font_path, 18)
            energy_text = font.render('NỘ', True, (255, 255, 255))
            screen.blit(energy_text, (115, 48))
            

        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)
        # if self.attack_hitbox:
        #     pygame.draw.rect(screen, (255, 255, 0), self.attack_hitbox, 2)

        effect_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "effect")
        martial1eff_path = os.path.join(effect_dir, "martial1.png")
        martial1eff_sheet = pygame.image.load(martial1eff_path).convert_alpha()
        eff1_w = martial1eff_sheet.get_width() // 3
        eff1_h = martial1eff_sheet.get_height()
        self.attack1_effect_frames = []
        for i in range(3):
            frame = martial1eff_sheet.subsurface((i * eff1_w, 0, eff1_w, eff1_h))
            scale_h = 100
            scale_w = int(frame.get_width() * (scale_h / frame.get_height()))
            frame = pygame.transform.scale(frame, (scale_w, scale_h))
            self.attack1_effect_frames.append(frame)
        martial2eff_path = os.path.join(effect_dir, "martial2.png")
        martial2eff_sheet = pygame.image.load(martial2eff_path).convert_alpha()
        eff2_w = martial2eff_sheet.get_width() // 3
        eff2_h = martial2eff_sheet.get_height()
        self.attack2_effect_frames = []
        for i in range(3):
            frame = martial2eff_sheet.subsurface((i * eff2_w, 0, eff2_w, eff2_h))
            scale_h = 40
            scale_w = int(frame.get_width() * (scale_h / frame.get_height()))
            frame = pygame.transform.scale(frame, (scale_w, scale_h))
            self.attack2_effect_frames.append(frame)

        if self.attack_hitbox and self.weapon_type != "Shield":
            if self.is_attacking and self.attack_stage == 1 and self.attack1_effect_index < len(self.attack1_effect_frames):
                if self.attack_hitbox:  # Kiểm tra hitbox khác None
                    eff_img = self.attack1_effect_frames[self.attack1_effect_index]
                    eff_rect = eff_img.get_rect(center=self.attack_hitbox.center)
                    if not self.facing_right:
                        eff_img = pygame.transform.flip(eff_img, True, False)
                    screen.blit(eff_img, eff_rect)
            if self.is_attacking and self.attack_stage == 2 and self.attack2_effect_index < len(self.attack2_effect_frames):
                if self.attack_hitbox:  # Kiểm tra hitbox khác None
                    eff_img = self.attack2_effect_frames[self.attack2_effect_index]
                    eff_rect = eff_img.get_rect(center=self.attack_hitbox.center)
                    if not self.facing_right:
                        eff_img = pygame.transform.flip(eff_img, True, False)
                    screen.blit(eff_img, eff_rect)

        if self.is_attacking and self.weapon_type == "Machate":
            idx = self.machate_attack_stage - 1
            if 0 <= idx < len(self.machate_sprites) and self.machate_attack_frame < len(self.machate_sprites[idx]):
                img = self.machate_sprites[idx][self.machate_attack_frame]
                offset_x, offset_y = self.machate_offsets[idx][self.machate_attack_frame]
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
        elif self.is_attacking and self.weapon_type == "Shield":
            img = self.sprites_shield_attack[min(self.attack_frame, len(self.sprites_shield_attack)-1)]
            offset_x, offset_y = self.frame_offsets_shield_attack[min(self.attack_frame, len(self.frame_offsets_shield_attack)-1)]
            draw_x = self.rect.x + offset_x
            draw_y = self.rect.y + offset_y
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, (draw_x, draw_y))
        elif self.is_attacking and self.weapon_type == "Martial":
            if self.attack_stage == 1:
                img = self.sprites_attack1[min(self.attack_frame, len(self.sprites_attack1)-1)]
                offset_x, offset_y = self.frame_offsets_attack1[min(self.attack_frame, len(self.frame_offsets_attack1)-1)]
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
            elif self.attack_stage == 2:
                img = self.sprites_attack2[min(self.attack_frame, len(self.sprites_attack2)-1)]
                offset_x, offset_y = self.frame_offsets_attack2[min(self.attack_frame, len(self.frame_offsets_attack2)-1)]
                draw_x = self.rect.x + offset_x
                draw_y = self.rect.y + offset_y
                if not self.facing_right:
                    img = pygame.transform.flip(img, True, False)
                screen.blit(img, (draw_x, draw_y))
        elif self.weapon_type == "Magic" and self.is_charging_energy:
            img = self.sprites_charge_magic[self.charge_magic_frame]
            offset_x, offset_y = self.frame_offsets_charge_magic[self.charge_magic_frame]
            draw_x = self.rect.x + offset_x
            draw_y = self.rect.y + offset_y
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, (draw_x, draw_y))

        if self.is_attacking and self.attack_stage == 1 and self.attack1_effect_index < len(self.attack1_effect_frames):
            if self.attack_hitbox:  # Kiểm tra hitbox khác None
                eff_img = self.attack1_effect_frames[self.attack1_effect_index]
                eff_rect = eff_img.get_rect(center=self.attack_hitbox.center)
                if not self.facing_right:
                    eff_img = pygame.transform.flip(eff_img, True, False)
                screen.blit(eff_img, eff_rect)
        if self.is_attacking and self.attack_stage == 2 and self.attack2_effect_index < len(self.attack2_effect_frames):
            if self.attack_hitbox:  # Kiểm tra hitbox khác None
                eff_img = self.attack2_effect_frames[self.attack2_effect_index]
                eff_rect = eff_img.get_rect(center=self.attack_hitbox.center)
                if not self.facing_right:
                    eff_img = pygame.transform.flip(eff_img, True, False)
                screen.blit(eff_img, eff_rect)

