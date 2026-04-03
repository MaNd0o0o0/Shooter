"""
save_manager.py - حفظ وتحميل بيانات اللعبة
"""

import json
import os
from config import SAVE_FILE


def load_game_data():
    """تحميل بيانات اللعبة المحفوظة"""
    default_data = {
        'owned_skins': ['default'],
        'equipped_skin': 'default',
        'achievements': {},
        'total_kills': 0,
        'bosses_defeated': 0,
        'speed_boost_uses': 0,
        'completed_boss_levels': [],
        'high_score': 0,
        'total_coins': 0,
        'settings': {
            'music_muted': False,
            'sfx_muted': False,
            'language': 'arabic'
        }
    }
    
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                default_data.update(loaded_data)
    except Exception as e:
        print(f"Error loading game data: {e}")
    
    return default_data


def save_game_data(game_data):
    """حفظ بيانات اللعبة"""
    try:
        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
        
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving game data: {e}")
        return False


def update_high_score(score):
    """تحديث أعلى نتيجة"""
    data = load_game_data()
    if score > data.get('high_score', 0):
        data['high_score'] = score
        save_game_data(data)
        return True
    return False


def add_total_coins(amount):
    """إضافة عملات إلى الإجمالي"""
    data = load_game_data()
    data['total_coins'] = data.get('total_coins', 0) + amount
    save_game_data(data)