from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

class LogoScreen(Widget):
    """شاشة الشعار السوداء"""
    def __init__(self, on_complete_callback=None, **kwargs):
        super(LogoScreen, self).__init__(**kwargs)
        self.on_complete_callback = on_complete_callback
        self.size = Window.size
        self.pos = (0, 0)
        
        # ✅ خلفية سوداء
        with self.canvas:
            Color(0, 0, 0, 1)
            self.bg = Rectangle(size=Window.size, pos=(0, 0))
        
        # ✅ إضافة الشعار في المنتصف
        self.logo = Image(
            source="assets/images/logo.jpeg",
            size=(900, 900),
            pos=(Window.width/2 - 450, Window.height/2 - 200)
        )
        self.add_widget(self.logo)
        
        # ✅ الانتقال للسبلاش بعد 3 ثواني
        Clock.schedule_once(lambda dt: self.next_screen(), 3.0)
    
    def next_screen(self):
        """الانتقال للشاشة التالية"""
        if self.on_complete_callback:
            self.on_complete_callback()