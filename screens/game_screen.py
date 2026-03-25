from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle, Line
from kivy.animation import Animation
from random import randint, choice
import time

# ==================== كلاس Bird (خلفية متحركة - ليس عدوًا) ====================
class Bird(Image):
    """🐦 طائر خلفية متحركة - لا يتفاعل مع اللعبة"""
    def __init__(self, **kwargs):
        from config import IMAGES_PATH
        super(Bird, self).__init__(source=f"{IMAGES_PATH}/bird.png", size=(80, 80), **kwargs)
        self.pos = (randint(Window.width, Window.width + 800), 
                    randint(Window.height - 300, Window.height - 150))
        self.speed = randint(2, 5)
    
    def update(self, dt=0.016):
        """تحريك الطائر في الخلفية فقط"""
        self.pos = (self.x - self.speed, self.y)
        if self.right < 0:
            self.pos = (Window.width + randint(0, 200), 
                        randint(Window.height - 300, Window.height - 150))

# ==================== استيرادات Core ====================
from core.audio_manager import (
    shoot_sound, explosion_sound, coin_sound, gun_sound,
    heal_sound, powerup_sound, bomb_sound, levelup_sound,
    background_music, boss_music, play_sound,
    start_background_music, stop_background_music
)
from core.save_manager import load_game_data, save_game_data

# ==================== استيرادات Entities ====================
from entities.player import Player
from entities.bullet import Bullet, BossBullet
from entities.enemy import Enemy, enemy_map
from entities.boss import Boss
from entities.powerup import PowerUp, Coin, Gun, Medical
from entities.effects import Explosion, Particle

# ==================== استيرادات Widgets ====================
from widgets.fancy_button import FancyButton
from widgets.joystick import Joystick
from widgets.labels import LevelUpLabel, AchievementPopup
# ==================== استيرادات manegers ==================
from managers.timer_manager import TimerManager
from managers.enemy_manager import EnemyManager
# ==================== استيرادات Config ====================
from config import (
    IMAGES_PATH, BOSS_LEVELS, MAX_BULLETS_COUNT, 
    MAX_BOSS_BULLETS, MAX_PARTICLES, MAX_ENEMIES,
    MAX_ENEMIES_ON_SCREEN, FPS
)

