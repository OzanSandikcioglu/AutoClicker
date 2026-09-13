# ⚡ AutoClicker

**🇹🇷 Türkçe: [README.tr.md](README.tr.md)**

A premium, lightweight, and universal Auto Clicker application built with Python and Tkinter. Featuring a modern responsive UI, custom hotkey binding, multiple languages, and DirectInput support for 3D/DirectX games.

> **Windows only.** The click engine is built on the Windows `SendInput` API, so the app does not run on macOS or Linux.

---

## ✨ Features

- **Universal DirectX/DirectInput Support:** Utilizes low-level Windows `SendInput` API with a custom frame-hold delay to work inside games (tested on *Trove* and other MMOs).
- **Custom Hotkey Binding:** Click the hotkey button and press any key - or a mouse side button - to set your start/stop toggle (`Esc` cancels). Holding the key down toggles once instead of repeatedly, and a hotkey bound to an ordinary character will not fire while you are typing into the interval boxes.
- **Mouse Buttons as Hotkeys:** The thumb buttons most gaming mice carry (`Mouse 4` / `Mouse 5`, and the wheel click as `Mouse 3`) can be bound just like a key, so the clicker can be toggled without leaving the mouse. Clicks the app injects itself are filtered out, while a macro button forwarded by mouse driver software still registers.
- **Pattern Mode:** Record a sequence of clicks - where each one lands, which button it used, and how long you paused before it - then replay that sequence until you stop it, or for a set length of time. A red frame around the screen shows while recording is on, since the window itself is usually behind whatever you are clicking.
- **Three Click Types:** Single, double, or hold down - with the left, right, or middle mouse button.
- **Hold Down Mode (Basılı Tut):** Continuously sends mouse down signals (reinforced every 25ms) so game engines register the hold. The button is always released when you stop or close the app, so it can never be left stuck down.
- **Precise Click Interval:** Set the interval in hours, minutes, seconds, and milliseconds (down to 1ms). The schedule is deadline based so it does not drift, and edits apply while it is still running.
- **Safe to Leave Running:** Clicks the app injects are ignored by its own window, so a cursor resting over the START button cannot switch the clicker off. Windows is also asked to stay awake for as long as clicking is active.
- **Administrator Aware:** Windows silently discards injected clicks aimed at a window that runs at a higher integrity level - `SendInput` still reports success, so a clicker with no warning just looks broken. The app checks its own token at startup and says whether it is elevated, with a one-click elevated restart when it is not. The release EXE carries a `requestedExecutionLevel="requireAdministrator"` manifest, so it asks for the UAC prompt by itself.
- **Multiple Languages:** Instant UI translation for **English**, **Türkçe**, **Deutsch**, **Español**, **Français**, and **中文**.
- **Dark/Light Mode:** Seamlessly switch between dark and light themes with a single toggle.

---

## 🎮 The Interface

| Control | What it does |
| :--- | :--- |
| **Click Interval** | Time between clicks, summed across the four boxes. `0 / 0 / 1 / 500` means one click every 1.5 seconds. Digits only; leaving every box empty falls back to 100ms. |
| **Click Type** | `Single` one click per interval, `Double` two rapid clicks per interval, `Hold` presses the button and keeps it down until you stop. |
| **Mouse Btn** | Which button is sent: left, right, or middle. |
| **Start** | Global start/stop key for whichever mode is showing, `F6` by default. Click the button, then press the key or mouse side button you want; `Esc` cancels the binding. It works even while another window (or a game) has focus. |
| **Rec** | Starts and ends a pattern recording, `F5` by default, and only shown in Pattern mode. Pressing it from the Clicker tab switches to Pattern and starts recording. One key cannot be bound to both jobs. |
| **START / STOP** | Same toggle as the hotkey. The bar turns teal and the status dot turns green while clicking. |
| **Clicks** | How many clicks have been sent since the current run started. |
| **Clicker / Pattern** | The two tabs under the toolbar. **Clicker** repeats one click where the pointer already is; **Pattern** replays a recorded sequence. Neither can be switched while something is running. |
| **Lang / Theme** | Language buttons and the dark/light switch; both apply instantly. |
| **Administrator** | Bottom strip. Green means the app is elevated and its clicks reach anything on screen. Amber means it is not, and the **Run as admin** button restarts it elevated. |

Clicks land wherever the mouse cursor happens to be - park the cursor on the target first, then start with the hotkey.

---

## 🔁 Pattern Mode

The **Pattern** tab records where you click instead of hammering one spot.

