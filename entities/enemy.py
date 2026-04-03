"""
enemy.py - الأعداء (مع Knockback و Stun حقيقي)
"""

from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from config import IMAGES_PATH
from random import randint


class BaseEnemy(Image):
    """كلاس أساسي للأعداء"""

    def __init__(self, image, size, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/{image}", size=size, **kwargs)

        self.health = 1
        self.max_health = 1
        self.speed = 4
        self.damage = 5
        self.reward = 10
        self.active = True
        self.frozen = False
        self.cpp_id = -1
        
        # خصائص knockback و stun
        self.stun_timer = 0
        self.knockback_timer = 0
        self.knockback_x = 0
        self.knockback_y = 0

        self._reset_position()

    def _reset_position(self):
        self.x = randint(Window.width, Window.width + 400)
        self.y = randint(100, Window.height - 100)

    def update(self, dt, player):
        if not self.active:
            return
        
        # 💥 KNOCKBACK أولاً
        if self.knockback_timer > 0:
            self.x += self.knockback_x * dt
            self.y += self.knockback_y * dt
            self.knockback_timer -= dt
            self.opacity = 0.7
            return
        
        # 🛑 STUN ثانياً
        if self.stun_timer > 0:
            self.stun_timer -= dt
            self.opacity = 0.5
            return
        
        self.opacity = 1.0
        self.x -= self.speed
        
        if self.right < 0:
            self._reset_position()

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def freeze(self):
        if hasattr(self, '_saved_speed'):
            return
        self._saved_speed = self.speed
        self.speed = 0
        self.frozen = True

    def unfreeze(self):
        if hasattr(self, '_saved_speed') and self._saved_speed is not None:
            self.speed = self._saved_speed
            self._saved_speed = None
            self.frozen = False
    
    def hit_animation(self):
        self.opacity = 0.5
        Clock.schedule_once(lambda dt: setattr(self, 'opacity', 1), 0.1)


class Enemy(BaseEnemy):
    """العدو الرئيسي"""
    
    def __init__(self, enemy_type="soldier", **kwargs):
        images = {
            "soldier": ("enemy.png", (80, 80), 1, 4, 5, 10),
            "armor": ("enemy_armor.png", (95, 95), 3, 2, 8, 25),
            "fast": ("enemy_fast.png", (70, 70), 1, 6, 5, 15),
            "bomber": ("enemy_bomber.png", (85, 85), 2, 3, 10, 20),
            "ghost": ("enemy_ghost.png", (80, 80), 2, 4, 7, 18),
        }

        image, size, health, speed, damage, reward = images.get(
            enemy_type, images["soldier"]
        )

        super().__init__(image, size, **kwargs)

        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.reward = reward
        self.enemy_type = enemy_type
        self.invisible_timer = 0
        self.visible = True
        
        self.stun_timer = 0
        self.knockback_timer = 0
        self.knockback_x = 0
        self.knockback_y = 0

        self._reset_position()


class EnemyFast(Enemy):
    def __init__(self, **kwargs):
        super().__init__("fast", **kwargs)


class EnemyArmor(Enemy):
    def __init__(self, **kwargs):
        super().__init__("armor", **kwargs)


class EnemyBomber(Enemy):
    def __init__(self, **kwargs):
        super().__init__("bomber", **kwargs)


class EnemyGhost(Enemy):
    def __init__(self, **kwargs):
        super().__init__("ghost", **kwargs)


enemy_map = {
    "soldier": lambda: Enemy("soldier"),
    "fast": EnemyFast,
    "armor": EnemyArmor,
    "bomber": EnemyBomber,
    "ghost": EnemyGhost,
}