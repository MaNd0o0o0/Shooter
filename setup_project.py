#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_project.py - نسخة مُصححة لإنشاء هيكل المشروع
"""
import os
import json

# ==================== محتوى الملفات (مختصر للضرورة) ====================

CONFIG_PY = '''"""config.py - إعدادات المشروع"""
from kivy.core.window import Window
import os

Window.fullscreen = 'auto'
WINDOW_WIDTH = Window.width
WINDOW_HEIGHT = Window.height

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

PLAYER_SIZE = (260, 260)
BULLET_SIZE = (50, 50)
BOSS_BULLET_SIZE = (40, 40)
POWERUP_SIZE = (80, 80)
COIN_SIZE = (100, 100)
ENEMY_SIZES = {'normal': (150,150), 'fast': (120,120), 'armor': (180,180), 'bomber': (150,150), 'ghost': (140,140)}
BOSS_SIZE = (500, 500)

PLAYER_SPEED = 8
BULLET_SPEED = 14
BOSS_BULLET_SPEED = 8
SCROLL_SPEEDS = {'mountains': 0.4, 'city': 1.5, 'items': 2}

MAX_BULLETS = 30
MAX_BOSS_BULLETS = 20
MAX_PARTICLES = 100
MAX_ENEMIES_ON_SCREEN = 8

BOSS_LEVELS = {3: "normal", 6: "fire", 9: "ice", 12: "electric", 15: "final"}

UI_COLORS = {'btn_normal': (0.2,0.6,0.9,1), 'btn_down': (0.1,0.5,0.8,1), 'health_bg': (0.15,0.15,0.15,0.9), 'health_fg': (1,0.3,0.3,1), 'shield': (0,0.5,1,0.5)}
BOUNDS = {'top': WINDOW_HEIGHT, 'bottom': 160, 'left': 0, 'right': WINDOW_WIDTH}
'''

AUDIO_MANAGER_PY = '''"""audio_manager.py - مدير الصوت"""
from kivy.core.audio import SoundLoader
from config import SOUNDS_DIRimport os

class AudioManager:
    def __init__(self, sfx_volume=1.0, music_volume=0.5):
        self.sfx_volume = sfx_volume
        self.music_volume = music_volume
        self.sfx_muted = self.music_muted = False
        self.sounds = {}
        self.background_music = self.boss_music = self._current_music = None
        self._load_sounds()
    
    def _load_sounds(self):
        sounds = {'shoot':'shoot.wav','explosion':'explosion.wav','coin':'coin.wav','gun':'gun.wav','heal':'heal.wav','powerup':'powerup.wav','bomb':'bomb.wav','levelup':'levelup.wav'}
        for k,f in sounds.items():
            s = SoundLoader.load(os.path.join(SOUNDS_DIR, f))
            if s: s.volume = self.sfx_volume; self.sounds[k] = s
    
    def load_music(self, bg='background_music.mp3', boss='BossBattle.wav'):
        for fname,attr in [(bg,'background_music'),(boss,'boss_music')]:
            m = SoundLoader.load(os.path.join(SOUNDS_DIR, fname))
            if m: m.volume = self.music_volume; m.loop = True; setattr(self, attr, m)
    
    def play_sfx(self, name):
        if not self.sfx_muted and name in self.sounds:
            try:
                s = self.sounds[name]
                if hasattr(s,'length') and s.length > 0: s.play()
            except: pass
    
    def play_background(self, use_boss=False):
        if self.music_muted: return
        self.stop_music()
        m = self.boss_music if use_boss else self.background_music
        if m and hasattr(m,'length') and m.length > 0:
            try: m.play(); self._current_music = m
            except: pass
    
    def stop_music(self):
        if self._current_music:
            try: self._current_music.stop()
            except: pass
        self._current_music = None
    
    def toggle_sfx(self): self.sfx_muted = not self.sfx_muted; return self.sfx_muted
    def toggle_music(self):
        self.music_muted = not self.music_muted
        if self.music_muted: self.stop_music()
        return self.music_muted
'''
SAVE_MANAGER_PY = '''"""save_manager.py - حفظ البيانات"""
import json, os

class SaveManager:
    def __init__(self, filename='game_data.json'): self.filename = filename
    def save(self, data):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e: print(f"Save error: {e}"); return False
    def load(self, default=None):
        if default is None: default = {}
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
        return default
    def delete(self):
        try:
            if os.path.exists(self.filename): os.remove(self.filename); return True
        except: pass
        return False
'''

FANCY_BUTTON_PY = '''"""fancy_button.py - زر مخصص"""
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

class FancyButton(Button):
    def __init__(self, normal_color=(0.2,0.6,0.9,1), down_color=(0.1,0.5,0.8,1), radius=20, font_size='28sp', **kwargs):
        super().__init__(**kwargs)
        self.normal_color, self.down_color, self.radius, self.font_size = normal_color, down_color, radius, font_size
        self.background_normal = self.background_down = ''; self.color = (1,1,1,1); self.bold = True
        self._draw_background()
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._on_state)
    def _draw_background(self):
        with self.canvas.before: Color(*self.normal_color); self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])
    def _update_rect(self, *args):
        if hasattr(self,'rect'): self.rect.pos = self.pos; self.rect.size = self.size
    def _on_state(self, inst, val):
        self.canvas.before.clear()
        with self.canvas.before: Color(*(self.down_color if val=='down' else self.normal_color)); self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])
'''

JOYSTICK_PY = '''"""joystick.py - عصا التحكم"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from math import sqrt

