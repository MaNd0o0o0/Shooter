"""
input_system.py - إدارة المدخلات والتحكم
"""

from kivy.core.window import Window
from typing import Optional, Callable, Tuple, Dict
from enum import Enum


class InputAction(Enum):
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    FIRE = "fire"
    PAUSE = "pause"
    SKILL = "skill"


class InputSystem:
    """نظام إدارة المدخلات والتحكم"""
    
    def __init__(self):
        self.key_states: Dict[str, bool] = {}
        self.active_touches: Dict[int, dict] = {}
        
        self.joystick_active = False
        self.joystick_direction = (0, 0)
        
        self.fire_button_pressed = False
        self.fire_touch_id = None
        
        self.action_callbacks: Dict[InputAction, list] = {}
        
        self.move_sensitivity = 1.0
        self.fire_rate = 0.15
        self.fire_delay = 0
        
        self._register_keyboard()
    
    def _register_keyboard(self):
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)
    
    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        action = self._key_to_action(key)
        if action:
            self.key_states[action.value] = True
            self._trigger_action(action, True)
        return True
    
    def _on_key_up(self, window, key, scancode):
        action = self._key_to_action(key)
        if action:
            self.key_states[action.value] = False
            self._trigger_action(action, False)
        return True
    
    def _key_to_action(self, key) -> Optional[InputAction]:
        key_map = {
            'w': InputAction.MOVE_UP, 's': InputAction.MOVE_DOWN,
            'a': InputAction.MOVE_LEFT, 'd': InputAction.MOVE_RIGHT,
            'up': InputAction.MOVE_UP, 'down': InputAction.MOVE_DOWN,
            'left': InputAction.MOVE_LEFT, 'right': InputAction.MOVE_RIGHT,
            'space': InputAction.FIRE, 'p': InputAction.PAUSE, 'e': InputAction.SKILL,
        }
        return key_map.get(key)
    
    def handle_touch_down(self, touch):
        self.active_touches[touch.uid] = {'pos': touch.pos, 'type': 'unknown'}
        
        if self._is_on_joystick(touch.pos):
            self.joystick_active = True
            self.active_touches[touch.uid]['type'] = 'joystick'
            self._update_joystick(touch.pos)
            return True
        
        if self._is_on_fire_button(touch.pos):
            self.fire_button_pressed = True
            self.fire_touch_id = touch.uid
            self.active_touches[touch.uid]['type'] = 'fire'
            self._trigger_action(InputAction.FIRE, True)
            return True
        
        return False
    
    def handle_touch_move(self, touch):
        if touch.uid not in self.active_touches:
            return False
        
        touch_data = self.active_touches[touch.uid]
        if touch_data['type'] == 'joystick':
            self._update_joystick(touch.pos)
            return True
        
        return False
    
    def handle_touch_up(self, touch):
        if touch.uid not in self.active_touches:
            return False
        
        touch_data = self.active_touches[touch.uid]
        
        if touch_data['type'] == 'joystick':
            self.joystick_active = False
            self.joystick_direction = (0, 0)
            del self.active_touches[touch.uid]
            return True
        
        if touch_data['type'] == 'fire':
            if self.fire_touch_id == touch.uid:
                self.fire_button_pressed = False
                self.fire_touch_id = None
                self._trigger_action(InputAction.FIRE, False)
            del self.active_touches[touch.uid]
            return True
        
        del self.active_touches[touch.uid]
        return False
    
    def _is_on_joystick(self, pos) -> bool:
        if not hasattr(self, 'joystick_area'):
            return False
        
        jx, jy = self.joystick_area
        radius = self.joystick_radius if hasattr(self, 'joystick_radius') else 150
        dx, dy = pos[0] - jx, pos[1] - jy
        return (dx*dx + dy*dy) ** 0.5 <= radius
    
    def _is_on_fire_button(self, pos) -> bool:
        if not hasattr(self, 'fire_button_area'):
            return False
        
        fx, fy = self.fire_button_area
        fw, fh = self.fire_button_size if hasattr(self, 'fire_button_size') else (80, 80)
        return fx <= pos[0] <= fx + fw and fy <= pos[1] <= fy + fh
    
    def _update_joystick(self, pos):
        if not hasattr(self, 'joystick_area'):
            return
        
        jx, jy = self.joystick_area
        dx, dy = pos[0] - jx, pos[1] - jy
        max_dist = self.joystick_radius if hasattr(self, 'joystick_radius') else 150
        distance = (dx*dx + dy*dy) ** 0.5
        
        if distance > max_dist:
            dx = dx / distance * max_dist
            dy = dy / distance * max_dist
            distance = max_dist
        
        if distance > 0:
            self.joystick_direction = (dx / max_dist, dy / max_dist)
        else:
            self.joystick_direction = (0, 0)
    
    def _trigger_action(self, action: InputAction, pressed: bool):
        if action in self.action_callbacks:
            for callback in self.action_callbacks[action]:
                try:
                    callback(pressed)
                except Exception as e:
                    print(f"Error in action callback: {e}")
    
    def register_action(self, action: InputAction, callback: Callable):
        if action not in self.action_callbacks:
            self.action_callbacks[action] = []
        self.action_callbacks[action].append(callback)
    
    def set_joystick_area(self, center: Tuple[float, float], radius: float = 150):
        self.joystick_area = center
        self.joystick_radius = radius
    
    def set_fire_button_area(self, pos: Tuple[float, float], size: Tuple[float, float] = (80, 80)):
        self.fire_button_area = pos
        self.fire_button_size = size
    
    def get_movement(self) -> Tuple[float, float]:
        keyboard_dx, keyboard_dy = 0, 0
        if self.key_states.get(InputAction.MOVE_LEFT.value, False):
            keyboard_dx = -1
        if self.key_states.get(InputAction.MOVE_RIGHT.value, False):
            keyboard_dx = 1
        if self.key_states.get(InputAction.MOVE_UP.value, False):
            keyboard_dy = 1
        if self.key_states.get(InputAction.MOVE_DOWN.value, False):
            keyboard_dy = -1
        
        if keyboard_dx != 0 or keyboard_dy != 0:
            length = (keyboard_dx*keyboard_dx + keyboard_dy*keyboard_dy) ** 0.5
            if length > 0:
                keyboard_dx /= length
                keyboard_dy /= length
            return (keyboard_dx * self.move_sensitivity, keyboard_dy * self.move_sensitivity)
        
        if self.joystick_active:
            return (self.joystick_direction[0] * self.move_sensitivity, self.joystick_direction[1] * self.move_sensitivity)
        
        return (0, 0)
    
    def is_firing(self) -> bool:
        return self.key_states.get(InputAction.FIRE.value, False) or self.fire_button_pressed
    
    def update(self, dt: float):
        if self.is_firing():
            self.fire_delay += dt
        else:
            self.fire_delay = 0
    
    def can_fire(self) -> bool:
        if self.is_firing() and self.fire_delay >= self.fire_rate:
            self.fire_delay = 0
            return True
        return False
    
    def reset(self):
        self.key_states.clear()
        self.active_touches.clear()
        self.joystick_active = False
        self.joystick_direction = (0, 0)
        self.fire_button_pressed = False
        self.fire_delay = 0