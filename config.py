"""
config.py - إعدادات اللعبة الكاملة
"""

import os
import pygame

# ==================== إعدادات النافذة ====================
pygame.init()
info = pygame.display.Info()
WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w, info.current_h
FULLSCREEN = True
FPS = 30

# ==================== إعدادات اللاعب ====================
PLAYER_SIZE = (150, 150)
PLAYER_START_POS = (120, 360)
MAX_HEALTH = 100
PLAYER_SPEED = 200
MAX_BULLETS = 5

# ==================== إعدادات الأعداء ====================
ENEMY_SPAWN_DELAY = 1.5
MAX_ENEMIES = 50
MAX_ENEMIES_ON_SCREEN = 15
MAX_ENEMIES_GLOBAL = 15

# أنواع الأعداء
ENEMY_TYPES = {
    "soldier": {"health": 1, "damage": 5, "speed": 100, "reward": 10, "size": (80, 80), "image": "enemy.png"},
    "armor": {"health": 3, "damage": 8, "speed": 70, "reward": 25, "size": (95, 95), "image": "enemy_armor.png"},
    "fast": {"health": 1, "damage": 5, "speed": 150, "reward": 15, "size": (70, 70), "image": "enemy_fast.png"},
    "bomber": {"health": 2, "damage": 10, "speed": 80, "reward": 20, "size": (85, 85), "image": "enemy_bomber.png"},
    "ghost": {"health": 2, "damage": 7, "speed": 90, "reward": 18, "size": (80, 80), "image": "enemy_ghost.png"},
}

# ==================== إعدادات البوسات (محسنة) ====================
BOSS_SIZE = (250, 250)  # 🔥 تم التخفيض من 500 إلى 250 لتحسين الأداء
BOSS_HEALTH = 300
BOSS_LEVELS = {
    3: "normal",
    6: "fire",
    9: "ice",
    12: "electric",
    15: "final"
}
BOSS_IMAGES = {
    "normal": "boss.png",
    "fire": "boss_fire.png",
    "ice": "boss_ice.png",
    "electric": "boss_electric.png",
    "final": "boss_final.png"
}

# ==================== إعدادات الرصاص ====================
BULLET_SIZE = (40, 40)
BULLET_SPEED = 25
MAX_BULLETS_COUNT = 80
MAX_BOSS_BULLETS = 30

# ==================== إعدادات الجسيمات ====================
MAX_PARTICLES = 100

# ==================== نظام التوازن ====================
MAX_BULLETS_GLOBAL = 80
MAX_ITEMS_GLOBAL = 20
SPAWN_WAVE_DELAY = 3
ENEMIES_PER_WAVE = 10
BOSS_SPAWN_WAVE = 5

# ==================== إعدادات الباوربس ====================
POWERUP_IMAGES = {
    "speed": "powerup_speed.png",
    "shield": "powerup_shield.png",
    "bomb": "powerup_bomb.png",
    "freeze": "powerup_freeze.png",
    "health": "powerup_health.png"
}

# ==================== مسارات الملفات ====================
ASSETS_PATH = 'assets'
IMAGES_PATH = f'{ASSETS_PATH}/images'
SOUNDS_PATH = f'{ASSETS_PATH}/sounds'
SAVE_FILE = 'data/game_data.json'

# إنشاء المجلدات
for path in [ASSETS_PATH, IMAGES_PATH, SOUNDS_PATH, 'data']:
    os.makedirs(path, exist_ok=True)