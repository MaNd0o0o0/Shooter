"""player.py - اللاعب"""
from entities.base_entity import BaseEntity
from config import PLAYER_SIZE, PLAYER_SPEED, BOUNDS

class Player(BaseEntity):
    SKINS = {"default":"player.png","blue":"player_blue.png","red":"player_red.png","gold":"player_gold.png","green":"player_green.png"}
    def __init__(self, skin="default", **kwargs):
        super().__init__(source=self.SKINS.get(skin,self.SKINS["default"]), size=PLAYER_SIZE, **kwargs)
        self.skin, self.speed, self.bullets_count, self.shield_active = skin, PLAYER_SPEED, 1, False
        self.pos = (120, BOUNDS['bottom']+50)
    def move(self, dx, dy, mult=1.0):
        self.pos = (max(BOUNDS['left'],min(self.x+dx*self.speed*mult, BOUNDS['right']-self.width)), max(BOUNDS['bottom'],min(self.y+dy*self.speed*mult, BOUNDS['top']-self.height)))
    def change_skin(self, name):        if name in self.SKINS: self.source = self.SKINS[name]; self.skin = name