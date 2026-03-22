"""bullet.py - الرصاصات"""
from entities.base_entity import BaseEntity
from config import BULLET_SIZE, BOSS_BULLET_SIZE, BULLET_SPEED, BOSS_BULLET_SPEED
from math import radians, cos, sin

class Bullet(BaseEntity):
    def __init__(self, pos, angle=0, **kwargs):
        super().__init__(source="bullet.png", size=BULLET_SIZE, pos=pos, **kwargs)
        self.angle, self.speed, self.distance = angle, BULLET_SPEED, 0
        self.max_distance = (self.parent.width*2) if self.parent else 2000
    def update(self, dt):
        rad = radians(self.angle); self.pos = (self.x+self.speed*cos(rad), self.y+self.speed*sin(rad)); self.distance += self.speed

class BossBullet(BaseEntity):    def __init__(self, pos, target_pos=None, **kwargs):
        super().__init__(source="boss_bullet.png", size=BOSS_BULLET_SIZE, pos=pos, **kwargs)
        self.speed, self.distance = BOSS_BULLET_SPEED, 0
        self.max_distance = (self.parent.width*2) if self.parent else 2000
        if target_pos:
            from math import atan2, degrees
            dx,dy = target_pos[0]-pos[0], target_pos[1]-pos[1]; self.angle = degrees(atan2(dy,dx))
        else: self.angle = 180
    def update(self, dt):
        rad = radians(self.angle); self.pos = (self.x+self.speed*cos(rad), self.y+self.speed*sin(rad)); self.distance += self.speed