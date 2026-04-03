"""
state_manager.py - إدارة حالات اللعبة
"""

from enum import Enum
from typing import Dict, Any, Optional
from core.event_system import event_bus, GameEvent


class GameState(Enum):
    """حالات اللعبة المختلفة"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SHOP = "shop"
    SETTINGS = "settings"
    ACHIEVEMENTS = "achievements"
    MISSIONS = "missions"
    LOADING = "loading"


class StateManager:
    """
    مدير حالات اللعبة - يتحكم في الانتقال بين الحالات
    """
    
    def __init__(self):
        self.event_bus = event_bus
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_data: Dict[str, Any] = {}
        
        # التحويلات المسموحة بين الحالات
        self.transitions = {
            GameState.MENU: {
                GameState.PLAYING: True,
                GameState.SETTINGS: True,
                GameState.SHOP: True,
                GameState.ACHIEVEMENTS: True,
                GameState.MISSIONS: True,
            },
            GameState.PLAYING: {
                GameState.PAUSED: True,
                GameState.GAME_OVER: True,
                GameState.MENU: True,
            },
            GameState.PAUSED: {
                GameState.PLAYING: True,
                GameState.MENU: True,
                GameState.SETTINGS: True,
            },
            GameState.GAME_OVER: {
                GameState.MENU: True,
                GameState.PLAYING: True,
            },
            GameState.SETTINGS: {
                GameState.MENU: True,
                GameState.PAUSED: True,
            },
            GameState.SHOP: {
                GameState.MENU: True,
                GameState.PLAYING: True,
            },
            GameState.ACHIEVEMENTS: {
                GameState.MENU: True,
            },
            GameState.MISSIONS: {
                GameState.MENU: True,
            },
            GameState.LOADING: {
                GameState.MENU: True,
                GameState.PLAYING: True,
            },
        }
        
        # تسجيل الأحداث
        self._register_events()
    
    def _register_events(self):
        """تسجيل أحداث تغيير الحالة"""
        self.event_bus.on(GameEvent.GAME_STARTED, lambda e: self.change_state(GameState.PLAYING))
        self.event_bus.on(GameEvent.GAME_PAUSED, lambda e: self.change_state(GameState.PAUSED))
        self.event_bus.on(GameEvent.GAME_RESUMED, lambda e: self.change_state(GameState.PLAYING))
        self.event_bus.on(GameEvent.GAME_OVER, lambda e: self.change_state(GameState.GAME_OVER))
    
    def change_state(self, new_state: GameState, data: Any = None) -> bool:
        """
        تغيير الحالة الحالية
        Returns: bool - نجاح العملية
        """
        # تحقق من صحة التحويل
        if new_state not in self.transitions.get(self.current_state, {}):
            print(f"⚠️ Invalid state transition: {self.current_state} -> {new_state}")
            return False
        
        # حفظ الحالة السابقة
        self.previous_state = self.current_state
        
        # تغيير الحالة
        old_state = self.current_state
        self.current_state = new_state
        
        # حفظ البيانات
        if data:
            self.state_data[new_state.value] = data
        
        # إطلاق حدث تغيير الحالة
        self.event_bus.emit(GameEvent.STATE_CHANGED, {
            'from': old_state,
            'to': new_state,
            'data': data
        })
        
        print(f"🔄 State changed: {old_state.value} -> {new_state.value}")
        return True
    
    def go_back(self) -> bool:
        """العودة للحالة السابقة"""
        if self.previous_state:
            return self.change_state(self.previous_state)
        return False
    
    def get_state_data(self, state: Optional[GameState] = None) -> Any:
        """الحصول على بيانات حالة"""
        if state is None:
            state = self.current_state
        return self.state_data.get(state.value)
    
    def set_state_data(self, state: GameState, data: Any):
        """تعيين بيانات حالة"""
        self.state_data[state.value] = data
    
    def is_state(self, state: GameState) -> bool:
        """التحقق من الحالة الحالية"""
        return self.current_state == state
    
    def is_playing(self) -> bool:
        """هل اللعبة قيد التشغيل؟"""
        return self.current_state == GameState.PLAYING
    
    def is_paused(self) -> bool:
        """هل اللعبة متوقفة مؤقتاً؟"""
        return self.current_state == GameState.PAUSED
    
    def is_menu(self) -> bool:
        """هل في القائمة؟"""
        return self.current_state == GameState.MENU
    
    def reset(self):
        """إعادة تعيين مدير الحالات"""
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_data.clear()