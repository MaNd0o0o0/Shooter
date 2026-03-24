from kivy.core.audio import SoundLoader
from config import SOUNDS_PATH

# ---------------- الأصوات ----------------
shoot_sound = SoundLoader.load(f'{SOUNDS_PATH}/shoot.wav')
explosion_sound = SoundLoader.load(f'{SOUNDS_PATH}/explosion.wav')
coin_sound = SoundLoader.load(f'{SOUNDS_PATH}/coin.wav')
gun_sound = SoundLoader.load(f'{SOUNDS_PATH}/gun.wav')
heal_sound = SoundLoader.load(f'{SOUNDS_PATH}/heal.wav')
powerup_sound = SoundLoader.load(f'{SOUNDS_PATH}/powerup.wav')
bomb_sound = SoundLoader.load(f'{SOUNDS_PATH}/bomb.wav')
levelup_sound = SoundLoader.load(f'{SOUNDS_PATH}/levelup.wav')

try:
    background_music = SoundLoader.load(f'{SOUNDS_PATH}/background_music.mp3')
    if background_music:
        background_music.volume = 0.30
        background_music.loop = True
except:
    background_music = None

boss_music = SoundLoader.load(f'{SOUNDS_PATH}/BossBattle.wav')
if boss_music:
    boss_music.loop = True

def play_sound(sound, muted=False):
    """تشغيل صوت مع التحقق من الكتم"""
    if sound and not muted:
        try:
            if hasattr(sound, 'length') and sound.length > 0:
                sound.play()
        except:
            pass

def start_background_music(muted=False, boss_active=False):
    """تشغيل موسيقى الخلفية"""
    if boss_active:
        if boss_music and not muted:
            try:
                if hasattr(boss_music, 'length') and boss_music.length > 0:
                    boss_music.play()
            except:
                pass
    else:
        if background_music and not muted:
            try:
                if hasattr(background_music, 'length') and background_music.length > 0:
                    background_music.play()
            except:
                pass

def stop_background_music():
    """إيقاف جميع الموسيقى"""
    if background_music:
        try:
            background_music.stop()
        except:
            pass
    if boss_music:
        try:
            boss_music.stop()
        except:
            pass