class Joystick(Widget):    def __init__(self, base_size=220, knob_size=100, **kwargs):
        super().__init__(**kwargs)
        self.base_size, self.knob_size, self.dx, self.dy, self.active, self.center_pos = base_size, knob_size, 0, 0, False, (0,0)
        with self.canvas: Color(1,1,1,0.25); self.base = Ellipse(size=(base_size,base_size), pos=(-500,-500)); Color(0,1,0,0.8); self.knob = Ellipse(size=(knob_size,knob_size), pos=(-500,-500))
    def on_touch_down(self, touch):
        self.active = True; self.center_pos = touch.pos
        self.base.pos = (touch.x-self.base_size/2, touch.y-self.base_size/2)
        self.knob.pos = (touch.x-self.knob_size/2, touch.y-self.knob_size/2)
        return super().on_touch_down(touch)
    def on_touch_move(self, touch):
        if not self.active: return
        dx, dy = touch.x-self.center_pos[0], touch.y-self.center_pos[1]
        dist = sqrt(dx**2+dy**2); max_d = self.base_size/2
        if dist > max_d: dx, dy = dx*max_d/dist, dy*max_d/dist
        self.knob.pos = (self.center_pos[0]+dx-self.knob_size/2, self.center_pos[1]+dy-self.knob_size/2)
        self.dx, self.dy = dx/max_d, dy/max_d
    def on_touch_up(self, touch):
        self.active = False; self.dx = self.dy = 0; self.base.pos = self.knob.pos = (-500,-500)
        return super().on_touch_up(touch)
'''

BASE_ENTITY_PY = '''"""base_entity.py - كلاس أساسي للكيانات"""
from kivy.uix.image import Image
from kivy.core.window import Window
from random import randint

class BaseEntity(Image):
    def __init__(self, source, size, pos=(0,0), **kwargs):
        super().__init__(source=source, size=size, pos=pos, **kwargs)
        self.health = self.max_health = 1; self.speed = self.damage = 0; self.active = True
    def update(self, dt): pass
    def is_offscreen(self, buffer=100):
        return self.x<-buffer or self.x>Window.width+buffer or self.y<-buffer or self.y>Window.height+buffer
    def take_damage(self, amount): self.health -= amount; return self.health <= 0
    def reset_position(self, x_range, y_range): self.pos = (randint(*x_range), randint(*y_range))
'''

PLAYER_PY = '''"""player.py - اللاعب"""
from entities.base_entity import BaseEntity
from config import PLAYER_SIZE, PLAYER_SPEED, BOUNDS

class Player(BaseEntity):
    SKINS = {"default":"player.png","blue":"player_blue.png","red":"player_red.png","gold":"player_gold.png","green":"player_green.png"}
    def __init__(self, skin="default", **kwargs):
        super().__init__(source=self.SKINS.get(skin,self.SKINS["default"]), size=PLAYER_SIZE, **kwargs)
        self.skin, self.speed, self.bullets_count, self.shield_active = skin, PLAYER_SPEED, 1, False
        self.pos = (120, BOUNDS['bottom']+50)
    def move(self, dx, dy, mult=1.0):
        self.pos = (max(BOUNDS['left'],min(self.x+dx*self.speed*mult, BOUNDS['right']-self.width)), max(BOUNDS['bottom'],min(self.y+dy*self.speed*mult, BOUNDS['top']-self.height)))
    def change_skin(self, name):        if name in self.SKINS: self.source = self.SKINS[name]; self.skin = name
'''

ENEMY_PY = '''"""enemy.py - الأعداء"""
from entities.base_entity import BaseEntity
from config import ENEMY_SIZES, WINDOW_WIDTH, WINDOW_HEIGHT
from random import randint

class BaseEnemy(BaseEntity):
    def __init__(self, source, size, speed, health, damage, **kwargs):
        super().__init__(source=source, size=size, **kwargs)
        self.speed, self.health, self.max_health, self.damage = speed, health, health, damage
        self._spawn()
    def _spawn(self): self.pos = (randint(WINDOW_WIDTH, WINDOW_WIDTH+400), randint(250, WINDOW_HEIGHT-150))
    def update(self, dt):
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0: self._spawn()

