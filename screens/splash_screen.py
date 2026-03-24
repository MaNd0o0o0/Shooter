from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from widgets.fancy_button import FancyButton
from config import IMAGES_PATH

class SplashScreen(Widget):
    def __init__(self, on_start_callback=None, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self.on_start_callback = on_start_callback
        self.size = Window.size
        self.pos = (0, 0)
        
        # صورة الخلفية
        splash_image = Image(source=f"{IMAGES_PATH}/splash.png", size=Window.size, pos=(0, 0))
        self.add_widget(splash_image)
        
        # زر البدء
        start_btn = FancyButton(
            text="▶️ Start Game",
            size_hint=(None, None),
            size=(250, 80),
            pos=(Window.width * 0.35, Window.height * 0.1),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size=28
        )
        start_btn.bind(on_release=lambda x: self.start_game())
        self.add_widget(start_btn)
    
    def start_game(self):
        if self.on_start_callback:
            self.on_start_callback()