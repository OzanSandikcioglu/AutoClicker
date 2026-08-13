# ⚡ AutoClicker

A premium, lightweight, and universal Auto Clicker application built with Python and Tkinter. Featuring a modern responsive UI, custom hotkey binding, multiple languages, and DirectInput support for 3D/DirectX games.

---

## ✨ Features

- **Universal DirectX/DirectInput Support:** Utilizes low-level Windows `SendInput` API with a custom frame-hold delay to work inside games (tested on *Trove* and other MMOs).
- **Custom Hotkey Binding:** Click and press any keyboard key to dynamically set your start/stop toggle hotkey.
- **Hold Down Mode (Basılı Tut):** Continuously sends mouse down signals (reinforced every 25ms) to hold down mouse buttons in-game.
- **Multiple Languages:** Instant UI translation support for **English**, **Türkçe**, **Deutsch**, **Español**, **Français**, and **中文**.
- **Dark/Light Mode:** Seamlessly switch between dark and light themes with a single toggle.
- **Automatic Administrator Relaunch:** Auto-requests elevated privileges (UAC prompt) to ensure game clicks are not blocked by Windows security.
- **Precise Click Interval:** Set click intervals in hours, minutes, seconds, and milliseconds (down to 1ms).

---

## 🚀 How to Use (Pre-compiled EXE)

1. Go to the **Releases** tab on the right side of this repository.
2. Download `AutoClicker.exe`.
3. Double-click the file to run. 
4. Accept the Windows User Account Control (UAC) prompt (required to send clicks to games).
5. Configure your settings, click the **Hotkey** button to bind your key, and press the key to start clicking!

---

## 🛠️ Build from Source (For Developers)

If you wish to modify the code or compile the executable yourself:

### Prerequisites
Make sure you have Python 3.10+ installed.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
python auto_clicker.py
```

### 3. Compile to EXE (PyInstaller)
Run the pre-configured build script:
```bash
build.bat
```
*Or manually compile using PyInstaller:*
```bash
pyinstaller --onedir --noconsole --uac-admin --version-file version_info.txt --name AutoClicker auto_clicker.py
```
The compiled executable will be located in the `dist/AutoClicker/` directory. Distribute the entire `AutoClicker` folder as a zip.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