1. Switch to **Pattern** and press **Record** - or just press the **Rec key** (`F5`), which switches tabs and starts recording for you.
2. Click your way through whatever you want repeated, in order. Each click is stored with its position, its button, and the pause you left before it.
3. **Press the Rec key again** to finish. The window will have gone behind whatever you clicked, and the key saves you from hunting for it - pressing **Finish** on the window works too.
4. Pick **Until stopped** or a **For** duration, set the **Gap** between passes, and press START or your hotkey.

| Detail | Behaviour |
| :--- | :--- |
| Clicks on the AutoClicker window | Not recorded, so pressing **Finish** never becomes part of the pattern. |
| Clicks on the taskbar | Not recorded either. Going back to the window through the taskbar was the easiest way to get a click into the pattern that you never meant to record. |
| Knowing it is recording | A red frame runs around the screen for as long as a recording is on. It is click-through, so it never swallows a click at the edge, and it never takes focus from what you are working in. |
| A stray click | **Undo** removes the last step; **Clear** throws the whole pattern away. |
| Side buttons while recording | Ignored - the click engine can only send left, right and middle. |
| Your own timing | Kept. Replay waits exactly as long as you did between clicks, with a 10 second cap on any single pause. |
| Length | Up to 200 clicks per pattern. |
| Where the pointer ends up | On the last point it clicked. Playback moves the real cursor, so leave the mouse alone while it runs and stop it with the hotkey. |
| Saving | Patterns live in memory only. Closing the app forgets them. |

---

## 📥 Which download do I need?

GitHub offers two different downloads and they are not interchangeable:

