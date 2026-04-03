"""
combat_system.py - نظام القتال والتصادم (نسخة محسنة للأداء)
"""

import math
import random
from kivy.core.window import Window


class CombatSystem:
    """نظام القتال - محسن للأداء مع تقليل عمليات التصادم"""
    
    def __init__(self):
        self.game_world = None
        self.event_bus = None
        self.pool_manager = None
        self.game = None
        
        # تأثيرات مؤقتة
        self.shield_active = False
        self.shield_timer = 0
        self.speed_active = False
        self.speed_timer = 0
        self.freeze_active = False
        self.freeze_timer = 0
        
        # إحصائيات
        self.combo = 0
        self.combo_timer = 0
        self.damage_multiplier = 1.0
        
        # ✅ عداد للإطارات (لتقليل العمليات)
        self.frame_counter = 0
    
    def set_game_world(self, game_world):
        self.game_world = game_world
    
    def set_event_bus(self, event_bus):
        self.event_bus = event_bus
    
    def set_pool_manager(self, pool_manager):
        self.pool_manager = pool_manager
    
    def set_game(self, game):
        self.game = game
    
    def update(self, dt):
        """تحديث القتال - مع تحسينات الأداء"""
        self._update_timers(dt)
        self._update_combo(dt)
        
        # ✅ تحديث التصادمات كل إطارين فقط (تقليل الحمل 50%)
        self.frame_counter += 1
        if self.frame_counter % 2 == 0:
            self._check_collisions_optimized()
    
    def _update_timers(self, dt):
        """تحديث المؤقتات"""
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
                if self.game:
                    for enemy in self.game.enemies:
                        if hasattr(enemy, 'unfreeze'):
                            enemy.unfreeze()
    
    def _update_combo(self, dt):
        """تحديث الكومبو"""
        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo = 0
    
    def _check_collisions_optimized(self):
        """🔥 نسخة محسنة من فحص التصادمات - تقليل العمليات بشكل كبير"""
        if not self.game:
            return
        
        # ✅ 1. تحديث الرصاصات أولاً (كل إطارين)
        if hasattr(self.game, 'update_bullets'):
            self.game.update_bullets(0.033)
        if hasattr(self.game, 'update_boss_bullets'):
            self.game.update_boss_bullets(0.033)
        
        # ✅ 2. الحصول على القوائم
        bullets = self.game.bullets
        enemies = self.game.enemies
        player = self.game.player
        
        if not bullets or not enemies:
            return
        
        # ✅ 3. تحديد الحد الأقصى للفحص (أول 15 فقط)
        max_bullets_to_check = min(len(bullets), 20)
        max_enemies_to_check = min(len(enemies), 20)
        
        bullets_to_check = bullets[:max_bullets_to_check]
        enemies_to_check = enemies[:max_enemies_to_check]
        
        # ✅ 4. فحص تصادم الرصاص مع الأعداء (باستخدام المسافة)
        for bullet in bullets_to_check[:]:
            if getattr(bullet, 'hit', False) or not bullet.active:
                continue
            
            bullet_center_x = bullet.center_x
            bullet_center_y = bullet.center_y
            
            for enemy in enemies_to_check[:]:
                if not enemy.active:
                    continue
                
                # ✅ فلترة سريعة جداً باستخدام المسافة (بدون collide_widget)
                dx = bullet_center_x - enemy.center_x
                dy = bullet_center_y - enemy.center_y
                distance_sq = dx*dx + dy*dy
                
                # نصف قطر التصادم 50 بكسل
                if distance_sq < 2500:  # 50^2
                    self._handle_bullet_hit_fast(bullet, enemy)
                    break
        
        # ✅ 5. فحص تصادم اللاعب مع الأعداء
        if player and player.active:
            player_center_x = player.center_x
            player_center_y = player.center_y
            
            for enemy in enemies_to_check[:]:
                if not enemy.active:
                    continue
                
                dx = player_center_x - enemy.center_x
                dy = player_center_y - enemy.center_y
                distance_sq = dx*dx + dy*dy
                
                # نصف قطر التصادم 80 بكسل
                if distance_sq < 6400:  # 80^2
                    self._handle_enemy_collision_fast(enemy)
    
    def _handle_bullet_hit_fast(self, bullet, enemy):
        """معالجة إصابة الرصاصة للعدو - نسخة سريعة"""
        bullet.hit = True
        
        damage = 2 if self.freeze_active else 1
        enemy.health -= damage
        
        # تطبيق stun بسيط
        enemy.stun_timer = 0.1
        
        if enemy.health <= 0:
            self._kill_enemy_fast(enemy)
        else:
            if hasattr(enemy, 'hit_animation'):
                enemy.hit_animation()
        
        # إزالة الرصاصة
        if bullet in self.game.bullets:
            self.game.bullets.remove(bullet)
            if bullet.parent:
                bullet.parent.remove_widget(bullet)
    
    def _handle_enemy_collision_fast(self, enemy):
        """معالجة تصادم اللاعب مع العدو - نسخة سريعة"""
        player = self.game.player
        
        # التحقق من الـ invincible
        if hasattr(player, 'invincible') and player.invincible:
            return
        
        # التحقق من مؤقت التصادم
        if hasattr(self.game, 'collision_timer') and self.game.collision_timer > 0:
            return
        
        # ضرر للاعب
        if not self.shield_active:
            if self.game_world:
                self.game_world.take_damage(enemy.damage)
            self.combo = 0
            self.game.collision_timer = 0.5
            
            # جعل اللاعب غير قابل للإصابة مؤقتاً
            if hasattr(player, 'set_invincible'):
                player.set_invincible(1.0)
        
        # 💀 قتل العدو عند التصادم
        self._kill_enemy_fast(enemy)
        
        # تأثيرات
        if hasattr(player, 'hit_animation'):
            player.hit_animation()
        
        if hasattr(self.game, 'play_sound') and hasattr(self.game, 'explosion_sound'):
            self.game.play_sound(self.game.explosion_sound)
    
    def _kill_enemy_fast(self, enemy):
        """قتل عدو بسرعة - بدون عمليات إضافية"""
        from entities.effects import Explosion
        
        # انفجار سريع
        explosion = Explosion(pos=enemy.pos, size=60)
        if self.game:
            self.game.add_widget(explosion)
        
        # إزالة العدو
        if enemy in self.game.enemies:
            self.game.enemies.remove(enemy)
        if enemy.parent:
            enemy.parent.remove_widget(enemy)
        
        # زيادة الإحصائيات
        self.combo += 1
        self.combo_timer = 2.0
        
        if self.game_world:
            self.game_world.score += 10
            self.game_world.xp += 15
        
        if self.game:
            self.game.total_kills += 1
        
        # إطلاق حدث
        if self.event_bus:
            self.event_bus.emit('enemy_killed', {
                'type': getattr(enemy, 'enemy_type', 'normal'),
                'position': enemy.pos,
                'combo': self.combo
            })
    
    def _handle_boss_hit(self, bullet):
        """معالجة إصابة البوس"""
        bullet.hit = True
        
        damage = 2 if self.freeze_active else 1
        self.game.boss.health -= damage
        
        if hasattr(self.game.boss, 'hit_animation'):
            self.game.boss.hit_animation()
        
        if self.game.boss.health <= 0:
            self._kill_boss()
        
        if bullet in self.game.bullets:
            self.game.bullets.remove(bullet)
            if bullet.parent:
                bullet.parent.remove_widget(bullet)
    
    def _kill_boss(self):
        """قتل البوس"""
        from entities.effects import Explosion
        
        if self.game and self.game.boss:
            explosion = Explosion(pos=self.game.boss.pos, size=150)
            self.game.add_widget(explosion)
        
        self.combo = 0
        
        if self.game_world:
            self.game_world.score += 30
            self.game_world.xp += 50
            self.game_world.coins += 50
        
        if self.game and self.game.boss and self.game.boss.parent:
            self.game.boss.parent.remove_widget(self.game.boss)
        if self.game:
            self.game.boss = None
        
        if self.event_bus:
            self.event_bus.emit('boss_defeated', {})
    
    def activate_powerup(self, power_type: str):
        """تفعيل الباور أب"""
        if power_type == "speed":
            self.speed_active = True
            self.speed_timer = 10
        elif power_type == "shield":
            self.shield_active = True
            self.shield_timer = 10
        elif power_type == "freeze":
            self.freeze_active = True
            self.freeze_timer = 5
            if self.game:
                for enemy in self.game.enemies:
                    if hasattr(enemy, 'freeze'):
                        enemy.freeze()
        elif power_type == "bomb":
            if self.game:
                for enemy in self.game.enemies[:]:
                    self._kill_enemy_fast(enemy)
        elif power_type == "health":
            if self.game_world:
                self.game_world.heal(50)
        
        if self.event_bus:
            self.event_bus.emit('powerup_activated', power_type)
    
    def has_shield(self) -> bool:
        return self.shield_active
    
    def has_speed(self) -> bool:
        return self.speed_active
    
    def has_freeze(self) -> bool:
        return self.freeze_active
    
    def reset(self):
        """إعادة تعيين نظام القتال"""
        self.shield_active = False
        self.speed_active = False
        self.freeze_active = False
        self.combo = 0
        self.combo_timer = 0
        self.damage_multiplier = 1.0
        self.frame_counter = 0