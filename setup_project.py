"""
setup_project.py - إنشاء الهيكل الأساسي للمشروع
"""

import os
import shutil

def create_project_structure():
    """إنشاء مجلدات المشروع"""
    folders = [
        'assets/images',
        'assets/sounds',
        'assets/fonts',
        'core',
        'systems',
        'layers',
        'entities',
        'widgets',
        'screens',
        'managers',
        'utils',
        'data',
        'cpp'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        init_file = os.path.join(folder.split('/')[0], '__init__.py')
        if folder.count('/') == 0:
            with open(init_file, 'a') as f:
                pass
    
    print("✅ Project structure created!")

def create_sample_files():
    """إنشاء ملفات عينة للصور والصوت"""
    # ملفات الصور الوهمية (سيتم استبدالها)
    sample_images = [
        'player.png', 'player_blue.png', 'player_red.png',
        'enemy.png', 'enemy_fast.png', 'enemy_armor.png',
        'boss.png', 'boss_fire.png', 'boss_ice.png',
        'bullet.png', 'boss_bullet.png',
        'coin.png', 'gun.png', 'medical.png',
        'powerup_speed.png', 'powerup_shield.png',
        'bg.png', 'splash.png', 'logo.jpeg'
    ]
    
    for img in sample_images:
        path = f'assets/images/{img}'
        if not os.path.exists(path):
            print(f"⚠️ Missing: {path}")
    
    print("✅ Sample file list created!")

if __name__ == '__main__':
    create_project_structure()
    create_sample_files()
    print("🚀 Project ready! Run main.py")