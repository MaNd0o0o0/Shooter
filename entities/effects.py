"""
effects.py - المؤثرات البصرية
"""

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse
from kivy.animation import Animation
from random import randint, uniform
from config import IMAGES_PATH


class Particle(Widget):
    """جسيم متحرك"""
    
    def __init__(self, pos, color=(1, 1, 1, 1), **kwargs):
        super(Particle, self).__init__(**kwargs)
        self.size = (6, 6)
        self.pos = pos
        self.velocity = (uniform(-80, 80), uniform(80, 200))
        self.lifetime = 1.0
        self.color = color
        
        with self.canvas:
            self.color_inst = Color(*color)
            self.circle = Ellipse(size=self.size, pos=self.pos)
    
    def update(self, dt):
        """تحديث حركة الجسيم"""
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.velocity = (self.velocity[0], self.velocity[1] - 150 * dt)
        
        self.lifetime -= dt
        self.circle.pos = self.pos
        
        # تلاشي
        alpha = max(0, self.lifetime * self.color[3] if len(self.color) > 3 else self.lifetime)
        self.color_inst.a = alpha
        
        return self.lifetime <= 0


class Explosion(Image):
    """انفجار"""
    
    def __init__(self, pos, size=80, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/explosion.png", size=(size, size), pos=pos, **kwargs)
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=self._remove)
        anim.start(self)
    
    def _remove(self, *args):
        if self.parent:
            self.parent.remove_widget(self)


class HealGlow(Image):
    """تأثير الشفاء"""
    
    def __init__(self, pos, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/heal_glow.png", size=(50, 50), pos=pos, **kwargs)
        anim = Animation(opacity=0, duration=0.5)
        anim.bind(on_complete=self._remove)
        anim.start(self)
    
    def _remove(self, *args):
        if self.parent:
            self.parent.remove_widget(self)


class ShieldEffect(Widget):
    """تأثير الدرع"""
    
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.size = (player.width * 1.6, player.height * 1.6)
        
        with self.canvas:
            Color(0, 0.6, 1, 0.4)
            self.circle = Ellipse(size=self.size, pos=self.pos)
        
        self.update_pos()
    
    def update_pos(self):
        """تحديث موقع الدرع حول اللاعب"""
        if self.player:
            self.pos = (self.player.center_x - self.size[0]/2,
                       self.player.center_y - self.size[1]/2)
            self.circle.pos = self.pos
    
    def update(self, dt):
        """تحديث الدرع"""
        self.update_pos()