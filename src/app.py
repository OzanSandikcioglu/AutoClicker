"""
AutoClicker - Main Application
Premium Tkinter UI with DirectInput support for games.
"""

import threading
import queue
import time
import os
import tkinter as tk
from pynput.keyboard import Key, Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

from src.translations import TRANSLATIONS, CLICK_KEYS, MBTN_KEYS, LANG_ORDER
from src.themes import THEMES
from src.mouse import (HOLD_SECONDS, INJECT_TAG, begin_high_resolution_timer,
                       end_high_resolution_timer, is_injected_event, keep_awake,
                       is_shell_window, top_level_at, top_level_of, win32_click_mouse,
                       win32_move_mouse, win32_press_mouse, win32_release_mouse)
from src.hotkey import get_key_name, get_mouse_name, is_mouse_hotkey
from src.elevation import is_elevated, relaunch_as_admin
from src.pattern import PatternRecorder
from src.overlay import RecordingBorder


class AutoClicker:
    WIDTH, HEIGHT = 440, 772
    MIN_INTERVAL = 0.001      # fastest the interval boxes may ask for
    DEFAULT_INTERVAL = 0.1    # used when every box is empty or zero
    MOVE_SETTLE = 0.015       # let a window notice the pointer before clicking

    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")
        self.root.resizable(False, False)
        self._center_window()

        # -- State --
        self.lang = "EN"
        self.theme = "dark"
        self.clicking = False
        self.click_count = 0
        self.click_thread = None
        self.holding = False
        # Windows drops injected clicks aimed at higher integrity windows, and
        # says nothing about it - so tell the user where they stand up front.
        self.elevated = is_elevated()

        # -- Threading --
        # The click worker and the keyboard listener never touch Tk directly:
        # they push callables onto _ui_q, which _pump drains on the main thread.
        self._stop_evt = threading.Event()
        self._ui_q = queue.Queue()
        self._shown_count = -1
        self._input_blocked = False
        self._hotkey_held = False
        self._pump_id = None
        self.mouse_kb = None        # low level mouse hook, only while needed
        self.mode = "clicker"
        self.recorder = PatternRecorder()
        self.recording = False
        self.rec_border = RecordingBorder(self.root)
        self._root_hwnd = None
        self._cfg = {"interval": self.DEFAULT_INTERVAL,
                     "btn": "left", "type": "single"}

        # -- Variables --
        self.v_hours = tk.StringVar(value="0")
        self.v_min = tk.StringVar(value="0")
        self.v_sec = tk.StringVar(value="0")
        self.v_ms = tk.StringVar(value="100")
        self.v_click_type = tk.StringVar(value="single")
        self.v_mbtn = tk.StringVar(value="left")
        self.v_repeat = tk.StringVar(value="forever")
        self.v_dur_h = tk.StringVar(value="0")
        self.v_dur_m = tk.StringVar(value="5")
        self.v_dur_s = tk.StringVar(value="0")
        self.v_gap = tk.StringVar(value="500")
        
        # -- Hotkey binding state --
        self.v_hotkey_str = "F6"
        self.v_rec_hotkey_str = "F5"
        self.binding_target = None      # "main" or "record" while binding
        self._rec_held = False

        # -- Widget refs --
        self.w = {}

        # -- Icon --
        try:
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icon.ico")
            if os.path.exists(p):
                self.root.iconbitmap(p)
        except Exception:
            pass

        # -- Build UI --
        self._build()
        self._apply_theme()

        # -- Keyboard listener --
        self.kb = KeyboardListener(on_press=self._on_key,
                                   on_release=self._on_key_release)
        self.kb.daemon = True
        self.kb.start()

        self._sync_mouse_listener()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._pump()

    def _center_window(self):
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}"
                           f"+{max((sw - self.WIDTH) // 2, 0)}"
                           f"+{max((sh - self.HEIGHT) // 2, 0)}")

    def _t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def _c(self, key):
        return THEMES[self.theme].get(key, "#ffffff")

    # =========================================================================
    #  BUILD UI
    # =========================================================================

    def _build(self):
        self.root.configure(bg=self._c("bg_main"))
        self._vcmd = (self.root.register(self._validate_number), "%P")

        # -- Top accent line (plain color, no emoji) --
        self.w["top_line"] = tk.Frame(self.root, height=3)
        self.w["top_line"].pack(fill="x")

        # -- Main container --
        self.w["main"] = tk.Frame(self.root, padx=22, pady=14)
        self.w["main"].pack(fill="both", expand=True)

        self._build_header()
        self._build_toolbar()
        self._build_mode_tabs()
        self._build_interval()
        self._build_settings()
        self._build_pattern()
        self._build_repeat()
        self._build_hotkeys()
        self._build_button()
        self._build_status()
        self._build_admin()
        self._set_mode(self.mode)
        self._install_click_guard()

    # --- Self-click guard -----------------------------------------------------

    @staticmethod
    def _validate_number(proposed):
        """Keep the interval boxes numeric so the click loop always parses."""
        return proposed == "" or (proposed.isascii() and proposed.isdigit()
                                  and len(proposed) <= 6)

    def _install_click_guard(self):
        """Swallow the clicks we inject before any widget reacts to them.

        Otherwise a cursor left resting over our own window means the injected
        clicks press our own buttons - most visibly toggling the clicker off
        again the instant it starts.
        """
        for seq in ("<Button-1>", "<ButtonRelease-1>", "<Double-Button-1>",
                    "<Button-2>", "<ButtonRelease-2>",
                    "<Button-3>", "<ButtonRelease-3>"):
            self.root.bind_class("SelfClickGuard", seq, self._drop_injected)
        self._tag_widget(self.root)

    def _tag_widget(self, widget):
        tags = widget.bindtags()
        if "SelfClickGuard" not in tags:
            widget.bindtags(("SelfClickGuard",) + tags)
        for child in widget.winfo_children():
            self._tag_widget(child)

    @staticmethod
    def _drop_injected(event):
        if is_injected_event():
            return "break"

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
                         relief="flat", justify="center", highlightthickness=0,
                         validate="key", validatecommand=self._vcmd)
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

    # --- Hotkey row -----------------------------------------------------------

    def _build_hotkeys(self):
        """Both hotkeys live here rather than inside a mode card: they work in
        either mode, so they have to be reachable from either one."""
        p = self.w["main"]
        row = tk.Frame(p)
        row.pack(fill="x", pady=(0, 6))
        self.w["hk_row"] = row

        left = tk.Frame(row)
        left.pack(side="left")
        self.w["hk_left"] = left
        self.w["hk_lbl"] = tk.Label(left, text=self._t("hotkey"), font=("Segoe UI", 9))
        self.w["hk_lbl"].pack(side="left", padx=(0, 6))
        self.w["hk_btn"] = tk.Button(left, text=self.v_hotkey_str,
                                     font=("Consolas", 9, "bold"), relief="flat",
                                     width=11, cursor="hand2",
                                     command=lambda: self._start_binding("main"))
        self.w["hk_btn"].pack(side="left")

        # packed only in pattern mode, where recording exists
        right = tk.Frame(row)
        self.w["hk_right"] = right
        self.w["rec_hk_lbl"] = tk.Label(right, text=self._t("rec_hotkey"),
                                        font=("Segoe UI", 9))
        self.w["rec_hk_lbl"].pack(side="left", padx=(0, 6))
        self.w["rec_hk_btn"] = tk.Button(right, text=self.v_rec_hotkey_str,
                                         font=("Consolas", 9, "bold"), relief="flat",
                                         width=11, cursor="hand2",
                                         command=lambda: self._start_binding("record"))
        self.w["rec_hk_btn"].pack(side="left")

    # --- Mode tabs ------------------------------------------------------------

    MODE_CARDS = {"clicker": ("int_outer", "set_outer"),
                  "pattern": ("pat_outer", "rep_outer")}

    def _build_mode_tabs(self):
        p = self.w["main"]
        bar = tk.Frame(p)
        bar.pack(fill="x", pady=(0, 8))
        self.w["mode_bar"] = bar

        self.mode_btns = {}
        for key in ("clicker", "pattern"):
            btn = tk.Label(bar, text=self._t(f"mode_{key}"), font=("Segoe UI", 9, "bold"),
                           padx=16, pady=5, cursor="hand2")
            btn.pack(side="left", padx=(0, 4))
            btn.bind("<Button-1>", lambda e, k=key: self._set_mode(k))
            self.mode_btns[key] = btn

    def _style_mode_tabs(self):
        for key, btn in self.mode_btns.items():
            if key == self.mode:
                btn.configure(bg=self._c("accent"), fg="#ffffff")
            else:
                btn.configure(bg=self._c("bg_input"), fg=self._c("text_secondary"))

    def _set_mode(self, mode):
        """Swap which pair of cards is on screen. Not while something runs."""
        if self.clicking or self.recording:
            return
        self.mode = mode
        for keys in self.MODE_CARDS.values():
            for key in keys:
                self.w[key].pack_forget()
        for key in self.MODE_CARDS[mode]:
            self.w[key].pack(fill="x", pady=(0, 8), before=self.w["hk_row"])
        if mode == "pattern":
            self.w["hk_right"].pack(side="right")
        else:
            self.w["hk_right"].pack_forget()
        self._style_mode_tabs()
        self._fit_window()
        self._draw_btn()

    def _fit_window(self):
        """Height follows the mode. The pattern cards need noticeably more room
        than the clicker ones, and one fixed height leaves the other mode
        looking half empty - or clips this one."""
        try:
            self.root.update_idletasks()
            need = (self.w["main"].winfo_reqheight()
                    + self.w["top_line"].winfo_reqheight())
            self.root.geometry(f"{self.WIDTH}x{max(need, 400)}")
        except tk.TclError:
            pass

    # --- Pattern card ---------------------------------------------------------

    def _build_pattern(self):
        p = self.w["main"]
        outer = tk.Frame(p, padx=1, pady=1)
        self.w["pat_outer"] = outer

        card = tk.Frame(outer, padx=14, pady=10)
        card.pack(fill="both")
        self.w["pat_card"] = card

        tr = tk.Frame(card)
        tr.pack(fill="x", pady=(0, 8))
        self.w["pat_tr"] = tr

        self.w["pat_dot"] = tk.Canvas(tr, width=8, height=8, highlightthickness=0)
        self.w["pat_dot"].pack(side="left", padx=(0, 8), pady=4)
        self.w["pat_title"] = tk.Label(tr, text=self._t("pattern_title"),
                                       font=("Segoe UI", 10, "bold"))
        self.w["pat_title"].pack(side="left")
        self.w["pat_count"] = tk.Label(tr, text="", font=("Segoe UI", 8))
        self.w["pat_count"].pack(side="right")

        row = tk.Frame(card)
        row.pack(fill="x")
        self.w["pat_row"] = row

        self.w["rec_btn"] = tk.Button(row, text=self._t("record"),
                                      font=("Segoe UI", 9, "bold"), relief="flat",
                                      width=14, cursor="hand2",
                                      command=self._toggle_recording)
        self.w["rec_btn"].pack(side="left")
        self.w["clr_btn"] = tk.Button(row, text=self._t("clear"), font=("Segoe UI", 9),
                                      relief="flat", width=8, cursor="hand2",
                                      command=self._clear_pattern)
        self.w["clr_btn"].pack(side="right")
        self.w["undo_btn"] = tk.Button(row, text=self._t("undo"), font=("Segoe UI", 9),
                                       relief="flat", width=8, cursor="hand2",
                                       command=self._undo_step)
        self.w["undo_btn"].pack(side="right", padx=(0, 6))

        self.w["pat_hint"] = tk.Label(card, text=self._t("pattern_hint"),
                                      font=("Segoe UI", 8), anchor="w",
                                      justify="left", wraplength=356)
        self.w["pat_hint"].pack(fill="x", pady=(7, 7))

        self.w["pat_list"] = tk.Listbox(card, height=5, font=("Consolas", 8),
                                        relief="flat", highlightthickness=0,
                                        activestyle="none", borderwidth=0,
                                        selectmode="none")
        self.w["pat_list"].pack(fill="x")

    # --- Repeat card ----------------------------------------------------------

    def _build_repeat(self):
        p = self.w["main"]
        outer = tk.Frame(p, padx=1, pady=1)
        self.w["rep_outer"] = outer

        card = tk.Frame(outer, padx=14, pady=10)
        card.pack(fill="both")
        self.w["rep_card"] = card

        tr = tk.Frame(card)
        tr.pack(fill="x", pady=(0, 8))
        self.w["rep_tr"] = tr
        self.w["rep_dot"] = tk.Canvas(tr, width=8, height=8, highlightthickness=0)
        self.w["rep_dot"].pack(side="left", padx=(0, 8), pady=4)
        self.w["rep_title"] = tk.Label(tr, text=self._t("repeat_title"),
                                       font=("Segoe UI", 10, "bold"))
        self.w["rep_title"].pack(side="left")

        r1 = tk.Frame(card)
        r1.pack(fill="x")
        self.w["rep_r1"] = r1
        self.w["rb_forever"] = tk.Radiobutton(r1, text=self._t("repeat_forever"),
                                              variable=self.v_repeat, value="forever",
                                              font=("Segoe UI", 9), highlightthickness=0)
        self.w["rb_forever"].pack(side="left")

        r2 = tk.Frame(card)
        r2.pack(fill="x", pady=(4, 0))
        self.w["rep_r2"] = r2
        self.w["rb_duration"] = tk.Radiobutton(r2, text=self._t("repeat_duration"),
                                               variable=self.v_repeat, value="duration",
                                               font=("Segoe UI", 9), highlightthickness=0)
        self.w["rb_duration"].pack(side="left")
        for key, var in (("hours", self.v_dur_h), ("minutes", self.v_dur_m),
                         ("seconds", self.v_dur_s)):
            entry = tk.Entry(r2, textvariable=var, width=3, font=("Consolas", 9, "bold"),
                             relief="flat", justify="center", highlightthickness=0,
                             validate="key", validatecommand=self._vcmd)
            entry.pack(side="left", padx=(6, 2), ipady=2)
            self.w[f"dur_{key}"] = entry
            label = tk.Label(r2, text=self._t(key), font=("Segoe UI", 7))
            label.pack(side="left")
            self.w[f"durl_{key}"] = label

        r3 = tk.Frame(card)
        r3.pack(fill="x", pady=(8, 0))
        self.w["rep_r3"] = r3
        self.w["gap_lbl"] = tk.Label(r3, text=self._t("repeat_gap"), font=("Segoe UI", 9))
        self.w["gap_lbl"].pack(side="left")
        self.w["gap_entry"] = tk.Entry(r3, textvariable=self.v_gap, width=6,
                                       font=("Consolas", 9, "bold"), relief="flat",
                                       justify="center", highlightthickness=0,
                                       validate="key", validatecommand=self._vcmd)
        self.w["gap_entry"].pack(side="left", padx=(8, 2), ipady=2)
        self.w["gap_unit"] = tk.Label(r3, text=self._t("milliseconds"), font=("Segoe UI", 7))
        self.w["gap_unit"].pack(side="left")

    # --- Recording ------------------------------------------------------------

    def _toggle_recording(self):
        if self.clicking:
            return
        if self.recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self._root_hwnd = top_level_of(self.root.winfo_id())
        self.recorder.start()
        self.recording = True
        # The window is about to end up behind whatever gets clicked, so the
        # screen has to be the thing that says recording is on.
        self.rec_border.show()
        self._sync_mouse_listener()
        self.w["st_lbl"].config(text=self._t("recording"), fg=self._c("accent_gold"))
        self._refresh_pattern_ui()

    def _stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        self.rec_border.hide()
        self._sync_mouse_listener()
        self.w["st_lbl"].config(text=self._t("stopped"), fg=self._c("text_secondary"))
        self._refresh_pattern_ui()

    def _undo_step(self):
        """Remove the last recorded click, for when one lands by accident."""
        if self.clicking:
            return
        if self.recorder.pop():
            self._refresh_pattern_ui()

    def _clear_pattern(self):
        if self.clicking or self.recording:
            return
        self.recorder.clear()
        self._refresh_pattern_ui()

    def _should_record(self, x, y):
        """False for clicks that are the user operating Windows, not clicking
        a target: our own window, and the taskbar they used to get back to it.
        """
        try:
            handle = top_level_at(x, y)
        except Exception:
            return True
        return handle != self._root_hwnd and not is_shell_window(handle)

    def _refresh_pattern_ui(self):
        steps = list(self.recorder.steps)
        box = self.w["pat_list"]
        box.delete(0, "end")
        for index, step in enumerate(steps, 1):
            box.insert("end", f"{index:>3}. ({step.x:>5},{step.y:>5})  "
                              f"{self._t(step.button):<6} +{step.delay:.2f}s")
        box.see("end")
        self.w["pat_count"].config(text=f"{len(steps)} {self._t('steps')}")
        self.w["rec_btn"].config(
            text=self._t("stop_record") if self.recording else self._t("record"),
            fg=self._c("red") if self.recording else self._c("accent"))

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

    # --- Administrator notice -------------------------------------------------

    def _build_admin(self):
        p = self.w["main"]
        outer = tk.Frame(p, padx=1, pady=1)
        outer.pack(fill="x", pady=(8, 0))
        self.w["adm_outer"] = outer

        inner = tk.Frame(outer, padx=14, pady=8)
        inner.pack(fill="both")
        self.w["adm_inner"] = inner

        row = tk.Frame(inner)
        row.pack(fill="x")
        self.w["adm_row"] = row

        self.w["adm_dot"] = tk.Canvas(row, width=10, height=10, highlightthickness=0)
        self.w["adm_dot"].pack(side="left", padx=(0, 8), pady=3)

        self.w["adm_lbl"] = tk.Label(
            row, font=("Segoe UI", 9, "bold"),
            text=self._t("admin_ok" if self.elevated else "admin_warn"))
        self.w["adm_lbl"].pack(side="left")

        if self.elevated:
            return

        self.w["adm_btn"] = tk.Button(row, text=self._t("run_as_admin"),
                                      font=("Segoe UI", 8, "bold"), relief="flat",
                                      cursor="hand2", command=self._relaunch_admin)
        self.w["adm_btn"].pack(side="right")

        self.w["adm_hint"] = tk.Label(inner, text=self._t("admin_hint"),
                                      font=("Segoe UI", 8), anchor="w",
                                      justify="left", wraplength=360)
        self.w["adm_hint"].pack(fill="x", pady=(5, 0))

    def _relaunch_admin(self):
        """Hand over to an elevated copy, if the user accepts the UAC prompt."""
        if relaunch_as_admin():
            self._on_close()
        else:
            self.w["adm_lbl"].config(text=self._t("admin_denied"), fg=self._c("red"))

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
        for k in ["set_card", "set_tr", "r1", "r2"]:
            self.w[k].configure(bg=card)
        self.w["set_title"].configure(bg=card, fg=acc)
        dot2 = self.w["set_dot"]
        dot2.configure(bg=card)
        dot2.delete("all")
        dot2.create_oval(1, 1, 7, 7, fill=self._c("accent2"), outline="")

        self.w["ct_lbl"].configure(bg=card, fg=tl)
        self.w["mb_lbl"].configure(bg=card, fg=tl)

        for rb, _ in self.ct_rbs + self.mb_rbs:
            rb.configure(bg=card, fg=t1, selectcolor=inp,
                         activebackground=card, activeforeground=acc)

        # Hotkey row
        for k in ["hk_row", "hk_left", "hk_right"]:
            self.w[k].configure(bg=bg)
        for k in ["hk_lbl", "rec_hk_lbl"]:
            self.w[k].configure(bg=bg, fg=tl)
        for k in ["hk_btn", "rec_hk_btn"]:
            self.w[k].configure(bg=inp, fg=self._c("accent_gold"),
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

        # Pattern card
        self.w["pat_outer"].configure(bg=brd)
        for k in ["pat_card", "pat_tr", "pat_row"]:
            self.w[k].configure(bg=card)
        self.w["pat_title"].configure(bg=card, fg=acc)
        pdot = self.w["pat_dot"]
        pdot.configure(bg=card)
        pdot.delete("all")
        pdot.create_oval(1, 1, 7, 7, fill=acc, outline="")
        self.w["pat_count"].configure(bg=card, fg=t2)
        self.w["pat_hint"].configure(bg=card, fg=t2)
        self.w["rec_btn"].configure(bg=inp, activebackground=acc, activeforeground="#ffffff")
        for k in ["clr_btn", "undo_btn"]:
            self.w[k].configure(bg=inp, fg=t2, activebackground=acc,
                                activeforeground="#ffffff")
        self.w["pat_list"].configure(bg=inp, fg=t1, selectbackground=inp,
                                     selectforeground=t1)

        # Repeat card
        self.w["rep_outer"].configure(bg=brd)
        for k in ["rep_card", "rep_tr", "rep_r1", "rep_r2", "rep_r3"]:
            self.w[k].configure(bg=card)
        self.w["rep_title"].configure(bg=card, fg=acc)
        rdot = self.w["rep_dot"]
        rdot.configure(bg=card)
        rdot.delete("all")
        rdot.create_oval(1, 1, 7, 7, fill=self._c("accent2"), outline="")
        for k in ["rb_forever", "rb_duration"]:
            self.w[k].configure(bg=card, fg=t1, selectcolor=inp,
                                activebackground=card, activeforeground=acc)
        for key in ["hours", "minutes", "seconds"]:
            self.w[f"dur_{key}"].configure(bg=inp, fg=acc, insertbackground=acc)
            self.w[f"durl_{key}"].configure(bg=card, fg=t2)
        self.w["gap_lbl"].configure(bg=card, fg=tl)
        self.w["gap_entry"].configure(bg=inp, fg=acc, insertbackground=acc)
        self.w["gap_unit"].configure(bg=card, fg=t2)

        # Mode tabs
        self.w["mode_bar"].configure(bg=bg)
        self._style_mode_tabs()
        self._refresh_pattern_ui()

        # Administrator notice
        tone = self._c("green") if self.elevated else self._c("accent_gold")
        self.w["adm_outer"].configure(bg=brd)
        for k in ["adm_inner", "adm_row"]:
            self.w[k].configure(bg=card)
        adot = self.w["adm_dot"]
        adot.configure(bg=card)
        adot.delete("all")
        adot.create_oval(1, 1, 9, 9, fill=tone, outline="")
        self.w["adm_lbl"].configure(bg=card, fg=tone)
        if not self.elevated:
            self.w["adm_hint"].configure(bg=card, fg=t2)
            self.w["adm_btn"].configure(bg=inp, fg=self._c("accent"),
                                        activebackground=acc, activeforeground="#ffffff")

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
        self.w["rec_hk_lbl"].config(text=self._t("rec_hotkey"))

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

        for key, btn in self.mode_btns.items():
            btn.config(text=self._t(f"mode_{key}"))
        self.w["pat_title"].config(text=self._t("pattern_title"))
        self.w["pat_hint"].config(text=self._t("pattern_hint"))
        self.w["clr_btn"].config(text=self._t("clear"))
        self.w["undo_btn"].config(text=self._t("undo"))
        self.w["rep_title"].config(text=self._t("repeat_title"))
        self.w["rb_forever"].config(text=self._t("repeat_forever"))
        self.w["rb_duration"].config(text=self._t("repeat_duration"))
        self.w["gap_lbl"].config(text=self._t("repeat_gap"))
        self.w["gap_unit"].config(text=self._t("milliseconds"))
        for key in ["hours", "minutes", "seconds"]:
            self.w[f"durl_{key}"].config(text=self._t(key))
        self._refresh_pattern_ui()
        self._fit_window()

        self.w["adm_lbl"].config(
            text=self._t("admin_ok" if self.elevated else "admin_warn"))
        if not self.elevated:
            self.w["adm_hint"].config(text=self._t("admin_hint"))
            self.w["adm_btn"].config(text=self._t("run_as_admin"))

    # =========================================================================
    #  CLICK LOGIC
    # =========================================================================

    def _get_interval(self):
        """Interval in seconds, read on the main thread only."""
        total = 0.0
        for var, factor in ((self.v_hours, 3600.0), (self.v_min, 60.0),
                            (self.v_sec, 1.0), (self.v_ms, 0.001)):
            try:
                total += max(int(var.get() or 0), 0) * factor
            except (ValueError, tk.TclError):
                continue
        if total <= 0:
            # Every box empty or zero would mean "as fast as possible", which is
            # never what somebody typing in the boxes meant to ask for.
            return self.DEFAULT_INTERVAL
        return max(total, self.MIN_INTERVAL)

    def _get_mbtn(self):
        return self.v_mbtn.get()

    def _get_duration(self):
        """Seconds the pattern should keep repeating, or None for no limit."""
        if self.v_repeat.get() != "duration":
            return None
        total = 0.0
        for var, factor in ((self.v_dur_h, 3600.0), (self.v_dur_m, 60.0),
                            (self.v_dur_s, 1.0)):
            try:
                total += max(int(var.get() or 0), 0) * factor
            except (ValueError, tk.TclError):
                continue
        return total

    def _get_gap(self):
        """Pause between one pass of the pattern and the next, in seconds."""
        try:
            return max(int(self.v_gap.get() or 0), 0) / 1000.0
        except (ValueError, tk.TclError):
            return 0.5

    def _snapshot_config(self):
        """Copy the Tk variables into plain values for the worker thread.

        tkinter is not thread-safe, so the click loop must never read a
        StringVar itself; the main thread refreshes this snapshot instead.
        """
        self._cfg = {"interval": self._get_interval(),
                     "btn": self._get_mbtn(),
                     "type": self.v_click_type.get(),
                     "mode": self.mode,
                     "steps": tuple(self.recorder.steps),
                     "gap": self._get_gap(),
                     "duration": self._get_duration()}
        return self._cfg

    def _post(self, fn):
        """Queue a callable to run on the main thread (safe from any thread)."""
        self._ui_q.put(fn)

    def _pump(self):
        """Drain background work and repaint the counter, on the main thread."""
        while True:
            try:
                fn = self._ui_q.get_nowait()
            except queue.Empty:
                break
            try:
                fn()
            except tk.TclError:
                pass

        if self.click_count != self._shown_count:
            self._shown_count = self.click_count
            self.w["cnt_val"].config(text=str(self.click_count))

        if self.clicking:
            self._snapshot_config()   # interval edits apply while running

        try:
            self._pump_id = self.root.after(50, self._pump)
        except tk.TclError:
            self._pump_id = None      # window is gone

    # --- Click worker ---------------------------------------------------------

    def _click_loop(self):
        cfg = self._cfg
        btn, ct = cfg["btn"], cfg["type"]
        begin_high_resolution_timer()
        keep_awake(True)
        try:
            if ct == "hold":
                self._hold_loop(btn)
            else:
                self._repeat_loop(btn, 2 if ct == "double" else 1)
        finally:
            keep_awake(False)
            end_high_resolution_timer()

    def _hold_loop(self, btn):
        self.holding = True
        self._post(lambda: self.w["st_lbl"].config(
            text=self._t("holding"), fg=self._c("accent_gold")))
        self.click_count = 1
        try:
            while not self._stop_evt.is_set():
                if not win32_press_mouse(btn):
                    self._report_blocked()
                # Keep reinforcing the down signal so game engines register it.
                self._stop_evt.wait(0.025)
        finally:
            # Release from the thread that pressed, and only once the loop has
            # really finished - releasing from _stop() could be overtaken by one
            # last press and leave the button stuck down.
            win32_release_mouse(btn)
            self.holding = False

    def _repeat_loop(self, btn, count):
        next_at = time.perf_counter()
        while not self._stop_evt.is_set():
            interval = self._cfg["interval"]
            # The 20ms button hold is what makes clicks land in games, but it
            # also caps the rate; shrink it when a faster interval is asked for.
            hold = (HOLD_SECONDS if interval >= 4 * HOLD_SECONDS
                    else max(interval / 4.0, 0.001))
            if not win32_click_mouse(btn, count=count, hold=hold):
                self._report_blocked()
            self.click_count += count

            now = time.perf_counter()
            next_at += interval
            if next_at < now:
                next_at = now      # fell behind, restart the schedule
            self._stop_evt.wait(next_at - now)

    def _pattern_loop(self):
        """Replay the recorded clicks: move, click, wait, over and over."""
        cfg = self._cfg
        steps, limit = cfg["steps"], cfg["duration"]
        started = time.perf_counter()
        begin_high_resolution_timer()
        keep_awake(True)
        try:
            while not self._stop_evt.is_set():
                for step in steps:
                    if step.delay and self._stop_evt.wait(step.delay):
                        return
                    win32_move_mouse(step.x, step.y)
                    # give the window under the pointer a moment to notice the
                    # move, or the click can land on whatever was there before
                    if self._stop_evt.wait(self.MOVE_SETTLE):
                        return
                    if not win32_click_mouse(step.button, count=1):
                        self._report_blocked()
                    self.click_count += 1
                    if limit is not None and time.perf_counter() - started >= limit:
                        return
                if self._stop_evt.wait(self._cfg["gap"]):
                    return
                if limit is not None and time.perf_counter() - started >= limit:
                    return
        finally:
            keep_awake(False)
            end_high_resolution_timer()
            self._post(self._finish_run)

    def _finish_run(self):
        """The worker stopped by itself, so catch the UI up with it."""
        if self.clicking:
            self._stop()

    def _report_blocked(self):
        """Windows refused our input (usually an elevated window has focus)."""
        if self._input_blocked:
            return
        self._input_blocked = True
        self._post(lambda: self.w["st_lbl"].config(
            text=self._t("blocked"), fg=self._c("red")))

    # --- Start / stop ---------------------------------------------------------

    def _toggle(self):
        if self.clicking:
            self._stop()
        else:
            self._start()

    def _start(self):
        if self.clicking or self.recording:
            return
        pattern = self.mode == "pattern"
        if pattern and not len(self.recorder):
            self.w["st_lbl"].config(text=self._t("no_pattern"), fg=self._c("red"))
            return
        self._join_worker()        # never leave two click loops running at once
        self._snapshot_config()
        self.clicking = True
        self.click_count = 0
        self._shown_count = -1
        self._input_blocked = False
        self._stop_evt.clear()
        self._draw_btn()
        self._draw_st_dot()
        self.w["st_lbl"].config(
            text=self._t("pattern_running" if pattern else "running"),
            fg=self._c("green"))
        self.click_thread = threading.Thread(
            target=self._pattern_loop if pattern else self._click_loop, daemon=True)
        self.click_thread.start()

    def _stop(self):
        if not self.clicking:
            return
        self.clicking = False
        self._join_worker()
        self._draw_btn()
        self._draw_st_dot()
        self.w["st_lbl"].config(text=self._t("stopped"), fg=self._c("text_secondary"))

    def _join_worker(self):
        """Wait for the click thread to finish before anything else happens."""
        self._stop_evt.set()
        t, self.click_thread = self.click_thread, None
        if t is not None and t.is_alive():
            t.join(timeout=2.0)
            if t.is_alive() or self.holding:
                # Wedged worker: make sure no button is left held down.
                try:
                    win32_release_mouse(self._cfg.get("btn", "left"))
                except Exception:
                    pass
                self.holding = False

    # --- Hotkey ---------------------------------------------------------------

    def _hotkey_is_mouse(self):
        return (is_mouse_hotkey(self.v_hotkey_str)
                or is_mouse_hotkey(self.v_rec_hotkey_str))

    def _sync_mouse_listener(self):
        """Run the low level mouse hook only when a mouse hotkey needs it.

        Most people bind a keyboard key, and a permanent WH_MOUSE_LL hook would
        put this app in the path of every mouse event on the system for
        nothing.
        """
        needed = (self.binding_target is not None or self._hotkey_is_mouse()
                  or self.recording)
        if needed and self.mouse_kb is None:
            self.mouse_kb = MouseListener(
                on_click=self._on_mouse,
                win32_event_filter=self._mouse_event_filter)
            self.mouse_kb.daemon = True
            self.mouse_kb.start()
        elif not needed and self.mouse_kb is not None:
            listener, self.mouse_kb = self.mouse_kb, None
            try:
                listener.stop()
            except Exception:
                pass

    @staticmethod
    def _mouse_event_filter(msg, data):
        """Drop the clicks this app injected, and only those.

        Filtering everything Windows marks as injected would be easier, but
        gaming mice forward their macro buttons through driver software that
        injects them too - those have to keep working as hotkeys.
        """
        if (data.dwExtraInfo or 0) == INJECT_TAG:
            return False

    def _on_mouse(self, x, y, button, pressed, injected=False):
        """Mouse hook thread: records clicks, or toggles on a side button."""
        if not pressed:
            return
        name = get_mouse_name(button)
        if self.recording:
            if name is not None and name in (self.v_rec_hotkey_str, self.v_hotkey_str):
                self._post(self._stop_recording)       # finish, hands free
            elif self._should_record(x, y):
                if not self.recorder.add(x, y, getattr(button, "name", "")):
                    self._post(self._stop_recording)   # pattern is full
                else:
                    self._post(self._refresh_pattern_ui)
            return
        if name is None:
            return                 # left/right are needed to operate the UI
        if self.binding_target is not None:
            self._post(lambda n=name: self._finish_binding(n))
        elif name == self.v_rec_hotkey_str:
            self._post(self._record_hotkey_pressed)
        elif name == self.v_hotkey_str:
            self._post(self._hotkey_toggle)

    def _binding_button(self, target):
        return self.w["rec_hk_btn"] if target == "record" else self.w["hk_btn"]

    def _start_binding(self, target="main"):
        if self.clicking or self.recording:
            return
        self.binding_target = target
        self._sync_mouse_listener()
        self._binding_button(target).configure(text=self._t("press_key"),
                                               fg=self._c("red"))

    def _finish_binding(self, name):
        target, self.binding_target = self.binding_target, None
        if target is None:
            return
        self._sync_mouse_listener()
        # The key just bound is still physically down; don't let its release or
        # auto-repeat count as a toggle.
        self._hotkey_held = True
        self._rec_held = True

        other = self.v_rec_hotkey_str if target == "main" else self.v_hotkey_str
        if name == other:
            # One key cannot mean two things; keep what was there and show it.
            self._update_hotkey_ui()
            self._binding_button(target).configure(fg=self._c("red"))
            self.root.after(900, self._update_hotkey_ui)
            return
        if target == "record":
            self.v_rec_hotkey_str = name
        else:
            self.v_hotkey_str = name
        self._sync_mouse_listener()
        self._update_hotkey_ui()

    def _cancel_binding(self):
        self.binding_target = None
        self._sync_mouse_listener()
        self._update_hotkey_ui()

    def _update_hotkey_ui(self):
        self.w["hk_btn"].configure(text=self.v_hotkey_str, fg=self._c("accent_gold"))
        self.w["rec_hk_btn"].configure(text=self.v_rec_hotkey_str,
                                       fg=self._c("accent_gold"))
        self._draw_btn()

    def _on_key(self, key):
        """Runs on the pynput listener thread - queue work, never touch Tk."""
        if self.binding_target is not None:
            if key == Key.esc:
                self.binding_target = None
                self._post(self._cancel_binding)
                return
            name = get_key_name(key)
            if name:
                self._post(lambda n=name: self._finish_binding(n))
            return

        name = get_key_name(key)
        if name == self.v_rec_hotkey_str:
            if self._rec_held:
                return             # Windows key auto-repeat, not a new press
            self._rec_held = True
            self._post(self._record_hotkey_pressed)
            return
        if name != self.v_hotkey_str:
            return
        if self._hotkey_held:
            return
        self._hotkey_held = True
        self._post(self._hotkey_toggle)

    def _on_key_release(self, key):
        name = get_key_name(key)
        if name == self.v_hotkey_str:
            self._hotkey_held = False
        if name == self.v_rec_hotkey_str:
            self._rec_held = False

    # Keys that put something into an entry box when pressed.
    _EDIT_KEYS = {"Space", "Backspace", "Delete"}

    def _types_text(self, name):
        return len(name) == 1 or name.startswith("Num ") or name in self._EDIT_KEYS

    def _blocked_by_entry(self, name):
        """A hotkey bound to an ordinary character must not fire while that
        character is being typed into one of the boxes."""
        return self._types_text(name) and self._entry_has_focus()

    def _record_hotkey_pressed(self):
        """The recording hotkey: start or end a recording, hands off the app."""
        if self.clicking:
            return                 # not in the middle of a run
        if self.recording:
            self._stop_recording()
            return
        if self._blocked_by_entry(self.v_rec_hotkey_str):
            return
        if self.mode != "pattern":
            self._set_mode("pattern")
        self._start_recording()

    def _hotkey_toggle(self):
        if self.recording:
            # Ending a recording takes priority: the macro cannot run yet
            # anyway, and this is the key most people will reach for.
            self._stop_recording()
            return
        # Stopping is never blocked - that one always has to work.
        if not self.clicking and self._blocked_by_entry(self.v_hotkey_str):
            return
        self._toggle()

    def _entry_has_focus(self):
        try:
            return isinstance(self.root.focus_get(), tk.Entry)
        except Exception:
            return False

    def _on_close(self):
        self.clicking = False
        self.rec_border.hide()
        self._join_worker()
        if self._pump_id is not None:
            # Cancel the queued pump, otherwise Tcl runs it after destroy() has
            # already deleted the callback and complains on the way out.
            try:
                self.root.after_cancel(self._pump_id)
            except tk.TclError:
                pass
            self._pump_id = None
        for listener in (self.kb, self.mouse_kb):
            if listener is not None:
                try:
                    listener.stop()
                except Exception:
                    pass
        self.mouse_kb = None
        try:
            self.root.destroy()
        except Exception:
            pass
