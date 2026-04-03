"""
player.py - شخصية اللاعب مع invincible
"""

from kivy.uix.image import Image
from kivy.clock import Clock
from config import IMAGES_PATH, PLAYER_SIZE, PLAYER_START_POS


class Player(Image):
    """شخصية اللاعب"""
    
    def __init__(self, skin="default", **kwargs):
        skin_images = {
            "default": f"{IMAGES_PATH}/player.png",
            "blue": f"{IMAGES_PATH}/player_blue.png",
            "red": f"{IMAGES_PATH}/player_red.png",
            "gold": f"{IMAGES_PATH}/player_gold.png",
            "green": f"{IMAGES_PATH}/player_green.png"
        }
        image = skin_images.get(skin, f"{IMAGES_PATH}/player.png")
        super(Player, self).__init__(source=image, size=PLAYER_SIZE, **kwargs)
        self.pos = PLAYER_START_POS
        self.skin = skin
        self.health = 100
        self.max_health = 100
        self.speed_multiplier = 1.0
        self.shield_active = False
        self.is_casting = False
        self.invincible_timer = 0
        self.invincible = False
    
    def update_skin(self, skin_name):
        """تحديث مظهر اللاعب"""
        skin_images = {
            "default": f"{IMAGES_PATH}/player.png",
            "blue": f"{IMAGES_PATH}/player_blue.png",
            "red": f"{IMAGES_PATH}/player_red.png",
            "gold": f"{IMAGES_PATH}/player_gold.png",
            "green": f"{IMAGES_PATH}/player_green.png"
        }
        if skin_name in skin_images:
            self.source = skin_images[skin_name]
            self.skin = skin_name
    
    def change_skin(self, skin_name):
        """تغيير السكن (توافق مع الكود القديم)"""
        self.update_skin(skin_name)
    
    def cast_animation(self):
        """أنيميشن إطلاق السحر"""
        if not self.is_casting:
            self.is_casting = True
            old_source = self.source
            Clock.schedule_once(lambda dt: setattr(self, 'source', old_source), 0.15)
            Clock.schedule_once(lambda dt: setattr(self, 'is_casting', False), 0.3)
    
    def hit_animation(self):
        """أنيميشن أخذ الضرر"""
        old_source = self.source
        self.opacity = 0.5
        Clock.schedule_once(lambda dt: setattr(self, 'opacity', 1), 0.15)
    
    def set_invincible(self, duration=1.0):
        """جعل اللاعب غير قابل للإصابة"""
        self.invincible = True
        Clock.schedule_once(lambda dt: setattr(self, 'invincible', False), duration)