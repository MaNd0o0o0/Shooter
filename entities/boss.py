from kivy.core.window import Window
from entities.base_entity import BaseEntity
from entities.bullet import BossBullet
from config import IMAGES_PATH, BOSS_SIZE, BOSS_HEALTH

class Boss(BaseEntity):
    def __init__(self, boss_type="normal", **kwargs):
        self.boss_type = boss_type
        boss_images = {
            "normal": f"{IMAGES_PATH}/boss.png",
            "fire": f"{IMAGES_PATH}/boss_fire.png",
            "ice": f"{IMAGES_PATH}/boss_ice.png",
            "electric": f"{IMAGES_PATH}/boss_electric.png",
            "final": f"{IMAGES_PATH}/boss_final.png"
        }
        image = boss_images.get(boss_type, f"{IMAGES_PATH}/boss.png")
        super(Boss, self).__init__(source=image, size=BOSS_SIZE, **kwargs)
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.pos = (Window.width - 600, Window.height/2 - 250)
        self.active = False
        self.shoot_timer = 0
        self.shoot_interval = 2.0
        self.move_direction = 1
        self.move_timer = 0
        self.entry_timer = 0
    
    def update(self, dt=0.016, player_pos=None, game=None):
        if not self.active:
            return
        if self.entry_timer < 2.0:
            self.entry_timer += dt
            if self.x > Window.width - 600:
                self.pos = (self.x - 3, self.y)
            return
        self.move_timer += dt
        if self.move_timer > 3:
            self.move_direction *= -1
            self.move_timer = 0
        new_y = self.y + self.move_direction * 2
        if 250 <= new_y <= Window.height - 350:
            self.pos = (self.x, new_y)
            self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_interval and player_pos and game:
            self.shoot(player_pos, game)
            self.shoot_timer = 0
    
    def shoot(self, player_pos, game):
        from core.audio_manager import shoot_sound
        bullet = BossBullet(pos=(self.x, self.center_y), target_pos=player_pos)
        game.boss_bullets.append(bullet)
        game.add_widget(bullet)
        game.play_sound(shoot_sound)