from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from widgets.fancy_button import FancyButton

class MainMenu(Widget):
    def __init__(self, callbacks=None, game_started=False, **kwargs):
        super(MainMenu, self).__init__(**kwargs)
        self.callbacks = callbacks or {}
        self.game_started = game_started
        self.size = Window.size
        self.pos = (0, 0)
        
        # خلفية شفافة
        with self.canvas:
            Color(0, 0, 0, 0.7)
            self.menu_bg = Rectangle(size=Window.size, pos=(0, 0))
        
        self.create_buttons()
    
    def create_buttons(self):
        y_positions = [0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        button_configs = []
        
        if self.game_started:
            button_configs.append({
                "text": "▶️ Resume",
                "callback": self.callbacks.get('resume'),
                "color": (0.2, 0.6, 0.9, 1)
            })
        else:
            button_configs.append({
                "text": "▶️ Play",
                "callback": self.callbacks.get('play'),
                "color": (0.2, 0.6, 0.9, 1)
            })
        
        button_configs.extend([
            {"text": "⚙️ Settings", "callback": self.callbacks.get('settings'), "color": (0.3, 0.7, 0.3, 1)},
            {"text": "🛒 Store", "callback": self.callbacks.get('store'), "color": (0.9, 0.6, 0.1, 1)},
            {"text": "🎨 Skins", "callback": self.callbacks.get('skins'), "color": (0.6, 0.3, 0.8, 1)},
            {"text": "🏆 Achievements", "callback": self.callbacks.get('achievements'), "color": (0.8, 0.5, 0.1, 1)},
            {"text": "🚪 Exit", "callback": self.callbacks.get('exit'), "color": (0.8, 0.2, 0.2, 1)}
        ])
        
        for i, config in enumerate(button_configs):
            btn = FancyButton(
                text=config["text"],
                size_hint=(None, None),
                size=(220, 70),
                pos=(Window.width * 0.35, Window.height * y_positions[i]),
                background_color=config["color"],
                color=(1, 1, 1, 1),
                font_size=26
            )
            if config["callback"]:
                btn.bind(on_release=config["callback"])
            self.add_widget(btn)