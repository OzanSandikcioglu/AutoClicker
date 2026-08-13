"""
AutoClicker - Hotkey Utilities
Keyboard key name resolution for pynput key events.
"""

from pynput.keyboard import Key


def get_key_name(key):
    """Convert a pynput key object to a human-readable string."""
    try:
        if isinstance(key, Key):
            name = key.name
            return name.replace('_', ' ').title()
        elif hasattr(key, 'char') and key.char is not None:
            return key.char.upper()
        elif hasattr(key, 'vk') and key.vk is not None:
            vk = key.vk
            if 112 <= vk <= 123:
                return f"F{vk - 111}"
            return f"Key {vk}"
    except:
        pass
    return str(key)
