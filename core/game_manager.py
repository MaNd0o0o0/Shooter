"""
game_manager.py - مدير اللعبة الرئيسي
"""

from kivy.clock import Clock
from typing import Dict, Any, Optional
from core.event_system import event_bus, GameEvent


class GameManager:
    """
    مدير اللعبة - يدير حالة اللعبة والإحصائيات
    """
    
    def __init__(self):
        self.event_bus = event_bus
        
        # إحصائيات اللعبة
        self.stats = {
            'score': 0,
            'coins': 0,
            'level': 1,
            'xp': 0,
            'health': 100,
            'max_health': 100,
            'bullets_count': 1,
            'total_kills': 0,
            'bosses_defeated': 0,
            'high_score': 0,
            'total_coins': 0
        }
        
        # إعدادات اللاعب
        self.player_settings = {
            'equipped_skin': 'default',
            'owned_skins': ['default'],
            'achievements': {},
            'completed_boss_levels': []
        }
        
        # إعدادات الصوت
        self.audio_settings = {
            'music_muted': False,
            'sfx_muted': False
        }
        
        # تسجيل الأحداث
        self._register_events()
    
    def _register_events(self):
        """تسجيل أحداث اللعبة"""
        self.event_bus.on(GameEvent.SCORE_CHANGED, self._on_score_changed)
        self.event_bus.on(GameEvent.COINS_CHANGED, self._on_coins_changed)
        self.event_bus.on(GameEvent.HEALTH_CHANGED, self._on_health_changed)
        self.event_bus.on(GameEvent.ENEMY_KILLED, self._on_enemy_killed)
        self.event_bus.on(GameEvent.BOSS_DEFEATED, self._on_boss_defeated)
        self.event_bus.on(GameEvent.GAME_OVER, self._on_game_over)
    
    def _on_score_changed(self, event):
        self.stats['score'] = event.data
        if self.stats['score'] > self.stats['high_score']:
            self.stats['high_score'] = self.stats['score']
    
    def _on_coins_changed(self, event):
        self.stats['coins'] = event.data
        self.stats['total_coins'] += event.data  # إضافة إلى الإجمالي
    
    def _on_health_changed(self, event):
        self.stats['health'] = event.data['current']
        self.stats['max_health'] = event.data['max']
    
    def _on_enemy_killed(self, event):
        self.stats['total_kills'] += 1
        self.add_score(10)
        self.add_xp(15)
    
    def _on_boss_defeated(self, event):
        self.stats['bosses_defeated'] += 1
        self.add_score(30)
        self.add_xp(50)
        self.add_coins(50)
    
    def _on_game_over(self, event):
        """نهاية اللعبة"""
        if self.stats['score'] > self.stats['high_score']:
            self.stats['high_score'] = self.stats['score']
        self.save_data()
    
    # ============ دوال إدارة النقاط ============
    
    def add_score(self, points: int):
        """إضافة نقاط"""
        self.stats['score'] += points
        self.event_bus.emit(GameEvent.SCORE_CHANGED, self.stats['score'])
    
    def add_coins(self, amount: int):
        """إضافة عملات"""
        self.stats['coins'] += amount
        self.event_bus.emit(GameEvent.COINS_CHANGED, self.stats['coins'])
    
    def add_xp(self, amount: int):
        """إضافة خبرة"""
        self.stats['xp'] += amount
        xp_needed = self.stats['level'] * 100
        
        if self.stats['xp'] >= xp_needed:
            self.level_up()
        else:
            self.event_bus.emit(GameEvent.XP_CHANGED, self.stats['xp'])
    
    def level_up(self):
        """رفع المستوى"""
        self.stats['level'] += 1
        self.stats['xp'] = 0
        self.stats['max_health'] += 20
        self.stats['health'] = self.stats['max_health']
        
        self.event_bus.emit(GameEvent.PLAYER_LEVEL_UP, self.stats['level'])
        self.event_bus.emit(GameEvent.HEALTH_CHANGED, {
            'current': self.stats['health'],
            'max': self.stats['max_health']
        })
    
    def take_damage(self, amount: int, has_shield: bool = False):
        """تلقي الضرر"""
        if has_shield:
            return
        
        self.stats['health'] -= amount
        if self.stats['health'] < 0:
            self.stats['health'] = 0
        
        self.event_bus.emit(GameEvent.HEALTH_CHANGED, {
            'current': self.stats['health'],
            'max': self.stats['max_health']
        })
        
        if self.stats['health'] <= 0:
            self.event_bus.emit(GameEvent.PLAYER_DIED)
            self.event_bus.emit(GameEvent.GAME_OVER, self.stats)
    
    def heal(self, amount: int):
        """الشفاء"""
        old_health = self.stats['health']
        self.stats['health'] = min(self.stats['health'] + amount, self.stats['max_health'])
        
        self.event_bus.emit(GameEvent.HEALTH_CHANGED, {
            'current': self.stats['health'],
            'max': self.stats['max_health']
        })
        self.event_bus.emit(GameEvent.PLAYER_HEALED, self.stats['health'] - old_health)
    
    # ============ دوال الإعدادات ============
    
    def toggle_music(self):
        """تبديل الموسيقى"""
        self.audio_settings['music_muted'] = not self.audio_settings['music_muted']
        return self.audio_settings['music_muted']
    
    def toggle_sfx(self):
        """تبديل المؤثرات الصوتية"""
        self.audio_settings['sfx_muted'] = not self.audio_settings['sfx_muted']
        return self.audio_settings['sfx_muted']
    
    def buy_skin(self, skin_id: str, price: int) -> bool:
        """شراء سكن"""
        if self.stats['coins'] >= price and skin_id not in self.player_settings['owned_skins']:
            self.stats['coins'] -= price
            self.player_settings['owned_skins'].append(skin_id)
            self.event_bus.emit(GameEvent.COINS_CHANGED, self.stats['coins'])
            return True
        return False
    
    def equip_skin(self, skin_id: str) -> bool:
        """تجهيز سكن"""
        if skin_id in self.player_settings['owned_skins']:
            self.player_settings['equipped_skin'] = skin_id
            return True
        return False
    
    # ============ دوال الحفظ والتحميل ============
    
    def save_data(self):
        """حفظ بيانات اللعبة"""
        from core.save_manager import save_game_data
        
        data = {
            'owned_skins': self.player_settings['owned_skins'],
            'equipped_skin': self.player_settings['equipped_skin'],
            'achievements': self.player_settings['achievements'],
            'total_kills': self.stats['total_kills'],
            'bosses_defeated': self.stats['bosses_defeated'],
            'completed_boss_levels': self.player_settings['completed_boss_levels'],
            'high_score': self.stats['high_score'],
            'total_coins': self.stats['total_coins'],
            'settings': self.audio_settings
        }
        
        save_game_data(data)
    
    def load_data(self):
        """تحميل بيانات اللعبة"""
        from core.save_manager import load_game_data
        
        data = load_game_data()
        self.player_settings['owned_skins'] = data.get('owned_skins', ['default'])
        self.player_settings['equipped_skin'] = data.get('equipped_skin', 'default')
        self.player_settings['achievements'] = data.get('achievements', {})
        self.stats['total_kills'] = data.get('total_kills', 0)
        self.stats['bosses_defeated'] = data.get('bosses_defeated', 0)
        self.player_settings['completed_boss_levels'] = data.get('completed_boss_levels', [])
        self.stats['high_score'] = data.get('high_score', 0)
        self.stats['total_coins'] = data.get('total_coins', 0)
        self.audio_settings = data.get('settings', self.audio_settings)
    
    def reset(self):
        """إعادة تعيين إحصائيات اللعبة"""
        self.stats = {
            'score': 0,
            'coins': 0,
            'level': 1,
            'xp': 0,
            'health': 100,
            'max_health': 100,
            'bullets_count': 1,
            'total_kills': 0,
            'bosses_defeated': 0,
            'high_score': self.stats['high_score'],
            'total_coins': self.stats['total_coins']
        }
    
    def get_stats(self) -> dict:
        """الحصول على الإحصائيات"""
        return self.stats.copy()
    
    def get_settings(self) -> dict:
        """الحصول على الإعدادات"""
        return self.audio_settings.copy()