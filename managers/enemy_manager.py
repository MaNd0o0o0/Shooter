from random import randint, choice
from config import MAX_ENEMIES, MAX_ENEMIES_ON_SCREEN
from entities.enemy import enemy_map, Enemy

class EnemyManager:
    def __init__(self, game):
        self.game = game

    def spawn(self, dt):
        g = self.game

        g.enemy_spawn_timer += dt

        spawn_chance = 15 + (g.game_level * 3)
        spawn_chance = min(spawn_chance, 50)

        if (
            g.enemy_spawn_timer >= g.enemy_spawn_delay and
            len(g.enemies) < min(MAX_ENEMIES, MAX_ENEMIES_ON_SCREEN)
            and randint(1, 100) <= spawn_chance
        ):
            g.enemy_spawn_timer = 0

            enemy_class = choice(list(enemy_map.values()))
            e = enemy_class()

            e.pos = g._get_spawn_pos()
            g.enemies.append(e)
            g.add_widget(e)

    def update(self, dt):
        g = self.game

        for e in g.enemies[:]:

            # ❄️ تأثير التجميد (شكل فقط)
            if g.freeze_active:
                e.opacity = 0.5
            else:
                e.opacity = 1

            # 🧠 حركة العدو (تتوقف فقط أثناء التجميد)
            if not g.freeze_active:
                dx = g.player.x - e.x
                dy = g.player.y - e.y
                dist = (dx**2 + dy**2) ** 0.5

                if dist != 0:
                    e.x += (dx / dist) * e.speed
                    e.y += (dy / dist) * e.speed

            # 💥 تصادم مع اللاعب
            if g.player.collide_widget(e):
                if not g.shield_active:
                    g.take_damage(e.damage)

                # لو عندك الدالة
                if hasattr(g, "handle_enemy_hit"):
                    g.handle_enemy_hit(e)

            # 🔫 ضرب العدو بالرصاص
            for b in g.bullets[:]:
                if b.collide_widget(e):

                    # ❄️ دامج مضاعف أثناء التجميد
                    if g.freeze_active:
                        e.health -= 2
                    else:
                        e.health -= 1

                    # تأثير الضرب
                    if hasattr(g, "handle_bullet_hit"):
                        g.handle_bullet_hit(e, b)

                    # 💀 موت العدو
                    if e.health <= 0:
                        g.handle_enemy_death(e)

                    # حذف الرصاصة
                    if b in g.bullets:
                        g.remove_widget(b)
                        g.bullets.remove(b)

                    break