# ==================== كلاس GameScreen ====================
class GameScreen(Widget):
    def __init__(self, on_game_over_callback=None, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.on_game_over_callback = on_game_over_callback
        
        self.current_screen = None
        self.settings_screen = None
        self.store_screen = None
        self.skins_screen = None
        self.achievements_screen = None
        self.logo_screen = None
        self.wave_offset = 0
        
        self.initialize_game_state()
        self.load_game_data()
        self.timer_manager = TimerManager(self)
        self.enemy_manager = EnemyManager(self)
        
        Clock.schedule_once(lambda dt: self.show_logo(), 0.1)
        
        with self.canvas.after:
            self.shield_color = Color(0, 0.6, 1, 0)  # أزرق شفاف
            self.shield_circle = Ellipse(pos=(0, 0), size=(0, 0))
            
        # خلفية
        with self.canvas.after:
            Color(0, 0, 0, 0.3)
            self.coin_bg = Rectangle(
                pos=(10, Window.height - 170),
                size=(150, 70)
            )
        
            # صورة الكوين
            self.coin_icon = Image(
                source=f"{IMAGES_PATH}/coin.png",
                size_hint=(None, None),
                size=(70, 70),
                pos=(10, Window.height - 170)
            )
            self.add_widget(self.coin_icon)
            
            # رقم الكوين
            self.coin_label = Label(
                text="0",
                font_size=40,
                bold=True,
                color=(1, 0.9, 0.2, 1),
                pos=(80, Window.height - 175),
                size_hint=(None, None)
            )
            self.add_widget(self.coin_label)
                  
    def initialize_game_state(self):
        """تهيئة حالة اللعبة"""
        self.music_muted = False
        self.sfx_muted = False
        self.music_playing = False
        self.coins_count = 0
        self.health = 100
        self.max_health = 100
        self.bullets_count = 1  # ✅ بدون مسافات
        self.score = 0
        self.xp = 0
        self.level = 1
        self.total_kills = 0
        self.bosses_defeated = 0
        self.bullets = []
        self.boss_bullets = []
        self.enemies = []  # ✅ بدون مسافات
        self.coins = []
        self.guns = []
        self.medicals = []
        self.powerups = []
        self.birds = []
        self.particles = []
        self.clock_event = None
        self.game_paused = False
        self.game_started = False
        self.boss = None
        self.boss_type = "normal"
        self.game_level = 1
        self.menu_overlay = None
        self.game_state_backup = None
        self.shield_active = False
        self.shield_timer = 0
        self.speed_active = False
        self.speed_timer = 0
        self.freeze_active = False
        self.freeze_timer = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1.5
        self.powerup_labels = {}
        self.player_skin = "default"
        self.owned_skins = ["default"]
        self.equipped_skin = "default"
        self.boss_levels = BOSS_LEVELS
        self.completed_boss_levels = set()
        self._boss_canvas_instructions = []
        self._shield_canvas_instructions = []
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.achievements = {
            "first_blood": {"name": "First Blood", "desc": "Kill 10 enemies", "progress": 0, "target": 10, "reward": 5, "unlocked": False, "icon": "🩸"},
            "boss_slayer": {"name": "Boss Slayer", "desc": "Defeat a boss", "progress": 0, "target": 1, "reward": 50, "unlocked": False, "icon": "🐉"},
            "coin_collector": {"name": "Coin Collector", "desc": "Collect 100 coins", "progress": 0, "target": 100, "reward": 25, "unlocked": False, "icon": "💰"},
            "speed_demon": {"name": "Speed Demon", "desc": "Use speed boost 5 times", "progress": 0, "target": 5, "reward": 30, "unlocked": False, "icon": "⚡"},
            "level_15": {"name": "Level 15 Hero", "desc": "Reach level 15", "progress": 0, "target": 15, "reward": 100, "unlocked": False, "icon": "🌟"},
        }
        self.speed_boost_uses = 0
        
        # ✅ متغيرات زر النار
        self.fire_button_pressed = False
        self.fire_delay = 0
        self.fire_button = None

        # Skills
        self.skill_ready = True
        self.skill_cooldown = 0
        self.skill_max_cooldown = 5

        # Combo
        self.combo = 0
        self.combo_timer = 0

        # Temp bullets boost
        self.temp_bullet_timer = 0
        self.base_bullets = 1

        self.fire_btn_touch = None
    
    def load_game_data(self):
        """تحميل بيانات اللعبة"""
        data = load_game_data()
        self.owned_skins = data.get('owned_skins', ['default'])
        self.equipped_skin = data.get('equipped_skin', 'default')
        self.achievements = data.get('achievements', self.achievements)
        self.total_kills = data.get('total_kills', 0)
        self.bosses_defeated = data.get('bosses_defeated', 0)
        self.speed_boost_uses = data.get('speed_boost_uses', 0)
        completed = data.get('completed_boss_levels', [])
        self.completed_boss_levels = set(completed)
    
    def save_game_data(self):        
        """حفظ بيانات اللعبة"""
        data = {
            'owned_skins': self.owned_skins,
            'equipped_skin': self.equipped_skin,
            'achievements': self.achievements,
            'total_kills': self.total_kills,
            'bosses_defeated': self.bosses_defeated,
            'speed_boost_uses': self.speed_boost_uses,
            'completed_boss_levels': list(self.completed_boss_levels)
        }
        save_game_data(data)
    
    def play_sound(self, sound):
        """تشغيل صوت"""
        play_sound(sound, self.sfx_muted)
    
    def _clear_all_screens(self):
        """مسح جميع الشاشات الزائدة"""
        self.current_screen = None
        
        for screen_name in ['settings_screen', 'store_screen', 'skins_screen', 'achievements_screen']:
            if hasattr(self, screen_name) and getattr(self, screen_name):
                screen = getattr(self, screen_name)
                if screen and screen.parent:
                    self.remove_widget(screen)
                setattr(self, screen_name, None)
        
        if self.menu_overlay and self.menu_overlay.parent:
            self.remove_widget(self.menu_overlay)
            self.menu_overlay = None
    
    def show_logo(self):
        """عرض شاشة الشعار"""
        from screens.logo_screen import LogoScreen
        
        self._clear_all_screens()
        self.clear_widgets()
        
        self.logo_screen = LogoScreen(on_complete_callback=self.show_splash)
        self.add_widget(self.logo_screen)
        self.current_screen = self.logo_screen
    
    def show_splash(self):
        """عرض شاشة البداية"""
        self._stop_game_loop()
        self._clear_all_screens()
        self.clear_widgets()
        
        self.current_screen = Image(source=f"{IMAGES_PATH}/splash.png", size=Window.size, pos=(0, 0))
        self.add_widget(self.current_screen)        
        start_btn = FancyButton(
            text="▶️ Start Game",
            size_hint=(None, None),
            size=(250, 80),
            pos=(Window.width * 0.35, Window.height * 0.1),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size=28
        )
        start_btn.bind(on_release=lambda x: self.start_game())
        self.add_widget(start_btn)
    
    def show_mainmenu(self):
        """عرض القائمة الرئيسية"""
        self._clear_all_screens()
        
        if self.game_started and not self.game_paused:
            self._pause_game()
        
        self.menu_overlay = Widget(size=Window.size, pos=(0, 0))
        with self.menu_overlay.canvas:
            Color(0, 0, 0, 0.7)
            self.menu_bg = Rectangle(size=Window.size, pos=(0, 0))
        self.add_widget(self.menu_overlay)
        
        if self.game_started:
            play_btn = FancyButton(
                text="▶️ Resume",
                size_hint=(None, None),
                size=(220, 70),
                pos=(Window.width * 0.35, Window.height * 0.6),
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                font_size=26
            )
            play_btn.bind(on_release=lambda x: self.resume_game_from_menu())
            self.menu_overlay.add_widget(play_btn)
        else:
            play_btn = FancyButton(
                text="▶️ Play",
                size_hint=(None, None),
                size=(220, 70),
                pos=(Window.width * 0.35, Window.height * 0.6),
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                font_size=26
            )
            play_btn.bind(on_release=lambda x: self.start_game())
            self.menu_overlay.add_widget(play_btn)        
        settings_btn = FancyButton(
            text="⚙️ Settings",
            size_hint=(None, None),
            size=(220, 70),
            pos=(Window.width * 0.35, Window.height * 0.5),
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=26
        )
        settings_btn.bind(on_release=lambda x: self.show_settings())
        self.menu_overlay.add_widget(settings_btn)
        
        store_btn = FancyButton(
            text="🛒 Store",
            size_hint=(None, None),
            size=(220, 70),
            pos=(Window.width * 0.35, Window.height * 0.4),
            background_color=(0.9, 0.6, 0.1, 1),
            color=(1, 1, 1, 1),
            font_size=26
        )
        store_btn.bind(on_release=lambda x: self.show_store())
        self.menu_overlay.add_widget(store_btn)
        
        skins_btn = FancyButton(
            text="🎨 Skins",
            size_hint=(None, None),
            size=(220, 70),
            pos=(Window.width * 0.35, Window.height * 0.3),
            background_color=(0.6, 0.3, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=26
        )
        skins_btn.bind(on_release=lambda x: self.show_skins())
        self.menu_overlay.add_widget(skins_btn)
        
        achievements_btn = FancyButton(
            text="🏆 Achievements",
            size_hint=(None, None),
            size=(220, 70),
            pos=(Window.width * 0.35, Window.height * 0.2),
            background_color=(0.8, 0.5, 0.1, 1),
            color=(1, 1, 1, 1),
            font_size=26
        )
        achievements_btn.bind(on_release=lambda x: self.show_achievements_menu())
        self.menu_overlay.add_widget(achievements_btn)
        
        exit_btn = FancyButton(            
          text="🚪 Exit",
            size_hint=(None, None),
            size=(220, 70),
            pos=(Window.width * 0.35, Window.height * 0.1),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=26
        )
        exit_btn.bind(on_release=lambda x: self.exit_game())
        self.menu_overlay.add_widget(exit_btn)
        
        self.current_screen = self.menu_overlay
    
    def exit_game(self):
        """خروج من اللعبة"""
        from kivy.app import App
        App.get_running_app().stop()
    
    def resume_game_from_menu(self):
        """استئناف اللعبة"""
        self._clear_all_screens()
        if self.game_started:
            self._resume_game()
    
    def start_game(self):
        """بدء اللعبة"""
        self._clear_all_screens()
        self._stop_game_loop()
        self.game_started = True
        self.game_paused = False
        
        self.score = 0
        self.coins_count = 0
        self.health = 100
        self.max_health = 100
        self.bullets_count = 1
        self.xp = 0
        self.level = 1
        self.game_level = 1
        self.total_kills = 0
        self.bullets = []
        self.boss_bullets = []
        self.enemies = []
        self.coins = []
        self.guns = []
        self.medicals = []
        self.powerups = []
        self.birds = []
        self.particles = []
        self.powerup_labels = {}        
        self.boss = None
        self.boss_type = "normal"
        self.game_state_backup = None
        self.shield_active = False
        self.speed_active = False
        self.freeze_active = False
        #self.enemy_spawn_timer = 0
        self.completed_boss_levels = set()
        self._boss_canvas_instructions = []
        self._shield_canvas_instructions = []
        self.fire_button_pressed = False
        self.fire_delay = 0
        
        self.create_background()
        self.create_player()
        self.create_enemies()
        self.create_ui()
        self.create_joystick()
        self.create_fire_button()
        
        start_background_music(self.music_muted, False)
        self.clock_event = Clock.schedule_interval(self.update, 1/FPS)
    
    def create_background(self):
        """إنشاء الخلفية"""
        self.sky = Image(
            source=f"{IMAGES_PATH}/bg.png",  # صورة السماء
            size=Window.size,
            pos=(0, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.sky)
        
        self.sea1 = Image(
            source=f"{IMAGES_PATH}/sea.png",  # حط صورة البحر
            size=(Window.width, 300),
            pos=(0, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        
        self.sea2 = Image(
            source=f"{IMAGES_PATH}/sea.png",
            size=(Window.width, 300),
            pos=(Window.width, 0),
            allow_stretch=True,
            keep_ratio=False
        )
        
        self.add_widget(self.sea1)
        self.add_widget(self.sea2)
        
        self.m1 = Image(source=f"{IMAGES_PATH}/mountains.png", size=(Window.width, 1500), pos=(0, Window.height - 2300))
        self.m2 = Image(source=f"{IMAGES_PATH}/mountains.png", size=(Window.width, 1500), pos=(Window.width, Window.height - 2300))
        self.add_widget(self.m1)
        self.add_widget(self.m2)
        
        self.clouds1 = Image(source=f"{IMAGES_PATH}/clouds.png", size=(Window.width, 600), pos=(0, Window.height - 600))
        self.clouds2 = Image(source=f"{IMAGES_PATH}/clouds.png", size=(Window.width, 600), pos=(Window.width, Window.height - 600))
        self.add_widget(self.clouds1)
        self.add_widget(self.clouds2)
        
        self.city1 = Image(source=f"{IMAGES_PATH}/city.png", size=(Window.width, 1500), pos=(0, - 150))
        self.city2 = Image(source=f"{IMAGES_PATH}/city.png", size=(Window.width, 1500), pos=(Window.width, - 150))
        self.add_widget(self.city1)
        self.add_widget(self.city2)
        
        self.birds = []
        for i in range(6):            
            b = Bird()
            self.birds.append(b)
            self.add_widget(b)
    
    def update_background(self, dt=0.016):
        import math
      
        """تحديث خلفية اللعبة"""
        self.m1.pos = (self.m1.x - 0.4, self.m1.y)
        self.m2.pos = (self.m2.x - 0.4, self.m2.y)
        if self.m1.right <= 0:
            self.m1.pos = (self.m2.right, self.m1.y)
        if self.m2.right <= 0:
            self.m2.pos = (self.m1.right, self.m2.y)
        
        self.clouds1.pos = (self.clouds1.x - 0.8, self.clouds1.y)
        self.clouds2.pos = (self.clouds2.x - 0.8, self.clouds2.y)
        if self.clouds1.right <= 0:
            self.clouds1.pos = (self.clouds2.right, self.clouds1.y)
        if self.clouds2.right <= 0:
            self.clouds2.pos = (self.clouds1.right, self.clouds2.y)
        
        self.city1.pos = (self.city1.x - 1.5, self.city1.y)
        self.city2.pos = (self.city2.x - 1.5, self.city2.y)
        if self.city1.right <= 0:
            self.city1.pos = (self.city2.right, self.city1.y)
        if self.city2.right <= 0:
            self.city2.pos = (self.city1.right, self.city2.y)
        
        for b in self.birds:
            b.update(dt)
            
                # 🌊 تحريك البحر
        sea_speed = 2.5
        
        self.sea1.x -= sea_speed
        self.sea2.x -= sea_speed
        
        if self.sea1.right <= 0:
            self.sea1.x = self.sea2.right
        
        if self.sea2.right <= 0:
            self.sea2.x = self.sea1.right
            
        self.wave_offset += dt * 3

        wave = math.sin(self.wave_offset) * 5
        self.sea1.y = wave
        self.sea2.y = wave
            
    def update_bar(self, bar_data, percent, dynamic_color=False):
        percent = max(0, min(1, percent))
    
        target_width = bar_data["max_width"] * percent
        current_width = bar_data["bar"].size[0]
    
        # Smooth animation
        new_width = current_width + (target_width - current_width) * 0.2
        bar_data["bar"].size = (new_width, bar_data["bar"].size[1])
    
        if dynamic_color:
            r = 1 - percent
            g = percent
            bar_data["color"].rgba = (r, g, 0.2, 1)
            
    def create_bar(self, x, y, width, height, color):
        
        bar_data = {}
    
        with self.canvas.after:
            Color(0.2, 0.2, 0.2, 0.8)
            bg = RoundedRectangle(pos=(x, y), size=(width, height), radius=[8])
    
            bar_color = Color(*color)
            bar = RoundedRectangle(pos=(x+2, y+2), size=(width-4, height-4), radius=[6])
    
        bar_data["bg"] = bg
        bar_data["bar"] = bar
        bar_data["color"] = bar_color
        bar_data["max_width"] = width - 4
    
        return bar_data
    
    def create_player(self):
        """إنشاء اللاعب"""
        self.player = Player(skin=self.equipped_skin)
        self.add_widget(self.player)
    
    def create_enemies(self):
        """إنشاء الأعداء الأوليين"""
        for i in range(2):
            e = Enemy()
            if i > 0 and len(self.enemies) > 0:
                prev_enemy = self.enemies[0]
                e.pos = (randint(Window.width, Window.width + 400),
                         prev_enemy.y + randint(150, 300) if prev_enemy.y < Window.height - 300
                         else prev_enemy.y - randint(150, 300))
            self.enemies.append(e)
            self.add_widget(e)
    
    def create_ui(self):
      
        # ❤️ Health
        self.health_bar = self.create_bar(20, Window.height-50, 300, 22, (0.9,0.2,0.2,1))
    
        # ⭐ XP
        self.xp_bar = self.create_bar(20, Window.height-80, 300, 16, (0.2,0.6,1,1))
    
        # ❤️ Health text
        self.health_text = Label(
            text="100/100",
            pos=(30, Window.height-50),
            size_hint=(None,None),
            font_size=16
        )
        self.add_widget(self.health_text)
    
        # 💰 Coins
        self.coins_label = Label(
            text="💰 0",
            pos=(20, Window.height-110),
            size_hint=(None,None),
            font_size=20
        )
        self.add_widget(self.coins_label)
    
        # 🧠 Level
        self.level_label = Label(
            text="Lv.1",
            pos=(250, Window.height-110),
            size_hint=(None,None),
            font_size=20
        )
        self.add_widget(self.level_label)
    
        # زر القائمة
        self.menu_btn = Button(
            text="☰",
            size_hint=(None,None),
            size=(80,80),
            pos=(Window.width-100, Window.height-100)
        )
        self.menu_btn.bind(on_release=lambda x: self.show_mainmenu())
        self.add_widget(self.menu_btn)
    
    def create_joystick(self):
        """إنشاء عصا التحكم"""
        self.joystick = Joystick()
        self.add_widget(self.joystick)
    
    def create_fire_button(self):
        """✅ إنشاء زر إطلاق النار (fire.png) - Hold to Shoot"""
        # صورة الزر
        self.fire_button = Image(
            source=f"{IMAGES_PATH}/fire.png",
            size=(150, 150),
            pos=(Window.width - 140, 140)
        )
        self.add_widget(self.fire_button)
    
        # ✅ زر شفاف للضغط مع تتبع الحالة
        self.fire_btn_touch = Button(
            size_hint=(None, None),
            size=(150, 150),
            pos=(Window.width - 140, 140),
            background_color=(0, 0, 0, 0)
        )
    
        # ✅ عند الضغط: بدء إطلاق النار
        self.fire_btn_touch.bind(on_press=lambda x: self.start_firing())
        # ✅ عند الرفع: إيقاف إطلاق النار
        self.fire_btn_touch.bind(on_release=lambda x: self.stop_firing())
    
        self.add_widget(self.fire_btn_touch)

    def start_firing(self):
        """بدء إطلاق النار المستمر"""
        self.fire_button_pressed = True
    def stop_firing(self):
        """إيقاف إطلاق النار"""
        self.fire_button_pressed = False
        self.fire_delay = 0
    
    def update(self, dt):
        """حلقة التحديث الرئيسية"""
        if self.game_paused or not self.game_started:
            return
        
        self.update_background(dt)
        self.update_player(dt)
        self.update_bullets(dt)
        self.update_boss_bullets(dt)
        self.update_particles(dt)
        self.timer_manager.update(dt)
        self.enemy_manager.spawn(dt)
        self.enemy_manager.update(dt)
        
        self.coin_label.text = str(self.coins_count)
    
        #self.update_enemies(dt)
        self.update_collectibles()
        self.update_boss(dt)
        self.update_ui()
        self.check_achievements()
        
        # ✅ إطلاق النار من زر النار فقط
        if self.fire_button_pressed:
            self.fire_delay += dt
            fire_rate = 0.1 if self.speed_active else 0.18
            if self.fire_delay > fire_rate:
                self.fire()
                self.fire_delay = 0
        
        if self.boss and self.boss.active:
            self.draw_boss_health_bar()
        
        if self.health <= 0:
            self.health = 0
            self.game_over()
            return
          
        if self.shield_active:
            self.shield_color.a = 0.25  # درجة الشفافية (قلل/زود براحتك)
        
            size = max(self.player.width, self.player.height) * 1.6
        
            self.shield_circle.size = (size, size)
            self.shield_circle.pos = (
                self.player.center_x - size / 2,
                self.player.center_y - size / 2
            )
        else:
            self.shield_color.a = 0
                    
    def update_player(self, dt):
        """تحديث حركة اللاعب"""
        speed_multiplier = 1.5 if self.speed_active else 1
        self.player.pos = (self.player.x + self.joystick.dx * 8 * speed_multiplier,
                           self.player.y + self.joystick.dy * 8 * speed_multiplier)
        
        if self.player.x < 0:
            self.player.pos = (0, self.player.y)
        if self.player.right > Window.width:
            self.player.pos = (Window.width - self.player.width, self.player.y)
        if self.player.y < 160:
            self.player.pos = (self.player.x, 160)
        if self.player.top > Window.height:            self.player.pos = (self.player.x, Window.height - self.player.height)
        
        # ❌ تم إزالة إطلاق النار من الجoystick
    
    
    def use_skill(self):
        if not self.skill_ready:
            return
        for e in self.enemies[:]:
            self.create_particles(e.pos, color=(1,0,0,1), count=20)
            self.remove_widget(e)
            self.enemies.remove(e)
            self.score += 10
        self.skill_ready = False
        self.skill_cooldown = self.skill_max_cooldown
    
    def take_damage(self, amount):
        """تقليل صحة اللاعب مع مراعاة الشيلد"""
        
        if self.shield_active:
            return  # 🛡 مفيش ضرر
    
        self.health -= amount
    
        if self.health < 0:
            self.health = 0

    def fire(self):

        """إطلاق الرصاص"""
        angles = []
        n = self.bullets_count
        if n == 1:
            angles = [0]
        elif n == 2:
            angles = [-5, 5]
        elif n == 3:
            angles = [-10, 0, 10]
        elif n == 4:
            angles = [-15, -5, 5, 15]
        elif n >= 5:
            angles = [-20, -10, 0, 10, 20]
        
        for angle in angles:
            bullet = Bullet(pos=(self.player.right, self.player.center_y), angle=angle)
            self.bullets.append(bullet)
            self.add_widget(bullet)
        self.play_sound(shoot_sound)
    
    def update_bullets(self, dt):
        """تحديث الرصاص"""
        for b in self.bullets[:]:
            b.update(dt)
            if (b.x > Window.width + 100 or b.x < -100 or
                b.y > Window.height + 100 or b.y < -100 or
                b.distance_traveled > b.max_distance):
                if b in self.bullets:
                    self.remove_widget(b)
                    self.bullets.remove(b)
    
    def update_boss_bullets(self, dt):
        """تحديث رصاص الزعيم"""
        for bb in self.boss_bullets[:]:
            bb.update(dt)
            if self.player.collide_widget(bb):
                if not self.shield_active:
                    self.health -= 10
                explosion = Explosion(pos=bb.pos)
                self.add_widget(explosion)
                self.play_sound(explosion_sound)
                if bb in self.boss_bullets:
                    self.remove_widget(bb)
                    self.boss_bullets.remove(bb)
            elif bb.x < -50 or bb.x > Window.width + 50 or bb.distance_traveled > bb.max_distance:                
                if bb in self.boss_bullets:
                    self.remove_widget(bb)
                    self.boss_bullets.remove(bb)
    
    def update_particles(self, dt):
        """تحديث الجسيمات"""
        for p in self.particles[:]:
            if p.update(dt):
                if p in self.particles:
                    self.remove_widget(p)
                    self.particles.remove(p)
    
    def handle_enemy_death(self, enemy):
        """✅ معالجة موت العدو"""
        self.total_kills += 1
        self.combo += 1
        self.combo_timer = 2

        rnd = randint(1, 100)
        
        # ✅ نسب ظهور محسنة
        if rnd <= 35:  # 35% Coin
            coin = Coin(pos=enemy.pos)
            self.coins.append(coin)
            self.add_widget(coin)
        elif rnd <= 50:  # 15% Gun
            gun = Gun(pos=enemy.pos)
            self.guns.append(gun)
            self.add_widget(gun)
        elif rnd <= 65:  # 15% Medical
            medical = Medical(pos=enemy.pos)
            self.medicals.append(medical)
            self.add_widget(medical)
        elif rnd <= 85:  # 20% PowerUp
            power_type = choice(["speed", "shield", "bomb", "freeze", "health"])
            powerup = PowerUp(pos=enemy.pos, power_type=power_type)
            self.powerups.append(powerup)
            self.add_widget(powerup)
        
        # ✅ تقليل النقاط من الأعداء (من 15 إلى 10)
        self.score += 10  # كان 15
        self.xp += 15
        
        if self.xp >= self.level * 100:
            self.level += 1
            self.xp = 0
            self.max_health += 20
            self.health = self.max_health
        
        enemy.pos = (randint(Window.width, Window.width + 400), randint(250, Window.height - 150))
        
    def handle_bullet_hit(self, enemy, bullet):
        """💥 لما الرصاصة تخبط العدو"""
        
        explosion = Explosion(pos=enemy.pos)
        self.add_widget(explosion)
    
        self.create_particles(enemy.pos, color=(1, 0.5, 0, 1), count=10)
    
        self.play_sound(explosion_sound)
        
    def handle_enemy_hit(self, enemy):
        """💥 لما العدو يخبط اللاعب"""
        
        explosion = Explosion(pos=enemy.pos)
        self.add_widget(explosion)
    
        self.create_particles(enemy.pos, color=(1, 0.3, 0, 1), count=15)
    
        self.play_sound(explosion_sound)
    
        # إعادة العدو لمكان جديد
        enemy.pos = self._get_spawn_pos()
        
        
    def update_collectibles(self):
        """تحديث العناصر القابلة للجمع"""
        for c in self.coins[:]:
            c.update()
            if self.player.collide_widget(c):
                self.coins_count += 1
                self.play_sound(coin_sound)
                self.remove_widget(c)
                self.coins.remove(c)
        
        for g in self.guns[:]:
            g.update()
            if self.player.collide_widget(g):
                if self.bullets_count < 5:
                    self.base_bullets = self.bullets_count + 1
                    self.bullets_count += 1
                    self.temp_bullet_timer = 8

                    self.bullets_count += 1
                    self.play_sound(gun_sound)
                self.remove_widget(g)
                self.guns.remove(g)
        
        for m in self.medicals[:]:
            m.update()
            if self.player.collide_widget(m):
                self.health = min(self.health + 30, self.max_health)
                self.remove_widget(m)
                self.medicals.remove(m)
                self.play_sound(heal_sound)
        
        for p in self.powerups[:]:
            p.update()
            if self.player.collide_widget(p):
                self.activate_powerup(p.power_type)
                self.play_sound(powerup_sound)
                self.remove_widget(p)
                self.powerups.remove(p)
            elif p.x < -100:
                if p in self.powerups:
                    self.remove_widget(p)
                    self.powerups.remove(p)
    
    def update_boss(self, dt):
        """✅ تحديث الزعيم - مع إصلاح مشكلة الظهور"""
        # حساب مستوى اللعبة بناءً على النقاط
        new_level = self.score // 100 + 1
        
        # ✅ تحديث مستوى اللعبة تدريجياً
        if new_level > self.game_level:
            self.game_level = new_level
            self.show_level_up(self.game_level)
            for e in self.enemies:
                e.speed += 0.3
        
        # ✅ ظهور البوس فقط في المستويات المحددة (3, 6, 9, 12, 15)
        # وليس في كل المستويات!
        if (self.game_level in self.boss_levels and
            not self.boss and  # ✅ لا بوس نشط حالياً
            self.game_level not in self.completed_boss_levels):  # ✅ لم يهزم من قبل
            boss_type = self.boss_levels[self.game_level]
            self.spawn_boss(boss_type)
        
        # تحديث البوس
        if self.boss and self.boss.active:
            self.boss.update(dt, player_pos=(self.player.x, self.player.y), game=self)
            
            if self.player.collide_widget(self.boss):
                if not self.shield_active:
                    self.health -= 1
            
            for b in self.bullets[:]:
                if b.collide_widget(self.boss):
                    self.boss.health -= 1
                    explosion = Explosion(pos=b.pos)
                    self.add_widget(explosion)
                    self.create_particles(b.pos, color=(1, 0.5, 0, 1), count=5)
                    self.play_sound(explosion_sound)
                    
                    if b in self.bullets:
                        self.remove_widget(b)
                        self.bullets.remove(b)
                    
                    if self.boss.health <= 0:
                        self.defeat_boss()
                        break
    
    def spawn_boss(self, boss_type="normal"):
        """ظهور الزعيم"""
        if self.boss:
            return
        
        while len(self.enemies) > 2:
            if self.enemies:
                enemy = self.enemies.pop(0)
                self.remove_widget(enemy)
        
        self.boss_type = boss_type
        self.boss = Boss(boss_type=boss_type)
        self.boss.active = True        
        self.add_widget(self.boss)
        
        boss_label = Label(
            text="⚠️ BOSS INCOMING! ⚠️",
            font_size=64,
            bold=True,
            color=(1, 0, 0, 1),
            pos=(Window.width/2 - 300, Window.height/2),
            size_hint=(None, None),
            size=(600, 100),
            halign='center'
        )
        self.add_widget(boss_label)
        Clock.schedule_once(lambda dt: self.remove_widget(boss_label) if boss_label.parent else None, 3)
        
        stop_background_music()
        start_background_music(self.music_muted, True)
    
    def defeat_boss(self):
        """هزيمة الزعيم"""
        self.bosses_defeated += 1
        self.completed_boss_levels.add(self.game_level)  # ✅ تسجيل المستوى المكتمل
        
        explosion = Explosion(pos=self.boss.pos)
        self.add_widget(explosion)
        self.create_particles(self.boss.pos, color=(1, 0, 0, 1), count=50)
        self.play_sound(explosion_sound)
        
        # ✅ تقليل النقاط المكتسبة من البوس (من 100 إلى 50)
        self.score += 30  # كان 100
        self.xp += 50
        self.coins_count += 50
        
        # ✅ إزالة شريط الصحة
        if hasattr(self, '_boss_canvas_instructions'):
            for instr in self._boss_canvas_instructions:
                try:
                    self.canvas.after.remove(instr)
                except:
                    pass
            self._boss_canvas_instructions = []
        
        self.remove_widget(self.boss)
        self.boss = None
        
        stop_background_music()
        start_background_music(self.music_muted, False)
        self.save_game_data()
    
    def update_ui(self):
        # ❤️ Health
        self.update_bar(self.health_bar, self.health/self.max_health, True)
        self.health_text.text = f"{int(self.health)}/{self.max_health}"
    
        # ⭐ XP
        self.update_bar(self.xp_bar, self.xp/(self.level*100))
    
        # 💰 Coins
        self.coins_label.text = f"💰 {self.coins_count}"
    
        # 🧠 Level
        self.level_label.text = f"Lv.{self.level}"
    
    def activate_powerup(self, power_type):
        """تفعيل القوة"""
        if power_type == "speed":
            self.speed_active = True
            self.speed_timer = 10
            self.speed_boost_uses += 1
        elif power_type == "shield":
            self.shield_active = True
            self.shield_timer = 10
        elif power_type == "freeze":
            self.freeze_active = True
            self.freeze_timer = 5
        
            # ❄️ تأثير بصري فوري على كل الأعداء
            for enemy in self.enemies:
                enemy.opacity = 0.5
        elif power_type == "bomb":
            for enemy in self.enemies[:]:
                explosion = Explosion(pos=enemy.pos)
                self.add_widget(explosion)
                self.create_particles(enemy.pos, color=(1, 0.5, 0, 1), count=20)
                self.remove_widget(enemy)
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                self.score += 15
            self.play_sound(bomb_sound)
        elif power_type == "health":
            self.health = min(self.health + 50, self.max_health)
    
    def create_particles(self, pos, color=(1, 1, 1, 1), count=10):
        """إنشاء جسيمات"""
        for _ in range(count):
            particle = Particle(pos, color=color)
            self.particles.append(particle)
            self.add_widget(particle)
    
    def show_level_up(self, new_level):
        """عرض مستوى جديد"""
        level_label = LevelUpLabel(new_level)
        self.add_widget(level_label)
        self.play_sound(levelup_sound)
    
    def check_achievements(self):
        """التحقق من الإنجازات"""
        for ach_id, ach in self.achievements.items():
            if not ach["unlocked"]:
                if ach_id == "first_blood":
                    ach["progress"] = self.total_kills
                elif ach_id == "boss_slayer":                    ach["progress"] = self.bosses_defeated
                elif ach_id == "coin_collector":
                    ach["progress"] = self.coins_count
                elif ach_id == "speed_demon":
                    ach["progress"] = self.speed_boost_uses
                elif ach_id == "level_15":
                    ach["progress"] = self.game_level
                
                if ach["progress"] >= ach["target"]:
                    ach["unlocked"] = True
                    self.coins_count += ach["reward"]
                    self.show_achievement(ach)
                    self.save_game_data()
    
    def show_achievement(self, achievement):
        """عرض إنجاز"""
        popup = AchievementPopup(achievement)
        self.add_widget(popup)
        self.play_sound(coin_sound)
    
    def _get_spawn_pos(self):
        """الحصول على موقع ظهور آمن"""
        for _ in range(10):
            x = randint(Window.width, Window.width + 400)
            y = randint(250, Window.height - 150)
            if self._is_position_safe(x, y):
                return (x, y)
        base_y = randint(250, Window.height - 150)
        return (randint(Window.width, Window.width + 400), base_y + randint(-50, 50))
    
    def _is_position_safe(self, x, y, min_dist=80):
        """التحقق من أن الموقع آمن"""
        for e in self.enemies:
            dist = ((e.x - x)**2 + (e.y - y)**2)**0.5
            if dist < min_dist:
                return False
        return True
    
    def _pause_game(self):
        """إيقاف اللعبة"""
        if self.clock_event:
            Clock.unschedule(self.update)
            self.clock_event = None
            self.game_paused = True
    
    def _resume_game(self):
        """استئناف اللعبة"""
        if self.game_started and not self.clock_event:
            self.clock_event = Clock.schedule_interval(self.update, 1/60)
        self.game_paused = False    
    def _stop_game_loop(self):
        """إيقاف حلقة اللعبة"""
        if self.clock_event:
            Clock.unschedule(self.update)
            self.clock_event = None
        self.game_started = False
    
    def draw_boss_health_bar(self):
        """✅ رسم شريط صحة البوس"""
        # مسح الشريط القديم
        if hasattr(self, '_boss_canvas_instructions'):
            for instr in self._boss_canvas_instructions:
                try:
                    self.canvas.after.remove(instr)
                except:
                    pass
            self._boss_canvas_instructions = []
        
        # إذا لم يكن هناك بوس نشط، لا ترسم شيئاً
        if not self.boss or not self.boss.active:
            return
        
        # حساب نسبة الصحة
        bar_width = 400
        bar_height = 25
        health_percent = max(0, self.boss.health / self.boss.max_health)
        
        # رسم الشريط
        self._boss_canvas_instructions = []
        with self.canvas.after:
            # خلفية الشريط (رمادية)
            Color(0.15, 0.15, 0.15, 0.9)
            bg = RoundedRectangle(
                pos=(Window.width//2 - bar_width//2, Window.height - 55),
                size=(bar_width, bar_height),
                radius=[6]
            )
            self._boss_canvas_instructions.append(bg)
            
            # شريط الصحة (أحمر)
            Color(1, 0.3, 0.3, 1)
            bar = RoundedRectangle(
                pos=(Window.width//2 - bar_width//2 + 3, Window.height - 52),
                size=(max(0, (bar_width - 6) * health_percent), bar_height - 6),
                radius=[3]
            )
            self._boss_canvas_instructions.append(bar)
    
    def game_over(self):
        """نهاية اللعبة"""
        self._stop_game_loop()
        stop_background_music()
        self.save_game_data()
        
        self.clear_widgets()        
        game_over_label = Label(text="💀 GAME OVER", font_size=60, color=(1, 0, 0, 1),
                                pos=(Window.width*0.3, Window.height*0.6),
                                size_hint=(None, None), size=(400, 80), halign='center')
        self.add_widget(game_over_label)
        
        score_label = Label(text=f"Final Score: {self.score}", font_size=32,
                            pos=(Window.width*0.35, Window.height*0.45),
                            size_hint=(None, None), size=(300, 50), halign='center')
        self.add_widget(score_label)
        
        restart_btn = FancyButton(text="🔄 Play Again", size_hint=(None, None), size=(250, 70),
                                  pos=(Window.width*0.35, Window.height*0.3),
                                  background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1), font_size=26)
        restart_btn.bind(on_release=lambda x: self.start_game())
        self.add_widget(restart_btn)
        
        menu_btn = FancyButton(text="🏠 Main Menu", size_hint=(None, None), size=(250, 70),
                               pos=(Window.width*0.35, Window.height*0.15),
                               background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), font_size=26)
        menu_btn.bind(on_release=lambda x: self.show_mainmenu())
        self.add_widget(menu_btn)
    
    def show_settings(self):
        """عرض الإعدادات"""
        if self.menu_overlay:
            self.remove_widget(self.menu_overlay)
            self.menu_overlay = None
        
        if self.settings_screen and self.settings_screen.parent:
            self.remove_widget(self.settings_screen)
        
        self._pause_game()
        
        self.settings_screen = Widget(size=Window.size, pos=(0, 0))
        with self.settings_screen.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size, pos=(0, 0))
        
        title = Label(text="⚙️ Settings", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width*0.35, Window.height*0.8),
                      size_hint=(None, None), size=(300, 60), halign='center')
        self.settings_screen.add_widget(title)
        
        self.music_btn = FancyButton(
            text="Music: OFF" if self.music_muted else "Music: ON",
            size_hint=(None, None),
            size=(300, 70),
            pos=(Window.width*0.35, Window.height*0.6),
            background_color=(0.6, 0.3, 0.8, 1),            color=(1, 1, 1, 1),
            font_size=24
        )
        self.music_btn.bind(on_release=lambda x: self.toggle_music())
        self.settings_screen.add_widget(self.music_btn)
        
        self.sfx_btn = FancyButton(
            text="SFX: OFF" if self.sfx_muted else "SFX: ON",
            size_hint=(None, None),
            size=(300, 70),
            pos=(Window.width*0.35, Window.height*0.5),
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size=24
        )
        self.sfx_btn.bind(on_release=lambda x: self.toggle_sfx())
        self.settings_screen.add_widget(self.sfx_btn)
        
        back_btn = FancyButton(
            text="⬅️ Back to Menu",
            size_hint=(None, None),
            size=(250, 70),
            pos=(Window.width*0.35, Window.height*0.3),
            background_color=(0.2, 0.8, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=24
        )
        back_btn.bind(on_release=lambda x: self.show_mainmenu())
        self.settings_screen.add_widget(back_btn)
        
        self.add_widget(self.settings_screen)
        self.current_screen = self.settings_screen
    
    def toggle_music(self):
        """تبديل الموسيقى"""
        self.music_muted = not self.music_muted
        if self.music_muted:
            stop_background_music()
        else:
            start_background_music(False, self.boss is not None)
        if hasattr(self, 'music_btn'):
            self.music_btn.text = "Music: OFF" if self.music_muted else "Music: ON"
    
    def toggle_sfx(self):
        """تبديل المؤثرات"""
        self.sfx_muted = not self.sfx_muted
        if hasattr(self, 'sfx_btn'):
            self.sfx_btn.text = "SFX: OFF" if self.sfx_muted else "SFX: ON"
    
    def show_store(self):        
        """عرض المتجر"""
        if self.menu_overlay:
            self.remove_widget(self.menu_overlay)
            self.menu_overlay = None
        
        if self.store_screen and self.store_screen.parent:
            self.remove_widget(self.store_screen)
        
        self._pause_game()
        
        self.store_screen = Widget(size=Window.size, pos=(0, 0))
        with self.store_screen.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size, pos=(0, 0))
        
        title = Label(text="🛒 GAME STORE", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width*0.35, Window.height*0.85),
                      size_hint=(None, None), size=(400, 60), halign='center')
        self.store_screen.add_widget(title)
        
        self.coins_label_store = Label(text=f"💰 Coins: {self.coins_count}", font_size=32, color=(1, 0.84, 0, 1),
                                        pos=(Window.width*0.35, Window.height*0.78),
                                        size_hint=(None, None), size=(300, 50), halign='center')
        self.store_screen.add_widget(self.coins_label_store)
        
        store_items = [
            {"name": "+50 Health", "price": 5, "icon": "❤️", "pos": (Window.width*0.1, Window.height*0.6)},
            {"name": "+1 Bullet", "price": 10, "icon": "🔫", "pos": (Window.width*0.35, Window.height*0.6)},
            {"name": "Speed Boost", "price": 15, "icon": "⚡", "pos": (Window.width*0.6, Window.height*0.6)},
            {"name": "Shield", "price": 20, "icon": "🛡️", "pos": (Window.width*0.1, Window.height*0.35)},
            {"name": "Bomb x3", "price": 25, "icon": "💣", "pos": (Window.width*0.35, Window.height*0.35)},
            {"name": "Max HP +50", "price": 50, "icon": "💖", "pos": (Window.width*0.6, Window.height*0.35)},
        ]
        
        for item in store_items:
            item_btn = FancyButton(
                text=f"{item['icon']} {item['name']}\n{item['price']} Coins",
                size_hint=(None, None), size=(220, 120), pos=item['pos'],
                background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1), font_size=20
            )
            item_btn.bind(on_release=lambda x, i=item: self.buy_store_item(i))
            self.store_screen.add_widget(item_btn)
        
        back_btn = FancyButton(text="⬅️ Back to Menu", size_hint=(None, None), size=(250, 70),
                               pos=(Window.width*0.35, Window.height*0.1),
                               background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), font_size=24)
        back_btn.bind(on_release=lambda x: self.show_mainmenu())
        self.store_screen.add_widget(back_btn)
        
        self.add_widget(self.store_screen)        
        self.current_screen = self.store_screen
    
    def buy_store_item(self, item):
        """شراء عنصر من المتجر"""
        if self.coins_count >= item['price']:
            self.coins_count -= item['price']
            
            if item['name'] == "+50 Health":
                self.health = min(self.health + 50, self.max_health)
            elif item['name'] == "+1 Bullet":
                if self.bullets_count < 5:
                    self.base_bullets = self.bullets_count + 1
                    self.bullets_count += 1
                    self.temp_bullet_timer = 8

                    self.bullets_count += 1
            elif item['name'] == "Speed Boost":
                self.speed_active = True
                self.speed_timer = 15
            elif item['name'] == "Shield":
                self.shield_active = True
                self.shield_timer = 15
            elif item['name'] == "Max HP +50":
                self.max_health += 50
                self.health = self.max_health
            
            if hasattr(self, 'coins_label_store'):
                self.coins_label_store.text = f"💰 Coins: {self.coins_count}"
            self.play_sound(coin_sound)
        else:
            error_label = Label(text="❌ Not Enough Coins!", font_size=36, color=(1, 0, 0, 1),
                                pos=(Window.width*0.35, Window.height*0.5),
                                size_hint=(None, None), size=(400, 50), halign='center')
            self.store_screen.add_widget(error_label)
            Clock.schedule_once(lambda dt: self.store_screen.remove_widget(error_label) if error_label.parent else None, 2)
    
    def show_skins(self):
        """عرض السكنات"""
        if self.menu_overlay:
            self.remove_widget(self.menu_overlay)
            self.menu_overlay = None
        
        if self.skins_screen and self.skins_screen.parent:
            self.remove_widget(self.skins_screen)
        
        self._pause_game()
        
        self.skins_screen = Widget(size=Window.size, pos=(0, 0))
        with self.skins_screen.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size, pos=(0, 0))
        
        title = Label(text="🎨 SKINS", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width*0.35, Window.height*0.85),                      size_hint=(None, None), size=(300, 60), halign='center')
        self.skins_screen.add_widget(title)
        
        skins = [
            {"name": "default", "icon": "⚪", "price": 0, "owned": True},
            {"name": "blue", "icon": "🔵", "price": 100, "owned": "blue" in self.owned_skins},
            {"name": "red", "icon": "🔴", "price": 100, "owned": "red" in self.owned_skins},
            {"name": "green", "icon": "🟢", "price": 100, "owned": "green" in self.owned_skins},
            {"name": "gold", "icon": "🟡", "price": 500, "owned": "gold" in self.owned_skins},
        ]
        
        y_pos = Window.height * 0.65
        for skin in skins:
            if skin["owned"] and skin["name"] == self.equipped_skin:
                status = "✅ Equipped"
            elif skin["owned"]:
                status = "✅ Owned"
            else:
                status = f"{skin['price']} Coins"
            
            skin_btn = FancyButton(
                text=f"{skin['icon']} {skin['name'].capitalize()}\n{status}",
                size_hint=(None, None), size=(250, 100),
                pos=(Window.width*0.35, y_pos),
                background_color=(0.2, 0.6, 0.9, 1) if skin["owned"] else (0.5, 0.5, 0.5, 1),
                color=(1, 1, 1, 1), font_size=20
            )
            skin_btn.bind(on_release=lambda x, s=skin: self.buy_or_equip_skin(s))
            self.skins_screen.add_widget(skin_btn)
            y_pos -= 120
        
        back_btn = FancyButton(text="⬅️ Back to Menu", size_hint=(None, None), size=(250, 70),
                               pos=(Window.width*0.35, Window.height*0.1),
                               background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), font_size=24)
        back_btn.bind(on_release=lambda x: self.show_mainmenu())
        self.skins_screen.add_widget(back_btn)
        
        self.add_widget(self.skins_screen)
        self.current_screen = self.skins_screen
    
    def buy_or_equip_skin(self, skin):
        """شراء أو تجهيز سكن"""
        if skin["owned"]:
            self.equipped_skin = skin["name"]
            self.save_game_data()
        elif self.coins_count >= skin["price"]:
            self.coins_count -= skin["price"]
            self.owned_skins.append(skin["name"])
            self.equipped_skin = skin["name"]
            self.save_game_data()        
            self.show_skins()
    
    def show_achievements_menu(self):
        """عرض الإنجازات"""
        if self.menu_overlay:
            self.remove_widget(self.menu_overlay)
            self.menu_overlay = None
        
        if self.achievements_screen and self.achievements_screen.parent:
            self.remove_widget(self.achievements_screen)
        
        self._pause_game()
        
        self.achievements_screen = Widget(size=Window.size, pos=(0, 0))
        with self.achievements_screen.canvas:
            Color(0.1, 0.15, 0.2, 1)
            Rectangle(size=Window.size, pos=(0, 0))
        
        title = Label(text="🏆 ACHIEVEMENTS", font_size=48, bold=True, color=(1, 1, 0, 1),
                      pos=(Window.width*0.35, Window.height*0.85),
                      size_hint=(None, None), size=(400, 60), halign='center')
        self.achievements_screen.add_widget(title)
        
        y_pos = Window.height * 0.65
        for ach_id, ach in self.achievements.items():
            status = "✅" if ach["unlocked"] else "⬜"
            progress = f"{ach['progress']}/{ach['target']}"
            
            ach_label = Label(
                text=f"{status} {ach['icon']} {ach['name']}\n{ach['desc']}\nProgress: {progress}",
                font_size=22,
                color=(0, 1, 0, 1) if ach["unlocked"] else (1, 1, 1, 1),
                pos=(Window.width*0.35, y_pos),
                size_hint=(None, None), size=(500, 80),
                halign='center', valign='middle'
            )
            self.achievements_screen.add_widget(ach_label)
            y_pos -= 100
        
        back_btn = FancyButton(text="⬅️ Back to Menu", size_hint=(None, None), size=(250, 70),
                               pos=(Window.width*0.35, Window.height*0.1),
                               background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), font_size=24)
        back_btn.bind(on_release=lambda x: self.show_mainmenu())
        self.achievements_screen.add_widget(back_btn)
        
        self.add_widget(self.achievements_screen)
        self.current_screen = self.achievements_screen