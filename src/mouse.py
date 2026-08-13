"""
AutoClicker - DirectInput Mouse Control
Low-level Windows SendInput API for game-compatible mouse clicks.
"""

import ctypes
import time

# --- Ctypes DirectInput mouse control structures ---------------------------
SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Mouse Flags
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040


def win32_press_mouse(btn_str):
    """Send a mouse button down event via DirectInput."""
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    if btn_str == "right":
        flags = MOUSEEVENTF_RIGHTDOWN
    elif btn_str == "mid":
        flags = MOUSEEVENTF_MIDDLEDOWN
    else:
        flags = MOUSEEVENTF_LEFTDOWN
    ii_.mi = MouseInput(0, 0, 0, flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def win32_release_mouse(btn_str):
    """Send a mouse button up event via DirectInput."""
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    if btn_str == "right":
        flags = MOUSEEVENTF_RIGHTUP
    elif btn_str == "mid":
        flags = MOUSEEVENTF_MIDDLEUP
    else:
        flags = MOUSEEVENTF_LEFTUP
    ii_.mi = MouseInput(0, 0, 0, flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def win32_click_mouse(btn_str, count=1):
    """Perform a full click (press + release) via DirectInput."""
    for _ in range(count):
        win32_press_mouse(btn_str)
        time.sleep(0.02)  # 20ms hold down duration so games catch the frame
        win32_release_mouse(btn_str)
        if count > 1:
            time.sleep(0.02)
