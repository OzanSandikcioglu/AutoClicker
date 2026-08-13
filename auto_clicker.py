"""
AutoClicker - Universal Auto Click Tool
Hotkey: F6 to Start/Stop
Supports: 6 languages, Dark/Light mode
"""

import threading
import time
import sys
import os
import tkinter as tk
import ctypes
from pynput.keyboard import Key, Listener as KeyboardListener

# --- Keyboard key name helper ----------------------------------------------
def get_key_name(key):
    try:
        if isinstance(key, Key):
            name = key.name
            return name.replace('_', ' ').title()
        elif hasattr(key, 'char') and key.char is not None:
            return key.char.upper()
        elif hasattr(key, 'vk') and key.vk is not None:
            vk = key.vk
            if 112 <= vk <= 123:
                return f"F{vk - 111}"
            return f"Key {vk}"
    except:
        pass
    return str(key)

# --- Ctypes DirectInput mouse control structures ---------------------------

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
    for _ in range(count):
        win32_press_mouse(btn_str)
        time.sleep(0.02)  # 20ms hold down duration so games catch the frame
        win32_release_mouse(btn_str)
        if count > 1:
            time.sleep(0.02)

# --- Color Themes -----------------------------------------------------------
THEMES = {
    "dark": {
        "bg_main":       "#0c0e14",
        "bg_card":       "#161a26",
        "bg_card_alt":   "#1c2133",
        "bg_input":      "#232840",
        "accent":        "#6c5ce7",
        "accent_hover":  "#8577ed",
        "accent2":       "#00cec9",
        "accent_gold":   "#fdcb6e",
        "green":         "#00e676",
        "red":           "#ff5252",
        "text_primary":  "#edf0f7",
        "text_secondary":"#6b7394",
        "text_label":    "#9ba3c2",
        "border":        "#2d3352",
        "btn_bg":        "#6c5ce7",
        "btn_hover":     "#8577ed",
        "btn_active":    "#00cec9",
        "btn_active_hov":"#00e0db",
    },
    "light": {
        "bg_main":       "#f0f2f8",
        "bg_card":       "#ffffff",
        "bg_card_alt":   "#f7f8fc",
        "bg_input":      "#eef0f7",
        "accent":        "#6c5ce7",
        "accent_hover":  "#5a4bd6",
        "accent2":       "#00b894",
        "accent_gold":   "#e17055",
        "green":         "#00b894",
        "red":           "#d63031",
        "text_primary":  "#1e2132",
        "text_secondary":"#8892b0",
        "text_label":    "#636e95",
        "border":        "#dde1ed",
        "btn_bg":        "#6c5ce7",
        "btn_hover":     "#5a4bd6",
        "btn_active":    "#00b894",
        "btn_active_hov":"#00a884",
    },
}

