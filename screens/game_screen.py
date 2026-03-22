"""game_screen.py - شاشة اللعب"""

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

        self.audio = audio_manager
        self.saver = save_manager
        self.player_data = player_data or {}

        self.state = {
            'score': 0, 'coins': 0,
            'health': 100, 'max_health': 100,
            'xp': 0, 'level': 1,
            'game_level': 1,
            'bullets_count': 1,
            'total_kills': 0,
            'bosses_defeated': 0
        }

        self.entities = {
            'bullets': [], 'boss_bullets': [],
            'enemies': [], 'coins': [],
            'powerups': [], 'particles': [],
            'guns': [], 'medicals': []
        }

        self.powerups_active = {'shield': False, 'speed': False, 'freeze': False}
        self.powerup_timers = {'shield': 0, 'speed': 0, 'freeze': 0}

        self.boss = None
        self.clock_event = None
        self.joystick = None

        self.ui_labels = {}
        self.fire_delay = 0
        self.enemy_spawn_timer = 0
        self.completed_boss_levels = set()

    # =========================
    # START
    # =========================
    def start(self):
        self._reset()
        self._setup_background()
        self._spawn_player()
        self._setup_ui()
        self._setup_controls()

        self.clock_event = Clock.schedule_interval(self.update, 1 / 60)
        self.audio.play_background()

    def _reset(self):
        self.clear_widgets()

        self.state.update({
            'score': 0, 'coins': 0,
            'health': 100, 'xp': 0,
            'level': 1, 'game_level': 1,
            'bullets_count': 1
        })

        for lst in self.entities.values():
            lst.clear()

        self.boss = None
        self.powerups_active = {k: False for k in self.powerups_active}
        self.completed_boss_levels.clear()

    # =========================
    # BACKGROUND
    # =========================
    def _setup_background(self):
        with self.canvas:
            Color(0.6, 0.85, 1, 1)
            self.sky = Rectangle(size=(WINDOW_WIDTH, WINDOW_HEIGHT), pos=(0, 0))

            Color(1, 0.9, 0.3, 1)
            self.sun = Ellipse(pos=(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 350), size=(200, 200))

            Color(0, 0.5, 0.9, 1)
            self.sea = Rectangle(size=(WINDOW_WIDTH, 750), pos=(0, 0))

        # Layers
        self.bg_m1 = Image(source="mountains.png", pos=(0, WINDOW_HEIGHT - 1780))
        self.bg_m2 = Image(source="mountains.png", pos=(WINDOW_WIDTH, WINDOW_HEIGHT - 1780))

        self.bg_c1 = Image(source="city.png", pos=(0, 300))
        self.bg_c2 = Image(source="city.png", pos=(WINDOW_WIDTH, 300))

        self.bg_l1 = Image(source="clouds.png", pos=(0, WINDOW_HEIGHT - 300))
        self.bg_l2 = Image(source="clouds.png", pos=(WINDOW_WIDTH, WINDOW_HEIGHT - 300))

        for w in [self.bg_m1, self.bg_m2, self.bg_c1, self.bg_c2, self.bg_l1, self.bg_l2]:
            self.add_widget(w)

    def _update_background(self, dt):
        layers = [
            (self.bg_m1, self.bg_m2, SCROLL_SPEEDS['mountains']),
            (self.bg_c1, self.bg_c2, SCROLL_SPEEDS['city']),
            (self.bg_l1, self.bg_l2, SCROLL_SPEEDS['clouds'])
        ]

        for m1, m2, speed in layers:
            m1.x -= speed
            m2.x -= speed

            if m1.right <= 0:
                m1.x = m2.right

            if m2.right <= 0:
                m2.x = m1.right

    # =========================
    # PLAYER
    # =========================
    def _spawn_player(self):
        skin = self.player_data.get('equipped_skin', 'default')
        self.player = Player(skin=skin)
        self.add_widget(self.player)

    def _update_player(self, dt):
        if self.joystick and self.joystick.active:
            mult = 1.5 if self.powerups_active['speed'] else 1.0
            self.player.move(self.joystick.dx, self.joystick.dy, mult)

            self.fire_delay += dt
            rate = 0.1 if self.powerups_active['speed'] else 0.18

            if self.fire_delay > rate:
                self._fire()
                self.fire_delay = 0

    def _fire(self):
        angles = {
            1: [0],
            2: [-5, 5],
            3: [-10, 0, 10],
            4: [-15, -5, 5, 15]
        }.get(self.player.bullets_count, [-20, -10, 0, 10, 20])

        for a in angles:
            b = Bullet(pos=(self.player.right, self.player.center_y), angle=a)
            self.entities['bullets'].append(b)
            self.add_widget(b)

        self.audio.play_sfx('shoot')

    # =========================
    # UPDATE LOOP
    # =========================
    def update(self, dt):
        self._update_background(dt)
        self._update_player(dt)
        self._spawn_enemies(dt)
        self._update_entities(dt)
        self._check_collisions()
        self._update_powerups(dt)
        self._update_ui()
        self._check_progression()
        self._check_game_over()

    # =========================
    # ENTITIES
    # =========================
    def _update_entities(self, dt):
        for name, lst in self.entities.items():
            for e in lst[:]:
                if hasattr(e, 'update'):
                    e.update(dt)

                if hasattr(e, 'is_offscreen') and e.is_offscreen():
                    lst.remove(e)
                    if e.parent:
                        self.remove_widget(e)

        if self.boss and self.boss.active:
            self.boss.update(dt, (self.player.x, self.player.y), self)

    # =========================
    # GAME OVER
    # =========================
    def _check_game_over(self):
        if self.state['health'] <= 0:
            self.state['health'] = 0
            self.pause()
            self.audio.stop_music()

    def pause(self):
        if self.clock_event:
            Clock.unschedule(self.update)
            self.clock_event = None