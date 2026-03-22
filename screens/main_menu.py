"""main_menu.py - القائمة الرئيسية"""
from kivy.uix.widget import Widget
from kivy.core.window import Window
from widgets.fancy_button import FancyButton
from config import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS

class MainMenuScreen(Widget):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs); self.app = app; self._build_ui()
    def _build_ui(self):
        with self.canvas:
            from kivy.graphics import Color, Rectangle
            Color(0.1,0.15,0.2,1); Rectangle(size=Window.size, pos=(0,0))
        for text,on_rel,col,y in [("▶️ Play",lambda:self.app.navigate_to('game'),UI_COLORS['btn_normal'],WINDOW_HEIGHT*0.6),("⚙️ Settings",lambda:None,(0.3,0.7,0.3,1),WINDOW_HEIGHT*0.5),("🛒 Store",lambda:None,(0.9,0.6,0.1,1),WINDOW_HEIGHT*0.4),("🎨 Skins",lambda:None,(0.6,0.3,0.8,1),WINDOW_HEIGHT*0.3),("🏆 Achievements",lambda:None,(0.8,0.5,0.1,1),WINDOW_HEIGHT*0.2),("🚪 Exit",lambda:self.app.stop(),(0.8,0.2,0.2,1),WINDOW_HEIGHT*0.1)]:
            btn = FancyButton(text=text, size=(220,70), pos=(WINDOW_WIDTH*0.35, y), normal_color=col, font_size='26sp')
            btn.bind(on_release=on_rel); self.add_widget(btn)