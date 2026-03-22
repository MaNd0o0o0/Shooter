"""joystick.py - عصا التحكم"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from math import sqrt

class Joystick(Widget):    def __init__(self, base_size=220, knob_size=100, **kwargs):
        super().__init__(**kwargs)
        self.base_size, self.knob_size, self.dx, self.dy, self.active, self.center_pos = base_size, knob_size, 0, 0, False, (0,0)
        with self.canvas: Color(1,1,1,0.25); self.base = Ellipse(size=(base_size,base_size), pos=(-500,-500)); Color(0,1,0,0.8); self.knob = Ellipse(size=(knob_size,knob_size), pos=(-500,-500))
    def on_touch_down(self, touch):
        self.active = True; self.center_pos = touch.pos
        self.base.pos = (touch.x-self.base_size/2, touch.y-self.base_size/2)
        self.knob.pos = (touch.x-self.knob_size/2, touch.y-self.knob_size/2)
        return super().on_touch_down(touch)
    def on_touch_move(self, touch):
        if not self.active: return
        dx, dy = touch.x-self.center_pos[0], touch.y-self.center_pos[1]
        dist = sqrt(dx**2+dy**2); max_d = self.base_size/2
        if dist > max_d: dx, dy = dx*max_d/dist, dy*max_d/dist
        self.knob.pos = (self.center_pos[0]+dx-self.knob_size/2, self.center_pos[1]+dy-self.knob_size/2)
        self.dx, self.dy = dx/max_d, dy/max_d
    def on_touch_up(self, touch):
        self.active = False; self.dx = self.dy = 0; self.base.pos = self.knob.pos = (-500,-500)
        return super().on_touch_up(touch)