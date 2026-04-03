"""
enemy_manager.py - إدارة الأعداء (اللاعب يخسر صحة والعدو يموت)
"""

from kivy.core.window import Window
from random import randint, choice
from config import MAX_ENEMIES, MAX_ENEMIES_ON_SCREEN
from entities.enemy import enemy_map, Enemy
from entities.effects import Explosion
from entities.powerup import Coin, Gun, Medical, PowerUp


class EnemyManager:
    """مدير الأعداء - العدو يموت واللاعب يخسر صحة عند التصادم"""
    
    def __init__(self, game):
        self.game = game
        self.frame_counter = 0
    
    def spawn(self, dt):
        """توليد أعداء جدد"""
        g = self.game
        
        if len(g.enemies) > 20:
            return
        
        g.enemy_spawn_timer += dt
        
        spawn_chance = 15 + (g.game_level * 3)
        spawn_chance = min(spawn_chance, 50)
        
        if (g.enemy_spawn_timer >= g.enemy_spawn_delay and
            len(g.enemies) < min(MAX_ENEMIES, MAX_ENEMIES_ON_SCREEN) and
            randint(1, 100) <= spawn_chance):
            
            g.enemy_spawn_timer = 0
            enemy_class = choice(list(enemy_map.values()))
            e = enemy_class()
            e.pos = g._get_spawn_pos()
            g.enemies.append(e)
            g.add_widget(e)
    
    def update(self, dt):
        """تحديث الأعداء - العدو يموت واللاعب يخسر صحة"""
        g = self.game
        
        if not hasattr(g, 'player') or not g.player:
            return
        
        self.frame_counter += 1
        
        # تحديث مؤقت التصادم (منع التصادم المتكرر)
        if hasattr(g, 'collision_timer'):
            g.collision_timer -= dt
            if g.collision_timer < 0:
                g.collision_timer = 0
        
        # تحديث الرصاصات كل إطارين
        if self.frame_counter % 2 == 0:
            if hasattr(g, 'update_bullets'):
                g.update_bullets(dt)
            if hasattr(g, 'update_boss_bullets'):
                g.update_boss_bullets(dt)
        
        # نسخة محدثة من الرصاصات
        bullets_list = g.bullets[:50]
        
        for e in g.enemies[:]:
            try:
                # تحديث العدو (حركته)
                if hasattr(e, 'update'):
                    e.update(dt, g.player)
                
                # تأثير التجميد
                if g.freeze_active:
                    e.opacity = 0.5
                else:
                    e.opacity = 1
                
                # 🔥🔥🔥 تصادم مع اللاعب - العدو يموت واللاعب يخسر صحة 🔥🔥🔥
                if g.player.collide_widget(e):
                    
                    # ✅ اللاعب يخسر صحة (مع مؤقت لمنع التصادم المتكرر)
                    if g.collision_timer <= 0 and not g.shield_active:
                        g.health -= e.damage
                        g.collision_timer = 0.5  # منع التصادم مرة أخرى لمدة نصف ثانية
                        
                        # صوت الضرر
                        if hasattr(g, 'play_sound'):
                            g.play_sound(explosion_sound)
                        
                        # تأثير اهتزاز الشاشة
                        if hasattr(g, 'render_layer') and hasattr(g.render_layer, 'screen_shake'):
                            g.render_layer.screen_shake(intensity=5, duration=0.2)
                        
                        # تأثير وميض اللاعب
                        if hasattr(g.player, 'hit_animation'):
                            g.player.hit_animation()
                    
                    # تأثيرات بصرية للتصادم
                    explosion = Explosion(pos=e.pos)
                    g.add_widget(explosion)
                    if hasattr(g, 'create_particles'):
                        g.create_particles(e.pos, color=(1, 0.5, 0, 1), count=15)
                    
                    # 💀💀💀 قتل العدو فوراً 💀💀💀
                    g.total_kills += 1
                    g.score += 15
                    g.xp += 15
                    
                    # رفع المستوى إذا لزم الأمر
                    if g.xp >= g.level * 100:
                        g.level += 1
                        g.xp = 0
                        g.max_health += 20
                        g.health = g.max_health
                        if hasattr(g, 'show_level_up'):
                            g.show_level_up(g.level)
                    
                    # توليد عناصر سلبية
                    rnd = randint(1, 100)
                    if rnd <= 35:
                        coin = Coin(pos=e.pos)
                        g.coins.append(coin)
                        g.add_widget(coin)
                    elif rnd <= 50:
                        gun = Gun(pos=e.pos)
                        g.guns.append(gun)
                        g.add_widget(gun)
                    elif rnd <= 65:
                        medical = Medical(pos=e.pos)
                        g.medicals.append(medical)
                        g.add_widget(medical)
                    elif rnd <= 85:
                        power_type = choice(["speed", "shield", "bomb", "freeze", "health"])
                        powerup = PowerUp(pos=e.pos, power_type=power_type)
                        g.powerups.append(powerup)
                        g.add_widget(powerup)
                    
                    # إزالة العدو
                    if e in g.enemies:
                        g.enemies.remove(e)
                    if e.parent:
                        e.parent.remove_widget(e)
                    
                    # ✅ التحقق من موت اللاعب
                    if g.health <= 0:
                        g.game_over()
                    
                    continue  # تخطي باقي الكود لهذا العدو
                
                # ضرب العدو بالرصاص
                for b in bullets_list:
                    if b.hit or not b.active:
                        continue
                    
                    # فلترة سريعة بالمسافة
                    if abs(b.x - e.x) > 100 or abs(b.y - e.y) > 100:
                        continue
                    
                    if b.collide_widget(e):
                        b.hit = True
                        
                        e.health -= 1
                        
                        # تأثيرات بصرية
                        explosion = Explosion(pos=e.pos)
                        g.add_widget(explosion)
                        if hasattr(g, 'create_particles'):
                            g.create_particles(e.pos, color=(1, 0.5, 0, 1), count=10)
                        
                        if e.health <= 0:
                            # قتل العدو
                            g.total_kills += 1
                            g.score += 15
                            g.xp += 15
                            
                            if g.xp >= g.level * 100:
                                g.level += 1
                                g.xp = 0
                                g.max_health += 20
                                g.health = g.max_health
                                if hasattr(g, 'show_level_up'):
                                    g.show_level_up(g.level)
                            
                            # توليد عناصر
                            rnd = randint(1, 100)
                            if rnd <= 35:
                                coin = Coin(pos=e.pos)
                                g.coins.append(coin)
                                g.add_widget(coin)
                            elif rnd <= 50:
                                gun = Gun(pos=e.pos)
                                g.guns.append(gun)
                                g.add_widget(gun)
                            elif rnd <= 65:
                                medical = Medical(pos=e.pos)
                                g.medicals.append(medical)
                                g.add_widget(medical)
                            elif rnd <= 85:
                                power_type = choice(["speed", "shield", "bomb", "freeze", "health"])
                                powerup = PowerUp(pos=e.pos, power_type=power_type)
                                g.powerups.append(powerup)
                                g.add_widget(powerup)
                            
                            # إزالة العدو
                            if e in g.enemies:
                                g.enemies.remove(e)
                            if e.parent:
                                e.parent.remove_widget(e)
                        
                        # إزالة الرصاصة
                        if b in g.bullets:
                            g.remove_widget(b)
                            g.bullets.remove(b)
                        break
                        
            except Exception as error:
                print(f"Enemy update error: {error}")
                continue
    
    def force_kill_enemy(self, enemy):
        """قتل عدو إجبارياً"""
        g = self.game
        if enemy in g.enemies:
            explosion = Explosion(pos=enemy.pos)
            g.add_widget(explosion)
            g.enemies.remove(enemy)
            if enemy.parent:
                enemy.parent.remove_widget(enemy)
            return True
        return False
    
    def force_kill_all_enemies(self):
        """قتل جميع الأعداء فوراً"""
        g = self.game
        for enemy in g.enemies[:]:
            explosion = Explosion(pos=enemy.pos)
            g.add_widget(explosion)
            if enemy in g.enemies:
                g.enemies.remove(enemy)
            if enemy.parent:
                enemy.parent.remove_widget(enemy)
        return len(g.enemies)