class EnemyFast(BaseEnemy):
    def __init__(self,**kw): super().__init__("enemy_fast.png",ENEMY_SIZES['fast'],randint(6,10),1,5,**kw)
class EnemyArmor(BaseEnemy):
    def __init__(self,**kw): super().__init__("enemy_armor.png",ENEMY_SIZES['armor'],2,5,8,**kw)
class EnemyBomber(BaseEnemy):
    def __init__(self,**kw): super().__init__("enemy_bomber.png",ENEMY_SIZES['bomber'],3,2,10,**kw)
class EnemyGhost(BaseEnemy):
    def __init__(self,**kw):
        super().__init__("enemy_ghost.png",ENEMY_SIZES['ghost'],4,2,7,**kw)
        self.visible, self.invisible_timer = True, 0
    def update(self, dt):
        super().update(dt)
        self.invisible_timer += dt
        if self.invisible_timer > 3: self.visible = not self.visible; self.opacity = 1.0 if self.visible else 0.3; self.invisible_timer = 0

ENEMY_TYPES = {"fast":EnemyFast,"armor":EnemyArmor,"bomber":EnemyBomber,"ghost":EnemyGhost,"normal":lambda **kw:BaseEnemy("enemy.png",ENEMY_SIZES['normal'],4,1,10,**kw)}
'''

BULLET_PY = '''"""bullet.py - الرصاصات"""
from entities.base_entity import BaseEntity
from config import BULLET_SIZE, BOSS_BULLET_SIZE, BULLET_SPEED, BOSS_BULLET_SPEED
from math import radians, cos, sin

class Bullet(BaseEntity):
    def __init__(self, pos, angle=0, **kwargs):
        super().__init__(source="bullet.png", size=BULLET_SIZE, pos=pos, **kwargs)
        self.angle, self.speed, self.distance = angle, BULLET_SPEED, 0
        self.max_distance = (self.parent.width*2) if self.parent else 2000
    def update(self, dt):
        rad = radians(self.angle); self.pos = (self.x+self.speed*cos(rad), self.y+self.speed*sin(rad)); self.distance += self.speed

class BossBullet(BaseEntity):    def __init__(self, pos, target_pos=None, **kwargs):
        super().__init__(source="boss_bullet.png", size=BOSS_BULLET_SIZE, pos=pos, **kwargs)
        self.speed, self.distance = BOSS_BULLET_SPEED, 0
        self.max_distance = (self.parent.width*2) if self.parent else 2000
        if target_pos:
            from math import atan2, degrees
            dx,dy = target_pos[0]-pos[0], target_pos[1]-pos[1]; self.angle = degrees(atan2(dy,dx))
        else: self.angle = 180
    def update(self, dt):
        rad = radians(self.angle); self.pos = (self.x+self.speed*cos(rad), self.y+self.speed*sin(rad)); self.distance += self.speed
'''

BOSS_PY = '''"""boss.py - نظام البوس"""
from entities.base_entity import BaseEntity
from entities.bullet import BossBullet
from config import BOSS_SIZE, BOSS_LEVELS, WINDOW_WIDTH, WINDOW_HEIGHT

class Boss(BaseEntity):
    IMAGES = {"normal":"boss.png","fire":"boss_fire.png","ice":"boss_ice.png","electric":"boss_electric.png","final":"boss_final.png"}
    def __init__(self, boss_type="normal", **kwargs):
        super().__init__(source=self.IMAGES.get(boss_type,self.IMAGES["normal"]), size=BOSS_SIZE, **kwargs)
        self.boss_type, self.health, self.max_health = boss_type, 300, 300
        self.pos = (WINDOW_WIDTH-600, WINDOW_HEIGHT/2-250); self.active = False
        self.shoot_timer, self.shoot_interval, self.move_dir, self.move_timer, self.entry_timer = 0, 2.0, 1, 0, 0
    def update(self, dt, player_pos=None, game=None):
        if not self.active: return
        if self.entry_timer < 2.0:
            self.entry_timer += dt
            if self.x > WINDOW_WIDTH-600: self.pos = (self.x-3, self.y)
            return
        self.move_timer += dt
        if self.move_timer > 3: self.move_dir *= -1; self.move_timer = 0
        ny = self.y + self.move_dir*2
        if 200 <= ny <= WINDOW_HEIGHT-300-self.height: self.pos = (self.x, ny)
        if self.shoot_timer >= self.shoot_interval and player_pos and game: self._shoot(player_pos, game); self.shoot_timer = 0
    def _shoot(self, player_pos, game):
        b = BossBullet(pos=(self.x, self.center_y), target_pos=player_pos)
        game.boss_bullets.append(b); game.add_widget(b); game.audio.play_sfx('shoot')
