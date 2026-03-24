from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from widgets.fancy_button import FancyButton

class SettingsScreen(Widget):
    def __init__(self, game_instance=None, on_back_callback=None, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.game_instance = game_instance
        self.on_back_callback = on_back_callback
        self.size = Window.size
        self.pos = (0, 0)
        
        with self.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size, pos=(0, 0))
        
        self.create_ui()
    
    def create_ui(self):
        title = Label(text="⚙️ Settings", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width*0.35, Window.height*0.8),
                      size_hint=(None, None), size=(300, 60), halign='center')
        self.add_widget(title)
        
        if self.game_instance:
            self.music_btn = FancyButton(
                text="Music: OFF" if self.game_instance.music_muted else "Music: ON",
                size_hint=(None, None),
                size=(300, 70),
                pos=(Window.width*0.35, Window.height*0.6),
                background_color=(0.6, 0.3, 0.8, 1),
                color=(1, 1, 1, 1),
                font_size=24
            )
            self.music_btn.bind(on_release=lambda x: self.toggle_music())
            self.add_widget(self.music_btn)
            
            self.sfx_btn = FancyButton(
                text="SFX: OFF" if self.game_instance.sfx_muted else "SFX: ON",
                size_hint=(None, None),
                size=(300, 70),
                pos=(Window.width*0.35, Window.height*0.5),
                background_color=(0.3, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                font_size=24
            )
            self.sfx_btn.bind(on_release=lambda x: self.toggle_sfx())
            self.add_widget(self.sfx_btn)
        
        back_btn = FancyButton(
            text="⬅️ Back to Menu",
            size_hint=(None, None),
            size=(250, 70),
            pos=(Window.width*0.35, Window.height*0.3),
            background_color=(0.2, 0.8, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=24
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        self.add_widget(back_btn)
    
    def toggle_music(self):
        if self.game_instance:
            self.game_instance.toggle_music()
            self.music_btn.text = "Music: OFF" if self.game_instance.music_muted else "Music: ON"
    
    def toggle_sfx(self):
        if self.game_instance:
            self.game_instance.toggle_sfx()
            self.sfx_btn.text = "SFX: OFF" if self.game_instance.sfx_muted else "SFX: ON"
    
    def go_back(self):
        if self.on_back_callback:
            self.on_back_callback()