"""enemy.py - الأعداء"""
from entities.base_entity import BaseEntity
from config import ENEMY_SIZES, WINDOW_WIDTH, WINDOW_HEIGHT
from random import randint

class BaseEnemy(BaseEntity):
    def __init__(self, source, size, speed, health, damage, **kwargs):
        super().__init__(source=source, size=size, **kwargs)
        self.speed, self.health, self.max_health, self.damage = speed, health, health, damage
        self._spawn()
    def _spawn(self): self.pos = (randint(WINDOW_WIDTH, WINDOW_WIDTH+400), randint(250, WINDOW_HEIGHT-150))
    def update(self, dt):
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0: self._spawn()

class EnemyFast(BaseEnemy):
    def __init__(self,**kw): super().__init__("enemy_fast.png",ENEMY_SIZES['fast'],randint(6,10),1,5,**kw)
class EnemyArmor(BaseEnemy):
    def __init__(self,**kw): super().__init__("enemy_armor.png",ENEMY_SIZES['armor'],2,5,8,**kw)
class EnemyBomber(BaseEnemy):
    def __init__(self,**kw): super().__init__("enemy_bomber.png",ENEMY_SIZES['bomber'],3,2,10,**kw)
class EnemyGhost(BaseEnemy):
    def __init__(self,**kw):
        super().__init__("enemy_ghost.png",ENEMY_SIZES['ghost'],4,2,7,**kw)
        self.visible, self.invisible_timer = True, 0
    def update(self, dt):
        super().update(dt)
        self.invisible_timer += dt
        if self.invisible_timer > 3: self.visible = not self.visible; self.opacity = 1.0 if self.visible else 0.3; self.invisible_timer = 0

ENEMY_TYPES = {"fast":EnemyFast,"armor":EnemyArmor,"bomber":EnemyBomber,"ghost":EnemyGhost,"normal":lambda **kw:BaseEnemy("enemy.png",ENEMY_SIZES['normal'],4,1,10,**kw)}