from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse
from kivy.animation import Animation
from random import randint

class Explosion(Image):
    def __init__(self, pos, **kwargs):
        from config import IMAGES_PATH
        super(Explosion, self).__init__(
            source=f"{IMAGES_PATH}/explosion.png", 
            size=(220, 220), 
            pos=pos, 
            **kwargs
        )
        self.opacity = 1
        anim = Animation(opacity=0, d=0.4)
        anim.bind(on_complete=self.remove_explosion)
        anim.start(self)
    
    def remove_explosion(self, *args):
        if self.parent:
            self.parent.remove_widget(self)

class Particle(Widget):
    def __init__(self, pos, color=(1, 1, 1, 1), **kwargs):
        super(Particle, self).__init__(**kwargs)
        self.size = (10, 10)
        self.pos = pos
        self.velocity = (randint(-5, 5), randint(-5, 5))
        self.lifetime = 1.0
        self.color = color
        with self.canvas:
            Color(*color)
            self.rect = Ellipse(size=self.size, pos=self.pos)
    
    def update(self, dt):
        self.pos = (self.x + self.velocity[0], self.y + self.velocity[1])
        self.lifetime -= dt
        size_reduction = 0.5
        new_size = (max(0, self.size[0] - size_reduction), max(0, self.size[1] - size_reduction))
        self.size = new_size
        self.rect.size = new_size
        self.rect.pos = self.pos
        if self.lifetime <= 0 and hasattr(self, 'canvas'):
            self.canvas.clear()
        return self.lifetime <= 0