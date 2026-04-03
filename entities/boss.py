"""
boss.py - البوسات (نسخة محسنة للأداء مع تحميل مسبق)
"""

from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from config import IMAGES_PATH, BOSS_SIZE, BOSS_HEALTH, BOSS_IMAGES
from entities.bullet import BossBullet
import math


class Boss(Image):
    """كلاس البوس الرئيسي - محسن للأداء"""
    
    # ✅ تحميل الصور مسبقاً (class variable) - مرة واحدة فقط لكل أنواع البوس
    _loaded_textures = {}
    _preloaded = False
    
    @classmethod
    def preload_all(cls):
        """تحميل جميع صور البوس مسبقاً"""
        if cls._preloaded:
            return
        from kivy.core.image import Image as CoreImage
        for boss_type, image_name in BOSS_IMAGES.items():
            try:
                path = f"{IMAGES_PATH}/{image_name}"
                texture = CoreImage(path).texture
                cls._loaded_textures[boss_type] = texture
                print(f"✅ Preloaded boss image: {boss_type}")
            except Exception as e:
                print(f"⚠️ Failed to preload {boss_type}: {e}")
        cls._preloaded = True
    
    def __init__(self, boss_type="normal", **kwargs):
        self.boss_type = boss_type
        
        # ✅ استخدام texture محمل مسبقاً إذا وجد
        if boss_type in Boss._loaded_textures:
            super().__init__(texture=Boss._loaded_textures[boss_type], size=BOSS_SIZE, **kwargs)
        else:
            image = BOSS_IMAGES.get(boss_type, "boss.png")
            super().__init__(source=f"{IMAGES_PATH}/{image}", size=BOSS_SIZE, **kwargs)
            # تخزين texture للاستخدام المستقبلي
            Boss._loaded_textures[boss_type] = self.texture
        
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.pos = (Window.width - 350, Window.height/2 - 125)  # مركز أفضل
        self.active = False
        self.shoot_timer = 0
        self.shoot_interval = 2.0
        self.move_direction = 1
        self.move_timer = 0
        self.entry_timer = 0
        self.pattern_timer = 0
        self.pattern_index = 0
        
        # ✅ منع إعادة تحميل الصورة
        self.source = ""
    
    def update(self, dt=0.016, player_pos=None, game=None):
        """تحديث البوس - محسن للأداء"""
        if not self.active:
            return
        
        # حركة الدخول (أسرع)
        if self.entry_timer < 2.0:
            self.entry_timer += dt
            if self.x > Window.width - 350:
                self.x -= 8
            return
        
        # حركة البوس (أبطأ لتقليل العمليات)
        self.move_timer += dt
        if self.move_timer > 2.5:
            self.move_direction *= -1
            self.move_timer = 0
        
        new_y = self.y + self.move_direction * 1.5
        if 150 <= new_y <= Window.height - 350:
            self.y = new_y
        
        # إطلاق النار
        self.shoot_timer += dt
        if self.shoot_timer >= self.shoot_interval and player_pos and game:
            self._shoot_pattern(player_pos, game)
            self.shoot_timer = 0
            self.shoot_interval = 2.5  # زيادة الفترة
    
    def _shoot_pattern(self, player_pos, game):
        """أنماط إطلاق حسب نوع البوس"""
        patterns = {
            'normal': self._shoot_normal,
            'fire': self._shoot_spread,
            'ice': self._shoot_three_way,
            'electric': self._shoot_circular,
            'final': self._shoot_final
        }
        
        pattern = patterns.get(self.boss_type, self._shoot_normal)
        pattern(player_pos, game)
    
    def _shoot_normal(self, player_pos, game):
        """إطلاق عادي - رصاصة واحدة"""
        bullet = BossBullet(pos=(self.x, self.center_y), target_pos=player_pos)
        game.boss_bullets.append(bullet)
        game.add_widget(bullet)
    
    def _shoot_spread(self, player_pos, game):
        """إطلاق متفرق - 3 رصاصات"""
        for angle in [-15, 0, 15]:
            bullet = BossBullet(pos=(self.x, self.center_y), angle=angle)
            game.boss_bullets.append(bullet)
            game.add_widget(bullet)
    
    def _shoot_three_way(self, player_pos, game):
        """إطلاق ثلاثي الاتجاهات"""
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.center_y
        base_angle = math.degrees(math.atan2(dy, dx))
        for angle in [base_angle - 20, base_angle, base_angle + 20]:
            bullet = BossBullet(pos=(self.x, self.center_y), angle=angle)
            game.boss_bullets.append(bullet)
            game.add_widget(bullet)
    
    def _shoot_circular(self, player_pos, game):
        """إطلاق دائري - 6 رصاصات فقط (بدلاً من 8)"""
        for i in range(6):
            angle = i * 60
            bullet = BossBullet(pos=(self.x, self.center_y), angle=angle)
            game.boss_bullets.append(bullet)
            game.add_widget(bullet)
    
    def _shoot_final(self, player_pos, game):
        """إطلاق نهائي - نمط معقد ولكن أقل رصاصات"""
        # صليبي
        for angle in [0, 90, 180, 270]:
            bullet = BossBullet(pos=(self.x, self.center_y), angle=angle)
            game.boss_bullets.append(bullet)
            game.add_widget(bullet)
        # قطري (4 فقط بدلاً من 6)
        for angle in [45, 135, 225, 315]:
            bullet = BossBullet(pos=(self.x, self.center_y), angle=angle)
            game.boss_bullets.append(bullet)
            game.add_widget(bullet)
    
    def hit_animation(self):
        """تأثير الإصابة"""
        self.opacity = 0.6
        Clock.schedule_once(lambda dt: setattr(self, 'opacity', 1), 0.1)
    
    def take_damage(self, amount):
        """أخذ ضرر"""
        self.health -= amount
        self.hit_animation()
        return self.health <= 0