"""
core/__init__.py - النواة الأساسية للعبة
"""

from core.audio_manager import *
from core.save_manager import *
from core.event_system import EventBus, GameEvent, event_bus
from core.game_engine import GameEngine
from core.game_manager import GameManager
from core.state_manager import StateManager, GameState

__all__ = [
    'EventBus',
    'GameEvent', 
    'event_bus',
    'GameEngine',
    'GameManager',
    'StateManager',
    'GameState'
]