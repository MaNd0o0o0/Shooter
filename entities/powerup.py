from entities.base_entity import BaseEntity
from config import IMAGES_PATH

class PowerUp(BaseEntity):
    def __init__(self, pos, power_type="speed", **kwargs):
        self.power_type = power_type
        icons = {
            "speed": f"{IMAGES_PATH}/powerup_speed.png",
            "shield": f"{IMAGES_PATH}/powerup_shield.png",
            "bomb": f"{IMAGES_PATH}/powerup_bomb.png",
            "freeze": f"{IMAGES_PATH}/powerup_freeze.png",
            "health": f"{IMAGES_PATH}/powerup_health.png"
        }
        icon = icons.get(power_type, f"{IMAGES_PATH}/coin.png")
        super(PowerUp, self).__init__(source=icon, size=(80, 80), pos=pos, **kwargs)
    
    def update(self, dt=0.016):
        self.pos = (self.x - 2, self.y)

class Coin(BaseEntity):
    def __init__(self, pos, **kwargs):
        super(Coin, self).__init__(source=f"{IMAGES_PATH}/coin.png", size=(100, 100), pos=pos, **kwargs)
    
    def update(self, dt=0.016):
        self.pos = (self.x - 2, self.y)

class Gun(BaseEntity):
    def __init__(self, pos, **kwargs):
        super(Gun, self).__init__(source=f"{IMAGES_PATH}/gun.png", size=(100, 100), pos=pos, **kwargs)
    
    def update(self, dt=0.016):
        self.pos = (self.x - 2, self.y)

class Medical(BaseEntity):
    def __init__(self, pos, **kwargs):
        super(Medical, self).__init__(source=f"{IMAGES_PATH}/medical.png", size=(100, 100), pos=pos, **kwargs)
    
    def update(self, dt=0.016):
        self.pos = (self.x - 2, self.y)