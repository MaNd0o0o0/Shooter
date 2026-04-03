"""
physics_manager.py - مدير الفيزياء باستخدام C++
"""

import os
import sys

# محاولة تحميل مكتبة C++
try:
    import physics_cpp
    CPP_AVAILABLE = True
    print("""
╔══════════════════════════════════════════════════════════╗
║     ✅ C++ PHYSICS ENGINE LOADED SUCCESSFULLY!          ║
║     🚀 Performance: HIGH                                ║
║     💀 Collision System: C++                            ║
║     🎯 Bullet Pool: C++                                 ║
║     📦 Spatial Grid: C++                                ║
╚══════════════════════════════════════════════════════════╝
    """)
except ImportError as e:
    CPP_AVAILABLE = False
    print(f"⚠️ C++ physics engine not available: {e}")
    print("   Using Python fallback (slower performance)")


class PhysicsManager:
    """
    مدير الفيزياء - يستخدم C++ كلما أمكن
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cpp_available = CPP_AVAILABLE
        
        if self.cpp_available:
            # تهيئة مكونات C++
            self.bullet_pool = physics_cpp.BulletPool(500)
            self.spatial_grid = physics_cpp.SpatialGrid(screen_width, screen_height, 150)
            self.collision_system = physics_cpp.CollisionSystem(screen_width, screen_height, 150)
            self.movement_array = physics_cpp.MovementArray(200)
            
            # ربط الأنظمة
            self.collision_system.set_bullet_pool(self.bullet_pool)
        else:
            # نسخة Python احتياطية
            self.bullet_pool = None
            self.spatial_grid = None
            self.collision_system = None
            self.movement_array = None
    
    def create_bullet_pool(self, size=500):
        """إنشاء تجمع رصاصات"""
        if self.cpp_available:
            return self.bullet_pool
        return None
    
    def get_bullet(self, x, y, angle, speed, max_distance):
        """الحصول على رصاصة من التجمع"""
        if self.cpp_available:
            return self.bullet_pool.get_bullet(x, y, angle, speed, max_distance)
        return -1
    
    def return_bullet(self, bullet_id):
        """إعادة رصاصة إلى التجمع"""
        if self.cpp_available:
            self.bullet_pool.return_bullet(bullet_id)
    
    def update_bullets(self, dt):
        """تحديث جميع الرصاصات"""
        if self.cpp_available:
            self.bullet_pool.update_bullets(dt, self.screen_width, self.screen_height)
    
    def add_enemy(self, enemy_id, x, y, w, h):
        """إضافة عدو إلى نظام التصادم"""
        if self.cpp_available:
            self.collision_system.add_enemy(enemy_id, x, y, w, h)
            self.spatial_grid.add_entity(x, y)
            return enemy_id
        return -1
    
    def update_enemy(self, enemy_id, x, y):
        """تحديث موقع عدو"""
        if self.cpp_available:
            self.collision_system.update_enemy_position(enemy_id, x, y)
            self.spatial_grid.update_position(enemy_id, x, y)
    
    def remove_enemy(self, enemy_id):
        """إزالة عدو"""
        if self.cpp_available:
            self.collision_system.remove_enemy(enemy_id)
            self.spatial_grid.remove_entity(enemy_id)
    
    def check_collisions(self, player_x, player_y, player_w, player_h):
        """فحص التصادمات"""
        if self.cpp_available:
            # فحص تصادم الرصاص مع الأعداء
            hit_enemies = self.collision_system.check_bullet_collisions(
                player_x, player_y, player_w, player_h
            )
            
            # فحص تصادم اللاعب مع الأعداء
            player_hit = self.collision_system.check_player_collision(
                player_x, player_y, player_w, player_h
            )
            
            return hit_enemies, player_hit
        
        return [], False
    
    def move_towards(self, x, y, target_x, target_y, speed, dt):
        """تحريك كيان نحو هدف (محسن)"""
        if self.cpp_available:
            physics_cpp.move_towards(x, y, target_x, target_y, speed, dt)
            return x, y
        
        # نسخة Python احتياطية
        import math
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0.01:
            move = speed * dt
            if move > dist:
                move = dist
            x += (dx / dist) * move
            y += (dy / dist) * move
        return x, y
    
    def fast_distance(self, x1, y1, x2, y2):
        """حساب المسافة بسرعة"""
        if self.cpp_available:
            return physics_cpp.fast_distance(x1, y1, x2, y2)
        
        import math
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def clear(self):
        """مسح جميع البيانات"""
        if self.cpp_available:
            self.collision_system.clear()
            self.spatial_grid.clear()
    
    def is_available(self):
        """التحقق من توفر C++"""
        return self.cpp_available