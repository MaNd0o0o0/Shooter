from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.core.window import Window

class LevelUpLabel(Label):
    def __init__(self, level, **kwargs):
        super(LevelUpLabel, self).__init__(
            text=f"🎉 LEVEL {level} UP! 🎉",
            font_size=72,
            bold=True,
            color=(1, 1, 0, 1),
            pos=(Window.width/2 - 250, Window.height/2),
            size_hint=(None, None),
            size=(500, 100),
            halign='center',
            valign='middle',
            **kwargs
        )
        self.opacity = 0
        anim = Animation(opacity=1, d=0.3) + Animation(duration=1.5) + Animation(opacity=0, d=0.5)
        anim.bind(on_complete=self.remove_self)
        anim.start(self)
    
    def remove_self(self, *args):
        if self.parent:
            self.parent.remove_widget(self)

class AchievementPopup(Label):
    def __init__(self, achievement, **kwargs):
        super(AchievementPopup, self).__init__(
            text=f"🏆 UNLOCKED!\n{achievement['name']}\n+{achievement['reward']} Coins",
            font_size=42,
            bold=True,
            color=(1, 1, 0, 1),
            pos=(Window.width/2 - 300, Window.height/2),
            size_hint=(None, None),
            size=(600, 150),
            halign='center',
            valign='middle',
            **kwargs
        )
        self.opacity = 0
        anim = Animation(opacity=1, d=0.3) + Animation(duration=2) + Animation(opacity=0, d=0.5)
        anim.bind(on_complete=self.remove_self)
        anim.start(self)
    
    def remove_self(self, *args):
        if self.parent:
            self.parent.remove_widget(self)