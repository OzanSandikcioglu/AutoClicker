"""
AutoClicker - Recording Overlay

While a recording is running the app window is behind whatever the user is
clicking, so the window itself cannot say that recording is on. The screen
can: a red frame around the whole desktop, which stays visible wherever they
are working.

The strips are click-through. Windows skips WS_EX_TRANSPARENT windows when it
decides what a click hit, so a click at the very edge of the screen still
reaches the window underneath - and still gets recorded.
"""

import ctypes
import tkinter as tk
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020     # click-through
WS_EX_NOACTIVATE = 0x08000000      # never takes focus from what is in front
WS_EX_TOOLWINDOW = 0x00000080      # stays out of the taskbar and alt-tab
OVERLAY_STYLES = (WS_EX_LAYERED | WS_EX_TRANSPARENT
                  | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)

SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN = 76, 77
SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 78, 79
GA_ROOT = 2

_set_long = getattr(user32, "SetWindowLongPtrW", None) or user32.SetWindowLongW
_get_long = getattr(user32, "GetWindowLongPtrW", None) or user32.GetWindowLongW
_set_long.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t)
_set_long.restype = ctypes.c_ssize_t
_get_long.argtypes = (wintypes.HWND, ctypes.c_int)
_get_long.restype = ctypes.c_ssize_t
user32.GetAncestor.argtypes = (wintypes.HWND, wintypes.UINT)
user32.GetAncestor.restype = wintypes.HWND


def virtual_screen():
    """Bounds covering every monitor, as (x, y, width, height)."""
    return (user32.GetSystemMetrics(SM_XVIRTUALSCREEN),
            user32.GetSystemMetrics(SM_YVIRTUALSCREEN),
            max(user32.GetSystemMetrics(SM_CXVIRTUALSCREEN), 1),
            max(user32.GetSystemMetrics(SM_CYVIRTUALSCREEN), 1))


class RecordingBorder:
    """A red frame around the screen, shown while a recording is running."""

    THICKNESS = 6
    COLOR = "#ff3b30"
    ALPHA = 0.85

    def __init__(self, root):
        self.root = root
        self._strips = []

    @property
    def visible(self):
        return bool(self._strips)

    def show(self):
        if self._strips:
            return
        x, y, w, h = virtual_screen()
        t = self.THICKNESS
        edges = ((w, t, x, y),                  # top
                 (w, t, x, y + h - t),          # bottom
                 (t, h, x, y),                  # left
                 (t, h, x + w - t, y))          # right
        for width, height, left, top in edges:
            try:
                self._strips.append(self._strip(width, height, left, top))
            except tk.TclError:
                self.hide()
                return

    def _strip(self, width, height, left, top):
        win = tk.Toplevel(self.root)
        win.withdraw()                     # styled before it is ever shown
        win.overrideredirect(True)
        win.configure(bg=self.COLOR)
        win.geometry(f"{width}x{height}+{left}+{top}")
        win.attributes("-topmost", True)
        win.attributes("-alpha", self.ALPHA)
        win.update_idletasks()

        handle = user32.GetAncestor(win.winfo_id(), GA_ROOT)
        _set_long(handle, GWL_EXSTYLE, _get_long(handle, GWL_EXSTYLE) | OVERLAY_STYLES)
        win.deiconify()
        return win

    def hide(self):
        strips, self._strips = self._strips, []
        for win in strips:
            try:
                win.destroy()
            except tk.TclError:
                pass
