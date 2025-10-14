import pygame as pg

class SpriteAnimated(pg.sprite.Sprite):
    def __init__(self, sprite_sheet, frame_width, frame_height, row, num_frames, time_per_frame=0.12, scale=1.0):
        super().__init__()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.row = row
        self.num_frames = num_frames
        self.time_per_frame = time_per_frame
        self.scale = scale
        self.frames = []
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        self.load_frames(sprite_sheet)
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()

    def load_frames(self, sprite_sheet):
        for i in range(self.num_frames):
            x = i * self.frame_width
            y = self.row * self.frame_height
            frame = sprite_sheet.subsurface(pg.Rect(x, y, self.frame_width, self.frame_height))
            if self.scale != 1.0:
                frame = pg.transform.scale(frame, (int(self.frame_width * self.scale), int(self.frame_height * self.scale)))
            self.frames.append(frame)

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.time_per_frame * 1000:
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.last_update = now
            self.image = self.frames[self.current_frame]

    def get_image(self, flip=False):
        img = self.frames[self.current_frame]
        if flip:
            img = pg.transform.flip(img, True, False)
        return img