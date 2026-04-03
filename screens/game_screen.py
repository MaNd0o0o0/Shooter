"""
game_screen.py - شاشة اللعب الرئيسية (مع نظام تصحيح)
"""

from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from random import randint, choice
import time
import traceback

from core.audio_manager import (
    shoot_sound, explosion_sound, coin_sound, gun_sound,
    heal_sound, powerup_sound, bomb_sound, levelup_sound,
    play_sound, start_background_music, stop_background_music
)
from core.save_manager import load_game_data, save_game_data
from core.event_system import event_bus, GameEvent

from entities.player import Player
from entities.bullet import Bullet, BossBullet
from entities.enemy import Enemy
from entities.boss import Boss
from entities.powerup import PowerUp, Coin, Gun, Medical
from entities.effects import Explosion

from widgets.fancy_button import FancyButton
from widgets.labels import LevelUpLabel

from managers.timer_manager import TimerManager
from managers.enemy_manager import EnemyManager
from managers.pool_manager import PoolManager
from managers.wave_manager import WaveManager

from layers.render_layer import RenderLayer

from config import IMAGES_PATH, FPS


class GameScreen(Widget):
    """شاشة اللعب الرئيسية - مع نظام تصحيح"""
    
    def __init__(self, on_game_over_callback=None, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        
        self.on_game_over_callback = on_game_over_callback
        
        # ==================== متغيرات التصحيح ====================
        self._update_counter = 0
        self._last_print_time = time.time()
        self._error_count = 0
        
        # ==================== متغيرات التحكم ====================
        self.joystick = None
        self.fire_btn_touch = None
        self.fire_button = None
        
        # ==================== إنشاء طبقة الرسم ====================
        self.render_layer = RenderLayer()
        
        # ==================== المتغيرات الأساسية ====================
        self.player = None
        self.bullets = []
        self.boss_bullets = []
        self.enemies = []
        self.coins = []
        self.guns = []
        self.medicals = []
        self.powerups = []
        self.boss = None
        self.boss_type = "normal"
        
        # حالة اللعبة
        self.game_started = False
        self.game_paused = False
        self.music_muted = False
        self.sfx_muted = False
        self.clock_event = None
        
        # إحصائيات اللاعب
        self.score = 0
        self.coins_count = 0
        self.health = 100
        self.max_health = 100
        self.bullets_count = 1
        self.base_bullets = 1
        self.xp = 0
        self.level = 1
        self.total_kills = 0
        self.bosses_defeated = 0
        
        # تأثيرات مؤقتة
        self.shield_active = False
        self.shield_timer = 0
        self.speed_active = False
        self.speed_timer = 0
        self.freeze_active = False
        self.freeze_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.temp_bullet_timer = 0
        self.collision_timer = 0
        
        # إطلاق النار
        self.fire_button_pressed = False
        self.fire_delay = 0
        
        # إعدادات الموجات
        self.wave_manager = None
        self.enemy_manager = None
        self.timer_manager = None
        self.pool_manager = None
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1.5
        self.game_level = 1
        
        # إنجازات ومهام
        self.achievements = {}
        self.missions = {
            "kill_20": {"name": "🗡️ Slayer", "desc": "Kill 20 enemies", "progress": 0, "target": 20, "reward": 30, "completed": False, "icon": "🗡️"},
            "collect_50": {"name": "💰 Collector", "desc": "Collect 50 coins", "progress": 0, "target": 50, "reward": 40, "completed": False, "icon": "💰"},
            "powerup_3": {"name": "✨ Power User", "desc": "Use 3 powerups", "progress": 0, "target": 3, "reward": 50, "completed": False, "icon": "✨"},
        }
        self.owned_skins = ["default"]
        self.equipped_skin = "default"
        self.completed_boss_levels = set()
        
        # مراجع للشاشات
        self.current_screen = None
        self.menu_overlay = None
        self.wave_offset = 0
        
        # عناصر الواجهة
        self.health_bar = None
        self.health_bg = None
        self.health_text = None
        self.xp_bar = None
        self.xp_bg = None
        self.coins_icon = None
        self.coins_label = None
        self.level_label = None
        self.menu_btn = None
        self.health_bar_color = None
        self.xp_bar_color = None
        
        # عناصر البوس
        self.boss_name_label = None
        self.boss_health_percent = None
        
        # عرض الشاشة
        self.width = Window.width
        self.height = Window.height
        
        # ==================== تهيئة المديرين ====================
        self.timer_manager = TimerManager(self)
        self.enemy_manager = EnemyManager(self)
        
        # ==================== تسجيل الأحداث ====================
        self._register_events()
        
        # ==================== تحميل البيانات ====================
        self.load_game_data()
        
        # ==================== عرض شاشة البداية ====================
        Clock.schedule_once(lambda dt: self.show_logo(), 0.1)
        
        print("✅ GameScreen initialized")
    
    def _register_events(self):
        """تسجيل أحداث اللعبة"""
        event_bus.on(GameEvent.HEALTH_CHANGED, self._on_health_changed)
        event_bus.on(GameEvent.SCORE_CHANGED, self._on_score_changed)
        event_bus.on(GameEvent.COINS_CHANGED, self._on_coins_changed)
        event_bus.on(GameEvent.ENEMY_KILLED, self._on_enemy_killed)
        event_bus.on(GameEvent.BOSS_DEFEATED, self._on_boss_defeated)
    
    def _on_health_changed(self, event):
        self.health = event.data['current']
        self.max_health = event.data['max']
    
    def _on_score_changed(self, event):
        self.score = event.data
    
    def _on_coins_changed(self, event):
        self.coins_count = event.data
    
    def _on_enemy_killed(self, event):
        self.total_kills += 1
        if event.data.get('combo', 0) >= 5:
            self._show_floating_text(f"{event.data['combo']}x COMBO!", event.data['position'], (1, 0.5, 0, 1))
    
    def _on_boss_defeated(self, event):
        self.bosses_defeated += 1
        self.completed_boss_levels.add(self.game_level)
        self.save_game_data()
    
    # ==================== دوال الصوت والحفظ ====================
    
    def play_sound(self, sound):
        play_sound(sound, self.sfx_muted)
    
    def load_game_data(self):
        data = load_game_data()
        self.owned_skins = data.get('owned_skins', ['default'])
        self.equipped_skin = data.get('equipped_skin', 'default')
        self.achievements = data.get('achievements', self.achievements)
        self.total_kills = data.get('total_kills', 0)
        self.bosses_defeated = data.get('bosses_defeated', 0)
        self.completed_boss_levels = set(data.get('completed_boss_levels', []))
    
    def save_game_data(self):
        data = {
            'owned_skins': self.owned_skins,
            'equipped_skin': self.equipped_skin,
            'achievements': self.achievements,
            'total_kills': self.total_kills,
            'bosses_defeated': self.bosses_defeated,
            'completed_boss_levels': list(self.completed_boss_levels)
        }
        save_game_data(data)
    
    # ==================== شاشات اللعبة ====================
    
    def show_logo(self):
        from screens.logo_screen import LogoScreen
        self._clear_all_screens()
        self.clear_widgets()
        self.logo_screen = LogoScreen(on_complete_callback=self.show_splash)
        self.add_widget(self.logo_screen)
        self.current_screen = self.logo_screen
    
    def show_splash(self):
        self._stop_game_loop()
        self._clear_all_screens()
        self.clear_widgets()
        
        from kivy.uix.image import Image
        splash = Image(
            source=f"{IMAGES_PATH}/splash.png",
            size=Window.size,
            pos=(0, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(splash)
        
        start_btn = FancyButton(
            text="▶️ Start Game",
            size_hint=(None, None),
            size=(300, 90),
            pos=(Window.width/2 - 150, Window.height * 0.12),
            background_color=(0.2, 0.6, 0.9, 1),
            font_size=32
        )
        start_btn.bind(on_release=lambda x: self.start_game())
        self.add_widget(start_btn)
    
    def show_main_menu(self, instance=None):
        from screens.main_menu import MainMenu
        self._clear_all_screens()
        if self.game_started and not self.game_paused:
            self._pause_game()
        
        self.main_menu = MainMenu(
            game_started=self.game_started,
            callbacks={
                'resume': self.resume_game,
                'play': self.start_game,
                'settings': self.show_settings,
                'store': self.show_store,
                'skins': self.show_skins,
                'achievements': self.show_achievements_menu,
                'missions': self.show_missions_menu,
                'exit': self.exit_game
            }
        )
        self.add_widget(self.main_menu)
        self.current_screen = self.main_menu
    
    def show_settings(self, instance=None):
        from screens.settings_screen import SettingsScreen
        self._pause_game()
        self.settings_screen = SettingsScreen(
            game_instance=self,
            on_back_callback=self.resume_game
        )
        self.add_widget(self.settings_screen)
    
    def show_store(self, instance=None):
        from screens.store_screen import StoreScreen
        self._pause_game()
        self.store_screen = StoreScreen(
            game_instance=self,
            on_back_callback=self.resume_game
        )
        self.add_widget(self.store_screen)
    
    def show_skins(self, instance=None):
        self._pause_game()
        from kivy.uix.label import Label
        screen = Widget(size=Window.size, pos=(0, 0))
        with screen.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size)
        
        title = Label(text="🎨 SKINS", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width/2 - 100, Window.height - 120), size=(200, 60))
        screen.add_widget(title)
        
        y = Window.height - 200
        skins = ['default', 'blue', 'red', 'gold', 'green']
        for skin in skins:
            status = "✅" if skin == self.equipped_skin else ("🔒" if skin not in self.owned_skins else "🟢")
            lbl = Label(text=f"{status} {skin.upper()}", font_size=28, color=(0.9, 0.9, 0.9, 1),
                        pos=(Window.width/2 - 100, y), size=(200, 50), halign='center')
            screen.add_widget(lbl)
            
            if skin != self.equipped_skin and skin in self.owned_skins:
                btn = FancyButton(text="EQUIP", size=(150, 50), pos=(Window.width/2 + 50, y),
                                  background_color=(0.2, 0.6, 0.9, 1), font_size=20)
                btn.bind(on_release=lambda x, s=skin: self.equip_skin(s) or self.remove_widget(screen))
                screen.add_widget(btn)
            y -= 70
        
        back_btn = FancyButton(text="BACK", size=(200, 50), pos=(Window.width/2 - 100, 50),
                               background_color=(0.8, 0.2, 0.2, 1), font_size=24)
        back_btn.bind(on_release=lambda x: self.resume_game() or self.remove_widget(screen))
        screen.add_widget(back_btn)
        self.add_widget(screen)
    
    def show_achievements_menu(self, instance=None):
        self._pause_game()
        from kivy.uix.label import Label
        screen = Widget(size=Window.size, pos=(0, 0))
        with screen.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size)
        
        title = Label(text="🏆 ACHIEVEMENTS", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width/2 - 150, Window.height - 120), size=(300, 60))
        screen.add_widget(title)
        
        y = Window.height - 200
        for ach in self.achievements.values():
            status = "✅" if ach.get("unlocked", False) else "⬜"
            lbl = Label(text=f"{status} {ach.get('icon', '🏆')} {ach.get('name', '')}\n{ach.get('desc', '')} ({ach.get('progress', 0)}/{ach.get('target', 0)})",
                        font_size=20, color=(0.8, 0.8, 0.8, 1), pos=(50, y), size=(Window.width-100, 60))
            screen.add_widget(lbl)
            y -= 70
        
        back_btn = FancyButton(text="BACK", size=(200, 50), pos=(Window.width/2 - 100, 50),
                               background_color=(0.5, 0.5, 0.5, 1), font_size=24)
        back_btn.bind(on_release=lambda x: self.resume_game() or self.remove_widget(screen))
        screen.add_widget(back_btn)
        self.add_widget(screen)
    
    def show_missions_menu(self, instance=None):
        self._pause_game()
        from kivy.uix.label import Label
        screen = Widget(size=Window.size, pos=(0, 0))
        with screen.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size)
        
        title = Label(text="📋 MISSIONS", font_size=48, bold=True, color=(0.5, 0.8, 0.2, 1),
                      pos=(Window.width/2 - 150, Window.height - 120), size=(300, 60))
        screen.add_widget(title)
        
        y = Window.height - 200
        for m in self.missions.values():
            status = "✅" if m["completed"] else "🟡"
            lbl = Label(text=f"{status} {m['icon']} {m['name']}\n{m['desc']} ({m['progress']}/{m['target']}) +{m['reward']}💰",
                        font_size=20, color=(0.9, 0.9, 0.9, 1), pos=(50, y), size=(Window.width-100, 60))
            screen.add_widget(lbl)
            y -= 70
        
        back_btn = FancyButton(text="BACK", size=(200, 50), pos=(Window.width/2 - 100, 50),
                               background_color=(0.5, 0.5, 0.5, 1), font_size=24)
        back_btn.bind(on_release=lambda x: self.resume_game() or self.remove_widget(screen))
        screen.add_widget(back_btn)
        self.add_widget(screen)
    
    def toggle_music(self, instance=None):
        self.music_muted = not self.music_muted
        if self.music_muted:
            stop_background_music()
        else:
            start_background_music(False, self.boss is not None)
    
    def toggle_sfx(self, instance=None):
        self.sfx_muted = not self.sfx_muted
    
    def buy_skin(self, skin_id, price):
        if self.coins_count >= price:
            self.coins_count -= price
            self.owned_skins.append(skin_id)
            self.save_game_data()
            return True
        return False
    
    def equip_skin(self, skin_id):
        self.equipped_skin = skin_id
        self.save_game_data()
        if self.player:
            self.player.update_skin(skin_id)
    
    def exit_game(self, instance=None):
        from kivy.app import App
        App.get_running_app().stop()
    
    # ==================== تحميل صور البوس مسبقاً ====================
    
    def preload_boss_images(self):
        """تحميل صور البوس مسبقاً قبل بدء اللعبة"""
        from entities.boss import Boss
        Boss.preload_all()
        print("✅ Boss images preloaded successfully")
    
    # ==================== بدء اللعبة ====================
    
    def start_game(self, instance=None):
        print("🎮 Starting game...")
        self._clear_all_screens()
        self._stop_game_loop()
        
        # تحميل صور البوس مسبقاً
        self.preload_boss_images()
        
        # إعادة تعيين الحالة
        self.game_started = True
        self.game_paused = False
        
        self.score = 0
        self.coins_count = 0
        self.health = 100
        self.max_health = 100
        self.bullets_count = 1
        self.base_bullets = 1
        self.xp = 0
        self.level = 1
        self.total_kills = 0
        self.bosses_defeated = 0
        self.game_level = 1
        
        self.collision_timer = 0
        
        self.bullets.clear()
        self.boss_bullets.clear()
        self.enemies.clear()
        self.coins.clear()
        self.guns.clear()
        self.medicals.clear()
        self.powerups.clear()
        
        self.shield_active = False
        self.speed_active = False
        self.freeze_active = False
        self.combo = 0
        self.combo_timer = 0
        
        for m in self.missions.values():
            m["progress"] = 0
            m["completed"] = False
        
        # إنشاء PoolManager
        self.pool_manager = PoolManager(self)
        
        # إضافة طبقة الرسم (الخلفيات) - أولاً
        self.add_widget(self.render_layer)
        
        # إنشاء اللاعب
        self.player = Player(skin=self.equipped_skin)
        self.add_widget(self.player)
        
        # إنشاء واجهة المستخدم
        self.create_ui()
        self.create_joystick()
        self.create_fire_button()
        
        # بدء الموسيقى
        start_background_music(self.music_muted, False)
        
        # إنشاء مدير الموجات
        self.wave_manager = WaveManager(self)
        
        # بدء حلقة التحديث
        self.clock_event = Clock.schedule_interval(self.update, 1/FPS)
        print("✅ Update loop scheduled")
    
    def create_ui(self):
        """إنشاء واجهة المستخدم"""
        from kivy.uix.label import Label
        from kivy.uix.image import Image
        from kivy.uix.button import Button
        from kivy.graphics import RoundedRectangle, Color
        
        bar_x = Window.width * 0.02
        bar_y = Window.height * 0.92
        bar_width = Window.width * 0.25
        bar_height = Window.height * 0.03
        
        # شريط الصحة
        with self.canvas.after:
            Color(0.2, 0.2, 0.2, 0.8)
            self.health_bg = RoundedRectangle(pos=(bar_x, bar_y), size=(bar_width, bar_height), radius=[8])
            self.health_bar_color = Color(0.9, 0.2, 0.2, 1)
            self.health_bar = RoundedRectangle(pos=(bar_x+2, bar_y+2), size=(bar_width-4, bar_height-4), radius=[6])
        
        self.health_text = Label(text="100/100", font_size=Window.height * 0.02, pos=(bar_x + 10, bar_y + 5), size=(150, 30))
        self.add_widget(self.health_text)
        
        # شريط الخبرة
        xp_y = bar_y - (Window.height * 0.04)
        with self.canvas.after:
            Color(0.2, 0.2, 0.2, 0.8)
            self.xp_bg = RoundedRectangle(pos=(bar_x, xp_y), size=(bar_width, Window.height * 0.02), radius=[8])
            self.xp_bar_color = Color(0.2, 0.6, 1, 1)
            self.xp_bar = RoundedRectangle(pos=(bar_x+2, xp_y+2), size=(bar_width-4, Window.height * 0.02 - 4), radius=[6])
        
        # العملات
        self.coins_icon = Image(source=f"{IMAGES_PATH}/coin.png", size=(50, 50), pos=(bar_x, xp_y - (Window.height * 0.09)))
        self.add_widget(self.coins_icon)
        
        self.coins_label = Label(text="0", font_size=Window.height * 0.04, bold=True, color=(1, 0.9, 0.2, 1),
                                 pos=(bar_x + 55, self.coins_icon.y + 5), size=(100, 50))
        self.add_widget(self.coins_label)
        
        # المستوى
        self.level_label = Label(text="Lv.1", font_size=Window.height * 0.025, pos=(bar_x + bar_width + 60, xp_y - (Window.height * 0.04)), size=(100, 40))
        self.add_widget(self.level_label)
        
        # زر القائمة
        menu_size = Window.width * 0.06
        self.menu_btn = Button(text="☰", size=(menu_size, menu_size), pos=(Window.width - menu_size - 15, Window.height - menu_size - 15),
                               font_size=menu_size * 0.6, background_color=(0.1, 0.1, 0.1, 0.8))
        self.menu_btn.bind(on_release=lambda x: self.show_main_menu())
        self.add_widget(self.menu_btn)
    
    def create_joystick(self):
        from widgets.joystick import Joystick
        from kivy.graphics import Ellipse, Color
        
        joy_pos = (Window.width * 0.08, Window.height * 0.12)
        self.joystick = Joystick()
        self.joystick.base_size = 280
        self.joystick.knob_size = 120
        self.joystick.pos = joy_pos
        self.joystick.fixed_pos = joy_pos
        
        self.joystick.canvas.clear()
        with self.joystick.canvas:
            Color(1, 1, 1, 0.25)
            self.joystick.base = Ellipse(size=(280, 280), pos=(joy_pos[0] - 140, joy_pos[1] - 140))
            Color(0, 1, 0, 0.8)
            self.joystick.knob = Ellipse(size=(120, 120), pos=(joy_pos[0] - 60, joy_pos[1] - 60))
        
        self.add_widget(self.joystick)
    
    def create_fire_button(self):
        from kivy.uix.image import Image
        from kivy.uix.button import Button
        
        fire_size = Window.width * 0.12
        fire_x = Window.width - fire_size - (Window.width * 0.05)
        fire_y = Window.height * 0.08
        
        self.fire_button = Image(source=f"{IMAGES_PATH}/fire.png", size=(fire_size, fire_size), pos=(fire_x, fire_y))
        self.add_widget(self.fire_button)
        
        self.fire_btn_touch = Button(size=(fire_size, fire_size), pos=(fire_x, fire_y), background_color=(0, 0, 0, 0))
        self.fire_btn_touch.bind(on_press=self.start_firing)
        self.fire_btn_touch.bind(on_release=self.stop_firing)
        self.add_widget(self.fire_btn_touch)
    
    # ==================== دوال اللعب ====================
    
    def start_firing(self, instance):
        self.fire_button_pressed = True
    
    def stop_firing(self, instance):
        self.fire_button_pressed = False
        self.fire_delay = 0
    
    def fire(self):
        if len(self.bullets) > 200:
            return
        
        angles = []
        n = self.bullets_count
        if n == 1:
            angles = [0]
        elif n == 2:
            angles = [-6, 6]
        elif n == 3:
            angles = [-12, 0, 12]
        elif n == 4:
            angles = [-18, -6, 6, 18]
        else:
            angles = [-24, -12, 0, 12, 24]
        
        for angle in angles:
            bullet = Bullet(pos=(self.player.right, self.player.center_y), angle=angle)
            self.bullets.append(bullet)
            self.add_widget(bullet)
        
        self.play_sound(shoot_sound)
    
    def update_bullets(self, dt):
        for b in self.bullets[:]:
            if b.update(dt):
                self.remove_widget(b)
                self.bullets.remove(b)
    
    def update_boss_bullets(self, dt):
        for bb in self.boss_bullets[:]:
            if bb.update(dt):
                self.remove_widget(bb)
                self.boss_bullets.remove(bb)
                continue
            
            if self.player and self.player.collide_widget(bb):
                if not self.shield_active:
                    self.health -= 10
                    self.play_sound(explosion_sound)
                self.remove_widget(bb)
                self.boss_bullets.remove(bb)
                if self.health <= 0:
                    self.game_over()
                break
    
    def update_collectibles(self):
        for c in self.coins[:]:
            c.update()
            if self.player and self.player.collide_widget(c):
                self.coins_count += 1
                self.play_sound(coin_sound)
                self.remove_widget(c)
                self.coins.remove(c)
                
                if not self.missions["collect_50"]["completed"]:
                    self.missions["collect_50"]["progress"] += 1
                    if self.missions["collect_50"]["progress"] >= self.missions["collect_50"]["target"]:
                        self.missions["collect_50"]["completed"] = True
                        self.coins_count += self.missions["collect_50"]["reward"]
                        self._show_mission_complete(self.missions["collect_50"])
        
        for g in self.guns[:]:
            g.update()
            if self.player and self.player.collide_widget(g):
                if self.bullets_count < 5:
                    self.bullets_count += 1
                    self.temp_bullet_timer = 8
                self.play_sound(gun_sound)
                self.remove_widget(g)
                self.guns.remove(g)
        
        for m in self.medicals[:]:
            m.update()
            if self.player and self.player.collide_widget(m):
                self.health = min(self.health + 30, self.max_health)
                self.play_sound(heal_sound)
                self.remove_widget(m)
                self.medicals.remove(m)
        
        for p in self.powerups[:]:
            p.update()
            if self.player and self.player.collide_widget(p):
                self.activate_powerup(p.power_type)
                self.play_sound(powerup_sound)
                self.remove_widget(p)
                self.powerups.remove(p)
                
                if not self.missions["powerup_3"]["completed"]:
                    self.missions["powerup_3"]["progress"] += 1
                    if self.missions["powerup_3"]["progress"] >= self.missions["powerup_3"]["target"]:
                        self.missions["powerup_3"]["completed"] = True
                        self.coins_count += self.missions["powerup_3"]["reward"]
                        self._show_mission_complete(self.missions["powerup_3"])
    
    def force_kill_all_enemies(self):
        """قتل جميع الأعداء فوراً (للباوربس)"""
        for enemy in self.enemies[:]:
            self.handle_enemy_death(enemy)
        return len(self.enemies)
    
    def activate_powerup(self, power_type):
        if power_type == "speed":
            self.speed_active = True
            self.speed_timer = 10
        elif power_type == "shield":
            self.shield_active = True
            self.shield_timer = 10
        elif power_type == "freeze":
            self.freeze_active = True
            self.freeze_timer = 5
            for enemy in self.enemies:
                enemy.opacity = 0.5
        elif power_type == "bomb":
            self.force_kill_all_enemies()
            self.play_sound(bomb_sound)
        elif power_type == "health":
            self.health = min(self.health + 50, self.max_health)
    
    def _get_spawn_pos(self):
        for _ in range(10):
            x = randint(Window.width, Window.width + 400)
            y = randint(250, Window.height - 150)
            
            safe = True
            for e in self.enemies:
                if ((e.x - x)**2 + (e.y - y)**2) ** 0.5 < 80:
                    safe = False
                    break
            
            if safe:
                return (x, y)
        
        return (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
    
    def handle_enemy_death(self, enemy):
        explosion = Explosion(pos=enemy.pos)
        self.add_widget(explosion)
        self.play_sound(explosion_sound)
        
        self.total_kills += 1
        self.combo += 1
        self.combo_timer = 2.0
        self.score += 10
        self.xp += 15
        
        if not self.missions["kill_20"]["completed"]:
            self.missions["kill_20"]["progress"] += 1
            if self.missions["kill_20"]["progress"] >= self.missions["kill_20"]["target"]:
                self.missions["kill_20"]["completed"] = True
                self.coins_count += self.missions["kill_20"]["reward"]
                self._show_mission_complete(self.missions["kill_20"])
        
        if self.xp >= self.level * 100:
            self.level_up()
        
        rnd = randint(1, 100)
        if rnd <= 35:
            coin = Coin(pos=enemy.pos)
            self.coins.append(coin)
            self.add_widget(coin)
        elif rnd <= 50:
            gun = Gun(pos=enemy.pos)
            self.guns.append(gun)
            self.add_widget(gun)
        elif rnd <= 65:
            medical = Medical(pos=enemy.pos)
            self.medicals.append(medical)
            self.add_widget(medical)
        elif rnd <= 85:
            power_type = choice(["speed", "shield", "bomb", "freeze", "health"])
            powerup = PowerUp(pos=enemy.pos, power_type=power_type)
            self.powerups.append(powerup)
            self.add_widget(powerup)
        
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        self.remove_widget(enemy)
        
        if hasattr(self, 'pool_manager') and hasattr(enemy, 'cpp_id'):
            self.pool_manager.return_enemy(enemy)
        
        event_bus.emit(GameEvent.ENEMY_KILLED, {'position': enemy.pos, 'combo': self.combo})
    
    def handle_enemy_hit(self, enemy):
        if not self.shield_active:
            self.health -= enemy.damage
            if self.health <= 0:
                self.game_over()
    
    def level_up(self):
        self.level += 1
        self.xp = 0
        self.max_health += 20
        self.health = self.max_health
        
        if self.level % 3 == 0 and self.bullets_count < 5:
            self.bullets_count += 1
        
        self._show_level_up(self.level)
        self.play_sound(levelup_sound)
        event_bus.emit(GameEvent.PLAYER_LEVEL_UP, self.level)
    
    def _show_level_up(self, new_level):
        level_label = LevelUpLabel(new_level)
        self.add_widget(level_label)
    
    def _show_mission_complete(self, mission):
        from kivy.uix.label import Label
        from kivy.animation import Animation
        
        popup = Label(
            text=f"✅ MISSION COMPLETE!\n{mission['icon']} {mission['name']}\n+{mission['reward']}💰",
            font_size=28, bold=True, color=(0.8, 1, 0.2, 1),
            pos=(Window.width/2 - 250, Window.height/2), size=(500, 120), halign='center'
        )
        self.add_widget(popup)
        anim = Animation(opacity=0, duration=3)
        anim.bind(on_complete=lambda *args: self.remove_widget(popup))
        anim.start(popup)
        self.play_sound(coin_sound)
    
    def _show_floating_text(self, text, pos, color):
        from kivy.uix.label import Label
        from kivy.animation import Animation
        
        label = Label(text=text, font_size=24, bold=True, color=color, pos=pos, size=(200, 40), halign='center')
        self.add_widget(label)
        anim = Animation(y=pos[1] + 50, opacity=0, duration=1)
        anim.bind(on_complete=lambda *args: self.remove_widget(label))
        anim.start(label)
    
    def update_ui(self):
        # تحديث شريط الصحة
        health_percent = self.health / self.max_health
        target_width = (Window.width * 0.25 - 4) * health_percent
        current_width = self.health_bar.size[0]
        new_width = current_width + (target_width - current_width) * 0.2
        self.health_bar.size = (new_width, self.health_bar.size[1])
        
        # تغيير لون شريط الصحة
        r = 1 - health_percent
        g = health_percent
        self.health_bar_color.rgba = (r, g, 0.2, 1)
        
        self.health_text.text = f"{int(self.health)}/{self.max_health}"
        
        # شريط الخبرة
        xp_needed = self.level * 100
        xp_percent = self.xp / xp_needed if xp_needed > 0 else 0
        target_xp_width = (Window.width * 0.25 - 4) * xp_percent
        current_xp_width = self.xp_bar.size[0]
        new_xp_width = current_xp_width + (target_xp_width - current_xp_width) * 0.2
        self.xp_bar.size = (new_xp_width, self.xp_bar.size[1])
        
        self.coins_label.text = str(self.coins_count)
        self.level_label.text = f"Lv.{self.level}"
    
    def draw_boss_health_bar(self):
        if not self.boss or not self.boss.active:
            self.remove_boss_health_bar()
            return
        
        from kivy.uix.label import Label
        from kivy.graphics import RoundedRectangle, Color
        
        health_percent = self.boss.health / self.boss.max_health
        bar_width = 600
        bar_height = 35
        center_x = Window.width // 2
        
        self.remove_boss_health_bar()
        
        with self.canvas.after:
            Color(0.1, 0.1, 0.1, 0.95)
            RoundedRectangle(pos=(center_x - bar_width//2, Window.height - 80), size=(bar_width, bar_height + 20), radius=[10])
            Color(0.9, 0.7, 0.2, 0.8)
            RoundedRectangle(pos=(center_x - bar_width//2 - 2, Window.height - 82), size=(bar_width + 4, bar_height + 24), radius=[12])
            Color(0.2, 0.2, 0.2, 0.9)
            RoundedRectangle(pos=(center_x - bar_width//2, Window.height - 75), size=(bar_width, bar_height), radius=[6])
            
            if health_percent > 0.5:
                color = (1 - (health_percent - 0.5) * 2, 1, 0.2, 1)
            elif health_percent > 0.25:
                color = (1, 0.5 + (health_percent - 0.25) * 2, 0.2, 1)
            else:
                color = (1, 0.2 + health_percent * 1.2, 0.2, 1)
            
            Color(*color)
            RoundedRectangle(pos=(center_x - bar_width//2 + 3, Window.height - 72), size=(max(0, (bar_width - 6) * health_percent), bar_height - 6), radius=[4])
        
        boss_names = {"normal": "IRON GENERAL", "fire": "FIRE LORD", "ice": "ICE WARDEN", "electric": "THUNDER KING", "final": "SHADOW EMPEROR"}
        boss_name = boss_names.get(self.boss_type, "BOSS")
        
        self.boss_name_label = Label(text=f"⚠️ {boss_name} ⚠️", font_size=28, bold=True, color=(1, 0.8, 0.2, 1),
                                     pos=(center_x - 150, Window.height - 55), size=(300, 40), halign='center')
        self.add_widget(self.boss_name_label)
        
        self.boss_health_percent = Label(text=f"{int(health_percent * 100)}%", font_size=20, bold=True, color=(1, 1, 1, 1),
                                         pos=(center_x + bar_width//2 - 60, Window.height - 72), size=(60, 30), halign='center')
        self.add_widget(self.boss_health_percent)
    
    def remove_boss_health_bar(self):
        if hasattr(self, 'boss_name_label') and self.boss_name_label:
            self.remove_widget(self.boss_name_label)
            self.boss_name_label = None
        if hasattr(self, 'boss_health_percent') and self.boss_health_percent:
            self.remove_widget(self.boss_health_percent)
            self.boss_health_percent = None
    
    def boss_defeated(self):
        self.bosses_defeated += 1
        self.completed_boss_levels.add(self.game_level)
        self.score += 30
        self.xp += 50
        self.coins_count += 50
        self.remove_boss_health_bar()
        self.remove_widget(self.boss)
        self.boss = None
        stop_background_music()
        start_background_music(self.music_muted, False)
        self.save_game_data()
        self.play_sound(explosion_sound)
        event_bus.emit(GameEvent.BOSS_DEFEATED, {'type': self.boss_type})
    
    def game_over(self):
        self._stop_game_loop()
        stop_background_music()
        self.save_game_data()
        self._show_game_over_screen()
    
    def _show_game_over_screen(self):
        self.clear_widgets()
        
        with self.canvas.before:
            Color(0, 0, 0, 0.9)
            Rectangle(size=Window.size, pos=(0, 0))
        
        from kivy.uix.label import Label
        game_over_label = Label(text="💀 GAME OVER", font_size=60, color=(1, 0, 0, 1),
                                pos=(Window.width*0.25, Window.height*0.6), size=(400, 80), halign='center')
        self.add_widget(game_over_label)
        
        score_label = Label(text=f"Final Score: {self.score}", font_size=32,
                            pos=(Window.width*0.35, Window.height*0.45), size=(300, 50), halign='center')
        self.add_widget(score_label)
        
        restart_btn = FancyButton(text="🔄 Play Again", size=(250, 70), pos=(Window.width*0.35, Window.height*0.3),
                                  background_color=(0.2, 0.6, 0.9, 1), font_size=26)
        restart_btn.bind(on_release=lambda x: self.start_game())
        self.add_widget(restart_btn)
        
        menu_btn = FancyButton(text="🏠 Main Menu", size=(250, 70), pos=(Window.width*0.35, Window.height*0.15),
                               background_color=(0.8, 0.2, 0.2, 1), font_size=26)
        menu_btn.bind(on_release=lambda x: self.show_main_menu())
        self.add_widget(menu_btn)
    
    def resume_game(self, instance=None):
        self._clear_all_screens()
        if self.game_started:
            self._resume_game()
    
    def _pause_game(self):
        if self.clock_event:
            Clock.unschedule(self.update)
            self.clock_event = None
            self.game_paused = True
            stop_background_music()
    
    def _resume_game(self):
        if self.game_started and not self.clock_event:
            self.clock_event = Clock.schedule_interval(self.update, 1/60)
            self.game_paused = False
            start_background_music(self.music_muted, self.boss is not None)
    
    def _stop_game_loop(self):
        if self.clock_event:
            Clock.unschedule(self.update)
            self.clock_event = None
        self.game_started = False
    
    def _clear_all_screens(self):
        for widget in self.children[:]:
            if widget not in [self.player, self.render_layer]:
                self.remove_widget(widget)
        self.current_screen = None
    
    # ==================== حلقة التحديث الرئيسية (مع تصحيح) ====================
    
    def update(self, dt):
        """حلقة التحديث الرئيسية - مع نظام تصحيح كامل"""
        
        # ✅ اختبار 1: هل الـ update شغال؟
        self._update_counter += 1
        
        # طباعة كل ثانية
        current_time = time.time()
        if current_time - self._last_print_time >= 1.0:
            print(f"🟢 UPDATE RUNNING - Frame: {self._update_counter}, "
                  f"Enemies: {len(self.enemies)}, Bullets: {len(self.bullets)}, "
                  f"Boss: {self.boss is not None}, Health: {self.health}")
            self._last_print_time = current_time
            self._update_counter = 0
        
        # ✅ اختبار 2: هل اللعبة في حالة صحيحة؟
        if not self.game_started:
            return
        
        if self.game_paused:
            return
        
        # ✅ اختبار 3: هل dt معقول؟
        if dt > 0.1:
            print(f"⚠️ Large dt: {dt}, clamping to 0.033")
            dt = 0.033
        
        # ✅ اختبار 4: هل المديرين موجودين؟
        if not hasattr(self, 'enemy_manager') or self.enemy_manager is None:
            print("❌ Enemy manager is None!")
            return
        
        try:
            # تحديث حركة اللاعب
            if self.joystick and self.player:
                speed = 8 * (1.5 if self.speed_active else 1.0)
                new_x = self.player.x + self.joystick.dx * speed
                new_y = self.player.y + self.joystick.dy * speed
                self.player.x = max(20, min(new_x, Window.width - self.player.width - 20))
                self.player.y = max(160, min(new_y, Window.height - self.player.height - 20))
            
            # تحديث الرصاصات
            self.update_bullets(dt)
            self.update_boss_bullets(dt)
            
            # تحديث العناصر
            self.update_collectibles()
            
            # تحديث المديرين
            if self.timer_manager:
                self.timer_manager.update(dt)
            if self.enemy_manager:
                self.enemy_manager.update(dt)
            if self.wave_manager:
                self.wave_manager.update(dt)
            
            # تحديث البوس
            if self.boss and self.boss.active:
                try:
                    player_pos = (self.player.x, self.player.y) if self.player else (0, 0)
                    self.boss.update(dt, player_pos, self)
                    
                    for b in self.bullets[:]:
                        if b.collide_widget(self.boss) and not getattr(b, 'hit', False):
                            b.hit = True
                            self.boss.health -= 1
                            if hasattr(self.boss, 'hit_animation'):
                                self.boss.hit_animation()
                            if b in self.bullets:
                                self.bullets.remove(b)
                                self.remove_widget(b)
                            if self.boss.health <= 0:
                                self.boss.active = False
                                self.boss_defeated()
                            break
                except Exception as e:
                    print(f"❌ Boss update error: {e}")
                    traceback.print_exc()
            
            # تحديث التأثيرات المؤقتة
            if self.shield_active:
                self.shield_timer -= dt
                if self.shield_timer <= 0:
                    self.shield_active = False
            
            if self.speed_active:
                self.speed_timer -= dt
                if self.speed_timer <= 0:
                    self.speed_active = False
            
            if self.freeze_active:
                self.freeze_timer -= dt
                if self.freeze_timer <= 0:
                    self.freeze_active = False
                    for enemy in self.enemies:
                        enemy.opacity = 1
            
            if self.combo_timer > 0:
                self.combo_timer -= dt
            else:
                self.combo = 0
            
            if self.temp_bullet_timer > 0:
                self.temp_bullet_timer -= dt
                if self.temp_bullet_timer <= 0 and self.bullets_count > self.base_bullets:
                    self.bullets_count = self.base_bullets
            
            if self.collision_timer > 0:
                self.collision_timer -= dt
            
            # إطلاق النار
            if self.fire_button_pressed:
                self.fire_delay += dt
                fire_rate = 0.1 if self.speed_active else 0.18
                if self.fire_delay > fire_rate:
                    self.fire()
                    self.fire_delay = 0
            
            # تحديث الخلفية
            if hasattr(self, 'render_layer') and self.render_layer:
                self.render_layer.update_background(dt)
                
            if hasattr(self, 'render_layer') and self.render_layer:
                self.render_layer.draw_shield(self.shield_active, 0.5)
            
            # تحديث واجهة المستخدم
            self.update_ui()
            self.draw_boss_health_bar()
            
            
            
            # التحقق من نهاية اللعبة
            if self.health <= 0:
                self.game_over()
                
        except Exception as e:
            self._error_count += 1
            print(f"❌❌❌ CRITICAL ERROR in update (#{self._error_count}): {e}")
            traceback.print_exc()
            
            # منع التكرار اللانهائي للأخطاء
            if self._error_count > 10:
                print("💀 Too many errors, forcing game over")
                self.game_over()
    
    # ==================== دوال اللمس ====================
    
    def on_touch_down(self, touch):
        if self.game_started and hasattr(self, 'joystick') and self.joystick:
            if self.joystick.collide_point(*touch.pos):
                self.joystick.on_touch_down(touch)
                return True
        
        if self.game_started and hasattr(self, 'fire_btn_touch') and self.fire_btn_touch:
            if self.fire_btn_touch.collide_point(*touch.pos):
                self.fire_btn_touch.on_touch_down(touch)
                return True
        
        return super(GameScreen, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.game_started and hasattr(self, 'joystick') and self.joystick:
            if hasattr(self.joystick, 'active') and self.joystick.active:
                self.joystick.on_touch_move(touch)
                return True
        return super(GameScreen, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.game_started and hasattr(self, 'joystick') and self.joystick:
            if hasattr(self.joystick, 'active') and self.joystick.active:
                self.joystick.on_touch_up(touch)
                return True
        
        if self.game_started and hasattr(self, 'fire_btn_touch') and self.fire_btn_touch:
            self.fire_btn_touch.on_touch_up(touch)
            return True
        
        return super(GameScreen, self).on_touch_up(touch)