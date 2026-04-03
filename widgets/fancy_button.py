"""
fancy_button.py - زر مزخرف مع تأثيرات
"""

from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle


class FancyButton(Button):
    """زر مخصص مع تأثيرات بصرية"""
    
    def __init__(self, **kwargs):
        self.gradient = kwargs.pop('gradient', False)
        self.shadow = kwargs.pop('shadow', True)
        
        super(FancyButton, self).__init__(**kwargs)
        
        self.background_normal = ''
        self.background_down = ''
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = kwargs.get('font_size', '28sp')
        self.radius = kwargs.get('radius', 20)
        
        self.normal_color = kwargs.get('background_color', (0.2, 0.6, 0.9, 1))
        self.down_color = kwargs.get('down_color', (0.1, 0.5, 0.8, 1))
        self.shadow_color = (0, 0, 0, 0.25)
        
        self._init_canvas()
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(state=self._on_state)
    
    def _init_canvas(self):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.shadow:
                Color(*self.shadow_color)
                self.shadow_rect = RoundedRectangle(
                    pos=(self.x + 3, self.y - 3),
                    size=self.size, radius=[self.radius]
                )
            Color(*self.normal_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius]
            )
            if self.gradient:
                Color(1, 1, 1, 0.2)
                self.grad_rect = RoundedRectangle(
                    pos=(self.x + 2, self.y + 2),
                    size=(self.width - 4, self.height - 4),
                    radius=[self.radius - 2]
                )
    
    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        if self.shadow:
            self.shadow_rect.pos = (self.x + 3, self.y - 3)
            self.shadow_rect.size = self.size
        if self.gradient and hasattr(self, 'grad_rect'):
            self.grad_rect.pos = (self.x + 2, self.y + 2)
            self.grad_rect.size = (self.width - 4, self.height - 4)
    
    def _on_state(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.shadow:
                Color(*self.shadow_color)
                self.shadow_rect = RoundedRectangle(
                    pos=(self.x + 3, self.y - 3),
                    size=self.size, radius=[self.radius]
                )
            if value == 'down':
                Color(*self.down_color)
            else:
                Color(*self.normal_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius]
            )
            if self.gradient:
                Color(1, 1, 1, 0.2)
                self.grad_rect = RoundedRectangle(
                    pos=(self.x + 2, self.y + 2),
                    size=(self.width - 4, self.height - 4),
                    radius=[self.radius - 2]
                )