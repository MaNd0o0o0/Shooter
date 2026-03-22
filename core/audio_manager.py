"""audio_manager.py - مدير الصوت"""
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