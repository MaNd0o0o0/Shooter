"""
ui_manager.py - إدارة واجهة المستخدم
"""

from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.animation import Animation


class UIManager:
    """مدير واجهة المستخدم - يدير العناصر البصرية"""
    
    def __init__(self, game):
        self.game = game
    
    def show_message(self, text, color=(1, 1, 1, 1), duration=2.0):
        """عرض رسالة عائمة"""
        label = Label(
            text=text,
            font_size=32,
            bold=True,
            color=color,
            pos=(Window.width/2 - 200, Window.height/2),
            size=(400, 60),
            halign='center'
        )
        self.game.add_widget(label)
        anim = Animation(opacity=0, duration=duration)
        anim.bind(on_complete=lambda *args: self.game.remove_widget(label))
        anim.start(label)
    
    def show_notification(self, text, icon="✅"):
        """عرض إشعار"""
        label = Label(
            text=f"{icon} {text}",
            font_size=28,
            bold=True,
            color=(0.3, 0.9, 0.3, 1),
            pos=(Window.width/2 - 200, Window.height - 100),
            size=(400, 50),
            halign='center'
        )
        self.game.add_widget(label)
        anim = Animation(opacity=0, duration=2)
        anim.bind(on_complete=lambda *args: self.game.remove_widget(label))
        anim.start(label)
    
    def show_floating_text(self, text, pos, color=(1, 1, 0, 1)):
        """عرض نص عائم في موقع محدد"""
        label = Label(
            text=text,
            font_size=24,
            bold=True,
            color=color,
            pos=pos,
            size=(200, 40),
            halign='center'
        )
        self.game.add_widget(label)
        anim = Animation(y=pos[1] + 50, opacity=0, duration=1)
        anim.bind(on_complete=lambda *args: self.game.remove_widget(label))
        anim.start(label)
    
    def update_health_bar(self):
        """تحديث شريط الصحة"""
        if hasattr(self.game, 'health_bar') and self.game.health_bar:
            percent = self.game.health / self.game.max_health
            # تحديث الشريط
            pass
    
    def update_xp_bar(self):
        """تحديث شريط الخبرة"""
        if hasattr(self.game, 'xp_bar') and self.game.xp_bar:
            xp_needed = self.game.level * 100
            percent = self.game.xp / xp_needed if xp_needed > 0 else 0
            # تحديث الشريط
            pass