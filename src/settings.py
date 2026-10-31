"""Central configuration for Italia 2008-2088: Neon Rebellion."""

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
TITLE = "Italia 2008-2088: Neon Rebellion"
FPS = 60

MAX_LEVELS = 8
TARGET_KILLS_PER_LEVEL = 12
ENEMY_SPAWN_TIME = 1.25

PLAYER_SPEED = 360
PLAYER_HEALTH = 100
LASER_SPEED = 760
LASER_COOLDOWN = 0.18

DIFFICULTIES = ("Easy", "Normal", "Hard")
DIFFICULTY_SETTINGS = {
    "Easy": {"spawn": 1.18, "enemy_health": 0.85, "damage": 0.75, "boss_health": 90},
    "Normal": {"spawn": 1.0, "enemy_health": 1.0, "damage": 1.0, "boss_health": 125},
    "Hard": {"spawn": 0.78, "enemy_health": 1.25, "damage": 1.25, "boss_health": 165},
}

WHITE = (245, 248, 255)
RED = (255, 65, 95)
GREEN = (55, 230, 150)
CYAN = (45, 225, 255)
YELLOW = (255, 220, 70)
GRAY = (135, 150, 170)
PURPLE = (195, 85, 255)
ORANGE = (255, 145, 55)
BLACK = (0, 0, 0)
DARK = (4, 7, 18)
PANEL = (9, 15, 32)
