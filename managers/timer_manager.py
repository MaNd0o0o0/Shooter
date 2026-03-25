class TimerManager:
    def __init__(self, game):
        self.game = game

    def update(self, dt):
        g = self.game

        # 🎯 Combo
        if g.combo_timer > 0:
            g.combo_timer -= dt
            if g.combo_timer <= 0:
                g.combo = 0

        # ⚡ Skill
        if not g.skill_ready:
            g.skill_cooldown -= dt
            if g.skill_cooldown <= 0:
                g.skill_ready = True

        # 🔫 Temp bullets
        if g.temp_bullet_timer > 0:
            g.temp_bullet_timer -= dt
            if g.temp_bullet_timer <= 0:
                g.bullets_count = g.base_bullets

        # ❄️ Freeze
        if g.freeze_active:
            g.freeze_timer -= dt
            if g.freeze_timer <= 0:
                g.freeze_active = False

                # رجوع شكل الأعداء
                for enemy in g.enemies:
                    enemy.opacity = 1

        # ⚡ Speed
        if g.speed_active:
            g.speed_timer -= dt
            if g.speed_timer <= 0:
                g.speed_active = False

        # 🛡 Shield
        if g.shield_active:
            g.shield_timer -= dt
            if g.shield_timer <= 0:
                g.shield_active = False