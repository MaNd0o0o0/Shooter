# إعدادات النافذة
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FULLSCREEN = 'auto'

# إعدادات اللاعب
PLAYER_SIZE = (260, 260)
PLAYER_START_POS = (120, 540)
MAX_HEALTH = 100
MAX_BULLETS = 5

# إعدادات الأعداء
ENEMY_SPAWN_DELAY = 1.5
MAX_ENEMIES = 5
MAX_ENEMIES_ON_SCREEN = 8

# إعدادات الرصاص
BULLET_SPEED = 14
BULLET_SIZE = (50, 50)
MAX_BULLETS_COUNT = 30
MAX_BOSS_BULLETS = 20

# إعدادات الزعماء
BOSS_SIZE = (500, 500)
BOSS_HEALTH = 300
BOSS_LEVELS = {
    3: "normal",
    6: "fire",
    9: "ice",
    12: "electric",
    15: "final"
}

# إعدادات النظام
FPS = 60
MAX_PARTICLES = 100
SAVE_FILE = 'game_data.json'

# مسارات الأصول
ASSETS_PATH = 'assets'
IMAGES_PATH = f'{ASSETS_PATH}/images'
SOUNDS_PATH = f'{ASSETS_PATH}/sounds'
FONTS_PATH = f'{ASSETS_PATH}/fonts'