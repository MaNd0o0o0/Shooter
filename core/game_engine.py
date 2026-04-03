"""
game_engine.py - المحرك الرئيسي للعبة
"""

from kivy.clock import Clock
from typing import Dict, Any, Optional
from core.event_system import event_bus, GameEvent


class GameEngine:
    """
    المحرك الرئيسي - يدير جميع الأنظمة ويتواصل عبر EventBus
    """
    
    def __init__(self):
        self.event_bus = event_bus
        self.layers: Dict[str, Any] = {}
        self.systems: Dict[str, Any] = {}
        
        # حالة المحرك
        self.running = False
        self.paused = False
        self.clock_event = None
        
        # إعدادات الأداء
        self.target_fps = 60
        self.max_delta = 0.033  # 30 FPS كحد أقصى للحركة
        self.delta_time = 0
        self.frame_count = 0
        self.fps = 0
        
        # تسجيل الأحداث الأساسية
        self._register_events()
    
    def _register_events(self):
        """تسجيل أحداث المحرك"""
        self.event_bus.on(GameEvent.GAME_STARTED, self._on_game_started)
        self.event_bus.on(GameEvent.GAME_PAUSED, self._on_game_paused)
        self.event_bus.on(GameEvent.GAME_RESUMED, self._on_game_resumed)
        self.event_bus.on(GameEvent.GAME_OVER, self._on_game_over)
    
    def register_layer(self, name: str, layer):
        """تسجيل طبقة في المحرك"""
        self.layers[name] = layer
        if hasattr(layer, 'set_engine'):
            layer.set_engine(self)
        if hasattr(layer, 'set_event_bus'):
            layer.set_event_bus(self.event_bus)
    
    def register_system(self, name: str, system):
        """تسجيل نظام في المحرك"""
        self.systems[name] = system
        if hasattr(system, 'set_engine'):
            system.set_engine(self)
        if hasattr(system, 'set_event_bus'):
            system.set_event_bus(self.event_bus)
    
    def get_layer(self, name: str) -> Optional[Any]:
        """الحصول على طبقة"""
        return self.layers.get(name)
    
    def get_system(self, name: str) -> Optional[Any]:
        """الحصول على نظام"""
        return self.systems.get(name)
    
    def start(self):
        """بدء تشغيل المحرك"""
        if self.running:
            return
        
        self.running = True
        self.paused = False
        self.frame_count = 0
        
        # إطلاق حدث بدء اللعبة
        self.event_bus.emit(GameEvent.GAME_STARTED)
        
        # بدء حلقة التحديث
        self.clock_event = Clock.schedule_interval(self.update, 1.0 / self.target_fps)
        Clock.schedule_interval(self._update_fps, 1.0)
    
    def pause(self):
        """إيقاف المحرك مؤقتاً"""
        if not self.running or self.paused:
            return
        self.paused = True
        self.event_bus.emit(GameEvent.GAME_PAUSED)
    
    def resume(self):
        """استئناف المحرك"""
        if not self.running or not self.paused:
            return
        self.paused = False
        self.event_bus.emit(GameEvent.GAME_RESUMED)
    
    def stop(self):
        """إيقاف المحرك"""
        self.running = False
        if self.clock_event:
            Clock.unschedule(self.clock_event)
            self.clock_event = None
    
    def update(self, dt: float):
        """
        حلقة التحديث الرئيسية
        يتم استدعاؤها كل إطار
        """
        if not self.running or self.paused:
            return
        
        # تحديد وقت التحديث (الحد الأقصى)
        self.delta_time = min(dt, self.max_delta)
        
        # 1. تحديث الطبقات (المنطق أولاً)
        for name, layer in self.layers.items():
            if hasattr(layer, 'update'):
                try:
                    layer.update(self.delta_time)
                except Exception as e:
                    print(f"Error updating layer {name}: {e}")
        
        # 2. تحديث الأنظمة
        for name, system in self.systems.items():
            if hasattr(system, 'update'):
                try:
                    system.update(self.delta_time)
                except Exception as e:
                    print(f"Error updating system {name}: {e}")
        
        self.frame_count += 1
    
    def _update_fps(self, dt):
        """تحديث إحصائيات FPS"""
        self.fps = self.frame_count
        self.frame_count = 0
    
    # ============ دوال استدعاء الأحداث ============
    
    def _on_game_started(self, event):
        """معالجة بدء اللعبة"""
        print("🎮 Game Engine: Game Started")
    
    def _on_game_paused(self, event):
        """معالجة إيقاف اللعبة"""
        print("⏸ Game Engine: Game Paused")
    
    def _on_game_resumed(self, event):
        """معالجة استئناف اللعبة"""
        print("▶ Game Engine: Game Resumed")
    
    def _on_game_over(self, event):
        """معالجة نهاية اللعبة"""
        print("💀 Game Engine: Game Over")
        self.stop()
    
    # ============ دوال مساعدة ============
    
    def get_state(self) -> dict:
        """الحصول على حالة المحرك الحالية"""
        return {
            'running': self.running,
            'paused': self.paused,
            'delta_time': self.delta_time,
            'fps': self.fps,
            'frame_count': self.frame_count
        }