# --- Translations ------------------------------------------------------------
TRANSLATIONS = {
    "EN": {
        "name": "English", "subtitle": "Auto Click Tool",
        "interval_title": "Click Interval", "hours": "Hours", "minutes": "Min",
        "seconds": "Sec", "milliseconds": "ms",
        "settings_title": "Click Settings", "click_type": "Click Type:",
        "single": "Single", "double": "Double", "hold": "Hold",
        "mouse_btn": "Mouse Btn:", "left": "Left", "right": "Right", "mid": "Middle",
        "hotkey": "Hotkey:", "start": "START", "stop": "STOP",
        "stopped": "Stopped", "running": "Running...", "holding": "Holding...",
        "clicks": "Clicks:", "lang": "Lang", "theme": "Theme",
    },
    "TR": {
        "name": "Türkçe", "subtitle": "Otomatik Tıklama Aracı",
        "interval_title": "Tık Aralığı", "hours": "Saat", "minutes": "Dak",
        "seconds": "San", "milliseconds": "ms",
        "settings_title": "Tık Ayarları", "click_type": "Tık Türü:",
        "single": "Tek", "double": "Çift", "hold": "Basılı",
        "mouse_btn": "Fare Btn:", "left": "Sol", "right": "Sağ", "mid": "Orta",
        "hotkey": "Kısayol:", "start": "BAŞLAT", "stop": "DURDUR",
        "stopped": "Durduruldu", "running": "Çalışıyor...", "holding": "Basılı Tutuluyor...",
        "clicks": "Tıklama:", "lang": "Dil", "theme": "Tema",
    },
    "DE": {
        "name": "Deutsch", "subtitle": "Automatisches Klick-Werkzeug",
        "interval_title": "Klickintervall", "hours": "Std", "minutes": "Min",
        "seconds": "Sek", "milliseconds": "ms",
        "settings_title": "Klick-Einstellungen", "click_type": "Klicktyp:",
        "single": "Einzel", "double": "Doppel", "hold": "Halten",
        "mouse_btn": "Maustaste:", "left": "Links", "right": "Rechts", "mid": "Mitte",
        "hotkey": "Taste:", "start": "STARTEN", "stop": "STOPPEN",
        "stopped": "Gestoppt", "running": "Lauft...", "holding": "Gehalten...",
        "clicks": "Klicks:", "lang": "Sprache", "theme": "Thema",
    },
    "ES": {
        "name": "Espanol", "subtitle": "Herramienta de Clic Automatico",
        "interval_title": "Intervalo de Clic", "hours": "Horas", "minutes": "Min",
        "seconds": "Seg", "milliseconds": "ms",
        "settings_title": "Ajustes de Clic", "click_type": "Tipo:",
        "single": "Simple", "double": "Doble", "hold": "Mantener",
        "mouse_btn": "Boton:", "left": "Izq", "right": "Der", "mid": "Med",
        "hotkey": "Tecla:", "start": "INICIAR", "stop": "DETENER",
        "stopped": "Detenido", "running": "Ejecutando...", "holding": "Manteniendo...",
        "clicks": "Clics:", "lang": "Idioma", "theme": "Tema",
    },
    "FR": {
        "name": "Francais", "subtitle": "Outil de Clic Automatique",
        "interval_title": "Intervalle de Clic", "hours": "Heures", "minutes": "Min",
        "seconds": "Sec", "milliseconds": "ms",
        "settings_title": "Parametres de Clic", "click_type": "Type:",
        "single": "Simple", "double": "Double", "hold": "Maintenir",
        "mouse_btn": "Bouton:", "left": "Gauche", "right": "Droit", "mid": "Milieu",
        "hotkey": "Raccourci:", "start": "DEMARRER", "stop": "ARRETER",
        "stopped": "Arrete", "running": "En cours...", "holding": "Maintenu...",
        "clicks": "Clics:", "lang": "Langue", "theme": "Theme",
    },
    "ZH": {
        "name": "Zhongwen", "subtitle": "Zi Dong Dian Ji Gong Ju",
        "interval_title": "Dian Ji Jian Ge", "hours": "Shi", "minutes": "Fen",
        "seconds": "Miao", "milliseconds": "ms",
        "settings_title": "Dian Ji She Zhi", "click_type": "Lei Xing:",
        "single": "Dan Ji", "double": "Shuang Ji", "hold": "An Zhu",
        "mouse_btn": "An Niu:", "left": "Zuo", "right": "You", "mid": "Zhong",
        "hotkey": "Kuai Jie:", "start": "KAI SHI", "stop": "TING ZHI",
        "stopped": "Yi Ting Zhi", "running": "Yun Xing Zhong...", "holding": "An Zhu Zhong...",
        "clicks": "Dian Ji:", "lang": "Yu Yan", "theme": "Zhu Ti",
    },
}

CLICK_KEYS = ["single", "double", "hold"]
MBTN_KEYS = ["left", "right", "mid"]
LANG_ORDER = ["EN", "TR", "DE", "ES", "FR", "ZH"]