| You want to... | Do this | What you actually get |
| :--- | :--- | :--- |
| **Just use the clicker** | Open [**Releases**](https://github.com/OzanSandikcioglu/AutoClicker/releases/latest) and download `AutoClicker-v1.6.0-win64.zip` | The ready-to-run app, about 12 MB. No Python, no building. |
| **Read or modify the code** | The green **Code** button → *Download ZIP*, or `git clone` | The source only, about 70 KB. It contains **no executable** - you would have to build one. |

> The green **Code** button at the top of the page is the one most people press first, and it is the wrong one if you only want to run the clicker: it hands you Python files, not an app.

---

## 🚀 How to Use (Pre-compiled EXE)

1. Open the [**Releases**](https://github.com/OzanSandikcioglu/AutoClicker/releases/latest) page.
2. Download `AutoClicker-v1.6.0-win64.zip` from the **Assets** list.
3. **Extract the whole folder.** `AutoClicker.exe` needs the `_internal` folder that sits next to it; copying the `.exe` out on its own will not start.
4. Run `AutoClicker.exe` and accept the Windows User Account Control (UAC) prompt - it is required to send clicks into games.
5. Set your interval, click type, and mouse button.
6. Move the cursor onto whatever you want clicked and press **F6** (or your own hotkey) to start. Press it again to stop.

<details>
<summary><b>Never done this before? Open this for the step-by-step version.</b></summary>

### 1. Download the file

Open the [Releases page](https://github.com/OzanSandikcioglu/AutoClicker/releases/latest). Near the bottom there is a list headed **Assets**. Click **`AutoClicker-v1.6.0-win64.zip`** in that list. It lands in your **Downloads** folder.

### 2. Unzip it - do not skip this

What you downloaded is a **zip file**: a compressed box with a lot of files inside it. You have to take them out first.

1. **Right-click** `AutoClicker-v1.6.0-win64.zip`.
2. Choose **Extract All...**
3. Press **Extract** in the window that opens.
4. A new window appears with a folder called **AutoClicker** in it.

> ⚠️ **This is where almost everyone goes wrong.** Double-clicking the zip and running `AutoClicker.exe` from inside it. Windows lets you, but **the app will not start**, because it cannot work without the `_internal` folder next to it. Extract first.

**Tip:** drag the **AutoClicker** folder onto your desktop so you can find it easily next time.

### 3. Open the app

Go into the **AutoClicker** folder and double-click **AutoClicker.exe**.

Up to two windows can appear. Both are normal:

**🔵 A blue window saying "Windows protected your PC"**

This means Windows has not seen the app before - not that it is harmful. Click the small **More info** text, then press the **Run anyway** button that appears.

**🛡️ A window asking "Do you want to allow this app to make changes to your device?"**

Say **Yes**. Without it the app still opens, but **its clicks will not work in some games**: Windows blocks unprivileged programs from sending clicks into them.

### 4. Set it up

- **Click Interval** - how long between clicks. Four boxes: Hours / Min / Sec / ms. Digits only. `100` in the ms box means ten clicks a second; for something slow, put `1` in the Sec box.
- **Click Type** - `Single` a normal click, `Double` a double click, `Hold` holds the button down (for mining, continuous fire, and so on).
- **Mouse Btn** - which button gets clicked: Left, Right or Middle.
- **Hotkey** - the start/stop key, **F6** to begin with. To change it, click the button and then press the key you want; a mouse side button works too. **Esc** cancels.

### 5. Run it

1. Move the mouse pointer over the thing you want clicked.
2. Press **F6** (or click the blue **START** bar).
3. Clicking starts and the counter at the bottom right goes up.
4. Press **F6** again to stop.

Clicks go wherever the pointer is sitting, so put the pointer in place first, then start.

### Removing it

Drag the **AutoClicker** folder to the recycle bin. That is all - the app installs nothing, writes nothing to the registry, and leaves no files anywhere else.

</details>

---

## 🧩 Troubleshooting

**Windows Defender or my antivirus flags the download.**
Auto clickers inject synthetic input, which is exactly what input-stealing malware does, so heuristic scanners flag them as a matter of course. The build is deliberately shipped as an unpacked `--onedir` folder with embedded version information to reduce this, but a fresh executable with no download reputation can still be flagged. Build it yourself from source (below) if you would rather not trust the release binary.

**I ran it once, then the file disappeared - after closing it or after a restart.**
The app did not delete itself: Windows Defender quarantined it. An unsigned executable whose whole job is injecting input is the exact shape its cloud protection ("block at first sight") and its potentially-unwanted-app filter act on, and that verdict often arrives *after* the first run or at the next scan - which is why the file seems to vanish on its own later. Open **Windows Security -> Protection history** to find the entry; if you trust the build you can restore it from there and add an exclusion.

Passing the file around through chat apps makes this much more likely, because the copy arrives stamped as internet-sourced with no download reputation behind it. Send people the [Releases](https://github.com/OzanSandikcioglu/AutoClicker/releases/latest) link instead of the file itself. Note that auto-clicker blocking is a policy call, not always a mistaken one: Windows 11 enables potentially-unwanted-app blocking by default, so a machine can remove it while yours keeps it happily.

**The status bar says "Blocked by Windows".**
`SendInput` itself was rejected, which happens while the UAC dialog or the lock screen owns the secure desktop. Dismiss it and start again. Note that this message cannot appear for the integrity-level case described below: Windows discards that input without reporting any failure, which is what the administrator strip is there to catch.

**Clicks work on the desktop but not inside my game.**
First check the strip at the bottom of the window. If it is amber, the app is not running as administrator, and Windows is dropping the clicks before the game ever sees them - press **Run as admin** and accept the UAC prompt. This is the usual cause. If the strip is already green, the game may only read raw input, and competitive titles with kernel-level anti-cheat deliberately reject injected input; no user-mode clicker reaches those.

**My mouse's macro button will not bind as a hotkey.**
Bindable buttons are the wheel click and the two thumb buttons - shown as `Mouse 3`, `Mouse 4` and `Mouse 5` - because those are the ones Windows reports as ordinary mouse buttons. Left and right are refused on purpose: binding one of them would mean every click in the interface toggles the clicker, including the clicks you would need to bind something else.

Buttons beyond those are usually handled entirely inside the mouse's own driver and never reach Windows as mouse input at all. The way around that is the mouse's configuration software (Logitech G HUB, Razer Synapse, and so on): map the button to a keyboard key - an unused function key such as `F9` works well - and then bind that key here. A button the driver forwards this way is injected input, and the app deliberately accepts it; only clicks it injected itself are ignored.

Note that a bound mouse button keeps doing its normal job as well. Binding `Mouse 5` does not stop it from being "forward" in your browser.

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
That installs `pynput`, which is the only thing needed to run the app. PyInstaller is only required to build the EXE, and `build.bat` installs it on its own.

### 2. Run the App
```bash
python auto_clicker.py
```
Running from source does not elevate on its own - the app will show the amber administrator strip. Either press **Run as admin**, or start the terminal as administrator, whenever you need clicks to land inside a game.

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
src/pattern.py         Recorded click sequences and their timing
src/elevation.py       Token elevation check and the user-initiated UAC restart
src/overlay.py         The click-through red frame shown while recording
src/themes.py          Dark and light colour palettes
src/translations.py    UI strings for the six supported languages
build.bat              One-shot PyInstaller build
version_info.txt       Windows version resource embedded into the EXE
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
