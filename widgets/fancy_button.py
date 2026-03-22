"""fancy_button.py - زر مخصص"""
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

class FancyButton(Button):
    def __init__(self, normal_color=(0.2,0.6,0.9,1), down_color=(0.1,0.5,0.8,1), radius=20, font_size='28sp', **kwargs):
        super().__init__(**kwargs)
        self.normal_color, self.down_color, self.radius, self.font_size = normal_color, down_color, radius, font_size
        self.background_normal = self.background_down = ''; self.color = (1,1,1,1); self.bold = True
        self._draw_background()
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._on_state)
    def _draw_background(self):
        with self.canvas.before: Color(*self.normal_color); self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])
    def _update_rect(self, *args):
        if hasattr(self,'rect'): self.rect.pos = self.pos; self.rect.size = self.size
    def _on_state(self, inst, val):
        self.canvas.before.clear()
        with self.canvas.before: Color(*(self.down_color if val=='down' else self.normal_color)); self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])