"""
screens/__init__.py - شاشات اللعبة
"""

from screens.game_screen import GameScreen
from screens.logo_screen import LogoScreen
from screens.main_menu import MainMenu
from screens.settings_screen import SettingsScreen
from screens.splash_screen import SplashScreen
from screens.store_screen import StoreScreen

__all__ = [
    'GameScreen',
    'LogoScreen',
    'MainMenu',
    'SettingsScreen',
    'SplashScreen',
    'StoreScreen'
]