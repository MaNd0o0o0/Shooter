"""labels.py - النصوص المخصصة"""
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.core.window import Window

class AnimatedLabel(Label):
    def __init__(self, text, pos, duration=2, fade_in=0.3, fade_out=0.5, **kwargs):
        super().__init__(text=text, pos=pos, opacity=0, size_hint=(None,None), halign='center', valign='middle', **kwargs)
        anim = Animation(opacity=1,d=fade_in)+Animation(duration=duration)+Animation(opacity=0,d=fade_out)
        anim.bind(on_complete=lambda *a: self.parent and self.parent.remove_widget(self)); anim.start(self)

class AchievementPopup(AnimatedLabel):
    def __init__(self, achievement, **kwargs):
        super().__init__(text=f"🏆 UNLOCKED!\n{achievement['name']}\n+{achievement['reward']} Coins", font_size=42, bold=True, color=(1,1,0,1), pos=(Window.width/2-300,Window.height/2), size=(600,150), **kwargs)