"""
main.py - نقطة الدخول الرئيسية مع نظام تصحيح
"""

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
import os
import sys

# إعدادات النافذة
Config.set('graphics', 'resizable', False)

from config import FULLSCREEN, WINDOW_WIDTH, WINDOW_HEIGHT

print("=" * 50)
print("🎮 GALAXY SHOOTER - DEBUG MODE")
print("=" * 50)


class GameApp(App):
    """تطبيق اللعبة الرئيسي"""
    
    def build(self):
        if FULLSCREEN:
            Window.fullscreen = 'auto'
        else:
            Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        
        Window.clearcolor = (0.05, 0.05, 0.1, 1)
        
        # إضافة فحص Clock دوري
        def check_clock(dt):
            print("🕐 Clock heartbeat - App is alive")
        
        Clock.schedule_interval(check_clock, 5.0)
        
        from screens.game_screen import GameScreen
        self.game_screen = GameScreen(on_game_over_callback=self.show_main_menu)
        
        print("✅ App built successfully")
        return self.game_screen
    
    def show_main_menu(self):
        if self.game_screen:
            self.game_screen.show_main_menu()
    
    def on_start(self):
        print("🎮 App started!")
    
    def on_stop(self):
        print("👋 App closing...")
        from core.audio_manager import cleanup_audio
        cleanup_audio()


if __name__ == '__main__':
    print("🚀 Launching game...")
    GameApp().run()
    print("👋 Game exited")