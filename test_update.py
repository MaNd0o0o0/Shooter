"""
test_update.py - اختبار بسيط للتأكد من أن الـ update يعمل
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window


class TestWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        Clock.schedule_interval(self.update, 1/60)
        print("✅ Test widget created, update scheduled")
    
    def update(self, dt):
        self.counter += 1
        if self.counter % 60 == 0:
            print(f"🟢 Update working! Frame {self.counter}")


class TestApp(App):
    def build(self):
        Window.size = (400, 600)
        return TestWidget()


if __name__ == '__main__':
    TestApp().run()