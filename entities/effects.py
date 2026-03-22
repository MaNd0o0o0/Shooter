"""effects.py - التأثيرات البصرية"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.core.window import Window
from random import randint

class Explosion(Image):
    def __init__(self, pos, **kwargs):
        super().__init__(source="explosion.png", size=(220,220), pos=pos, **kwargs); self.opacity = 1
        anim = Animation(opacity=0, d=0.4); anim.bind(on_complete=lambda *a: self.parent and self.parent.remove_widget(self)); anim.start(self)

class Particle(Widget):
    def __init__(self, pos, color=(1,1,1,1), **kwargs):
        super().__init__(**kwargs); self.size, self.pos = (10,10), pos
        self.velocity, self.lifetime, self.color = (randint(-5,5),randint(-5,5)), 1.0, color
        with self.canvas: Color(*color); self.rect = Ellipse(size=self.size, pos=self.pos)
    def update(self, dt):
        self.pos = (self.x+self.velocity[0], self.y+self.velocity[1]); self.lifetime -= dt
        ns = (max(0,self.size[0]-0.5), max(0,self.size[1]-0.5)); self.size = ns; self.rect.size = ns; self.rect.pos = self.pos
        return self.lifetime <= 0