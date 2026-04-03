"""
logo_screen.py - شاشة الشعار
"""

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label


class LogoScreen(Widget):
    """شاشة الشعار السوداء"""
    
    def __init__(self, on_complete_callback=None, **kwargs):
        super(LogoScreen, self).__init__(**kwargs)
        self.on_complete_callback = on_complete_callback
        self.size = Window.size
        self.pos = (0, 0)
        
        with self.canvas:
            Color(0, 0, 0, 1)
            self.bg = Rectangle(size=Window.size, pos=(0, 0))
        
        logo_size = min(Window.width * 0.95, 900)
        self.logo = Image(
            source="assets/images/logo.jpeg",
            size=(logo_size, logo_size),
            pos=(Window.width/2 - logo_size/2, Window.height/2 - logo_size/2)
        )
        self.add_widget(self.logo)
        
        self.loading_label = Label(
            text="Loading...",
            font_size=20,
            color=(0.7, 0.7, 0.7, 1),
            pos=(Window.width/2 - 50, Window.height * 0.1),
            size=(100, 40)
        )
        self.add_widget(self.loading_label)
        
        Clock.schedule_once(lambda dt: self.next_screen(), 3.0)
    
    def next_screen(self):
        if self.on_complete_callback:
            self.on_complete_callback()