"""base_entity.py - كلاس أساسي للكيانات"""
from kivy.uix.image import Image
from kivy.core.window import Window
from random import randint

class BaseEntity(Image):
    def __init__(self, source, size, pos=(0,0), **kwargs):
        super().__init__(source=source, size=size, pos=pos, **kwargs)
        self.health = self.max_health = 1; self.speed = self.damage = 0; self.active = True
    def update(self, dt): pass
    def is_offscreen(self, buffer=100):
        return self.x<-buffer or self.x>Window.width+buffer or self.y<-buffer or self.y>Window.height+buffer
    def take_damage(self, amount): self.health -= amount; return self.health <= 0
    def reset_position(self, x_range, y_range): self.pos = (randint(*x_range), randint(*y_range))