"""
pool_manager.py - إدارة تجمعات الكائنات باستخدام C++
"""

from typing import List, Optional, Dict
from random import randint
from core.physics_manager import PhysicsManager


class PoolManager:
    """مدير تجمعات الكائنات - يستخدم C++ كلما أمكن"""
    
    def __init__(self, game):
        self.game = game
        # ✅ إضافة width و height للعبة
        if hasattr(game, 'width'):
            self.physics = PhysicsManager(game.width, game.height)
        else:
            from kivy.core.window import Window
            self.physics = PhysicsManager(Window.width, Window.height)
        
        self.bullet_pool = []
        self.boss_bullet_pool = []
        self.enemy_pools: Dict[str, List] = {}
        self.coin_pool = []
        self.gun_pool = []
        self.medical_pool = []
        self.powerup_pool = []
        
        self.pool_sizes = {
            'bullet': 200,
            'boss_bullet': 100,
            'enemy': 100,
            'coin': 50,
            'gun': 20,
            'medical': 20,
            'powerup': 50,
        }
        
        self._init_pools()
    
    def _init_pools(self):
        """تهيئة تجمعات الكائنات"""
        from entities.bullet import Bullet, BossBullet
        from entities.powerup import Coin, Gun, Medical, PowerUp
        from entities.enemy import Enemy
        
        # تجمع الرصاص (سيستخدم C++ إذا كان متاحاً)
        for _ in range(self.pool_sizes['bullet']):
            bullet = Bullet(pos=(0, 0), angle=0)
            bullet.active = False
            bullet.cpp_id = -1
            self.bullet_pool.append(bullet)
        
        # تجمع رصاص البوس
        for _ in range(self.pool_sizes['boss_bullet']):
            bullet = BossBullet(pos=(0, 0))
            bullet.active = False
            self.boss_bullet_pool.append(bullet)
        
        # تجمع الأعداء
        enemy_types = ['soldier', 'fast', 'armor', 'bomber', 'ghost']
        for etype in enemy_types:
            self.enemy_pools[etype] = []
            for _ in range(self.pool_sizes['enemy'] // len(enemy_types)):
                enemy = Enemy(etype)
                enemy.active = False
                enemy.cpp_id = -1
                self.enemy_pools[etype].append(enemy)
        
        # تجمع العملات
        for _ in range(self.pool_sizes['coin']):
            coin = Coin(pos=(0, 0))
            coin.active = False
            self.coin_pool.append(coin)
        
        # تجمع تطوير الرصاص
        for _ in range(self.pool_sizes['gun']):
            gun = Gun(pos=(0, 0))
            gun.active = False
            self.gun_pool.append(gun)
        
        # تجمع الشفاء
        for _ in range(self.pool_sizes['medical']):
            medical = Medical(pos=(0, 0))
            medical.active = False
            self.medical_pool.append(medical)
        
        # تجمع الباوربس
        power_types = ['speed', 'shield', 'bomb', 'freeze', 'health']
        for _ in range(self.pool_sizes['powerup'] // len(power_types)):
            for ptype in power_types:
                powerup = PowerUp(pos=(0, 0), power_type=ptype)
                powerup.active = False
                self.powerup_pool.append(powerup)
    
    def get_bullet(self, pos, angle):
        """الحصول على رصاصة - يستخدم C++ إذا أمكن"""
        # استخدام C++ للحصول على رصاصة
        if self.physics.is_available():
            cpp_id = self.physics.get_bullet(pos[0], pos[1], angle, 25, 2000)
            if cpp_id != -1:
                # البحث عن رصاصة غير نشطة لربطها بـ C++
                for bullet in self.bullet_pool:
                    if not bullet.active:
                        bullet.pos = pos
                        bullet.angle = angle
                        bullet.active = True
                        bullet.cpp_id = cpp_id
                        return bullet
        
        # نسخة Python احتياطية
        for bullet in self.bullet_pool:
            if not bullet.active:
                bullet.pos = pos
                bullet.angle = angle
                bullet.active = True
                bullet.hit = False
                bullet.distance_traveled = 0
                return bullet
        
        from entities.bullet import Bullet
        bullet = Bullet(pos=pos, angle=angle)
        self.bullet_pool.append(bullet)
        return bullet
    
    def get_boss_bullet(self, pos, target_pos=None):
        """الحصول على رصاصة بوس"""
        for bullet in self.boss_bullet_pool:
            if not bullet.active:
                bullet.pos = pos
                bullet.active = True
                bullet.hit = False
                bullet.distance_traveled = 0
                if target_pos:
                    import math
                    dx = target_pos[0] - pos[0]
                    dy = target_pos[1] - pos[1]
                    bullet.angle = math.degrees(math.atan2(dy, dx))
                return bullet
        
        from entities.bullet import BossBullet
        bullet = BossBullet(pos=pos, target_pos=target_pos)
        self.boss_bullet_pool.append(bullet)
        return bullet
    
    def return_bullet(self, bullet):
        """إعادة الرصاصة إلى التجمع"""
        if hasattr(bullet, 'cpp_id') and bullet.cpp_id != -1:
            self.physics.return_bullet(bullet.cpp_id)
            bullet.cpp_id = -1
        
        bullet.active = False
        if bullet.parent:
            bullet.parent.remove_widget(bullet)
    
    def return_boss_bullet(self, bullet):
        """إعادة رصاصة البوس إلى التجمع"""
        bullet.active = False
        if bullet.parent:
            bullet.parent.remove_widget(bullet)
    
    def get_enemy(self, enemy_type: str, pos):
        """الحصول على عدو"""
        if enemy_type in self.enemy_pools:
            for enemy in self.enemy_pools[enemy_type]:
                if not enemy.active:
                    enemy.pos = pos
                    enemy.health = enemy.max_health
                    enemy.active = True
                    
                    # إضافة إلى نظام C++ للتصادم
                    if self.physics.is_available():
                        enemy.cpp_id = self.physics.add_enemy(
                            id(enemy), pos[0], pos[1], enemy.width, enemy.height
                        )
                    
                    return enemy
        
        from entities.enemy import Enemy
        enemy = Enemy(enemy_type)
        enemy.pos = pos
        self.enemy_pools[enemy_type].append(enemy)
        return enemy
    
    def return_enemy(self, enemy):
        """إعادة العدو إلى التجمع"""
        if hasattr(enemy, 'cpp_id') and enemy.cpp_id != -1:
            self.physics.remove_enemy(enemy.cpp_id)
            enemy.cpp_id = -1
        
        enemy.active = False
        if enemy.parent:
            enemy.parent.remove_widget(enemy)
    
    def get_coin(self, pos):
        """الحصول على عملة"""
        for coin in self.coin_pool:
            if not coin.active:
                coin.pos = pos
                coin.active = True
                return coin
        
        from entities.powerup import Coin
        coin = Coin(pos=pos)
        self.coin_pool.append(coin)
        return coin
    
    def return_coin(self, coin):
        """إعادة العملة إلى التجمع"""
        coin.active = False
        if coin.parent:
            coin.parent.remove_widget(coin)
    
    def get_gun(self, pos):
        """الحصول على تطوير رصاص"""
        for gun in self.gun_pool:
            if not gun.active:
                gun.pos = pos
                gun.active = True
                return gun
        
        from entities.powerup import Gun
        gun = Gun(pos=pos)
        self.gun_pool.append(gun)
        return gun
    
    def return_gun(self, gun):
        """إعادة التطوير إلى التجمع"""
        gun.active = False
        if gun.parent:
            gun.parent.remove_widget(gun)
    
    def get_medical(self, pos):
        """الحصول على شفاء"""
        for medical in self.medical_pool:
            if not medical.active:
                medical.pos = pos
                medical.active = True
                return medical
        
        from entities.powerup import Medical
        medical = Medical(pos=pos)
        self.medical_pool.append(medical)
        return medical
    
    def return_medical(self, medical):
        """إعادة الشفاء إلى التجمع"""
        medical.active = False
        if medical.parent:
            medical.parent.remove_widget(medical)
    
    def get_powerup(self, pos, power_type):
        """الحصول على باور أب"""
        for powerup in self.powerup_pool:
            if not powerup.active and powerup.power_type == power_type:
                powerup.pos = pos
                powerup.active = True
                return powerup
        
        from entities.powerup import PowerUp
        powerup = PowerUp(pos=pos, power_type=power_type)
        self.powerup_pool.append(powerup)
        return powerup
    
    def return_powerup(self, powerup):
        """إعادة الباور أب إلى التجمع"""
        powerup.active = False
        if powerup.parent:
            powerup.parent.remove_widget(powerup)
    
    def get_boss(self, boss_type: str):
        """الحصول على بوس"""
        from entities.boss import Boss
        return Boss(boss_type=boss_type)
    
    def return_boss(self, boss):
        """إعادة البوس"""
        if boss.parent:
            boss.parent.remove_widget(boss)
    
    def update_cpp_physics(self, dt):
        """تحديث فيزياء C++"""
        if self.physics.is_available():
            self.physics.update_bullets(dt)
    
    def update(self, dt):
        """تحديث التجمعات"""
        # تحديث فيزياء C++
        self.update_cpp_physics(dt)
        
        # تنظيف الكائنات غير النشطة من القوائم
        self._cleanup_pools()
    
    def _cleanup_pools(self):
        """تنظيف التجمعات من الكائنات غير النشطة"""
        # تنظيف الرصاصات
        self.bullet_pool = [b for b in self.bullet_pool if b.active or not b.parent]
        
        # تنظيف رصاصات البوس
        self.boss_bullet_pool = [b for b in self.boss_bullet_pool if b.active or not b.parent]
        
        # تنظيف العملات
        self.coin_pool = [c for c in self.coin_pool if c.active or not c.parent]
        
        # تنظيف التطويرات
        self.gun_pool = [g for g in self.gun_pool if g.active or not g.parent]
        
        # تنظيف الشفاء
        self.medical_pool = [m for m in self.medical_pool if m.active or not m.parent]
        
        # تنظيف الباوربس
        self.powerup_pool = [p for p in self.powerup_pool if p.active or not p.parent]
    
    def clear_all(self):
        """مسح جميع التجمعات"""
        # إعادة جميع الكائنات النشطة إلى التجمعات
        for bullet in self.bullet_pool:
            if bullet.active:
                self.return_bullet(bullet)
        
        for bullet in self.boss_bullet_pool:
            if bullet.active:
                self.return_boss_bullet(bullet)
        
        for enemy_type in self.enemy_pools:
            for enemy in self.enemy_pools[enemy_type]:
                if enemy.active:
                    self.return_enemy(enemy)
        
        for coin in self.coin_pool:
            if coin.active:
                self.return_coin(coin)
        
        for gun in self.gun_pool:
            if gun.active:
                self.return_gun(gun)
        
        for medical in self.medical_pool:
            if medical.active:
                self.return_medical(medical)
        
        for powerup in self.powerup_pool:
            if powerup.active:
                self.return_powerup(powerup)
        
        # مسح فيزياء C++
        if self.physics.is_available():
            self.physics.clear()
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات التجمعات"""
        return {
            'bullet_pool': len(self.bullet_pool),
            'boss_bullet_pool': len(self.boss_bullet_pool),
            'active_bullets': sum(1 for b in self.bullet_pool if b.active),
            'enemy_pools': {k: len(v) for k, v in self.enemy_pools.items()},
            'coin_pool': len(self.coin_pool),
            'gun_pool': len(self.gun_pool),
            'medical_pool': len(self.medical_pool),
            'powerup_pool': len(self.powerup_pool),
            'cpp_available': self.physics.is_available()
        }