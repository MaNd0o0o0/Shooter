from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from widgets.fancy_button import FancyButton

class StoreScreen(Widget):
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
                      pos=(Window.width*0.35, Window.height*0.85),
                      size_hint=(None, None), size=(400, 60), halign='center')
        self.add_widget(title)
        
        coins_label = Label(text=f"💰 Coins: {self.game_instance.coins_count if self.game_instance else 0}",
                            font_size=32, color=(1, 0.84, 0, 1),
                            pos=(Window.width*0.35, Window.height*0.78),
                            size_hint=(None, None), size=(300, 50), halign='center')
        self.add_widget(coins_label)
        
        store_items = [
            {"name": "+50 Health", "price": 5, "icon": "❤️", "pos": (Window.width*0.1, Window.height*0.6)},
            {"name": "+1 Bullet", "price": 10, "icon": "🔫", "pos": (Window.width*0.35, Window.height*0.6)},
            {"name": "Speed Boost", "price": 15, "icon": "⚡", "pos": (Window.width*0.6, Window.height*0.6)},
            {"name": "Shield", "price": 20, "icon": "🛡️", "pos": (Window.width*0.1, Window.height*0.35)},
            {"name": "Bomb x3", "price": 25, "icon": "💣", "pos": (Window.width*0.35, Window.height*0.35)},
            {"name": "Max HP +50", "price": 50, "icon": "💖", "pos": (Window.width*0.6, Window.height*0.35)},
        ]
        
        for item in store_items:
            item_btn = FancyButton(
                text=f"{item['icon']} {item['name']}\n{item['price']} Coins",
                size_hint=(None, None), size=(220, 120), pos=item['pos'],
                background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1), font_size=20
            )
            item_btn.bind(on_release=lambda x, i=item: self.buy_item(i, coins_label))
            self.add_widget(item_btn)
        
        back_btn = FancyButton(text="⬅️ Back to Menu", size_hint=(None, None), size=(250, 70),
                               pos=(Window.width*0.35, Window.height*0.1),
                               background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), font_size=24)
        back_btn.bind(on_release=lambda x: self.go_back())
        self.add_widget(back_btn)
    
    def buy_item(self, item, coins_label):
        if self.game_instance and self.game_instance.coins_count >= item['price']:
            self.game_instance.coins_count -= item['price']
            
            if item['name'] == "+50 Health":
                self.game_instance.health = min(self.game_instance.health + 50, self.game_instance.max_health)
            elif item['name'] == "+1 Bullet":
                if self.game_instance.bullets_count < 5:
                    self.game_instance.bullets_count += 1
            elif item['name'] == "Speed Boost":
                self.game_instance.speed_active = True
                self.game_instance.speed_timer = 15
            elif item['name'] == "Shield":
                self.game_instance.shield_active = True
                self.game_instance.shield_timer = 15
            elif item['name'] == "Max HP +50":
                self.game_instance.max_health += 50
                self.game_instance.health = self.game_instance.max_health
            
            coins_label.text = f"💰 Coins: {self.game_instance.coins_count}"
            self.game_instance.play_sound(self.game_instance.coin_sound if hasattr(self.game_instance, 'coin_sound') else None)
        else:
            error_label = Label(text="❌ Not Enough Coins!", font_size=36, color=(1, 0, 0, 1),
                                pos=(Window.width*0.35, Window.height*0.5),
                                size_hint=(None, None), size=(400, 50), halign='center')
            self.add_widget(error_label)
            Clock.schedule_once(lambda dt: self.remove_widget(error_label) if error_label.parent else None, 2)
    
    def go_back(self):
        if self.on_back_callback:
            self.on_back_callback()