"""
ui_layer.py - إدارة واجهة المستخدم
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.core.window import Window
from kivy.animation import Animation
from typing import Callable
from config import IMAGES_PATH


class UILayer(Widget):
    """يدير واجهة المستخدم والعناصر التفاعلية"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.health_bar = None
        self.xp_bar = None
        self.health_text = None
        self.coins_label = None
        self.level_label = None
        self.menu_btn = None
        self.fire_button = None
        self.fire_btn_touch = None
        self.joystick = None
        
        self.showing_menu = False
        self._init_ui()
    
    def _init_ui(self):
        bar_x = Window.width * 0.02
        bar_y = Window.height * 0.92
        bar_width = Window.width * 0.25
        bar_height = Window.height * 0.03
        
        self.health_bar = self._create_bar(bar_x, bar_y, bar_width, bar_height, (0.9, 0.2, 0.2, 1))
        
        xp_y = bar_y - (Window.height * 0.04)
        self.xp_bar = self._create_bar(bar_x, xp_y, bar_width, Window.height * 0.02, (0.2, 0.6, 1, 1))
        
        self.health_text = Label(text="100/100", font_size=Window.height * 0.02, pos=(bar_x + 10, bar_y + 5), size=(150, 30))
        self.add_widget(self.health_text)
        
        self.coins_icon = Image(source=f"{IMAGES_PATH}/coin.png", size=(50, 50), pos=(bar_x, xp_y - (Window.height * 0.09)))
        self.add_widget(self.coins_icon)
        
        self.coins_label = Label(text="0", font_size=Window.height * 0.04, bold=True, color=(1, 0.9, 0.2, 1), pos=(bar_x + 55, self.coins_icon.y + 5), size=(100, 50))
        self.add_widget(self.coins_label)
        
        self.level_label = Label(text="Lv.1", font_size=Window.height * 0.025, pos=(bar_x + bar_width + 60, xp_y - (Window.height * 0.04)), size=(100, 40))
        self.add_widget(self.level_label)
        
        menu_size = Window.width * 0.06
        self.menu_btn = Button(text="☰", size=(menu_size, menu_size), pos=(Window.width - menu_size - 15, Window.height - menu_size - 15), font_size=menu_size * 0.6, background_color=(0.1, 0.1, 0.1, 0.8))
        self.add_widget(self.menu_btn)
    
    def _create_bar(self, x, y, width, height, color):
        bar_data = {}
        with self.canvas.after:
            Color(0.2, 0.2, 0.2, 0.8)
            bg = RoundedRectangle(pos=(x, y), size=(width, height), radius=[8])
            bar_color = Color(*color)
            bar = RoundedRectangle(pos=(x+2, y+2), size=(width-4, height-4), radius=[6])
        bar_data["bg"] = bg
        bar_data["bar"] = bar
        bar_data["color"] = bar_color
        bar_data["max_width"] = width - 4
        return bar_data
    
    def update_bar(self, bar_data, percent, dynamic_color=False):
        percent = max(0, min(1, percent))
        target_width = bar_data["max_width"] * percent
        current_width = bar_data["bar"].size[0]
        new_width = current_width + (target_width - current_width) * 0.2
        bar_data["bar"].size = (new_width, bar_data["bar"].size[1])
        if dynamic_color:
            r = 1 - percent
            g = percent
            bar_data["color"].rgba = (r, g, 0.2, 1)
    
    def update_stats(self, health: int, max_health: int, xp: int, level: int, coins: int):
        health_percent = health / max_health
        self.update_bar(self.health_bar, health_percent, True)
        self.health_text.text = f"{health}/{max_health}"
        
        xp_needed = level * 100
        xp_percent = xp / xp_needed if xp_needed > 0 else 0
        self.update_bar(self.xp_bar, xp_percent)
        
        self.coins_label.text = str(coins)
        self.level_label.text = f"Lv.{level}"
    
    def update_health(self, health: int, max_health: int):
        health_percent = health / max_health
        self.update_bar(self.health_bar, health_percent, True)
        self.health_text.text = f"{health}/{max_health}"
    
    def update_score(self, score: int):
        pass
    
    def update_coins(self, coins: int):
        self.coins_label.text = str(coins)
    
    def create_joystick(self, pos=None, base_size=280, knob_size=120):
        from widgets.joystick import Joystick
        
        if pos is None:
            pos = (Window.width * 0.08, Window.height * 0.12)
        
        self.joystick = Joystick()
        self.joystick.base_size = base_size
        self.joystick.knob_size = knob_size
        self.joystick.pos = pos
        self.joystick.fixed_pos = pos
        
        self.joystick.canvas.clear()
        with self.joystick.canvas:
            Color(1, 1, 1, 0.25)
            self.joystick.base = Ellipse(size=(base_size, base_size), pos=(pos[0] - base_size/2, pos[1] - base_size/2))
            Color(0, 1, 0, 0.8)
            self.joystick.knob = Ellipse(size=(knob_size, knob_size), pos=(pos[0] - knob_size/2, pos[1] - knob_size/2))
        
        self.add_widget(self.joystick)
        return self.joystick
    
    def create_fire_button(self, pos=None, size=None):
        if size is None:
            size = Window.width * 0.12
        if pos is None:
            pos = (Window.width - size - (Window.width * 0.05), Window.height * 0.08)
        
        self.fire_button = Image(source=f"{IMAGES_PATH}/fire.png", size=(size, size), pos=pos)
        self.add_widget(self.fire_button)
        
        self.fire_btn_touch = Button(size=(size, size), pos=pos, background_color=(0, 0, 0, 0))
        self.add_widget(self.fire_btn_touch)
        
        return self.fire_btn_touch
    
    def show_level_up(self, new_level: int):
        level_label = Label(text=f"🌟 LEVEL {new_level} UP! 🌟", font_size=72, bold=True, color=(1, 1, 0, 1), pos=(Window.width/2 - 300, Window.height/2), size=(600, 100), halign='center')
        self.add_widget(level_label)
        anim = Animation(font_size=90, duration=0.2) + Animation(font_size=72, duration=0.2) + Animation(opacity=0, duration=0.8)
        anim.bind(on_complete=lambda *args: self.remove_widget(level_label))
        anim.start(level_label)
    
    def show_mission_complete(self, mission):
        popup = Label(text=f"✅ MISSION COMPLETE!\n{mission['icon']} {mission['name']}\n+{mission['reward']}💰", font_size=28, bold=True, color=(0.8, 1, 0.2, 1), pos=(Window.width/2 - 250, Window.height/2), size=(500, 120), halign='center')
        self.add_widget(popup)
        anim = Animation(opacity=0, duration=3)
        anim.bind(on_complete=lambda *args: self.remove_widget(popup))
        anim.start(popup)
    
    def show_boss_warning(self, boss_type: str):
        label = Label(text=f"⚠️ {boss_type.upper()} BOSS INCOMING! ⚠️", font_size=48, bold=True, color=(1, 0.3, 0, 1), pos=(Window.width/2 - 300, Window.height/2), size=(600, 80), halign='center')
        self.add_widget(label)
        anim = Animation(opacity=0, duration=2)
        anim.bind(on_complete=lambda *args: self.remove_widget(label))
        anim.start(label)
    
    def show_boss_defeated(self):
        label = Label(text="🏆 BOSS DEFEATED! 🏆", font_size=48, bold=True, color=(1, 0.9, 0.2, 1), pos=(Window.width/2 - 250, Window.height/2), size=(500, 80), halign='center')
        self.add_widget(label)
        anim = Animation(opacity=0, duration=2)
        anim.bind(on_complete=lambda *args: self.remove_widget(label))
        anim.start(label)
    
    def set_menu_callback(self, callback: Callable):
        if self.menu_btn:
            self.menu_btn.bind(on_release=lambda x: callback())
    
    def set_fire_button_callbacks(self, on_press: Callable, on_release: Callable):
        if self.fire_btn_touch:
            self.fire_btn_touch.bind(on_press=on_press)
            self.fire_btn_touch.bind(on_release=on_release)
    
    def update(self, dt):
        pass