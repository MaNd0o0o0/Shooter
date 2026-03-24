from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

class FancyButton(Button):
    def __init__(self, **kwargs):
        super(FancyButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = kwargs.get('font_size', '28sp')
        self.radius = kwargs.get('radius', 20)
        self.normal_color = kwargs.get('normal_color', (0.2, 0.6, 0.9, 1))
        self.down_color = kwargs.get('down_color', (0.1, 0.5, 0.8, 1))
        with self.canvas.before:
            Color(*self.normal_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(state=self._on_state)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _on_state(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            if value == 'down':
                Color(*self.down_color)
            else:
                Color(*self.normal_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])