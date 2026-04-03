"""
game_world.py - منطق اللعبة وإدارة الكيانات
"""

from kivy.core.window import Window
from typing import List, Optional, Dict, Any
from random import randint, choice
import math


class GameWorld:
    """يدير منطق اللعبة والكيانات والفيزياء"""
    
    def __init__(self):
        # حالة اللاعب
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.coins = 0
        self.xp = 0
        self.level = 1
        self.bullets_count = 1
        self.total_kills = 0
        self.bosses_defeated = 0
        
        # قوائم الكيانات
        self.bullets: List = []
        self.boss_bullets: List = []
        self.enemies: List = []
        self.coins_list: List = []
        self.guns: List = []
        self.medicals: List = []
        self.powerups: List = []
        self.particles: List = []
        
        # البوس
        self.boss = None
        self.boss_type = "normal"
        
        # المؤثرات
        self.shield_active = False
        self.shield_timer = 0
        self.speed_active = False
        self.speed_timer = 0
        self.freeze_active = False
        self.freeze_timer = 0
        
        # القتال
        self.combo = 0
        self.combo_timer = 0
        self.temp_bullet_timer = 0
        self.base_bullets = 1
        
        # الموجات
        self.wave = 1
        self.enemies_to_spawn = 10
        self.enemies_spawned = 0
        self.enemies_killed_in_wave = 0
        self.spawn_timer = 0
        self.spawn_delay = 1.5
        self.wave_in_progress = False
        self.boss_wave = False
        
        # إطلاق النار
        self.fire_delay = 0
        self.fire_rate = 0.18
        self.fire_button_pressed = False
        
        # مراجع
        self.player = None
        self.pool_manager = None
        self.event_callback = None
        self.event_bus = None
    
    def set_player(self, player):
        self.player = player
    
    def set_pool_manager(self, pool_manager):
        self.pool_manager = pool_manager
    
    def set_event_callback(self, callback):
        self.event_callback = callback
    
    def set_event_bus(self, event_bus):
        self.event_bus = event_bus
    
    def start_wave(self, wave_number: int):
        """بدء موجة جديدة"""
        self.wave = wave_number
        self.enemies_spawned = 0
        self.enemies_killed_in_wave = 0
        self.wave_in_progress = True
        
        if wave_number <= 3:
            self.enemies_to_spawn = 5 + wave_number * 2
        elif wave_number <= 6:
            self.enemies_to_spawn = 12 + (wave_number - 3) * 3
        else:
            self.enemies_to_spawn = 20 + (wave_number - 6) * 2
        
        self.boss_wave = (wave_number % 5 == 0)
        
        if self.boss_wave:
            self.enemies_to_spawn = max(5, self.enemies_to_spawn // 2)
        
        self._emit_event('wave_started', {
            'wave': wave_number,
            'enemies': self.enemies_to_spawn,
            'is_boss_wave': self.boss_wave
        })
    
    def update(self, dt: float):
        """تحديث منطق اللعبة"""
        self._update_timers(dt)
        self._update_wave(dt)
        
        # تحديث الكومبو
        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo = 0
        
        # تحديث إطلاق النار
        if self.fire_button_pressed:
            self.fire_delay += dt
            fire_rate = self.fire_rate * (0.7 if self.speed_active else 1.0)
            if self.fire_delay > fire_rate:
                self.fire()
                self.fire_delay = 0
        
        # تحديث الرصاصات المؤقتة
        if self.temp_bullet_timer > 0:
            self.temp_bullet_timer -= dt
            if self.temp_bullet_timer <= 0 and self.bullets_count > self.base_bullets:
                self.bullets_count = self.base_bullets
    
    def _update_timers(self, dt: float):
        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.speed_active:
            self.speed_timer -= dt
            if self.speed_timer <= 0:
                self.speed_active = False
        
        if self.freeze_active:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.freeze_active = False
                for enemy in self.enemies:
                    if hasattr(enemy, 'unfreeze'):
                        enemy.unfreeze()
    
    def _update_wave(self, dt: float):
        if not self.wave_in_progress:
            return
        
        if self.enemies_killed_in_wave >= self.enemies_to_spawn:
            self._complete_wave()
            return
        
        if self.enemies_spawned < self.enemies_to_spawn:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                self._spawn_enemy()
                self.enemies_spawned += 1
    
    def _spawn_enemy(self):
        if not self.pool_manager:
            return
        
        enemy_type = self._select_enemy_type()
        x = randint(Window.width, Window.width + 400)
        y = randint(100, Window.height - 100)
        
        enemy = self.pool_manager.get_enemy(enemy_type, (x, y))
        if enemy:
            self.enemies.append(enemy)
            self._emit_event('enemy_spawned', {'type': enemy_type, 'position': (x, y)})
        
        if self.boss_wave and self.enemies_spawned >= self.enemies_to_spawn and not self.boss:
            self._spawn_boss()
    
    def _spawn_boss(self):
        if not self.pool_manager:
            return
        
        if self.wave >= 15:
            boss_type = choice(['normal', 'fire', 'ice', 'electric', 'final'])
        elif self.wave >= 10:
            boss_type = choice(['normal', 'fire', 'ice', 'electric'])
        elif self.wave >= 5:
            boss_type = choice(['normal', 'fire', 'ice'])
        else:
            boss_type = 'normal'
        
        self.boss = self.pool_manager.get_boss(boss_type)
        self.boss_type = boss_type
        self._emit_event('boss_spawned', {'type': boss_type, 'wave': self.wave})
    
    def _select_enemy_type(self) -> str:
        if self.wave >= 10:
            return choice(['soldier', 'fast', 'armor', 'bomber', 'ghost'])
        elif self.wave >= 5:
            return choice(['soldier', 'fast', 'armor', 'bomber'])
        elif self.wave >= 3:
            return choice(['soldier', 'fast', 'armor'])
        else:
            return choice(['soldier', 'fast'])
    
    def _complete_wave(self):
        self.wave_in_progress = False
        bonus = self.wave * 20
        self.coins += bonus
        self.score += bonus * 10
        self._emit_event('wave_completed', {
            'wave': self.wave,
            'bonus': bonus,
            'next_wave': self.wave + 1
        })
    
    def fire(self):
        if not self.player or not self.pool_manager:
            return
        
        angles = self._calculate_angles()
        for angle in angles:
            bullet = self.pool_manager.get_bullet(
                pos=(self.player.right, self.player.center_y),
                angle=angle
            )
            if bullet:
                self.bullets.append(bullet)
        
        self._emit_event('bullets_fired', {'count': len(angles)})
    
    def _calculate_angles(self) -> List[float]:
        n = self.bullets_count
        if n == 1:
            return [0]
        elif n == 2:
            return [-6, 6]
        elif n == 3:
            return [-12, 0, 12]
        elif n == 4:
            return [-18, -6, 6, 18]
        else:
            return [-24, -12, 0, 12, 24]
    
    def handle_enemy_death(self, enemy):
        self.total_kills += 1
        self.enemies_killed_in_wave += 1
        self.combo += 1
        self.combo_timer = 2.0
        self.score += 10
        self.xp += 15
        
        if self.xp >= self.level * 100:
            self.level_up()
        
        self._spawn_loot(enemy.pos)
        
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        
        self._emit_event('enemy_killed', {
            'type': getattr(enemy, 'enemy_type', 'normal'),
            'position': enemy.pos,
            'combo': self.combo
        })
    
    def handle_boss_death(self):
        self.bosses_defeated += 1
        self.score += 30
        self.xp += 50
        self.coins += 50
        self.enemies_killed_in_wave = self.enemies_to_spawn
        self.boss = None
        self._emit_event('boss_defeated', {
            'type': self.boss_type,
            'wave': self.wave
        })
    
    def level_up(self):
        self.level += 1
        self.xp = 0
        self.max_health += 20
        self.health = self.max_health
        
        if self.level % 3 == 0 and self.base_bullets < 5:
            self.base_bullets += 1
            self.bullets_count = self.base_bullets
        
        self._emit_event('level_up', {
            'level': self.level,
            'max_health': self.max_health,
            'bullets': self.bullets_count
        })
    
    def take_damage(self, amount: int):
        if self.shield_active:
            self._emit_event('damage_blocked', {'amount': amount})
            return
        
        self.health -= amount
        if self.health < 0:
            self.health = 0
        
        self._emit_event('player_damaged', {
            'damage': amount,
            'current_health': self.health,
            'max_health': self.max_health
        })
        
        if self.player:
            self.player.hit_animation()
        
        if self.health <= 0:
            self.game_over()
    
    def heal(self, amount: int):
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        self._emit_event('player_healed', {
            'amount': self.health - old_health,
            'current_health': self.health
        })
    
    def activate_powerup(self, power_type: str):
        if power_type == "speed":
            self.speed_active = True
            self.speed_timer = 10
        elif power_type == "shield":
            self.shield_active = True
            self.shield_timer = 10
        elif power_type == "freeze":
            self.freeze_active = True
            self.freeze_timer = 5
            for enemy in self.enemies:
                if hasattr(enemy, 'freeze'):
                    enemy.freeze()
        elif power_type == "bomb":
            for enemy in self.enemies[:]:
                self.handle_enemy_death(enemy)
        elif power_type == "health":
            self.heal(50)
        
        self._emit_event('powerup_activated', {'type': power_type})
    
    def _spawn_loot(self, pos):
        if not self.pool_manager:
            return
        
        rnd = randint(1, 100)
        if rnd <= 35:
            coin = self.pool_manager.get_coin(pos)
            if coin:
                self.coins_list.append(coin)
        elif rnd <= 50:
            gun = self.pool_manager.get_gun(pos)
            if gun:
                self.guns.append(gun)
        elif rnd <= 65:
            medical = self.pool_manager.get_medical(pos)
            if medical:
                self.medicals.append(medical)
        elif rnd <= 85:
            power_type = choice(["speed", "shield", "bomb", "freeze", "health"])
            powerup = self.pool_manager.get_powerup(pos, power_type)
            if powerup:
                self.powerups.append(powerup)
    
    def game_over(self):
        self.wave_in_progress = False
        self._emit_event('game_over', {
            'score': self.score,
            'coins': self.coins,
            'level': self.level,
            'kills': self.total_kills,
            'bosses': self.bosses_defeated
        })
    
    def reset(self):
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.coins = 0
        self.xp = 0
        self.level = 1
        self.bullets_count = 1
        self.base_bullets = 1
        self.total_kills = 0
        self.bosses_defeated = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_killed_in_wave = 0
        self.wave_in_progress = False
        self.boss = None
        self.shield_active = False
        self.speed_active = False
        self.freeze_active = False
        self.combo = 0
        
        self.bullets.clear()
        self.boss_bullets.clear()
        self.enemies.clear()
        self.coins_list.clear()
        self.guns.clear()
        self.medicals.clear()
        self.powerups.clear()
        self.particles.clear()
    
    def _emit_event(self, event_name: str, data: Any = None):
        if self.event_callback:
            self.event_callback(event_name, data)
        if self.event_bus:
            self.event_bus.emit(event_name, data)
    
    def get_state(self) -> Dict:
        return {
            'health': self.health,
            'max_health': self.max_health,
            'score': self.score,
            'coins': self.coins,
            'xp': self.xp,
            'level': self.level,
            'wave': self.wave,
            'bullets_count': self.bullets_count,
            'total_kills': self.total_kills,
            'combo': self.combo,
            'shield_active': self.shield_active,
            'speed_active': self.speed_active,
            'freeze_active': self.freeze_active,
            'wave_progress': self.enemies_killed_in_wave / self.enemies_to_spawn if self.enemies_to_spawn > 0 else 0
        }