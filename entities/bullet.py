"""
bullet.py - الرصاصات
"""

from kivy.core.window import Window
from kivy.uix.image import Image
from config import IMAGES_PATH, BULLET_SIZE, BULLET_SPEED
from math import radians, cos, sin


class Bullet(Image):
    """رصاصة اللاعب"""
    
    def __init__(self, pos, angle=0, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/bullet.png", size=BULLET_SIZE, pos=pos, **kwargs)
        self.angle = angle
        self.speed = BULLET_SPEED
        self.distance_traveled = 0
        self.max_distance = Window.width * 2
        self.hit = False
        self.active = True
        self.cpp_id = -1
    
    def update(self, dt=0.016):
        if self.hit or not self.active:
            return True
        
        try:
            rad = radians(self.angle)
            move_x = self.speed * cos(rad)
            move_y = self.speed * sin(rad)
            
            self.x += move_x
            self.y += move_y
            self.distance_traveled += self.speed
            
            if (self.x > Window.width + 100 or self.x < -100 or
                self.y > Window.height + 100 or self.y < -100 or
                self.distance_traveled > self.max_distance):
                self.active = False
                return True
            
            return False
        except:
            return True
    
    def collide_widget(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)


class BossBullet(Image):
    """رصاصة البوس - محسنة"""
    
    def __init__(self, pos, angle=None, target_pos=None, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/boss_bullet.png", size=(30, 30), pos=pos, **kwargs)  # حجم أصغر
        self.speed = 8
        self.distance_traveled = 0
        self.max_distance = Window.width * 2
        self.hit = False
        self.active = True
        self.cpp_id = -1
        
        if angle is not None:
            self.angle = angle
        elif target_pos:
            import math
            dx = target_pos[0] - pos[0]
            dy = target_pos[1] - pos[1]
            self.angle = math.degrees(math.atan2(dy, dx))
        else:
            self.angle = 180
    
    def update(self, dt=0.016):
        if self.hit or not self.active:
            return True
        
        try:
            rad = radians(self.angle)
            move_x = self.speed * cos(rad)
            move_y = self.speed * sin(rad)
            
            self.x += move_x
            self.y += move_y
            self.distance_traveled += self.speed
            
            if (self.x < -50 or self.x > Window.width + 50 or
                self.distance_traveled > self.max_distance):
                self.active = False
                return True
            
            return False
        except:
            return True
    
    def collide_widget(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)