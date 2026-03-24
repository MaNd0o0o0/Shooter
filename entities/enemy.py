from kivy.core.window import Window
from entities.base_entity import BaseEntity
from config import IMAGES_PATH
from random import randint

class EnemyFast(BaseEntity):
    def __init__(self, **kwargs):
        super(EnemyFast, self).__init__(
            source=f"{IMAGES_PATH}/enemy_fast.png", 
            size=(120, 120), 
            **kwargs
        )
        self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
        self.speed = randint(6, 10)
        self.health = 1
        self.max_health = 1
        self.damage = 5
    
    def update(self, dt=0.016, game=None):
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0:
            self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))

class EnemyArmor(BaseEntity):
    def __init__(self, **kwargs):
        super(EnemyArmor, self).__init__(
            source=f"{IMAGES_PATH}/enemy_armor.png", 
            size=(180, 180), 
            **kwargs
        )
        self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
        self.speed = 2
        self.health = 5
        self.max_health = 5
        self.damage = 8
    
    def update(self, dt=0.016, game=None):
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0:
            self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))

class EnemyBomber(BaseEntity):
    def __init__(self, **kwargs):
        super(EnemyBomber, self).__init__(
            source=f"{IMAGES_PATH}/enemy_bomber.png", 
            size=(150, 150), 
            **kwargs
        )
        self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
        self.speed = 3        
        self.health = 2
        self.max_health = 2
        self.damage = 10
    
    def update(self, dt=0.016, game=None):
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0:
            self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))

class EnemyGhost(BaseEntity):
    def __init__(self, **kwargs):
        super(EnemyGhost, self).__init__(
            source=f"{IMAGES_PATH}/enemy_ghost.png", 
            size=(140, 140), 
            **kwargs
        )
        self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
        self.speed = 4
        self.health = 2
        self.max_health = 2
        self.visible = True
        self.invisible_timer = 0
        self.opacity = 1
        self.damage = 7
    
    def update(self, dt=0.016, game=None):
        self.pos = (self.x - self.speed, self.y)
        self.invisible_timer += dt
        if self.invisible_timer > 3:
            self.visible = not self.visible
            self.opacity = 1.0 if self.visible else 0.3
            self.invisible_timer = 0
        if self.right < 0:
            self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
            self.opacity = 1
            self.visible = True

class Enemy(BaseEntity):
    def __init__(self, **kwargs):
        super(Enemy, self).__init__(
            source=f"{IMAGES_PATH}/enemy.png", 
            size=(150, 150), 
            **kwargs
        )
        self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
        self.speed = 4
        self.health = 1
        self.max_health = 1
        self.damage = 10
    def update(self, dt=0.016, game=None):
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0:
            self.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))

class Bird(BaseEntity):
    def __init__(self, **kwargs):
        super(Bird, self).__init__(
            source=f"{IMAGES_PATH}/bird.png", 
            size=(80, 80), 
            **kwargs
        )
        self.pos = (randint(Window.width, Window.width + 800), randint(Window.height - 300, Window.height - 150))
        self.speed = randint(2, 5)
    
    def update(self, dt=0.016):  # ✅ إضافة dt كمعلمة اختيارية
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0:
            self.pos = (Window.width + randint(0, 200), randint(Window.height - 300, Window.height - 150))
    
    def update(self, dt=0.016):
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0:
            self.pos = (Window.width + randint(0, 200), randint(Window.height - 300, Window.height - 150))

# ---------------- Enemy Map ----------------
enemy_map = {
    "fast": EnemyFast,
    "armor": EnemyArmor,
    "bomber": EnemyBomber,
    "ghost": EnemyGhost
}