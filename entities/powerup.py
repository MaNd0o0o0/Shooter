"""powerup.py - العناصر القابلة للجمع"""
from entities.base_entity import BaseEntity
from config import POWERUP_SIZE, COIN_SIZE, SCROLL_SPEEDS

class PowerUp(BaseEntity):
    ICONS = {"speed":"powerup_speed.png","shield":"powerup_shield.png","bomb":"powerup_bomb.png","freeze":"powerup_freeze.png","health":"powerup_health.png"}
    def __init__(self, pos, power_type="speed", **kwargs):
        super().__init__(source=self.ICONS.get(power_type,"coin.png"), size=POWERUP_SIZE, pos=pos, **kwargs)
        self.power_type, self.speed = power_type, SCROLL_SPEEDS['items']
    def update(self, dt): self.pos = (self.x - self.speed, self.y)
class Coin(BaseEntity):
    def __init__(self, pos, **kwargs):
        super().__init__(source="coin.png", size=COIN_SIZE, pos=pos, **kwargs); self.speed = SCROLL_SPEEDS['items']
    def update(self, dt): self.pos = (self.x - self.speed, self.y)

class Collectible(BaseEntity):
    def __init__(self, source, pos, **kwargs):
        super().__init__(source=source, size=COIN_SIZE, pos=pos, **kwargs); self.speed = SCROLL_SPEEDS['items']
    def update(self, dt): self.pos = (self.x - self.speed, self.y)