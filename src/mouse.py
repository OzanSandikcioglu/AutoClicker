"""
AutoClicker - DirectInput Mouse Control
Low-level Windows SendInput API for game-compatible mouse clicks.
"""

import ctypes
from ctypes import wintypes
from time import perf_counter as _perf_counter, sleep as _sleep

user32 = ctypes.WinDLL("user32", use_last_error=True)

try:
    _winmm = ctypes.WinDLL("winmm")
except OSError:
    _winmm = None

# --- Ctypes DirectInput mouse control structures ---------------------------
# ULONG_PTR is 8 bytes on x64 and 4 on x86; WPARAM has exactly that width.
ULONG_PTR = wintypes.WPARAM
_PTR_MASK = (1 << (ctypes.sizeof(ULONG_PTR) * 8)) - 1

# Signature stamped into every event we inject. Lets the UI recognise our own
# clicks when they land on our own window (see is_injected_event).
INJECT_TAG = 0x41434C4B  # 'ACLK'


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class KeybdInput(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD)]


class Input_I(ctypes.Union):
    # Keyboard/hardware members are listed so the union gets the size Windows
    # expects for an INPUT record.
    _fields_ = [("mi", MouseInput),
                ("ki", KeybdInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD),
                ("ii", Input_I)]


user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT
user32.GetMessageExtraInfo.argtypes = ()
user32.GetMessageExtraInfo.restype = wintypes.LPARAM

INPUT_MOUSE = 0

# Mouse Flags
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

_DOWN_FLAGS = {"left": MOUSEEVENTF_LEFTDOWN,
               "right": MOUSEEVENTF_RIGHTDOWN,
               "mid": MOUSEEVENTF_MIDDLEDOWN}
_UP_FLAGS = {"left": MOUSEEVENTF_LEFTUP,
             "right": MOUSEEVENTF_RIGHTUP,
             "mid": MOUSEEVENTF_MIDDLEUP}

# How long a button stays down so games catch the frame.
HOLD_SECONDS = 0.020


def _send(flags):
    """Push a single tagged mouse event through SendInput. True if accepted."""
    inp = Input(type=INPUT_MOUSE,
                ii=Input_I(mi=MouseInput(0, 0, 0, flags, 0, INJECT_TAG)))
    return user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(Input)) == 1


def _busy_sleep(duration):
    """Sleep that stays accurate for the very short holds used between clicks."""
    if duration <= 0:
        return
    end = _perf_counter() + duration
    if duration > 0.002:
        _sleep(duration - 0.001)
    while _perf_counter() < end:
        pass


def win32_press_mouse(btn_str):
    """Send a mouse button down event via DirectInput."""
    return _send(_DOWN_FLAGS.get(btn_str, MOUSEEVENTF_LEFTDOWN))


def win32_release_mouse(btn_str):
    """Send a mouse button up event via DirectInput."""
    return _send(_UP_FLAGS.get(btn_str, MOUSEEVENTF_LEFTUP))


def win32_click_mouse(btn_str, count=1, hold=HOLD_SECONDS, gap=None):
    """Perform full clicks (press + release) via DirectInput.

    `hold` is the button-down duration, shrunk automatically by the caller when
    the requested click interval is shorter than the default game-friendly 20ms.
    Returns False if Windows rejected any of the events (e.g. a more privileged
    window is blocking injected input).
    """
    ok = True
    if gap is None:
        gap = hold
    for i in range(count):
        ok = win32_press_mouse(btn_str) and ok
        _busy_sleep(hold)
        ok = win32_release_mouse(btn_str) and ok
        if i < count - 1:
            _busy_sleep(gap)
    return ok


def is_injected_event():
    """True when the message Windows is dispatching right now is one of ours.

    Injected clicks that land on the AutoClicker window would otherwise press
    our own buttons - most visibly toggling the clicker off again.
    """
    try:
        return (user32.GetMessageExtraInfo() & _PTR_MASK) == INJECT_TAG
    except Exception:
        return False


ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

try:
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _kernel32.SetThreadExecutionState.argtypes = (wintypes.DWORD,)
    _kernel32.SetThreadExecutionState.restype = wintypes.DWORD
except (OSError, AttributeError):
    _kernel32 = None


def keep_awake(enabled):
    """Hold off sleep/screen blanking while clicking.

    An unattended run is the whole point of the app, and a machine that dozes
    off silently swallows every click that follows.
    """
    if _kernel32 is None:
        return
    flags = ES_CONTINUOUS
    if enabled:
        flags |= ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    try:
        _kernel32.SetThreadExecutionState(flags)
    except Exception:
        pass


def begin_high_resolution_timer():
    """Ask Windows for 1ms scheduler granularity so short intervals hold up."""
    if _winmm is not None:
        try:
            _winmm.timeBeginPeriod(1)
        except Exception:
            pass


def end_high_resolution_timer():
    if _winmm is not None:
        try:
            _winmm.timeEndPeriod(1)
        except Exception:
            pass
