"""
powerup.py - الباوربس والعناصر
"""

from kivy.uix.image import Image
from config import IMAGES_PATH, POWERUP_IMAGES


class PowerUp(Image):
    """باور أب"""
    
    def __init__(self, pos, power_type="speed", **kwargs):
        self.power_type = power_type
        icon = POWERUP_IMAGES.get(power_type, "powerup_speed.png")
        super().__init__(source=f"{IMAGES_PATH}/{icon}", size=(70, 70), pos=pos, **kwargs)
        self.active = True
    
    def update(self, dt=0.016):
        """تحديث حركة الباور أب"""
        if self.active:
            self.x -= 2
            if self.x < -100:
                self.active = False


class Coin(Image):
    """عملة"""
    
    def __init__(self, pos, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/coin.png", size=(60, 60), pos=pos, **kwargs)
        self.active = True
    
    def update(self, dt=0.016):
        """تحديث حركة العملة"""
        if self.active:
            self.x -= 2
            if self.x < -100:
                self.active = False


class Gun(Image):
    """تطوير الرصاص"""
    
    def __init__(self, pos, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/gun.png", size=(60, 60), pos=pos, **kwargs)
        self.active = True
    
    def update(self, dt=0.016):
        """تحديث حركة التطوير"""
        if self.active:
            self.x -= 2
            if self.x < -100:
                self.active = False


class Medical(Image):
    """علاج"""
    
    def __init__(self, pos, **kwargs):
        super().__init__(source=f"{IMAGES_PATH}/medical.png", size=(60, 60), pos=pos, **kwargs)
        self.active = True
    
    def update(self, dt=0.016):
        """تحديث حركة العلاج"""
        if self.active:
            self.x -= 2
            if self.x < -100:
                self.active = False