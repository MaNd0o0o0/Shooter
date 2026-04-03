"""
event_system.py - نظام الأحداث المركزي (Event Bus)
"""

from enum import Enum, auto
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict


class GameEvent(Enum):
    """جميع أحداث اللعبة في مكان واحد"""
    
    # أحداث اللاعب
    PLAYER_DAMAGED = auto()
    PLAYER_HEALED = auto()
    PLAYER_DIED = auto()
    PLAYER_LEVEL_UP = auto()
    PLAYER_MOVED = auto()
    
    # أحداث القتال
    ENEMY_SPAWNED = auto()
    ENEMY_KILLED = auto()
    BOSS_SPAWNED = auto()
    BOSS_DAMAGED = auto()
    BOSS_DEFEATED = auto()
    BULLET_FIRED = auto()
    BULLET_HIT = auto()
    
    # أحداث العناصر
    COIN_COLLECTED = auto()
    POWERUP_COLLECTED = auto()
    POWERUP_ACTIVATED = auto()
    
    # أحداث الموجات
    WAVE_STARTED = auto()
    WAVE_COMPLETED = auto()
    
    # أحداث الواجهة
    SCORE_CHANGED = auto()
    COINS_CHANGED = auto()
    HEALTH_CHANGED = auto()
    XP_CHANGED = auto()
    LEVEL_CHANGED = auto()
    
    # أحداث النظام
    GAME_STARTED = auto()
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()
    GAME_OVER = auto()
    
    # أحداث الإنجازات
    ACHIEVEMENT_UNLOCKED = auto()
    MISSION_COMPLETED = auto()


@dataclass
class Event:
    """كيان الحدث"""
    type: GameEvent
    data: Any = None
    source: Any = None
    timestamp: float = field(default_factory=lambda: __import__('time').time())


class EventBus:
    """
    ناقل الأحداث المركزي
    جميع الأنظمة تتواصل من خلاله (Singleton)
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listeners = defaultdict(list)
            cls._instance._history = []
        return cls._instance
    
    def emit(self, event_type: GameEvent, data: Any = None, source: Any = None):
        """إطلاق حدث"""
        event = Event(event_type, data, source)
        self._history.append(event)
        
        # الاحتفاظ بآخر 200 حدث فقط
        if len(self._history) > 200:
            self._history.pop(0)
        
        # إعلام جميع المستمعين
        for callback in self._listeners[event_type]:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event listener for {event_type}: {e}")
    
    def on(self, event_type: GameEvent, callback: Callable):
        """الاستماع لحدث"""
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
    
    def off(self, event_type: GameEvent, callback: Callable):
        """إلغاء الاستماع لحدث"""
        if callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
    
    def once(self, event_type: GameEvent, callback: Callable):
        """الاستماع لحدث مرة واحدة فقط"""
        def wrapper(event):
            callback(event)
            self.off(event_type, wrapper)
        self.on(event_type, wrapper)
    
    def clear(self):
        """مسح جميع المستمعين"""
        self._listeners.clear()
    
    def get_history(self, event_type: GameEvent = None) -> List[Event]:
        """الحصول على سجل الأحداث"""
        if event_type:
            return [e for e in self._history if e.type == event_type]
        return self._history.copy()


# Singleton instance
event_bus = EventBus()