"""
AutoClicker - Hotkey Utilities
Keyboard key name resolution for pynput key events.
"""

from pynput.keyboard import Key


def _name_from_vk(vk):
    if 112 <= vk <= 135:               # VK_F1 .. VK_F24
        return f"F{vk - 111}"
    if 96 <= vk <= 105:                # numpad digits
        return f"Num {vk - 96}"
    if 48 <= vk <= 57 or 65 <= vk <= 90:
        return chr(vk)                 # digits and letters, layout independent
    return f"Key {vk}"


def get_key_name(key):
    """Convert a pynput key object to a human-readable string.

    The same key must always produce the same name, whether it is pressed while
    binding a hotkey or later while the app is running - including when a
    modifier such as Ctrl is held, which makes pynput report a control
    character instead of a letter.
    """
    try:
        if isinstance(key, Key):
            return key.name.replace('_', ' ').title()

        char = getattr(key, 'char', None)
        vk = getattr(key, 'vk', None)

        # Ctrl+A arrives as '\x01'; fall back to the virtual key code so the
        # name matches the one recorded without the modifier.
        if char is not None and char.isprintable():
            return char.upper()
        if vk is not None:
            return _name_from_vk(vk)
        if char is not None:
            return char.upper()
    except Exception:
        pass
    return str(key)
