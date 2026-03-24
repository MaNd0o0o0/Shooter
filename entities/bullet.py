from kivy.core.window import Window
from entities.base_entity import BaseEntity
from config import IMAGES_PATH, BULLET_SIZE, BULLET_SPEED
from math import radians, cos, sin

class Bullet(BaseEntity):
    def __init__(self, pos, angle=0, **kwargs):
        super(Bullet, self).__init__(
            source=f"{IMAGES_PATH}/bullet.png", 
            size=BULLET_SIZE, 
            pos=pos, 
            **kwargs
        )
        self.angle = angle
        self.speed = BULLET_SPEED
        self.distance_traveled = 0
        self.max_distance = Window.width * 2
    
    def update(self, dt=0.016):
        rad = radians(self.angle)
        move_x = self.speed * cos(rad)
        move_y = self.speed * sin(rad)
        self.pos = (self.x + move_x, self.y + move_y)
        self.distance_traveled += self.speed

class BossBullet(BaseEntity):
    def __init__(self, pos, target_pos=None, bullet_type="normal", **kwargs):
        super(BossBullet, self).__init__(
            source=f"{IMAGES_PATH}/boss_bullet.png", 
            size=(40, 40), 
            pos=pos, 
            **kwargs
        )
        self.speed = 8
        self.bullet_type = bullet_type
        self.distance_traveled = 0
        self.max_distance = Window.width * 2
        if target_pos:
            import math
            dx = target_pos[0] - pos[0]
            dy = target_pos[1] - pos[1]
            self.angle = math.degrees(math.atan2(dy, dx))
        else:
            self.angle = 180
    
    def update(self, dt=0.016):
        rad = radians(self.angle)
        move_x = self.speed * cos(rad)
        move_y = self.speed * sin(rad)
        self.pos = (self.x + move_x, self.y + move_y)
        self.distance_traveled += self.speed