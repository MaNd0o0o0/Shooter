"""
audio_manager.py - إدارة الصوت والموسيقى
"""

from kivy.core.audio import SoundLoader
from config import SOUNDS_PATH
import os

# ==================== تحميل الأصوات ====================
_sounds = {}

def _load_sound(filename):
    """تحميل صوت من الملف"""
    path = f'{SOUNDS_PATH}/{filename}'
    if os.path.exists(path):
        return SoundLoader.load(path)
    return None

# تحميل جميع الأصوات
shoot_sound = _load_sound('shoot.wav')
explosion_sound = _load_sound('explosion.wav')
coin_sound = _load_sound('coin.wav')
gun_sound = _load_sound('gun.wav')
heal_sound = _load_sound('heal.wav')
powerup_sound = _load_sound('powerup.wav')
bomb_sound = _load_sound('bomb.wav')
levelup_sound = _load_sound('levelup.wav')

# موسيقى الخلفية
background_music = _load_sound('background_music.mp3')
boss_music = _load_sound('BossBattle.wav')

if background_music:
    background_music.loop = True
    background_music.volume = 0.7
if boss_music:
    boss_music.loop = True
    boss_music.volume = 0.8

# حالة التشغيل
_background_music_playing = False
_current_music = None


def play_sound(sound, muted=False):
    """تشغيل صوت مع التحقق من الكتم"""
    if sound and not muted:
        try:
            sound.play()
        except:
            pass


def start_background_music(muted=False, is_boss=False):
    """تشغيل الموسيقى الخلفية"""
    global _background_music_playing, _current_music
    
    if muted:
        return
    
    if _background_music_playing:
        stop_background_music()
    
    music = boss_music if is_boss else background_music
    if music:
        try:
            music.loop = True
            music.play()
            _background_music_playing = True
            _current_music = music
        except:
            pass


def stop_background_music():
    """إيقاف الموسيقى الخلفية"""
    global _background_music_playing, _current_music
    
    if _current_music:
        try:
            _current_music.stop()
        except:
            pass
    
    _background_music_playing = False
    _current_music = None


def cleanup_audio():
    """تنظيف الصوت عند الإغلاق"""
    stop_background_music()