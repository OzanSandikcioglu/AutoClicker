# ⚡ AutoClicker

A premium, lightweight, and universal Auto Clicker application built with Python and Tkinter. Featuring a modern responsive UI, custom hotkey binding, multiple languages, and DirectInput support for 3D/DirectX games.

> **Windows only.** The click engine is built on the Windows `SendInput` API, so the app does not run on macOS or Linux.

---

## ✨ Features

- **Universal DirectX/DirectInput Support:** Utilizes low-level Windows `SendInput` API with a custom frame-hold delay to work inside games (tested on *Trove* and other MMOs).
- **Custom Hotkey Binding:** Click the hotkey button and press any key to set your start/stop toggle (`Esc` cancels). Holding the key down toggles once instead of repeatedly, and a hotkey bound to an ordinary character will not fire while you are typing into the interval boxes.
- **Three Click Types:** Single, double, or hold down - with the left, right, or middle mouse button.
- **Hold Down Mode (Basılı Tut):** Continuously sends mouse down signals (reinforced every 25ms) so game engines register the hold. The button is always released when you stop or close the app, so it can never be left stuck down.
- **Precise Click Interval:** Set the interval in hours, minutes, seconds, and milliseconds (down to 1ms). The schedule is deadline based so it does not drift, and edits apply while it is still running.
- **Safe to Leave Running:** Clicks the app injects are ignored by its own window, so a cursor resting over the START button cannot switch the clicker off. Windows is asked to stay awake while clicking is active, and the status bar tells you if Windows refuses the injected input.
- **Runs as Administrator:** The executable carries a `requestedExecutionLevel="requireAdministrator"` manifest, so Windows raises the UAC prompt at launch and clicks are not blocked by security boundaries.
- **Multiple Languages:** Instant UI translation for **English**, **Türkçe**, **Deutsch**, **Español**, **Français**, and **中文**.
- **Dark/Light Mode:** Seamlessly switch between dark and light themes with a single toggle.

---

## 🎮 The Interface

| Control | What it does |
| :--- | :--- |
| **Click Interval** | Time between clicks, summed across the four boxes. `0 / 0 / 1 / 500` means one click every 1.5 seconds. Digits only; leaving every box empty falls back to 100ms. |
| **Click Type** | `Single` one click per interval, `Double` two rapid clicks per interval, `Hold` presses the button and keeps it down until you stop. |
| **Mouse Btn** | Which button is sent: left, right, or middle. |
| **Hotkey** | Global start/stop key, `F6` by default. Click the button, then press the key you want; `Esc` cancels the binding. It works even while another window (or a game) has focus. |
| **START / STOP** | Same toggle as the hotkey. The bar turns teal and the status dot turns green while clicking. |
| **Clicks** | How many clicks have been sent since the current run started. |
| **Lang / Theme** | Language buttons and the dark/light switch; both apply instantly. |

Clicks land wherever the mouse cursor happens to be - park the cursor on the target first, then start with the hotkey.

---

## 🚀 How to Use (Pre-compiled EXE)

1. Go to the **Releases** section of this repository.
2. Download the `AutoClicker` zip archive.
3. **Extract the whole folder.** `AutoClicker.exe` needs the `_internal` folder that sits next to it; copying the `.exe` out on its own will not start.
4. Run `AutoClicker.exe` and accept the Windows User Account Control (UAC) prompt - it is required to send clicks into games.
5. Set your interval, click type, and mouse button.
6. Move the cursor onto whatever you want clicked and press **F6** (or your own hotkey) to start. Press it again to stop.

---

## 🧩 Troubleshooting

**Windows Defender or my antivirus flags the download.**
Auto clickers inject synthetic input, which is exactly what input-stealing malware does, so heuristic scanners flag them as a matter of course. The build is deliberately shipped as an unpacked `--onedir` folder with embedded version information to reduce this, but a fresh executable with no download reputation can still be flagged. Build it yourself from source (below) if you would rather not trust the release binary.

**The status bar says "Blocked by Windows" and nothing gets clicked.**
Windows refuses injected input aimed at a window running at a higher integrity level than the sender. Run `AutoClicker.exe` as administrator (right click → *Run as administrator*), which the release build requests automatically. A locked screen or the UAC dialog itself will also swallow clicks.

**Clicks work on the desktop but not inside my game.**
Some games only read raw input, and competitive titles with anti-cheat deliberately reject injected input. Try `Hold` mode or a slower interval first; if the game uses kernel-level anti-cheat, no user-mode clicker will reach it.

**The hotkey does nothing while I am editing an interval box.**
That is intentional for hotkeys bound to an ordinary character or digit, so typing `5` into a box cannot start the clicker. Function keys such as `F6` are unaffected, and stopping is never blocked.

**Nothing happens when I double-click the `.exe`.**
The `_internal` folder must sit next to it - see step 3 above.

---

## 🛠️ Build from Source (For Developers)

### Prerequisites
Windows, and Python 3.10 or newer.

### 1. Clone and Install Dependencies
```bash
git clone https://github.com/OzanSandikcioglu/AutoClicker.git
cd AutoClicker
pip install -r requirements.txt
```

### 2. Run the App
```bash
python auto_clicker.py
```
Run from a terminal without administrator rights during development; you only need the elevated build to click into games.

### 3. Compile to EXE (PyInstaller)
Run the pre-configured build script:
```bash
build.bat
```
*Or manually compile using PyInstaller:*
```bash
pyinstaller --onedir --noconsole --uac-admin --version-file version_info.txt --name AutoClicker auto_clicker.py
```
The build lands in `dist/AutoClicker/`. Distribute that entire folder as a zip - `--onedir` keeps the Python runtime beside the executable instead of unpacking it at startup, which is both faster and far less likely to trip antivirus heuristics.

### Project Structure
```
auto_clicker.py        Entry point; creates the Tk root and the app
src/app.py             UI, theming, click worker, hotkey handling
src/mouse.py           SendInput click engine, injected-event tagging, timers
src/hotkey.py          pynput key -> stable key name resolution
src/themes.py          Dark and light colour palettes
src/translations.py    UI strings for the six supported languages
build.bat              One-shot PyInstaller build
version_info.txt       Windows version resource embedded into the EXE
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