class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")
        self.root.geometry("440x680")
        self.root.resizable(False, False)

        # -- State --
        self.lang = "EN"
        self.theme = "dark"
        self.clicking = False
        self.click_count = 0
        self.click_thread = None
        self.holding = False

        # -- Variables --
        self.v_hours = tk.StringVar(value="0")
        self.v_min = tk.StringVar(value="0")
        self.v_sec = tk.StringVar(value="0")
        self.v_ms = tk.StringVar(value="100")
        self.v_click_type = tk.StringVar(value="single")
        self.v_mbtn = tk.StringVar(value="left")
        
        # -- Hotkey binding state --
        self.v_hotkey_str = "F6"
        self.binding_hotkey = False

        # -- Widget refs --
        self.w = {}

        # -- Icon --
        try:
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(p):
                self.root.iconbitmap(p)
        except Exception:
            pass

        # -- Build UI --
        self._build()
        self._apply_theme()

        # -- Keyboard listener --
        self.kb = KeyboardListener(on_press=self._on_key)
        self.kb.daemon = True
        self.kb.start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def _c(self, key):
        return THEMES[self.theme].get(key, "#ffffff")

    # =========================================================================
    #  BUILD UI
    # =========================================================================

    def _build(self):
        self.root.configure(bg=self._c("bg_main"))

        # -- Top accent line (plain color, no emoji) --
        self.w["top_line"] = tk.Frame(self.root, height=3)
        self.w["top_line"].pack(fill="x")

        # -- Main container --
        self.w["main"] = tk.Frame(self.root, padx=22, pady=14)
        self.w["main"].pack(fill="both", expand=True)

        self._build_header()
        self._build_toolbar()
        self._build_interval()
        self._build_settings()
        self._build_button()
        self._build_status()

    # --- Header --------------------------------------------------------------

    def _build_header(self):
        p = self.w["main"]
        hdr = tk.Frame(p)
        hdr.pack(fill="x", pady=(0, 8))
        self.w["hdr"] = hdr

        # Logo circle (drawn with canvas, no emoji)
        self.w["logo"] = tk.Canvas(hdr, width=44, height=44, highlightthickness=0)
        self.w["logo"].pack(side="left", padx=(0, 12))

        # Title
        tcol = tk.Frame(hdr)
        tcol.pack(side="left")
        self.w["hdr_tcol"] = tcol

        trow = tk.Frame(tcol)
        trow.pack(anchor="w")
        self.w["hdr_trow"] = trow

        self.w["t1"] = tk.Label(trow, text="Auto", font=("Segoe UI", 22, "bold"))
        self.w["t1"].pack(side="left")

        self.w["t2"] = tk.Label(trow, text="Clicker", font=("Segoe UI", 22, "bold"))
        self.w["t2"].pack(side="left")

        self.w["sub"] = tk.Label(tcol, text=self._t("subtitle"), font=("Segoe UI", 9))
        self.w["sub"].pack(anchor="w", pady=(1, 0))

    def _draw_logo(self):
        c = self.w["logo"]
        c.delete("all")
        bg = self._c("bg_main")
        c.configure(bg=bg)
        c.create_oval(2, 2, 42, 42, fill=self._c("bg_card"), outline=self._c("accent"), width=2)
        # Lightning bolt drawn as polygon (no emoji)
        c.create_polygon(
            24, 8, 16, 24, 21, 24, 18, 36, 28, 20, 23, 20, 26, 8,
            fill=self._c("accent_gold"), outline=""
        )

    # --- Toolbar (Lang + Theme) -----------------------------------------------

    def _build_toolbar(self):
        p = self.w["main"]
        bar = tk.Frame(p)
        bar.pack(fill="x", pady=(0, 4))
        self.w["toolbar"] = bar

        # Language buttons
        lf = tk.Frame(bar)
        lf.pack(side="left")
        self.w["lf"] = lf

        self.w["lang_lbl"] = tk.Label(lf, text=self._t("lang"), font=("Segoe UI", 8))
        self.w["lang_lbl"].pack(side="left", padx=(0, 6))

        self.lang_btns = {}
        for code in LANG_ORDER:
            active = code == self.lang
            btn = tk.Label(
                lf, text=code, font=("Segoe UI", 8, "bold"),
                padx=6, pady=2, cursor="hand2"
            )
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, c=code: self._set_lang(c))
            btn.bind("<Enter>", lambda e, b=btn, c=code: self._lang_hover(b, c, True))
            btn.bind("<Leave>", lambda e, b=btn, c=code: self._lang_hover(b, c, False))
            self.lang_btns[code] = btn

        # Theme toggle
        tf = tk.Frame(bar)
        tf.pack(side="right")
        self.w["tf"] = tf

        self.w["theme_lbl"] = tk.Label(tf, text=self._t("theme"), font=("Segoe UI", 8))
        self.w["theme_lbl"].pack(side="left", padx=(0, 6))

        self.w["toggle"] = tk.Canvas(tf, width=48, height=24, highlightthickness=0, cursor="hand2")
        self.w["toggle"].pack(side="left")
        self.w["toggle"].bind("<Button-1>", lambda e: self._toggle_theme())

        # Dark/Light text label (no emoji)
        self.w["mode_txt"] = tk.Label(tf, text="Dark", font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.w["mode_txt"].pack(side="left", padx=(4, 0))
        self.w["mode_txt"].bind("<Button-1>", lambda e: self._toggle_theme())

        # Separator
        self.w["sep"] = tk.Frame(p, height=1)
        self.w["sep"].pack(fill="x", pady=(4, 8))

    def _lang_hover(self, btn, code, entering):
        if entering and code != self.lang:
            btn.configure(bg=self._c("accent_hover"), fg="#ffffff")
        else:
            self._style_lang_btn(btn, code)

    def _style_lang_btn(self, btn, code):
        if code == self.lang:
            btn.configure(bg=self._c("accent"), fg="#ffffff")
        else:
            btn.configure(bg=self._c("bg_input"), fg=self._c("text_secondary"))

    def _draw_toggle(self):
        c = self.w["toggle"]
        c.delete("all")
        bg = self._c("bg_main")
        c.configure(bg=bg)

        is_dark = self.theme == "dark"
        pill = self._c("accent") if is_dark else self._c("border")
        knob_clr = "#edf0f7" if is_dark else "#ffffff"

        # Pill shape
        c.create_oval(0, 0, 24, 24, fill=pill, outline="")
        c.create_oval(24, 0, 48, 24, fill=pill, outline="")
        c.create_rectangle(12, 0, 36, 24, fill=pill, outline="")

        # Knob
        kx = 32 if is_dark else 16
        c.create_oval(kx - 9, 3, kx + 9, 21, fill=knob_clr, outline="")

        self.w["mode_txt"].configure(text="Dark" if is_dark else "Light")

    # --- Interval Card --------------------------------------------------------

    def _build_interval(self):
        p = self.w["main"]
        outer = tk.Frame(p, padx=1, pady=1)
        outer.pack(fill="x", pady=(0, 8))
        self.w["int_outer"] = outer

        card = tk.Frame(outer, padx=14, pady=10)
        card.pack(fill="both")
        self.w["int_card"] = card

        # Title row
        tr = tk.Frame(card)
        tr.pack(fill="x", pady=(0, 8))
        self.w["int_tr"] = tr

        self.w["int_dot"] = tk.Canvas(tr, width=8, height=8, highlightthickness=0)
        self.w["int_dot"].pack(side="left", padx=(0, 8), pady=4)

        self.w["int_title"] = tk.Label(tr, text=self._t("interval_title"),
                                        font=("Segoe UI", 10, "bold"))
        self.w["int_title"].pack(side="left")

        # Inputs row
        irow = tk.Frame(card)
        irow.pack(fill="x")
        self.w["int_irow"] = irow

        for key, var in [("hours", self.v_hours), ("minutes", self.v_min),
                         ("seconds", self.v_sec), ("milliseconds", self.v_ms)]:
            f = tk.Frame(irow)
            f.pack(side="left", expand=True, fill="x", padx=3)

            eb = tk.Frame(f, padx=1, pady=1)
            eb.pack(side="top", pady=(0, 2))
            self.w[f"eb_{key}"] = eb

            e = tk.Entry(eb, textvariable=var, width=5, font=("Consolas", 12, "bold"),
                         relief="flat", justify="center", highlightthickness=0)
            e.pack(ipady=3)
            e.bind("<FocusIn>", lambda ev, b=eb: b.configure(bg=self._c("accent")))
            e.bind("<FocusOut>", lambda ev, b=eb: b.configure(bg=self._c("border")))
            self.w[f"e_{key}"] = e

            l = tk.Label(f, text=self._t(key), font=("Segoe UI", 7))
            l.pack(side="top")
            self.w[f"l_{key}"] = l

    # --- Settings Card --------------------------------------------------------

    def _build_settings(self):
        p = self.w["main"]
        outer = tk.Frame(p, padx=1, pady=1)
        outer.pack(fill="x", pady=(0, 8))
        self.w["set_outer"] = outer

        card = tk.Frame(outer, padx=14, pady=10)
        card.pack(fill="both")
        self.w["set_card"] = card

        # Title row
        tr = tk.Frame(card)
        tr.pack(fill="x", pady=(0, 8))
        self.w["set_tr"] = tr

        self.w["set_dot"] = tk.Canvas(tr, width=8, height=8, highlightthickness=0)
        self.w["set_dot"].pack(side="left", padx=(0, 8), pady=4)

        self.w["set_title"] = tk.Label(tr, text=self._t("settings_title"),
                                        font=("Segoe UI", 10, "bold"))
        self.w["set_title"].pack(side="left")

        # Click type
        r1 = tk.Frame(card)
        r1.pack(fill="x", pady=(0, 6))
        self.w["r1"] = r1

        self.w["ct_lbl"] = tk.Label(r1, text=self._t("click_type"),
                                     font=("Segoe UI", 9), width=10, anchor="w")
        self.w["ct_lbl"].pack(side="left")

        self.ct_rbs = []
        for key in CLICK_KEYS:
            rb = tk.Radiobutton(r1, text=self._t(key), variable=self.v_click_type,
                                value=key, font=("Segoe UI", 9), highlightthickness=0)
            rb.pack(side="left", padx=(4, 0))
            self.ct_rbs.append((rb, key))

        # Mouse button
        r2 = tk.Frame(card)
        r2.pack(fill="x", pady=(0, 6))
        self.w["r2"] = r2

        self.w["mb_lbl"] = tk.Label(r2, text=self._t("mouse_btn"),
                                     font=("Segoe UI", 9), width=10, anchor="w")
        self.w["mb_lbl"].pack(side="left")

        self.mb_rbs = []
        for key in MBTN_KEYS:
            rb = tk.Radiobutton(r2, text=self._t(key), variable=self.v_mbtn,
                                value=key, font=("Segoe UI", 9), highlightthickness=0)
            rb.pack(side="left", padx=(4, 0))
            self.mb_rbs.append((rb, key))

        # Hotkey
        r3 = tk.Frame(card)
        r3.pack(fill="x")
        self.w["r3"] = r3

        self.w["hk_lbl"] = tk.Label(r3, text=self._t("hotkey"),
                                     font=("Segoe UI", 9), width=10, anchor="w")
        self.w["hk_lbl"].pack(side="left")

        # Hotkey Bind Button
        self.w["hk_btn"] = tk.Button(r3, text=self.v_hotkey_str, font=("Consolas", 9, "bold"),
                                     relief="flat", width=12, cursor="hand2", command=self._start_binding)
        self.w["hk_btn"].pack(side="left", padx=(4, 0))

    # --- Toggle Button --------------------------------------------------------

    def _build_button(self):
        p = self.w["main"]
        bf = tk.Frame(p)
        bf.pack(fill="x", pady=(4, 8))
        self.w["bf"] = bf

        self.w["btn"] = tk.Canvas(bf, width=396, height=52, highlightthickness=0, cursor="hand2")
        self.w["btn"].pack()
        self.w["btn"].bind("<Button-1>", lambda e: self._toggle())
        self.w["btn"].bind("<Enter>", lambda e: self._draw_btn(hover=True))
        self.w["btn"].bind("<Leave>", lambda e: self._draw_btn(hover=False))

    def _draw_btn(self, hover=False):
        c = self.w["btn"]
        c.delete("all")
        c.configure(bg=self._c("bg_main"))

        if self.clicking:
            clr = self._c("btn_active_hov") if hover else self._c("btn_active")
        else:
            clr = self._c("btn_hover") if hover else self._c("btn_bg")

        # Glow (dark only)
        if self.theme == "dark":
            r0, g0, b0 = int(clr[1:3], 16), int(clr[3:5], 16), int(clr[5:7], 16)
            br, bg_, bb = int(self._c("bg_main")[1:3], 16), int(self._c("bg_main")[3:5], 16), int(self._c("bg_main")[5:7], 16)
            for i in range(3):
                a = 0.12 - i * 0.03
                gc = f"#{min(int(r0*a+br*(1-a)),255):02x}{min(int(g0*a+bg_*(1-a)),255):02x}{min(int(b0*a+bb*(1-a)),255):02x}"
                o = 3 - i
                self._pill(c, o, o, 396 - o, 52 - o, 14, gc)

        self._pill(c, 3, 3, 393, 49, 12, clr)

        hk = self.v_hotkey_str
        sym = "||" if self.clicking else ">"
        word = self._t("stop") if self.clicking else self._t("start")
        c.create_text(198, 26, text=f"{sym}  {word}  ({hk})",
                       font=("Segoe UI", 13, "bold"), fill="#ffffff")

    def _pill(self, canvas, x1, y1, x2, y2, r, color):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
               x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        canvas.create_polygon(pts, smooth=True, fill=color, outline="")

    # --- Status Bar -----------------------------------------------------------

    def _build_status(self):
        p = self.w["main"]
        outer = tk.Frame(p, padx=1, pady=1)
        outer.pack(fill="x")
        self.w["st_outer"] = outer

        inner = tk.Frame(outer, padx=14, pady=8)
        inner.pack(fill="both")
        self.w["st_inner"] = inner

        left = tk.Frame(inner)
        left.pack(side="left")
        self.w["st_left"] = left

        self.w["st_dot"] = tk.Canvas(left, width=12, height=12, highlightthickness=0)
        self.w["st_dot"].pack(side="left", padx=(0, 8))

        self.w["st_lbl"] = tk.Label(left, text=self._t("stopped"),
                                     font=("Segoe UI", 9, "bold"))
        self.w["st_lbl"].pack(side="left")

        right = tk.Frame(inner)
        right.pack(side="right")
        self.w["st_right"] = right

        self.w["cnt_lbl"] = tk.Label(right, text=self._t("clicks"), font=("Segoe UI", 9))
        self.w["cnt_lbl"].pack(side="left")

        self.w["cnt_val"] = tk.Label(right, text="0", font=("Consolas", 13, "bold"))
        self.w["cnt_val"].pack(side="left", padx=(4, 0))

    def _draw_st_dot(self):
        d = self.w["st_dot"]
        d.delete("all")
        d.configure(bg=self._c("bg_card"))
        clr = self._c("green") if self.clicking else self._c("red")
        d.create_oval(1, 1, 11, 11, fill=clr, outline="")

    # =========================================================================
    #  THEME SYSTEM
    # =========================================================================

    def _apply_theme(self):
        bg = self._c("bg_main")
        card = self._c("bg_card")
        inp = self._c("bg_input")
        t1 = self._c("text_primary")
        t2 = self._c("text_secondary")
        tl = self._c("text_label")
        brd = self._c("border")
        acc = self._c("accent")

        self.root.configure(bg=bg)
        self.w["top_line"].configure(bg=acc)
        self.w["main"].configure(bg=bg)

        # Header
        for k in ["hdr", "hdr_tcol", "hdr_trow"]:
            self.w[k].configure(bg=bg)
        self.w["t1"].configure(bg=bg, fg=t1)
        self.w["t2"].configure(bg=bg, fg=acc)
        self.w["sub"].configure(bg=bg, fg=t2)
        self._draw_logo()

        # Toolbar
        for k in ["toolbar", "lf", "tf"]:
            self.w[k].configure(bg=bg)
        self.w["lang_lbl"].configure(bg=bg, fg=t2)
        self.w["theme_lbl"].configure(bg=bg, fg=t2)
        self.w["mode_txt"].configure(bg=bg, fg=t2)

        for code, btn in self.lang_btns.items():
            self._style_lang_btn(btn, code)

        self._draw_toggle()
        self.w["sep"].configure(bg=brd)

        # Interval card
        self.w["int_outer"].configure(bg=brd)
        for k in ["int_card", "int_tr", "int_irow"]:
            self.w[k].configure(bg=card)
        self.w["int_title"].configure(bg=card, fg=acc)
        dot = self.w["int_dot"]
        dot.configure(bg=card)
        dot.delete("all")
        dot.create_oval(1, 1, 7, 7, fill=acc, outline="")

        for key in ["hours", "minutes", "seconds", "milliseconds"]:
            self.w[f"eb_{key}"].configure(bg=brd)
            self.w[f"e_{key}"].configure(bg=inp, fg=acc, insertbackground=acc)
            self.w[f"l_{key}"].configure(bg=card, fg=t2)
            self.w[f"e_{key}"].master.master.configure(bg=card)

        # Settings card
        self.w["set_outer"].configure(bg=brd)
        for k in ["set_card", "set_tr", "r1", "r2", "r3"]:
            self.w[k].configure(bg=card)
        self.w["set_title"].configure(bg=card, fg=acc)
        dot2 = self.w["set_dot"]
        dot2.configure(bg=card)
        dot2.delete("all")
        dot2.create_oval(1, 1, 7, 7, fill=self._c("accent2"), outline="")

        self.w["ct_lbl"].configure(bg=card, fg=tl)
        self.w["mb_lbl"].configure(bg=card, fg=tl)
        self.w["hk_lbl"].configure(bg=card, fg=tl)

        for rb, _ in self.ct_rbs + self.mb_rbs:
            rb.configure(bg=card, fg=t1, selectcolor=inp,
                         activebackground=card, activeforeground=acc)

        self.w["hk_btn"].configure(bg=inp, fg=self._c("accent_gold"),
                                   activebackground=acc, activeforeground="#ffffff")

        # Button
        self.w["bf"].configure(bg=bg)
        self._draw_btn()

        # Status
        self.w["st_outer"].configure(bg=brd)
        for k in ["st_inner", "st_left", "st_right"]:
            self.w[k].configure(bg=card)
        self._draw_st_dot()
        self.w["st_lbl"].configure(bg=card,
                                    fg=self._c("green") if self.clicking else t2)
        self.w["cnt_lbl"].configure(bg=card, fg=t2)
        self.w["cnt_val"].configure(bg=card, fg=self._c("accent_gold"))

    # =========================================================================
    #  LANGUAGE & THEME SWITCHING
    # =========================================================================

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme()

    def _set_lang(self, code):
        if code == self.lang:
            return
        self.lang = code

        for c, btn in self.lang_btns.items():
            self._style_lang_btn(btn, c)

        self.w["sub"].config(text=self._t("subtitle"))
        self.w["lang_lbl"].config(text=self._t("lang"))
        self.w["theme_lbl"].config(text=self._t("theme"))
        self.w["int_title"].config(text=self._t("interval_title"))
        self.w["set_title"].config(text=self._t("settings_title"))

        for key in ["hours", "minutes", "seconds", "milliseconds"]:
            self.w[f"l_{key}"].config(text=self._t(key))

        self.w["ct_lbl"].config(text=self._t("click_type"))
        self.w["mb_lbl"].config(text=self._t("mouse_btn"))
        self.w["hk_lbl"].config(text=self._t("hotkey"))

        for rb, key in self.ct_rbs:
            rb.config(text=self._t(key))
        for rb, key in self.mb_rbs:
            rb.config(text=self._t(key))

        self._draw_btn()

        if self.clicking:
            sk = "holding" if self.holding else "running"
            self.w["st_lbl"].config(text=self._t(sk))
        else:
            self.w["st_lbl"].config(text=self._t("stopped"))

        self.w["cnt_lbl"].config(text=self._t("clicks"))

    # =========================================================================
    #  CLICK LOGIC
    # =========================================================================

    def _get_interval(self):
        try:
            h = int(self.v_hours.get() or 0)
            m = int(self.v_min.get() or 0)
            s = int(self.v_sec.get() or 0)
            ms = int(self.v_ms.get() or 0)
            return max(h * 3600 + m * 60 + s + ms / 1000.0, 0.001)
        except ValueError:
            return 0.1

    def _get_mbtn(self):
        return self.v_mbtn.get()

    def _click_loop(self):
        interval = self._get_interval()
        btn = self._get_mbtn()
        ct = self.v_click_type.get()

        if ct == "hold":
            self.holding = True
            self.click_count = 1
            self.root.after(0, self._update_count)
            self.root.after(0, lambda: self.w["st_lbl"].config(
                text=self._t("holding"), fg=self._c("accent_gold")))
            while self.clicking:
                win32_press_mouse(btn)
                time.sleep(0.025)  # Continuously reinforce hold down signal so the game engine registers it
            return

        dbl = ct == "double"
        while self.clicking:
            win32_click_mouse(btn, count=2 if dbl else 1)
            self.click_count += 1
            self.root.after(0, self._update_count)
            time.sleep(interval)

    def _update_count(self):
        self.w["cnt_val"].config(text=str(self.click_count))

    def _toggle(self):
        if self.clicking:
            self._stop()
        else:
            self._start()

    def _start(self):
        self.clicking = True
        self.click_count = 0
        self._draw_btn()
        self._draw_st_dot()
        self.w["st_lbl"].config(text=self._t("running"), fg=self._c("green"))
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()

    def _stop(self):
        self.clicking = False
        if self.holding:
            win32_release_mouse(self._get_mbtn())
            self.holding = False
        self._draw_btn()
        self._draw_st_dot()
        self.w["st_lbl"].config(text=self._t("stopped"), fg=self._c("text_secondary"))

    def _start_binding(self):
        if self.clicking:
            return
        self.binding_hotkey = True
        self.w["hk_btn"].configure(text="..." if self.lang != "TR" else "Tuşa basın...", fg=self._c("red"))

    def _update_hotkey_ui(self):
        self.w["hk_btn"].configure(text=self.v_hotkey_str, fg=self._c("accent_gold"))
        self._draw_btn()

    def _on_key(self, key):
        if self.binding_hotkey:
            name = get_key_name(key)
            if name:
                self.v_hotkey_str = name
                self.binding_hotkey = False
                self.root.after(0, self._update_hotkey_ui)
            return

        if get_key_name(key) == self.v_hotkey_str:
            self.root.after(0, self._toggle)

    def _on_close(self):
        self.clicking = False
        if self.holding:
            try: win32_release_mouse(self._get_mbtn())
            except: pass
        try: self.kb.stop()
        except: pass
        self.root.destroy()
        sys.exit(0)


# --- Entry Point --------------------------------------------------------------
# NOTE: Admin elevation (UAC) is now handled by the embedded Windows manifest
# via PyInstaller's --uac-admin flag. No need for runtime ShellExecuteW.

if __name__ == "__main__":
    root = tk.Tk()
    root.update_idletasks()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"440x680+{(sw-440)//2}+{(sh-680)//2}")
    app = AutoClicker(root)
    root.mainloop()
