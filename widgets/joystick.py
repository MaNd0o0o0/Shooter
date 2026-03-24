from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window

class Joystick(Widget):
    def __init__(self, **kwargs):
        super(Joystick, self).__init__(**kwargs)
        self.base_size = 310
        self.knob_size = 150
        self.dx = 0
        self.dy = 0
        self.active = False
        self.touch_id = None  # ✅ تتبع معرف اللمسة
        
        # ✅ تثبيت الجoystick في أسفل يسار الشاشة
        self.fixed_pos = (200, 200)
        self.center_pos = self.fixed_pos
        
        # رسم الجoystick في الموقع الثابت
        with self.canvas:
            Color(1, 1, 1, 0.25)
            self.base = Ellipse(
                size=(self.base_size, self.base_size),
                pos=(self.fixed_pos[0] - self.base_size/2, 
                     self.fixed_pos[1] - self.base_size/2)
            )
            Color(0, 1, 0, 0.8)
            self.knob = Ellipse(
                size=(self.knob_size, self.knob_size),
                pos=(self.fixed_pos[0] - self.knob_size/2, 
                     self.fixed_pos[1] - self.knob_size/2)
            )
    
    def on_touch_down(self, touch):
        # ✅ التحقق من لمس منطقة الجoystick فقط
        dist = ((touch.x - self.fixed_pos[0])**2 + (touch.y - self.fixed_pos[1])**2) ** 0.5
        if dist <= self.base_size/2:
            self.active = True
            self.touch_id = touch.uid  # ✅ حفظ معرف اللمسة
            self.center_pos = self.fixed_pos
            return True  # ✅ استهلاك اللمسة
        return super(Joystick, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        # ✅ التحقق من أن اللمسة تنتمي للجoystick
        if not self.active or touch.uid != self.touch_id:
            return
        dx = touch.x - self.fixed_pos[0]
        dy = touch.y - self.fixed_pos[1]
        dist = (dx**2 + dy**2)**0.5
        max_dist = self.base_size/2
        if dist > max_dist:
            scale = max_dist/dist
            dx *= scale
            dy *= scale
        self.knob.pos = (self.fixed_pos[0] + dx - self.knob_size/2,
                         self.fixed_pos[1] + dy - self.knob_size/2)
        self.dx = dx/max_dist
        self.dy = dy/max_dist
    
    def on_touch_up(self, touch):
        # ✅ التحقق من أن اللمسة تنتمي للجoystick
        if self.active and touch.uid == self.touch_id:
            self.active = False
            self.touch_id = None
            self.dx = 0
            self.dy = 0
            # إعادة المقبض للمركز
            self.knob.pos = (self.fixed_pos[0] - self.knob_size/2, 
                             self.fixed_pos[1] - self.knob_size/2)
            return True
        return super(Joystick, self).on_touch_up(touch)