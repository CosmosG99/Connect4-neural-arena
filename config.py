import pygame

# Default Base Resolution (Logical)
BASE_WIDTH = 1920
BASE_HEIGHT = 1080

# Theme Definitions
THEMES = {
    "Space": { # Original Premium Theme
        "bg": (5, 6, 12),
        "grid": (25, 35, 75),
        "accent1": (210, 170, 70), # Gold
        "accent2": (110, 70, 240), # Purple
        "highlight": (245, 220, 170),
        "p1": (230, 30, 50),
        "p2": (245, 195, 20),
        "panel": (10, 15, 35, 250),
        "particles": [(140, 80, 255), (100, 50, 200)]
    },
    "Cyberpunk": {
        "bg": (10, 5, 20),
        "grid": (40, 10, 60),
        "accent1": (255, 0, 120), # Neon Pink
        "accent2": (0, 255, 255), # Cyan
        "highlight": (255, 255, 100),
        "p1": (255, 20, 147),
        "p2": (0, 255, 127),
        "panel": (20, 5, 30, 245),
        "particles": [(255, 0, 255), (0, 255, 255)]
    },
    "Neon": {
        "bg": (0, 0, 0),
        "grid": (20, 20, 20),
        "accent1": (50, 255, 50), # Electric Green
        "accent2": (255, 50, 50), # Electric Red
        "highlight": (255, 255, 255),
        "p1": (0, 255, 255),
        "p2": (255, 0, 255),
        "panel": (5, 5, 5, 250),
        "particles": [(0, 255, 0), (0, 255, 255)]
    },
    "Retro Arcade": {
        "bg": (15, 10, 30),
        "grid": (100, 40, 150),
        "accent1": (255, 255, 0), # Arcade Yellow
        "accent2": (0, 180, 255), # Arcade Blue
        "highlight": (255, 255, 255),
        "p1": (255, 60, 0),
        "p2": (255, 215, 0),
        "panel": (20, 15, 45, 240),
        "particles": [(255, 100, 0), (0, 255, 255)]
    },
    "Minimalist": {
        "bg": (25, 25, 28),
        "grid": (45, 45, 48),
        "accent1": (180, 180, 185), # Silver
        "accent2": (80, 80, 85),   # Dark Gray
        "highlight": (255, 255, 255),
        "p1": (220, 220, 220),
        "p2": (120, 120, 125),
        "panel": (35, 35, 38, 250),
        "particles": [(200, 200, 205), (100, 100, 105)]
    }
}

# Board Logic Dimensions
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER = 1
AI_AGENT = 2

# Game Modes
MODE_H_VS_AI = 1
MODE_AI_VS_AI = 2
MODE_H_VS_H = 3

# Difficulties
DIFF_EASY = 1
DIFF_MEDIUM = 2
DIFF_HARD = 3
DIFF_EXPERT = 4
DIFF_IMPOSSIBLE = 5

AI_MOVE_DELAY = 1.0  # Cinematic delay between AI moves
FPS = 60

class ConfigManager:
    def __init__(self):
        self.screen_width = 1280
        self.screen_height = 720
        self.is_fullscreen = False
        self.scale_factor = self.screen_width / BASE_WIDTH
        
        # Current Theme State
        self.themes = THEMES
        self.current_theme_name = "Space"
        self.apply_theme("Space")

    def apply_theme(self, name):
        if name in THEMES:
            self.current_theme_name = name
            t = THEMES[name]
            self.BG_COLOR = t["bg"]
            self.GRID_COLOR = t["grid"]
            self.THEME_ACCENT_1 = t["accent1"]
            self.THEME_ACCENT_2 = t["accent2"]
            self.THEME_HIGHLIGHT = t["highlight"]
            self.PLAYER1_COLOR = t["p1"]
            self.PLAYER2_COLOR = t["p2"]
            self.PANEL_BG = t["panel"]
            self.PARTICLE_COLORS = t["particles"]
            
            # Derived colors
            self.WHITE = (255, 255, 255)
            self.TEXT_COLOR = (220, 225, 235)
            self.HOVER_COLOR = tuple(min(255, c + 30) for c in self.GRID_COLOR)

    def update_resolution(self, width, height, fullscreen):
        self.screen_width = width
        self.screen_height = height
        self.is_fullscreen = fullscreen
        
        # Calculate scale factor maintaining aspect ratio or fitting screen
        scale_w = width / BASE_WIDTH
        scale_h = height / BASE_HEIGHT
        self.scale_factor = min(scale_w, scale_h)

    def s(self, value):
        """Scale a value based on the current scale factor"""
        if isinstance(value, tuple):
            return tuple(int(v * self.scale_factor) for v in value)
        if isinstance(value, pygame.Rect):
            return pygame.Rect(int(value.x * self.scale_factor), int(value.y * self.scale_factor),
                               int(value.width * self.scale_factor), int(value.height * self.scale_factor))
        return int(value * self.scale_factor)

# Global config instance
config = ConfigManager()
