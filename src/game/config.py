"""
Config cho game settings
"""

# Game settings
GAME_SETTINGS = {
    "FPS": 60,
    "MOVEMENT_SPEED": 4.5,  # Tốc độ di chuyển (pixels per frame) — increased by 50%
    "JUMP_SPEED": -15,    # Tốc độ nhảy (âm vì đi lên)
    "JUMP_COOLDOWN": 200, # Milliseconds giữa các lần nhảy
    "GRAVITY": 1,         # Trọng lực
    "MAX_FALL_SPEED": 10, # Tốc độ rơi tối đa
}

# Input settings  
INPUT_SETTINGS = {
    "KEY_REPEAT_DELAY": 50,  # Milliseconds delay cho key repeat
    "DOUBLE_TAP_TIME": 300,  # Milliseconds để detect double tap
}

# Graphics settings
GRAPHICS_SETTINGS = {
    "SCREEN_WIDTH": 800,
    "SCREEN_HEIGHT": 600,
    "FULLSCREEN": False,
    "VSYNC": True,
}

# Audio settings
AUDIO_SETTINGS = {
    "MASTER_VOLUME": 1.0,
    "SFX_VOLUME": 0.8,
    "MUSIC_VOLUME": 0.6,
}