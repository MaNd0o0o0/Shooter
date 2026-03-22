"""save_manager.py - حفظ البيانات"""
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