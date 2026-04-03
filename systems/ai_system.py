"""
ai_system.py - نظام الذكاء الاصطناعي للأعداء
"""

from kivy.core.window import Window
import math
import random


class AISystem:
    """نظام التحكم في سلوك الأعداء"""
    
    def __init__(self):
        self.game_world = None
        self.event_bus = None
        self.game = None
        
        self.behaviors = {
            'soldier': self._behavior_chase,
            'fast': self._behavior_chase_fast,
            'armor': self._behavior_chase_slow,
            'bomber': self._behavior_bomber,
            'ghost': self._behavior_ghost,
        }
    
    def set_game_world(self, game_world):
        self.game_world = game_world
    
    def set_event_bus(self, event_bus):
        self.event_bus = event_bus
    
    def set_game(self, game):
        self.game = game
    
    def update(self, dt: float):
        """تحديث جميع الأعداء"""
        if not self.game or not self.game.player:
            return
        
        player = self.game.player
        player_pos = (player.center_x, player.center_y)
        
        for enemy in self.game.enemies[:]:
            if not enemy.active:
                continue
            
            # تجميد الحركة
            if hasattr(self.game, 'freeze_active') and self.game.freeze_active:
                continue
            
            enemy_type = getattr(enemy, 'enemy_type', 'soldier')
            behavior = self.behaviors.get(enemy_type, self._behavior_chase)
            behavior(enemy, player_pos, dt)
            
            # تحديث الموقع
            enemy.pos = (enemy.x, enemy.y)
            
            # حدود الشاشة
            enemy.x = max(0, min(enemy.x, Window.width - enemy.width))
            enemy.y = max(0, min(enemy.y, Window.height - enemy.height))
    
    def _behavior_chase(self, enemy, player_pos, dt):
        """سلوك الملاحقة العادي"""
        dx = player_pos[0] - enemy.center_x
        dy = player_pos[1] - enemy.center_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            move_x = (dx / dist) * enemy.speed
            move_y = (dy / dist) * enemy.speed
            enemy.x += move_x
            enemy.y += move_y
    
    def _behavior_chase_fast(self, enemy, player_pos, dt):
        """سلوك الملاحقة السريع"""
        dx = player_pos[0] - enemy.center_x
        dy = player_pos[1] - enemy.center_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            move_x = (dx / dist) * enemy.speed * 1.2
            move_y = (dy / dist) * enemy.speed * 1.2
            enemy.x += move_x
            enemy.y += move_y
    
    def _behavior_chase_slow(self, enemy, player_pos, dt):
        """سلوك الملاحقة البطيء (الدبابات)"""
        dx = player_pos[0] - enemy.center_x
        dy = player_pos[1] - enemy.center_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            move_x = (dx / dist) * enemy.speed * 0.7
            move_y = (dy / dist) * enemy.speed * 0.7
            enemy.x += move_x
            enemy.y += move_y
    
    def _behavior_bomber(self, enemy, player_pos, dt):
        """سلوك المفجر - يحاول الاقتراب"""
        dx = player_pos[0] - enemy.center_x
        dy = player_pos[1] - enemy.center_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        # انفجار إذا كان قريباً جداً
        if dist < 80:
            if self.game_world:
                self.game_world.handle_enemy_death(enemy)
            return
        
        if dist > 0:
            move_x = (dx / dist) * enemy.speed
            move_y = (dy / dist) * enemy.speed
            enemy.x += move_x
            enemy.y += move_y
    
    def _behavior_ghost(self, enemy, player_pos, dt):
        """سلوك الشبح - حركة متعرجة"""
        # حركة متعرجة
        enemy.x += enemy.speed * math.sin(enemy.y * 0.05)
        enemy.y += enemy.speed * math.cos(enemy.x * 0.05)
        
        # يتجه نحو اللاعب ببطء
        dx = player_pos[0] - enemy.center_x
        dy = player_pos[1] - enemy.center_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            enemy.x += (dx / dist) * enemy.speed * 0.3
            enemy.y += (dy / dist) * enemy.speed * 0.3
    
    def reset(self):
        """إعادة تعيين نظام الذكاء الاصطناعي"""
        pass