'''

POWERUP_PY = '''"""powerup.py - العناصر القابلة للجمع"""
from entities.base_entity import BaseEntity
from config import POWERUP_SIZE, COIN_SIZE, SCROLL_SPEEDS

class PowerUp(BaseEntity):
    ICONS = {"speed":"powerup_speed.png","shield":"powerup_shield.png","bomb":"powerup_bomb.png","freeze":"powerup_freeze.png","health":"powerup_health.png"}
    def __init__(self, pos, power_type="speed", **kwargs):
        super().__init__(source=self.ICONS.get(power_type,"coin.png"), size=POWERUP_SIZE, pos=pos, **kwargs)
        self.power_type, self.speed = power_type, SCROLL_SPEEDS['items']
    def update(self, dt): self.pos = (self.x - self.speed, self.y)
class Coin(BaseEntity):
    def __init__(self, pos, **kwargs):
        super().__init__(source="coin.png", size=COIN_SIZE, pos=pos, **kwargs); self.speed = SCROLL_SPEEDS['items']
    def update(self, dt): self.pos = (self.x - self.speed, self.y)

class Collectible(BaseEntity):
    def __init__(self, source, pos, **kwargs):
        super().__init__(source=source, size=COIN_SIZE, pos=pos, **kwargs); self.speed = SCROLL_SPEEDS['items']
    def update(self, dt): self.pos = (self.x - self.speed, self.y)
