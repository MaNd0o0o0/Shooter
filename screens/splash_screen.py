"""
splash_screen.py - شاشة البداية
"""

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.label import Label
from widgets.fancy_button import FancyButton
from config import IMAGES_PATH


class SplashScreen(Widget):
    """شاشة البداية مع الأزرار"""
    
    def __init__(self, on_start_callback=None, on_settings_callback=None,
                 on_store_callback=None, on_achievements_callback=None,
                 on_exit_callback=None, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self.on_start_callback = on_start_callback
        self.on_settings_callback = on_settings_callback
        self.on_store_callback = on_store_callback
        self.on_achievements_callback = on_achievements_callback
        self.on_exit_callback = on_exit_callback
        self.size = Window.size
        self.pos = (0, 0)
        
        splash_image = Image(
            source=f"{IMAGES_PATH}/splash.png",
            size=Window.size, pos=(0, 0),
            allow_stretch=True, keep_ratio=False
        )
        self.add_widget(splash_image)
        
        title = Label(
            text="GALAXY SHOOTER",
            font_size=48, bold=True, color=(1, 0.9, 0.2, 1),
            pos=(Window.width/2 - 200, Window.height * 0.85), size=(400, 60), halign='center'
        )
        self.add_widget(title)
        
        start_btn = FancyButton(
            text="▶️ START GAME",
            size=(350, 90), pos=(Window.width/2 - 175, Window.height * 0.6),
            background_color=(0.2, 0.6, 0.9, 1), font_size=32
        )
        start_btn.bind(on_release=lambda x: self.start_game())
        self.add_widget(start_btn)
        
        button_width = 160
        button_height = 60
        button_y = Window.height * 0.15
        spacing = 20
        total_width = (button_width * 4) + (spacing * 3)
        start_x = (Window.width - total_width) / 2
        
        settings_btn = FancyButton(
            text="⚙️\nSETTINGS", size=(button_width, button_height),
            pos=(start_x, button_y), background_color=(0.4, 0.5, 0.7, 1), font_size=18
        )
        settings_btn.bind(on_release=lambda x: self.open_settings())
        self.add_widget(settings_btn)
        
        store_btn = FancyButton(
            text="🛒\nSTORE", size=(button_width, button_height),
            pos=(start_x + button_width + spacing, button_y),
            background_color=(0.9, 0.6, 0.1, 1), font_size=18
        )
        store_btn.bind(on_release=lambda x: self.open_store())
        self.add_widget(store_btn)
        
        achievements_btn = FancyButton(
            text="🏆\nACHIEVEMENTS", size=(button_width, button_height),
            pos=(start_x + (button_width + spacing) * 2, button_y),
            background_color=(0.8, 0.5, 0.1, 1), font_size=18
        )
        achievements_btn.bind(on_release=lambda x: self.open_achievements())
        self.add_widget(achievements_btn)
        
        exit_btn = FancyButton(
            text="🚪\nEXIT", size=(button_width, button_height),
            pos=(start_x + (button_width + spacing) * 3, button_y),
            background_color=(0.8, 0.2, 0.2, 1), font_size=18
        )
        exit_btn.bind(on_release=lambda x: self.exit_game())
        self.add_widget(exit_btn)
    
    def start_game(self):
        if self.on_start_callback:
            self.on_start_callback()
    
    def open_settings(self):
        if self.on_settings_callback:
            self.on_settings_callback()
    
    def open_store(self):
        if self.on_store_callback:
            self.on_store_callback()
    
    def open_achievements(self):
        if self.on_achievements_callback:
            self.on_achievements_callback()
    
    def exit_game(self):
        if self.on_exit_callback:
            self.on_exit_callback()