"""config.py - إعدادات المشروع"""
from kivy.core.window import Window
import os

Window.fullscreen = 'auto'
WINDOW_WIDTH = Window.width
WINDOW_HEIGHT = Window.height

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

PLAYER_SIZE = (260, 260)
BULLET_SIZE = (50, 50)
BOSS_BULLET_SIZE = (40, 40)
POWERUP_SIZE = (80, 80)
COIN_SIZE = (100, 100)
ENEMY_SIZES = {'normal': (150,150), 'fast': (120,120), 'armor': (180,180), 'bomber': (150,150), 'ghost': (140,140)}
BOSS_SIZE = (500, 500)

PLAYER_SPEED = 8
BULLET_SPEED = 14
BOSS_BULLET_SPEED = 8
SCROLL_SPEEDS = {'mountains': 0.4, 'city': 1.5, 'items': 2, 'clouds': 1.1}

MAX_BULLETS = 30
MAX_BOSS_BULLETS = 20
MAX_PARTICLES = 100
MAX_ENEMIES_ON_SCREEN = 8

BOSS_LEVELS = {3: "normal", 6: "fire", 9: "ice", 12: "electric", 15: "final"}

UI_COLORS = {'btn_normal': (0.2,0.6,0.9,1), 'btn_down': (0.1,0.5,0.8,1), 'health_bg': (0.15,0.15,0.15,0.9), 'health_fg': (1,0.3,0.3,1), 'shield': (0,0.5,1,0.5)}
BOUNDS = {'top': WINDOW_HEIGHT, 'bottom': 160, 'left': 0, 'right': WINDOW_WIDTH}