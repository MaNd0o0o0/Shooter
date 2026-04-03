"""
store_screen.py - شاشة المتجر
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from widgets.fancy_button import FancyButton


class StoreScreen(Widget):
    """شاشة المتجر لشراء العناصر"""
    
    def __init__(self, game_instance=None, on_back_callback=None, **kwargs):
        super(StoreScreen, self).__init__(**kwargs)
        self.game_instance = game_instance
        self.on_back_callback = on_back_callback
        self.size = Window.size
        self.pos = (0, 0)
        
        with self.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size, pos=(0, 0))
        
        self.create_ui()
    
    def create_ui(self):
        title = Label(text="🛒 GAME STORE", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width/2 - 150, Window.height*0.85), size=(300, 60), halign='center')
        self.add_widget(title)
        
        coins_value = self.game_instance.coins_count if self.game_instance else 0
        self.coins_label = Label(text=f"💰 COINS: {coins_value}", font_size=32, color=(1, 0.84, 0, 1),
                                 pos=(Window.width/2 - 100, Window.height*0.78), size=(200, 50), halign='center')
        self.add_widget(self.coins_label)
        
        store_items = [
            {"name": "+50 HEALTH", "price": 5, "icon": "❤️", "effect": "health",
             "pos": (Window.width*0.1, Window.height*0.6)},
            {"name": "+1 BULLET", "price": 10, "icon": "🔫", "effect": "bullet",
             "pos": (Window.width*0.35, Window.height*0.6)},
            {"name": "SPEED BOOST", "price": 15, "icon": "⚡", "effect": "speed",
             "pos": (Window.width*0.6, Window.height*0.6)},
            {"name": "SHIELD", "price": 20, "icon": "🛡️", "effect": "shield",
             "pos": (Window.width*0.1, Window.height*0.35)},
            {"name": "BOMB X3", "price": 25, "icon": "💣", "effect": "bomb",
             "pos": (Window.width*0.35, Window.height*0.35)},
            {"name": "MAX HP +50", "price": 50, "icon": "💖", "effect": "max_health",
             "pos": (Window.width*0.6, Window.height*0.35)},
        ]
        
        for item in store_items:
            btn = FancyButton(
                text=f"{item['icon']} {item['name']}\n{item['price']} COINS",
                size=(220, 120), pos=item['pos'],
                background_color=(0.2, 0.6, 0.9, 1), font_size=20
            )
            btn.bind(on_release=lambda x, i=item: self.buy_item(i))
            self.add_widget(btn)
        
        back_btn = FancyButton(
            text="⬅️ BACK",
            size=(250, 70), pos=(Window.width/2 - 125, Window.height*0.1),
            background_color=(0.8, 0.2, 0.2, 1), font_size=24
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        self.add_widget(back_btn)
    
    def update_coins_label(self):
        if self.game_instance:
            self.coins_label.text = f"💰 COINS: {self.game_instance.coins_count}"
    
    def buy_item(self, item):
        if not self.game_instance:
            return
        
        if self.game_instance.coins_count >= item['price']:
            self.game_instance.coins_count -= item['price']
            
            if item['effect'] == "health":
                self.game_instance.health = min(self.game_instance.health + 50, self.game_instance.max_health)
            elif item['effect'] == "bullet":
                if self.game_instance.bullets_count < 5:
                    self.game_instance.base_bullets = self.game_instance.bullets_count + 1
                    self.game_instance.bullets_count += 1
                    self.game_instance.temp_bullet_timer = 8
            elif item['effect'] == "speed":
                self.game_instance.speed_active = True
                self.game_instance.speed_timer = 15
            elif item['effect'] == "shield":
                self.game_instance.shield_active = True
                self.game_instance.shield_timer = 15
            elif item['effect'] == "bomb":
                from entities.effects import Explosion
                for enemy in self.game_instance.enemies[:]:
                    explosion = Explosion(pos=enemy.pos)
                    self.game_instance.add_widget(explosion)
                    self.game_instance.remove_widget(enemy)
                    self.game_instance.enemies.remove(enemy)
                    self.game_instance.score += 15
                self.game_instance.play_sound(self.game_instance.bomb_sound)
            elif item['effect'] == "max_health":
                self.game_instance.max_health += 50
                self.game_instance.health = self.game_instance.max_health
            
            self.update_coins_label()
            self.game_instance.play_sound(self.game_instance.coin_sound)
            self.show_message("✅ PURCHASED!", (0.3, 0.8, 0.3, 1))
        else:
            self.show_message("❌ NOT ENOUGH COINS!", (0.9, 0.2, 0.2, 1))
    
    def show_message(self, text, color):
        msg = Label(text=text, font_size=36, color=color,
                    pos=(Window.width/2 - 150, Window.height/2), size=(300, 50), halign='center')
        self.add_widget(msg)
        Clock.schedule_once(lambda dt: self.remove_widget(msg) if msg.parent else None, 2)
    
    def go_back(self):
        if self.on_back_callback:
            self.on_back_callback()