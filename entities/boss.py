"""boss.py - نظام البوس"""
from entities.base_entity import BaseEntity
from entities.bullet import BossBullet
from config import BOSS_SIZE, BOSS_LEVELS, WINDOW_WIDTH, WINDOW_HEIGHT

class Boss(BaseEntity):
    IMAGES = {"normal":"boss.png","fire":"boss_fire.png","ice":"boss_ice.png","electric":"boss_electric.png","final":"boss_final.png"}
    def __init__(self, boss_type="normal", **kwargs):
        super().__init__(source=self.IMAGES.get(boss_type,self.IMAGES["normal"]), size=BOSS_SIZE, **kwargs)
        self.boss_type, self.health, self.max_health = boss_type, 300, 300
        self.pos = (WINDOW_WIDTH-600, WINDOW_HEIGHT/2-250); self.active = False
        self.shoot_timer, self.shoot_interval, self.move_dir, self.move_timer, self.entry_timer = 0, 2.0, 1, 0, 0
    def update(self, dt, player_pos=None, game=None):
        if not self.active: return
        if self.entry_timer < 2.0:
            self.entry_timer += dt
            if self.x > WINDOW_WIDTH-600: self.pos = (self.x-3, self.y)
            return
        self.move_timer += dt
        if self.move_timer > 3: self.move_dir *= -1; self.move_timer = 0
        ny = self.y + self.move_dir*2
        if 200 <= ny <= WINDOW_HEIGHT-300-self.height: self.pos = (self.x, ny)
        if self.shoot_timer >= self.shoot_interval and player_pos and game: self._shoot(player_pos, game); self.shoot_timer = 0
    def _shoot(self, player_pos, game):
        b = BossBullet(pos=(self.x, self.center_y), target_pos=player_pos)
        game.boss_bullets.append(b); game.add_widget(b); game.audio.play_sfx('shoot')