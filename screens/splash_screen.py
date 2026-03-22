"""splash_screen.py - شاشة البداية"""
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from widgets.fancy_button import FancyButton

class SplashScreen(Widget):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs); self.app = app; self._build_ui()
    def _build_ui(self):
        splash = Image(source="splash.png", size=Window.size, pos=(0,0)); self.add_widget(splash)
        btn = FancyButton(text="▶️ Start Game", size=(250,80), pos=(Window.width*0.35, Window.height*0.1))
        btn.bind(on_release=lambda x: self.app.navigate_to('main_menu')); self.add_widget(btn)