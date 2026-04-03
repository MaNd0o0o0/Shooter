"""
timer_manager.py - إدارة المؤقتات
"""


class TimerManager:
    """مدير المؤقتات - يدير جميع المؤقتات في اللعبة"""
    
    def __init__(self, game):
        self.game = game
    
    def update(self, dt):
        """تحديث جميع المؤقتات"""
        g = self.game
        
        if dt > 0.1:
            dt = 0.033
        
        # مؤقت الكومبو
        if g.combo_timer > 0:
            g.combo_timer -= dt
            if g.combo_timer <= 0:
                g.combo = 0
        
        # مؤقت السكل
        if hasattr(g, 'skill_ready') and not g.skill_ready:
            g.skill_cooldown -= dt
            if g.skill_cooldown <= 0:
                g.skill_ready = True
        
        # مؤقت الرصاصات المؤقتة
        if g.temp_bullet_timer > 0:
            g.temp_bullet_timer -= dt
            if g.temp_bullet_timer <= 0:
                g.bullets_count = g.base_bullets
        
        # مؤقت التجميد
        if g.freeze_active:
            g.freeze_timer -= dt
            if g.freeze_timer <= 0:
                g.freeze_active = False
                for enemy in g.enemies:
                    try:
                        enemy.opacity = 1
                        if hasattr(enemy, 'unfreeze'):
                            enemy.unfreeze()
                    except:
                        pass
        
        # مؤقت السرعة
        if g.speed_active:
            g.speed_timer -= dt
            if g.speed_timer <= 0:
                g.speed_active = False
        
        # مؤقت الدرع
        if g.shield_active:
            g.shield_timer -= dt
            if g.shield_timer <= 0:
                g.shield_active = False