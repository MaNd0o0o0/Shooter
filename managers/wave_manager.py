"""
wave_manager.py - نظام الموجات (متوافق مع الكود القديم)
"""

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.animation import Animation
from random import choice
from config import MAX_ENEMIES_GLOBAL, SPAWN_WAVE_DELAY, ENEMIES_PER_WAVE, BOSS_SPAWN_WAVE


class WaveManager:
    """مدير الموجات - متوافق مع نظام الموجات القديم"""
    
    def __init__(self, game):
        self.game = game
        self.wave_timer = 0
        self.wave_number = 1
        self.enemies_this_wave = 0
        self.wave_active = False
        self.boss_wave = False
        self.enemies_to_spawn = 0
        self.spawn_queue = []
    
    def start_wave(self):
        self.wave_active = True
        self.enemies_this_wave = 0
        self.boss_wave = (self.wave_number % BOSS_SPAWN_WAVE == 0)
        
        enemies_to_spawn = ENEMIES_PER_WAVE + (self.wave_number // 2)
        enemies_to_spawn = min(enemies_to_spawn, MAX_ENEMIES_GLOBAL)
        self.enemies_to_spawn = enemies_to_spawn
        
        self.show_wave_message()
        self.spawn_queue = list(range(enemies_to_spawn))
        Clock.schedule_once(lambda dt: self.spawn_next_enemy(), 0.5)
    
    def spawn_next_enemy(self):
        if len(self.spawn_queue) > 0:
            self.spawn_queue.pop(0)
            self.spawn_enemy()
            if len(self.spawn_queue) > 0:
                Clock.schedule_once(lambda dt: self.spawn_next_enemy(), 0.6)
    
    def spawn_enemy(self):
        if len(self.game.enemies) < MAX_ENEMIES_GLOBAL:
            enemy_type = self.get_enemy_type()
            
            from entities.enemy import Enemy
            e = Enemy(enemy_type)
            pos = self.game._get_spawn_pos()
            e.pos = pos
            
            self.game.enemies.append(e)
            self.game.add_widget(e)
            self.enemies_this_wave += 1
            
            if self.boss_wave and not self.game.boss:
                self.spawn_boss()
    
    def spawn_boss(self):
        from entities.boss import Boss
        from core.audio_manager import stop_background_music, start_background_music
        
        if self.wave_number < 5:
            boss_type = "normal"
        elif self.wave_number < 10:
            boss_type = "fire"
        elif self.wave_number < 15:
            boss_type = "ice"
        elif self.wave_number < 20:
            boss_type = "electric"
        else:
            boss_type = "final"
        
        self.game.boss_type = boss_type
        self.game.boss = Boss(boss_type=boss_type)
        self.game.boss.active = True
        self.game.boss.pos = (Window.width - 350, Window.height/2 - 200)
        
        self.game.add_widget(self.game.boss)
        
        boss_label = Label(
            text=f"⚠️ BOSS {boss_type.upper()} INCOMING! ⚠️",
            font_size=48,
            bold=True,
            color=(1, 0.3, 0, 1),
            pos=(Window.width/2 - 300, Window.height/2),
            size=(600, 80),
            halign='center'
        )
        self.game.add_widget(boss_label)
        Clock.schedule_once(lambda dt: self.game.remove_widget(boss_label) if boss_label.parent else None, 3)
        
        stop_background_music()
        start_background_music(self.game.music_muted, True)
    
    def get_enemy_type(self):
        if self.wave_number < 3:
            return "soldier"
        elif self.wave_number < 6:
            return choice(["soldier", "fast"])
        elif self.wave_number < 10:
            return choice(["soldier", "fast", "armor"])
        else:
            return choice(["soldier", "fast", "armor", "bomber", "ghost"])
    
    def show_wave_message(self):
        if self.boss_wave:
            text = f"🔥 WAVE {self.wave_number} - BOSS INCOMING! 🔥"
            color = (1, 0.3, 0, 1)
        else:
            text = f"⚔️ WAVE {self.wave_number} ⚔️"
            color = (1, 0.8, 0, 1)
        
        label = Label(
            text=text,
            font_size=88,
            bold=True,
            color=color,
            pos=(Window.width/2 - 300, Window.height/2),
            size=(600, 100),
            halign='center'
        )
        self.game.add_widget(label)
        anim = Animation(opacity=0, duration=2)
        anim.bind(on_complete=lambda *args: self.game.remove_widget(label) if label.parent else None)
        anim.start(label)
    
    def end_wave(self):
        from core.audio_manager import stop_background_music, start_background_music
        
        self.wave_active = False
        self.wave_number += 1
        
        bonus = self.wave_number * 5
        self.game.coins_count += bonus
        
        bonus_label = Label(
            text=f"+{bonus}💰",
            font_size=32,
            bold=True,
            color=(1, 0.9, 0.2, 1),
            pos=(Window.width/2 - 50, Window.height/2),
            size=(100, 50),
            halign='center'
        )
        self.game.add_widget(bonus_label)
        anim = Animation(opacity=0, y=bonus_label.y + 50, duration=1)
        anim.bind(on_complete=lambda *args: self.game.remove_widget(bonus_label) if bonus_label.parent else None)
        anim.start(bonus_label)
        
        stop_background_music()
        start_background_music(self.game.music_muted, False)
    
    def update(self, dt):
        if dt > 0.1:
            dt = 0.033
        
        if not self.wave_active:
            self.wave_timer += dt
            if self.wave_timer >= SPAWN_WAVE_DELAY:
                self.wave_timer = 0
                self.start_wave()
        else:
            if len(self.game.enemies) == 0 and self.enemies_this_wave > 0:
                if not self.game.boss or (self.game.boss and not self.game.boss.active):
                    self.end_wave()