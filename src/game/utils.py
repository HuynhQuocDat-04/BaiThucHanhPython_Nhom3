def load_image(file_path):
    """Load an image from the specified file path."""
    import pygame
    try:
        image = pygame.image.load(file_path)
        return image
    except pygame.error as e:
        print(f"Unable to load image: {file_path}. Error: {e}")
        return None

def load_sound(file_path):
    """Load a sound from the specified file path."""
    import pygame
    try:
        sound = pygame.mixer.Sound(file_path)
        return sound
    except pygame.error as e:
        print(f"Unable to load sound: {file_path}. Error: {e}")
        return None

def check_collision(rect1, rect2):
    """Check if two rectangles collide."""
    return rect1.colliderect(rect2)

def clamp(value, min_value, max_value):
    """Clamp a value between a minimum and maximum."""
    return max(min_value, min(value, max_value))