'''

EFFECTS_PY = '''"""effects.py - التأثيرات البصرية"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.core.window import Window
from random import randint

class Explosion(Image):
    def __init__(self, pos, **kwargs):
        super().__init__(source="explosion.png", size=(220,220), pos=pos, **kwargs); self.opacity = 1
        anim = Animation(opacity=0, d=0.4); anim.bind(on_complete=lambda *a: self.parent and self.parent.remove_widget(self)); anim.start(self)

class Particle(Widget):
    def __init__(self, pos, color=(1,1,1,1), **kwargs):
        super().__init__(**kwargs); self.size, self.pos = (10,10), pos
        self.velocity, self.lifetime, self.color = (randint(-5,5),randint(-5,5)), 1.0, color
        with self.canvas: Color(*color); self.rect = Ellipse(size=self.size, pos=self.pos)
    def update(self, dt):
        self.pos = (self.x+self.velocity[0], self.y+self.velocity[1]); self.lifetime -= dt
        ns = (max(0,self.size[0]-0.5), max(0,self.size[1]-0.5)); self.size = ns; self.rect.size = ns; self.rect.pos = self.pos
        return self.lifetime <= 0
'''

LABELS_PY = '''"""labels.py - النصوص المخصصة"""
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.core.window import Window

class AnimatedLabel(Label):
    def __init__(self, text, pos, duration=2, fade_in=0.3, fade_out=0.5, **kwargs):
        super().__init__(text=text, pos=pos, opacity=0, size_hint=(None,None), halign='center', valign='middle', **kwargs)
        anim = Animation(opacity=1,d=fade_in)+Animation(duration=duration)+Animation(opacity=0,d=fade_out)
        anim.bind(on_complete=lambda *a: self.parent and self.parent.remove_widget(self)); anim.start(self)

class AchievementPopup(AnimatedLabel):
    def __init__(self, achievement, **kwargs):
        super().__init__(text=f"🏆 UNLOCKED!\\n{achievement['name']}\\n+{achievement['reward']} Coins", font_size=42, bold=True, color=(1,1,0,1), pos=(Window.width/2-300,Window.height/2), size=(600,150), **kwargs)'''

GAME_SCREEN_PY = '''"""game_screen.py - شاشة اللعب"""
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.label import Label
from kivy.uix.image import Image
from config import *
from widgets.joystick import Joystick
from widgets.fancy_button import FancyButton
from entities.player import Player
from entities.enemy import ENEMY_TYPES
from entities.bullet import Bullet
from entities.boss import Boss
from entities.powerup import PowerUp, Coin, Collectible
from entities.effects import Explosion, Particle

class GameScreen(Widget):
    def __init__(self, audio_manager, save_manager, player_data=None, **kwargs):
        super().__init__(**kwargs)
        self.audio, self.saver, self.player_data = audio_manager, save_manager, player_data or {}
        self.state = {'score':0,'coins':0,'health':100,'max_health':100,'xp':0,'level':1,'game_level':1,'bullets_count':1,'total_kills':0,'bosses_defeated':0}
        self.entities = {'bullets':[],'boss_bullets':[],'enemies':[],'coins':[],'powerups':[],'particles':[],'guns':[],'medicals':[]}
        self.powerups_active = {'shield':False,'speed':False,'freeze':False}
        self.powerup_timers = {'shield':0,'speed':0,'freeze':0}
        self.boss = self.clock_event = self.joystick = None
        self.ui_labels, self.fire_delay, self.enemy_spawn_timer = {}, 0, 0
        self.completed_boss_levels = set()
    
    def start(self):
        self._reset(); self._setup_background(); self._spawn_player(); self._setup_ui(); self._setup_controls()
        self.clock_event = Clock.schedule_interval(self.update, 1/60); self.audio.play_background()
    
    def _reset(self):
        self.clear_widgets()
        self.state.update({'score':0,'coins':0,'health':100,'xp':0,'level':1,'game_level':1,'bullets_count':1})
        for lst in self.entities.values(): lst.clear()
        self.boss = None; self.powerups_active = {k:False for k in self.powerups_active}; self.completed_boss_levels.clear()
    
    def _setup_background(self):
        with self.canvas:
            Color(0.6,0.85,1,1); self.sky = Rectangle(size=(WINDOW_WIDTH,WINDOW_HEIGHT), pos=(0,0))
            Color(1,0.9,0.3,1); self.sun = Ellipse(pos=(WINDOW_WIDTH-300,WINDOW_HEIGHT-350), size=(200,200))
            Color(0,0.5,0.9,1); self.sea = Rectangle(size=(WINDOW_WIDTH,750), pos=(0,0))
        self.bg_m1 = Image(source="mountains.png", size=(WINDOW_WIDTH,1500), pos=(0,WINDOW_HEIGHT-1780))
        self.bg_m2 = Image(source="mountains.png", size=(WINDOW_WIDTH,1500), pos=(WINDOW_WIDTH,WINDOW_HEIGHT-1780))
        self.bg_c1 = Image(source="city.png", size=(WINDOW_WIDTH,1500), pos=(0,300))
        self.bg_c2 = Image(source="city.png", size=(WINDOW_WIDTH,1500), pos=(WINDOW_WIDTH,300))
        for w in [self.bg_m1,self.bg_m2,self.bg_c1,self.bg_c2]: self.add_widget(w)    
    def _spawn_player(self):
        skin = self.player_data.get('equipped_skin','default'); self.player = Player(skin=skin); self.add_widget(self.player)
    
    def _setup_ui(self):
        for key,pos in {'score':(20,WINDOW_HEIGHT-40),'coins':(20,WINDOW_HEIGHT-80),'health':(20,WINDOW_HEIGHT-120),'xp':(20,WINDOW_HEIGHT-160),'level':(20,WINDOW_HEIGHT-200)}.items():
            lbl = Label(text=f"{key.capitalize()}: 0", pos=pos, size_hint=(None,None), size=(200,40), halign='left')
            self.add_widget(lbl); self.ui_labels[key] = lbl
    
    def _setup_controls(self):
        self.joystick = Joystick(); self.add_widget(self.joystick)
        self.pause_btn = FancyButton(text="⏸️", size=(80,80), pos=(WINDOW_WIDTH-100,WINDOW_HEIGHT-100))
        self.pause_btn.bind(on_release=lambda x: self.pause()); self.add_widget(self.pause_btn)
    
    def update(self, dt):
        self._update_background(dt); self._update_player(dt); self._spawn_enemies(dt)
        self._update_entities(dt); self._check_collisions(); self._update_powerups(dt)
        self._update_ui(); self._check_progression(); self._check_game_over()
    
    def _update_background(self, dt):
        for m1,m2 in [(self.bg_m1,self.bg_m2),(self.bg_c1,self.bg_c2)]:
            spd = SCROLL_SPEEDS['mountains'] if m1==self.bg_m1 else SCROLL_SPEEDS['city']
            m1.pos = (m1.x-spd, m1.y); m2.pos = (m2.x-spd, m2.y)
            if m1.right<=0: m1.pos=(m2.right,m1.y)
            if m2.right<=0: m2.pos=(m1.right,m2.y)
    
    def _update_player(self, dt):
        if self.joystick and self.joystick.active:
            mult = 1.5 if self.powerups_active['speed'] else 1.0
            self.player.move(self.joystick.dx, self.joystick.dy, mult)
            self.fire_delay += dt
            rate = 0.1 if self.powerups_active['speed'] else 0.18
            if self.fire_delay > rate: self._fire(); self.fire_delay = 0
    
    def _fire(self):
        angles = {1:[0],2:[-5,5],3:[-10,0,10],4:[-15,-5,5,15]}.get(self.player.bullets_count, [-20,-10,0,10,20])
        for a in angles: b = Bullet(pos=(self.player.right,self.player.center_y), angle=a); self.entities['bullets'].append(b); self.add_widget(b)
        self.audio.play_sfx('shoot')
    
    def _spawn_enemies(self, dt):
        if self.boss: return
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= 2.5 and len(self.entities['enemies']) < MAX_ENEMIES_ON_SCREEN:
            self.enemy_spawn_timer = 0
            from random import choice, randint
            if self.state['game_level']>=3 and randint(1,100)<=min(50,15+self.state['game_level']*3):
                e = ENEMY_TYPES[choice(list(ENEMY_TYPES.keys()))](); self.entities['enemies'].append(e); self.add_widget(e)
    
    def _update_entities(self, dt):
        for name,lst in self.entities.items():            for e in lst[:]:
                if hasattr(e,'update'): e.update(dt)
                if hasattr(e,'is_offscreen') and e.is_offscreen():
                    lst.remove(e)
                    if e.parent: self.remove_widget(e)
        if self.boss and self.boss.active: self.boss.update(dt, (self.player.x,self.player.y), self)
    
    def _check_collisions(self):
        for b in self.entities['bullets'][:]:
            for e in self.entities['enemies'][:]:
                if b.collide_widget(e):
                    e.take_damage(1); self._spawn_explosion(e.pos)
                    if e.health<=0: self._on_enemy_killed(e)
                    if b in self.entities['bullets']: self.entities['bullets'].remove(b); 
                        if b.parent: self.remove_widget(b)
                    break
            if self.boss and self.boss.active and b.collide_widget(self.boss):
                self.boss.take_damage(1); self._spawn_explosion(b.pos)
                if b in self.entities['bullets']: self.entities['bullets'].remove(b); 
                    if b.parent: self.remove_widget(b)
                if self.boss.health<=0: self._on_boss_defeated()
        for bb in self.entities['boss_bullets'][:]:
            if self.player.collide_widget(bb) and not self.powerups_active['shield']: self.state['health']-=10
            if bb in self.entities['boss_bullets']: self.entities['boss_bullets'].remove(bb); 
                if bb.parent: self.remove_widget(bb)
        for e in self.entities['enemies'][:]:
            if self.player.collide_widget(e) and not self.powerups_active['shield']:
                self.state['health']-=e.damage; self._spawn_explosion(e.pos)
        for ctype in ['coins','powerups','guns','medicals']:
            for item in self.entities[ctype][:]:
                if self.player.collide_widget(item): self._collect_item(item,ctype)
    
    def _on_enemy_killed(self, enemy):
        self.state['total_kills']+=1; self.state['score']+=15; self.state['xp']+=15
        from random import randint,choice
        r=randint(1,100)
        if r<=30: self._spawn_drop(enemy.pos,'coin')
        elif r<=40: self._spawn_drop(enemy.pos,'gun')
        elif r<=45: self._spawn_drop(enemy.pos,'medical')
        elif r<=50: self._spawn_drop(enemy.pos,'powerup',choice(['speed','shield','bomb','freeze','health']))
        if self.state['xp']>=self.state['level']*100: self.state['level']+=1; self.state['xp']=0; self.state['max_health']+=20; self.state['health']=self.state['max_health']
        enemy._spawn()
    
    def _on_boss_defeated(self):
        self.state['bosses_defeated']+=1; self.completed_boss_levels.add(self.state['game_level'])
        self._spawn_explosion(self.boss.pos,50)
        self.state['score']+=100; self.state['xp']+=100; self.state['coins']+=25
        if self.boss.parent: self.remove_widget(self.boss); self.boss=None
        self.audio.stop_music(); self.audio.play_background()
        self.saver.save({'bosses_defeated':self.state['bosses_defeated'],'completed_boss_levels':list(self.completed_boss_levels)})    
    def _spawn_drop(self, pos, dtype, ptype=None):
        if dtype=='coin': c=Coin(pos=pos); self.entities['coins'].append(c); self.add_widget(c)
        elif dtype=='gun': g=Collectible("gun.png",pos=pos); self.entities['guns'].append(g); self.add_widget(g)
        elif dtype=='medical': m=Collectible("medical.png",pos=pos); self.entities['medicals'].append(m); self.add_widget(m)
        elif dtype=='powerup' and ptype: p=PowerUp(pos=pos,power_type=ptype); self.entities['powerups'].append(p); self.add_widget(p)
    
    def _collect_item(self, item, ctype):
        if ctype=='coins': self.state['coins']+=1; self.audio.play_sfx('coin')
        elif ctype=='guns' and self.player.bullets_count<5: self.player.bullets_count+=1; self.audio.play_sfx('gun')
        elif ctype=='medicals': self.state['health']=min(self.state['health']+30,self.state['max_health']); self.audio.play_sfx('heal')
        elif ctype=='powerups': self._activate_powerup(item.power_type); self.audio.play_sfx('powerup')
        if item.parent: self.remove_widget(item)
        if item in self.entities[ctype]: self.entities[ctype].remove(item)
    
    def _activate_powerup(self, ptype):
        if ptype=='bomb':
            for e in self.entities['enemies'][:]: self._spawn_explosion(e.pos,20); 
                if e.parent: self.remove_widget(e)
            self.entities['enemies'].clear()
        else: self.powerups_active[ptype]=True; self.powerup_timers[ptype]=10 if ptype!='freeze' else 5
    
    def _update_powerups(self, dt):
        for pt in self.powerups_active:
            if self.powerups_active[pt]:
                self.powerup_timers[pt]-=dt
                if self.powerup_timers[pt]<=0: self.powerups_active[pt]=False
    
    def _spawn_explosion(self, pos, count=10):
        exp=Explosion(pos=pos); self.add_widget(exp)
        for _ in range(count): p=Particle(pos=pos); self.entities['particles'].append(p); self.add_widget(p)
        self.audio.play_sfx('explosion')
    
    def _check_progression(self):
        nl = self.state['score']//100+1
        if nl>self.state['game_level']: self.state['game_level']=nl
            for e in self.entities['enemies']: e.speed+=0.3
        if self.state['game_level'] in BOSS_LEVELS and not self.boss and self.state['game_level'] not in self.completed_boss_levels:
            self.boss = Boss(boss_type=BOSS_LEVELS[self.state['game_level']]); self.boss.active=True; self.add_widget(self.boss)
            self.audio.stop_music(); self.audio.play_background(use_boss=True)
    
    def _update_ui(self):
        self.ui_labels['score'].text=f"Score: {self.state['score']}"; self.ui_labels['coins'].text=f"Coins: {self.state['coins']}"
        self.ui_labels['health'].text=f"Health: {self.state['health']}/{self.state['max_health']}"; self.ui_labels['xp'].text=f"XP: {self.state['xp']}/{self.state['level']*100}"; self.ui_labels['level'].text=f"Level: {self.state['level']}"
    
    def _check_game_over(self):
        if self.state['health']<=0: self.state['health']=0; self.pause(); self.audio.stop_music()
    
    def pause(self):
        if self.clock_event: Clock.unschedule(self.update); self.clock_event=None'''

SPLASH_PY = '''"""splash_screen.py - شاشة البداية"""
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from widgets.fancy_button import FancyButton

class SplashScreen(Widget):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs); self.app = app; self._build_ui()
    def _build_ui(self):
        splash = Image(source="splash.png", size=Window.size, pos=(0,0)); self.add_widget(splash)
        btn = FancyButton(text="▶️ Start Game", size=(250,80), pos=(Window.width*0.35, Window.height*0.1))
        btn.bind(on_release=lambda x: self.app.navigate_to('main_menu')); self.add_widget(btn)
'''

MAIN_MENU_PY = '''"""main_menu.py - القائمة الرئيسية"""
from kivy.uix.widget import Widget
from kivy.core.window import Window
from widgets.fancy_button import FancyButton
from config import WINDOW_WIDTH, WINDOW_HEIGHT, UI_COLORS

class MainMenuScreen(Widget):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs); self.app = app; self._build_ui()
    def _build_ui(self):
        with self.canvas:
            from kivy.graphics import Color, Rectangle
            Color(0.1,0.15,0.2,1); Rectangle(size=Window.size, pos=(0,0))
        for text,on_rel,col,y in [("▶️ Play",lambda:self.app.navigate_to('game'),UI_COLORS['btn_normal'],WINDOW_HEIGHT*0.6),("⚙️ Settings",lambda:None,(0.3,0.7,0.3,1),WINDOW_HEIGHT*0.5),("🛒 Store",lambda:None,(0.9,0.6,0.1,1),WINDOW_HEIGHT*0.4),("🎨 Skins",lambda:None,(0.6,0.3,0.8,1),WINDOW_HEIGHT*0.3),("🏆 Achievements",lambda:None,(0.8,0.5,0.1,1),WINDOW_HEIGHT*0.2),("🚪 Exit",lambda:self.app.stop(),(0.8,0.2,0.2,1),WINDOW_HEIGHT*0.1)]:
            btn = FancyButton(text=text, size=(220,70), pos=(WINDOW_WIDTH*0.35, y), normal_color=col, font_size='26sp')
            btn.bind(on_release=on_rel); self.add_widget(btn)
'''

MAIN_PY = '''"""main.py - نقطة الدخول"""
from kivy.app import App
from config import *
from core.audio_manager import AudioManager
from core.save_manager import SaveManager
from screens.splash_screen import SplashScreen

class SpaceShooterApp(App):
    def build(self):
        self.title = "Space Shooter"
        self.audio = AudioManager(); self.audio.load_music()
        self.saver = SaveManager()
        self.player_data = self.saver.load(default={'owned_skins':['default'],'equipped_skin':'default','achievements':{},'total_coins':0})
        return SplashScreen(self)
    def navigate_to(self, screen_name, **kwargs):        if screen_name=='game':
            from screens.game_screen import GameScreen
            return GameScreen(audio_manager=self.audio, save_manager=self.saver, player_data=self.player_data, **kwargs)
        elif screen_name=='main_menu':
            from screens.main_menu import MainMenuScreen
            return MainMenuScreen(self, **kwargs)
        return SplashScreen(self)
    def on_stop(self): self.saver.save(self.player_data); self.audio.stop_music()

if __name__ == '__main__': SpaceShooterApp().run()
'''

REQUIREMENTS_TXT = 'Kivy>=2.3.0\nKivy-Garden>=0.1.5\n'

# ==================== دوال الإنشاء المُصححة ====================

def create_file(path, content):
    """إنشاء ملف مع المحتوى - معالجة المسارات الفارغة"""
    dir_name = os.path.dirname(path)
    # ✅ الحل: إذا كان dirname فارغاً (ملف في المجلد الحالي)، لا نحاول إنشاء مجلد
    if dir_name and dir_name != '':
        os.makedirs(dir_name, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✓ تم إنشاء: {path}")

def create_init(path):
    create_file(path, '"""Package init"""\n')

def main():
    print("🎮 جاري إنشاء هيكل مشروع Space Shooter...\\n")
    
    # إنشاء المجلدات
    folders = ['assets/images','assets/sounds','assets/fonts','core','widgets','entities','screens','utils']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ مجلد: {folder}")
    
    # ملفات __init__.py
    for pkg in ['core','widgets','entities','screens','utils']:
        create_init(f"{pkg}/__init__.py")
    
    # الملفات الرئيسية (في الجذر - بدون مجلد)
    root_files = {
        'config.py': CONFIG_PY,
        'main.py': MAIN_PY,
        'requirements.txt': REQUIREMENTS_TXT,
    }
    for path, content in root_files.items():
        create_file(path, content)    
    # الملفات في المجلدات الفرعية
    sub_files = {
        'core/audio_manager.py': AUDIO_MANAGER_PY,
        'core/save_manager.py': SAVE_MANAGER_PY,
        'widgets/fancy_button.py': FANCY_BUTTON_PY,
        'widgets/joystick.py': JOYSTICK_PY,
        'entities/base_entity.py': BASE_ENTITY_PY,
        'entities/player.py': PLAYER_PY,
        'entities/enemy.py': ENEMY_PY,
        'entities/bullet.py': BULLET_PY,
        'entities/boss.py': BOSS_PY,
        'entities/powerup.py': POWERUP_PY,
        'entities/effects.py': EFFECTS_PY,
        'widgets/labels.py': LABELS_PY,
        'screens/game_screen.py': GAME_SCREEN_PY,
        'screens/splash_screen.py': SPLASH_PY,
        'screens/main_menu.py': MAIN_MENU_PY,
    }
    for path, content in sub_files.items():
        create_file(path, content)
    
    # ملفات توضيحية للـ assets
    create_file('assets/images/README.txt', "ضع ملفات الصور هنا: player.png, enemy.png, bullet.png, boss.png, etc.")
    create_file('assets/sounds/README.txt', "ضع ملفات الأصوات هنا: shoot.wav, explosion.wav, background_music.mp3, etc.")
    
    print("\\n" + "="*60)
    print("✅ اكتمل إنشاء المشروع بنجاح! 🎉")
    print("="*60)
    print("""
📁 هيكل المشروع الجاهز:
├── 📄 main.py              ← شغّل هذا الملف لبدء اللعبة
├── 📄 config.py            ← كل الثوابت والإعدادات هنا
├── 📄 requirements.txt     ← المكتبات المطلوبة
├── 📁 assets/
│   ├── 📁 images/          ← ضع الصور هنا
│   ├── 📁 sounds/          ← ضع الأصوات هنا
│   └── 📁 fonts/           ← للخطوط المخصصة
├── 📁 core/                ← المديرات الأساسية
├── 📁 widgets/             ← مكونات الواجهة
├── 📁 entities/            ← كيانات اللعبة
└── 📁 screens/             ← شاشات التطبيق

🚀 خطوات التشغيل:
1️⃣  ثبّت المكتبات:  pip install -r requirements.txt
2️⃣  انسخ الصور والأصوات إلى مجلد assets/
3️⃣  شغّل اللعبة:    python main.py

💡 ملاحظة: تأكد أن أسماء الملفات في assets/ تطابق الأسماء في الكود
""")
if __name__ == '__main__':
    main()