from kivy.core.window import Window
from entities.base_entity import BaseEntity
from config import IMAGES_PATH, PLAYER_SIZE, PLAYER_START_POS

class Player(BaseEntity):
    def __init__(self, skin="default", **kwargs):
        skin_images = {
            "default": f"{IMAGES_PATH}/player.png",
            "blue": f"{IMAGES_PATH}/player_blue.png",
            "red": f"{IMAGES_PATH}/player_red.png",
            "gold": f"{IMAGES_PATH}/player_gold.png",
            "green": f"{IMAGES_PATH}/player_green.png"
        }
        image = skin_images.get(skin, f"{IMAGES_PATH}/player.png")
        super(Player, self).__init__(source=image, size=PLAYER_SIZE, **kwargs)
        self.pos = PLAYER_START_POS
        self.skin = skin
        self.health = 100
        self.max_health = 100
        self.speed_multiplier = 1.0
        self.shield_active = False