from kivy.app import App
from kivy.core.window import Window
from config import FULLSCREEN

# إعداد النافذة
Window.fullscreen = FULLSCREEN

class GameApp(App):
    def build(self):
        from screens.game_screen import GameScreen
        self.game_screen = GameScreen(on_game_over_callback=self.handle_game_state)
        return self.game_screen
    
    def handle_game_state(self, state, score=0):
        """معالجة حالة اللعبة"""
        if state == 'menu':
            self.show_main_menu()
        elif state == 'game_over':
            self.show_game_over(score)
    
    def show_main_menu(self):
        """عرض القائمة الرئيسية"""
        from screens.main_menu import MainMenu
        
        callbacks = {
            'play': lambda x: self.start_game(),
            'resume': lambda x: self.resume_game(),
            'settings': lambda x: self.show_settings(),
            'store': lambda x: self.show_store(),
            'skins': lambda x: self.show_skins(),
            'achievements': lambda x: self.show_achievements(),
            'exit': lambda x: self.stop()
        }
        
        menu = MainMenu(callbacks=callbacks, game_started=self.game_screen.game_started)
        Window.clearcolor = (0, 0, 0, 1)
        Window.add_widget(menu)
    
    def start_game(self):
        """بدء لعبة جديدة"""
        self.game_screen.start_game()
    
    def resume_game(self):
        """استئناف اللعبة"""
        self.game_screen.game_paused = False
    
    def show_settings(self):
        """عرض الإعدادات"""
        from screens.settings_screen import SettingsScreen
        settings = SettingsScreen(game_instance=self.game_screen, on_back_callback=self.show_main_menu)
        Window.add_widget(settings)
    
    def show_store(self):
        """عرض المتجر"""
        from screens.store_screen import StoreScreen
        store = StoreScreen(game_instance=self.game_screen, on_back_callback=self.show_main_menu)
        Window.add_widget(store)
    
    def show_skins(self):
        """عرض.skin"""
        pass
    
    def show_achievements(self):
        """عرض الإنجازات"""
        pass
    
    def show_game_over(self, score):
        """عرض شاشة نهاية اللعبة"""
        pass
    
    def on_stop(self):
        """عند إيقاف التطبيق"""
        from core.audio_manager import background_music, boss_music
        if background_music:
            try:
                background_music.stop()
            except:
                pass
        if boss_music:
            try:
                boss_music.stop()
            except:
                pass

if __name__ == '__main__':
    GameApp().run()