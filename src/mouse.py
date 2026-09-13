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
user32.GetSystemMetrics.argtypes = (ctypes.c_int,)
user32.GetSystemMetrics.restype = ctypes.c_int
user32.GetCursorPos.argtypes = (ctypes.POINTER(wintypes.POINT),)
user32.GetCursorPos.restype = wintypes.BOOL
user32.WindowFromPoint.argtypes = (wintypes.POINT,)
user32.WindowFromPoint.restype = wintypes.HWND
user32.GetAncestor.argtypes = (wintypes.HWND, wintypes.UINT)
user32.GetAncestor.restype = wintypes.HWND
user32.SetCursorPos.argtypes = (ctypes.c_int, ctypes.c_int)
user32.SetCursorPos.restype = wintypes.BOOL

INPUT_MOUSE = 0

# Mouse Flags
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000

# Virtual screen metrics, so absolute moves land correctly on multi monitor
# setups and on monitors placed left of or above the primary one.
SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN = 76, 77
SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 78, 79
GA_ROOT = 2

_DOWN_FLAGS = {"left": MOUSEEVENTF_LEFTDOWN,
               "right": MOUSEEVENTF_RIGHTDOWN,
               "mid": MOUSEEVENTF_MIDDLEDOWN}
_UP_FLAGS = {"left": MOUSEEVENTF_LEFTUP,
             "right": MOUSEEVENTF_RIGHTUP,
             "mid": MOUSEEVENTF_MIDDLEUP}

# How long a button stays down so games catch the frame.
HOLD_SECONDS = 0.020


def _send(flags, dx=0, dy=0):
    """Push a single tagged mouse event through SendInput. True if accepted."""
    inp = Input(type=INPUT_MOUSE,
                ii=Input_I(mi=MouseInput(dx, dy, 0, flags, 0, INJECT_TAG)))
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


def win32_move_mouse(x, y):
    """Put the pointer on a screen position with a tagged absolute move.

    SendInput is used rather than SetCursorPos because games that read the
    input stream see this one and ignore the other.
    """
    left = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    top = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    width = max(user32.GetSystemMetrics(SM_CXVIRTUALSCREEN), 1)
    height = max(user32.GetSystemMetrics(SM_CYVIRTUALSCREEN), 1)
    # Absolute coordinates run 0..65535 across the virtual desktop, and Windows
    # maps them back with pixel = value * size // 65536. Aiming at the middle of
    # the pixel inverts that exactly; scaling by 65535/(size-1) misses by one
    # pixel at many positions.
    nx = min(max(int((int(x) - left + 0.5) * 65536 / width), 0), 65535)
    ny = min(max(int((int(y) - top + 0.5) * 65536 / height), 0), 65535)
    ok = _send(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK,
               nx, ny)
    # The normalised coordinates above round to the wrong pixel at some
    # positions, and a pattern aimed at a small target cannot afford that.
    # SetCursorPos takes plain pixels, so it lands exactly; the SendInput move
    # still happened first, which is the one games watching the input stream
    # actually see.
    user32.SetCursorPos(int(x), int(y))
    return ok


def get_cursor_pos():
    """Current pointer position as (x, y), or None if Windows refused."""
    point = wintypes.POINT()
    if user32.GetCursorPos(ctypes.byref(point)):
        return point.x, point.y
    return None


def top_level_at(x, y):
    """Handle of the top level window under a screen point."""
    point = wintypes.POINT(int(x), int(y))
    return user32.GetAncestor(user32.WindowFromPoint(point), GA_ROOT)


def top_level_of(handle):
    """Top level window a child handle belongs to."""
    return user32.GetAncestor(handle, GA_ROOT)


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
