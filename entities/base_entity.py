from kivy.uix.image import Image

class BaseEntity(Image):
    """كلاس أساسي لجميع الكيانات في اللعبة"""
    
    def __init__(self, source, size, pos=(0, 0), **kwargs):
        super(BaseEntity, self).__init__(source=source, size=size, pos=pos, **kwargs)
        self.health = 1
        self.max_health = 1
        self.speed = 0
        self.damage = 0
        self.active = True
    
    def update(self, dt=0.016):
        """تحديث حالة الكيان - يتم تجاوزها في الكلاسات الفرعية"""
        pass
    
    def take_damage(self, amount):
        """تطبيق الضرر على الكيان"""
        self.health -= amount
        if self.health <= 0:
            self.active = False
    
    def is_alive(self):
        """التحقق مما إذا كان الكيان حيًا"""
        return self.health > 0 and self.active