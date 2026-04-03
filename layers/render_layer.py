"""
render_layer.py - إدارة الرسم والعرض البصري (مع دائرة الشيلد)
"""

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from typing import List, Optional
from random import randint
import math


class RenderLayer(Widget):
    """يدير جميع عناصر الرسم في اللعبة"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # مراجع للكيانات
        self.player = None
        self.bullets = []
        self.boss_bullets = []
        self.enemies = []
        self.coins = []
        self.guns = []
        self.medicals = []
        self.powerups = []
        self.boss = None
        
        # عناصر الخلفية
        self.clouds = []
        self.birds = []
        
        # ✅ مؤثرات الشيلد
        self.shield_circle = None
        self.shield_color = None
        self.shield_alpha = 0
        self.shield_pulse = 0
        self.shield_pulse_direction = 1
        
        # شريط صحة البوس
        self.boss_name_label = None
        self.boss_health_percent = None
        
        # تهيئة الخلفية
        self._init_background()
        
        self.wave_offset = 0
        self.show_debug = False
    
    def _init_background(self):
        from config import IMAGES_PATH
        
        self.sky = Image(
            source=f"{IMAGES_PATH}/bg.png",
            size=Window.size,
            pos=(0, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.sky)
        
        self.mountain1 = Image(
            source=f"{IMAGES_PATH}/mountains.png",
            size=(Window.width, Window.height),
            pos=(0, 150),
            allow_stretch=True,
            keep_ratio=False
        )
        self.mountain2 = Image(
            source=f"{IMAGES_PATH}/mountains.png",
            size=(Window.width, Window.height),
            pos=(Window.width, 150),
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.mountain1)
        self.add_widget(self.mountain2)
        
        self.city1 = Image(
            source=f"{IMAGES_PATH}/city.png",
            size=(Window.width, Window.height),
            pos=(0, 100),
            allow_stretch=True,
            keep_ratio=False
        )
        self.city2 = Image(
            source=f"{IMAGES_PATH}/city.png",
            size=(Window.width, Window.height),
            pos=(Window.width, 100),
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.city1)
        self.add_widget(self.city2)
        
        self.sea1 = Image(
            source=f"{IMAGES_PATH}/sea.png",
            size=(Window.width, 180),
            pos=(0, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        self.sea2 = Image(
            source=f"{IMAGES_PATH}/sea.png",
            size=(Window.width, 180),
            pos=(Window.width, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.sea1)
        self.add_widget(self.sea2)
        
        cloud_positions = [
            {"x": 50, "y": 550, "size": (150, 50), "speed": 0.4},
            {"x": 350, "y": 580, "size": (200, 60), "speed": 0.5},
            {"x": 750, "y": 520, "size": (180, 55), "speed": 0.45},
        ]
        
        for pos in cloud_positions:
            cloud = Image(
                source=f"{IMAGES_PATH}/clouds.png",
                size=pos["size"],
                pos=(pos["x"], pos["y"]),
                allow_stretch=True,
                keep_ratio=False
            )
            cloud.speed = pos["speed"]
            self.clouds.append(cloud)
            self.add_widget(cloud)
        
        for i in range(3):
            bird = Image(
                source=f"{IMAGES_PATH}/bird.png",
                size=(55, 55)
            )
            bird.pos = (randint(Window.width, Window.width + 800), randint(Window.height - 250, Window.height - 100))
            bird.speed = randint(2, 5)
            self.birds.append(bird)
            self.add_widget(bird)
    
    def update_background(self, dt: float):
        self.mountain1.x -= 0.8
        self.mountain2.x -= 0.8
        if self.mountain1.right <= 0:
            self.mountain1.x = self.mountain2.right
        if self.mountain2.right <= 0:
            self.mountain2.x = self.mountain1.right
        
        self.city1.x -= 1.5
        self.city2.x -= 1.5
        if self.city1.right <= 0:
            self.city1.x = self.city2.right
        if self.city2.right <= 0:
            self.city2.x = self.city1.right
        
        self.sea1.x -= 3
        self.sea2.x -= 3
        if self.sea1.right <= 0:
            self.sea1.x = self.sea2.right
        if self.sea2.right <= 0:
            self.sea2.x = self.sea1.right
        
        for cloud in self.clouds:
            cloud.x -= cloud.speed
            if cloud.right < 0:
                cloud.x = Window.width + randint(100, 500)
                cloud.y = randint(450, 620)
        
        for bird in self.birds:
            bird.x -= bird.speed
            if bird.right < 0:
                bird.x = Window.width + randint(0, 200)
                bird.y = randint(Window.height - 250, Window.height - 100)
        
        self.wave_offset += dt * 3
        wave_y = math.sin(self.wave_offset) * 6
        self.sea1.y = wave_y
        self.sea2.y = wave_y
    
    def update_entities(self):
        """تحديث مواقع الكيانات المرسومة"""
        # ✅ تحديث موقع دائرة الشيلد
        if self.player and hasattr(self, 'shield_circle'):
            size = max(self.player.width, self.player.height) * 1.8
            self.shield_circle.size = (size, size)
            self.shield_circle.pos = (
                self.player.center_x - size/2,
                self.player.center_y - size/2
            )
    
    def draw_shield(self, active: bool, alpha: float = 0.4):
        """
        رسم دائرة زرقاء حول اللاعب عند تفعيل الشيلد
        مع تأثير نبض (pulse)
        """
        if not self.player:
            return
        
        # ✅ إنشاء دائرة الشيلد إذا لم تكن موجودة
        if not hasattr(self, 'shield_circle'):
            with self.canvas.after:
                self.shield_color = Color(0, 0.5, 1, 0)
                self.shield_circle = Ellipse(pos=(0, 0), size=(0, 0))
        
        if active:
            # ✅ تأثير النبض (pulse) - تتغير الشفافية
            self.shield_pulse += 0.05 * self.shield_pulse_direction
            if self.shield_pulse >= 1:
                self.shield_pulse = 1
                self.shield_pulse_direction = -1
            elif self.shield_pulse <= 0.3:
                self.shield_pulse = 0.3
                self.shield_pulse_direction = 1
            
            # ✅ الشفافية النهائية (alpha الأساسي + تأثير النبض)
            final_alpha = alpha * (0.5 + self.shield_pulse * 0.5)
            self.shield_color.rgba = (0, 0.5, 1, final_alpha)
            
            # ✅ حجم الدائرة
            size = max(self.player.width, self.player.height) * 1.8
            self.shield_circle.size = (size, size)
            self.shield_circle.pos = (
                self.player.center_x - size/2,
                self.player.center_y - size/2
            )
        else:
            # ✅ إخفاء الدائرة
            self.shield_color.a = 0
            self.shield_pulse = 0
    
    def draw_boss_health_bar(self, boss_name: str, health_percent: float, boss_type: str = "normal"):
        bar_width = 600
        bar_height = 35
        center_x = Window.width // 2
        
        self.remove_boss_health_bar()
        
        with self.canvas.after:
            Color(0.1, 0.1, 0.1, 0.95)
            RoundedRectangle(pos=(center_x - bar_width//2, Window.height - 80), size=(bar_width, bar_height + 20), radius=[10])
            Color(0.9, 0.7, 0.2, 0.8)
            RoundedRectangle(pos=(center_x - bar_width//2 - 2, Window.height - 82), size=(bar_width + 4, bar_height + 24), radius=[12])
            Color(0.2, 0.2, 0.2, 0.9)
            RoundedRectangle(pos=(center_x - bar_width//2, Window.height - 75), size=(bar_width, bar_height), radius=[6])
            
            if health_percent > 0.5:
                color = (1 - (health_percent - 0.5) * 2, 1, 0.2, 1)
            elif health_percent > 0.25:
                color = (1, 0.5 + (health_percent - 0.25) * 2, 0.2, 1)
            else:
                color = (1, 0.2 + health_percent * 1.2, 0.2, 1)
            
            Color(*color)
            RoundedRectangle(pos=(center_x - bar_width//2 + 3, Window.height - 72), size=(max(0, (bar_width - 6) * health_percent), bar_height - 6), radius=[4])
        
        boss_names = {'normal': 'IRON GENERAL', 'fire': 'FIRE LORD', 'ice': 'ICE WARDEN', 'electric': 'THUNDER KING', 'final': 'SHADOW EMPEROR'}
        display_name = boss_names.get(boss_type, boss_name.upper())
        
        self.boss_name_label = Label(text=f"⚠️ {display_name} ⚠️", font_size=28, bold=True, color=(1, 0.8, 0.2, 1), pos=(center_x - 150, Window.height - 55), size=(300, 40), halign='center')
        self.add_widget(self.boss_name_label)
        
        self.boss_health_percent = Label(text=f"{int(health_percent * 100)}%", font_size=20, bold=True, color=(1, 1, 1, 1), pos=(center_x + bar_width//2 - 60, Window.height - 72), size=(60, 30), halign='center')
        self.add_widget(self.boss_health_percent)
    
    def remove_boss_health_bar(self):
        if self.boss_name_label and self.boss_name_label.parent:
            self.remove_widget(self.boss_name_label)
            self.boss_name_label = None
        if self.boss_health_percent and self.boss_health_percent.parent:
            self.remove_widget(self.boss_health_percent)
            self.boss_health_percent = None
    
    def screen_shake(self, intensity: float = 10, duration: float = 0.3):
        original_pos = self.pos
        
        def shake_step(dt, step):
            offset_x = randint(-int(intensity), int(intensity))
            offset_y = randint(-int(intensity), int(intensity))
            self.pos = (original_pos[0] + offset_x, original_pos[1] + offset_y)
        
        def stop_shake(dt):
            self.pos = original_pos
        
        steps = int(duration / 0.016)
        for i in range(steps):
            Clock.schedule_once(lambda dt, s=i: shake_step(dt, s), i * 0.016)
        Clock.schedule_once(stop_shake, duration)
    
    def show_text_popup(self, text: str, pos, color=(1, 1, 0, 1), duration: float = 1.0):
        label = Label(text=text, font_size=24, bold=True, color=color, pos=pos, size=(200, 40), halign='center')
        self.add_widget(label)
        anim = Animation(y=pos[1] + 50, opacity=0, duration=duration)
        anim.bind(on_complete=lambda *args: self.remove_widget(label))
        anim.start(label)
    
    def clear_all(self):
        for widget in list(self.children):
            if widget not in [self.sky, self.mountain1, self.mountain2, self.city1, self.city2, self.sea1, self.sea2]:
                if widget not in self.clouds and widget not in self.birds:
                    self.remove_widget(widget)
        
        self.remove_boss_health_bar()
        
        if hasattr(self, 'shield_circle'):
            self.canvas.after.remove(self.shield_circle)
            self.canvas.after.remove(self.shield_color)
            self.shield_circle = None
            self.shield_color = None
    
    def update(self, dt):
        pass