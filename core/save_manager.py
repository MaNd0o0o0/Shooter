import json
import os
from config import SAVE_FILE

def load_game_data():
    """تحميل بيانات اللعبة المحفوظة"""
    data = {
        'owned_skins': ['default'],
        'equipped_skin': 'default',
        'achievements': {},
        'total_kills': 0,
        'bosses_defeated': 0,
        'speed_boost_uses': 0,
        'completed_boss_levels': []
    }
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                data.update(loaded_data)
    except:
        pass
    return data

def save_game_data(game_data):
    """حفظ بيانات اللعبة"""
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving game data: {e}")