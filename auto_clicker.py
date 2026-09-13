"""
AutoClicker - Universal Auto Click Tool
Hotkey: F6 to Start/Stop
Supports: 6 languages, Dark/Light mode
"""

import tkinter as tk
from src.app import AutoClicker

# --- Entry Point --------------------------------------------------------------
# NOTE: Admin elevation (UAC) is now handled by the embedded Windows manifest
# via PyInstaller's --uac-admin flag. No need for runtime ShellExecuteW.

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)   # sizes and centres its own window
    root.mainloop()
