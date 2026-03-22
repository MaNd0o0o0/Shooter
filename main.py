"""main.py - نقطة الدخول"""
from kivy.app import App
from config import *
from core.audio_manager import AudioManager
from core.save_manager import SaveManager
from screens.splash_screen import SplashScreen

class SpaceShooterApp(App):
    def build(self):
        self.title = "Space Shooter"
        self.audio = AudioManager(); self.audio.load_music()
        self.saver = SaveManager()
        self.player_data = self.saver.load(default={'owned_skins':['default'],'equipped_skin':'default','achievements':{},'total_coins':0})
        return SplashScreen(self)
    def navigate_to(self, screen_name, **kwargs):
        if screen_name=='game':
            from screens.game_screen import GameScreen
            return GameScreen(audio_manager=self.audio, save_manager=self.saver, player_data=self.player_data, **kwargs)
        elif screen_name=='main_menu':
            from screens.main_menu import MainMenuScreen
            return MainMenuScreen(self, **kwargs)
        return SplashScreen(self)
    def on_stop(self): self.saver.save(self.player_data); self.audio.stop_music()

if __name__ == '__main__': SpaceShooterApp().run()