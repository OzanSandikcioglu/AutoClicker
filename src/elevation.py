"""
AutoClicker - Windows Elevation Helpers

Windows drops injected input aimed at a window whose process runs at a higher
integrity level than the sender, and it does so silently: SendInput still
reports success. That is why clicks land on the desktop but do nothing in some
games unless AutoClicker itself runs as administrator - so the app has to look
at its own token and say what it sees.
"""

import ctypes
import os
import subprocess
import sys
from ctypes import wintypes

advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32", use_last_error=True)

TOKEN_QUERY = 0x0008
TOKEN_ELEVATION_CLASS = 20          # TOKEN_INFORMATION_CLASS.TokenElevation
SW_SHOWNORMAL = 1
SE_ERR_THRESHOLD = 32               # ShellExecuteW returns >32 on success


class TOKEN_ELEVATION(ctypes.Structure):
    _fields_ = [("TokenIsElevated", wintypes.DWORD)]


kernel32.GetCurrentProcess.argtypes = ()
kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
kernel32.CloseHandle.restype = wintypes.BOOL

advapi32.OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD,
                                      ctypes.POINTER(wintypes.HANDLE))
advapi32.OpenProcessToken.restype = wintypes.BOOL
advapi32.GetTokenInformation.argtypes = (wintypes.HANDLE, ctypes.c_int,
                                         ctypes.c_void_p, wintypes.DWORD,
                                         ctypes.POINTER(wintypes.DWORD))
advapi32.GetTokenInformation.restype = wintypes.BOOL

shell32.ShellExecuteW.argtypes = (wintypes.HWND, wintypes.LPCWSTR,
                                  wintypes.LPCWSTR, wintypes.LPCWSTR,
                                  wintypes.LPCWSTR, ctypes.c_int)
shell32.ShellExecuteW.restype = ctypes.c_void_p


def is_elevated():
    """True when this process holds an elevated administrator token."""
    try:
        token = wintypes.HANDLE()
        if not advapi32.OpenProcessToken(kernel32.GetCurrentProcess(),
                                         TOKEN_QUERY, ctypes.byref(token)):
            return False
        try:
            info = TOKEN_ELEVATION()
            written = wintypes.DWORD()
            ok = advapi32.GetTokenInformation(token, TOKEN_ELEVATION_CLASS,
                                              ctypes.byref(info),
                                              ctypes.sizeof(info),
                                              ctypes.byref(written))
            return bool(ok and info.TokenIsElevated)
        finally:
            kernel32.CloseHandle(token)
    except Exception:
        return False


def relaunch_as_admin():
    """Start a fresh elevated copy of the app and report whether it launched.

    Only ever called because the user pressed the button. The release EXE gets
    its elevation from the embedded manifest instead - nothing here runs by
    itself at startup, which is what made antivirus heuristics unhappy before.
    """
    try:
        exe = sys.executable
        if getattr(sys, "frozen", False):
            params = subprocess.list2cmdline(sys.argv[1:])
        else:
            script = os.path.abspath(sys.argv[0])
            params = subprocess.list2cmdline([script] + sys.argv[1:])
        workdir = os.path.dirname(os.path.abspath(sys.argv[0])) or None
        rc = shell32.ShellExecuteW(None, "runas", exe, params or None,
                                   workdir, SW_SHOWNORMAL)
        return (rc or 0) > SE_ERR_THRESHOLD
    except Exception:
        return False
