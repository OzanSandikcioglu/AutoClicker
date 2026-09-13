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
from src.pattern import PatternRecorder
from src.overlay import RecordingBorder
from src.widgets import Segmented, round_rect


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
        self.v_lang = tk.StringVar(value=self.lang)
        self.v_mode = tk.StringVar(value=self.mode)
        
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

        # traced only now, so building the UI cannot trip them
        self.v_lang.trace_add("write", lambda *_a: self._on_lang_var())
        self.v_mode.trace_add("write", lambda *_a: self._on_mode_var())
        self.v_repeat.trace_add("write", lambda *_a: self._sync_repeat_fields())

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

    FONT = "Segoe UI"
    MONO = "Consolas"

    def _build(self):
        self.root.configure(bg=self._c("bg"))
        self._vcmd = (self.root.register(self._validate_number), "%P")

        self.w["top_line"] = tk.Frame(self.root, height=2)
        self.w["top_line"].pack(fill="x")

        self.w["main"] = tk.Frame(self.root, padx=18, pady=16)
        self.w["main"].pack(fill="both", expand=True)

        self._build_header()
        self._build_mode_tabs()
        self._build_interval()
        self._build_settings()
        self._build_pattern()
        self._build_repeat()
        self._build_hotkeys()
        self._build_button()
        self._build_status()
        self._set_mode(self.mode)
        self._install_click_guard()

    # --- Small building blocks ------------------------------------------------

    def _card(self, key):
        """A flat panel. The surface colour carries it - no drawn borders."""
        card = tk.Frame(self.w["main"], padx=16, pady=14)
        self.w[key] = card
        return card

    def _upper(self, text):
        """Uppercase that keeps the Turkish dotted capital I intact."""
        if self.lang == "TR":
            text = text.replace("i", "\u0130")
        return text.upper()

    def _section(self, parent, key, text):
        """A quiet uppercase label introducing a group of controls."""
        label = tk.Label(parent, text=self._upper(text), font=(self.FONT, 8, "bold"),
                         anchor="w")
        label.pack(fill="x", pady=(0, 9))
        self.w[key] = label
        return label

    def _field(self, parent, key, var, caption, width=5, size=14):
        """A number box with its unit underneath and a ring when focused."""
        holder = tk.Frame(parent)
        ring = tk.Frame(holder, padx=1, pady=1)
        ring.pack(fill="x")
        entry = tk.Entry(ring, textvariable=var, width=width, relief="flat",
                         justify="center", highlightthickness=0, bd=0,
                         font=(self.MONO, size, "bold"),
                         validate="key", validatecommand=self._vcmd)
        entry.pack(fill="x", ipady=6)
        entry.bind("<FocusIn>", lambda _e, r=ring: r.configure(bg=self._c("accent")))
        entry.bind("<FocusOut>", lambda _e, r=ring: r.configure(bg=self._c("border")))
        unit = tk.Label(holder, text=caption, font=(self.FONT, 8))
        unit.pack(pady=(5, 0))
        self.w[f"holder_{key}"] = holder
        self.w[f"ring_{key}"] = ring
        self.w[f"e_{key}"] = entry
        self.w[f"l_{key}"] = unit
        return holder

    def _soft_button(self, parent, key, text, command, width=9, accent=False):
        button = tk.Button(parent, text=text, font=(self.FONT, 9, "bold"),
                           relief="flat", bd=0, width=width, cursor="hand2",
                           command=command, activeforeground=self._c("on_accent"))
        self.w[key] = button
        self.w.setdefault("_accent_buttons", set())
        if accent:
            self.w["_accent_buttons"].add(key)
        return button

    # --- Header ---------------------------------------------------------------

    def _build_header(self):
        head = tk.Frame(self.w["main"])
        head.pack(fill="x", pady=(0, 14))
        self.w["hdr"] = head

        self.w["logo"] = tk.Canvas(head, width=38, height=38, highlightthickness=0,
                                   bd=0)
        self.w["logo"].pack(side="left", padx=(0, 11))

        titles = tk.Frame(head)
        titles.pack(side="left")
        self.w["hdr_titles"] = titles

        row = tk.Frame(titles)
        row.pack(anchor="w")
        self.w["hdr_row"] = row
        self.w["t1"] = tk.Label(row, text="Auto", font=(self.FONT, 17, "bold"))
        self.w["t1"].pack(side="left")
        self.w["t2"] = tk.Label(row, text="Clicker", font=(self.FONT, 17, "bold"))
        self.w["t2"].pack(side="left")

        self.w["sub"] = tk.Label(titles, text=self._t("subtitle"),
                                 font=(self.FONT, 8))
        self.w["sub"].pack(anchor="w")

        self.w["theme_btn"] = tk.Canvas(head, width=64, height=30, bd=0,
                                        highlightthickness=0, cursor="hand2")
        self.w["theme_btn"].pack(side="right")
        self.w["theme_btn"].bind("<Button-1>", lambda _e: self._toggle_theme())

        self.w["lang_seg"] = Segmented(
            self.w["main"], self.v_lang,
            [(code, code) for code in LANG_ORDER], self._c,
            font=(self.FONT, 8, "bold"), height=26, ground="bg")
        self.w["lang_seg"].pack(fill="x", pady=(0, 10))

    def _draw_logo(self):
        canvas = self.w["logo"]
        canvas.delete("all")
        canvas.configure(bg=self._c("bg"))
        round_rect(canvas, 0, 0, 38, 38, 11, fill=self._c("accent"), outline="")
        canvas.create_polygon(22, 8, 15, 21, 19, 21, 16, 30, 24, 17, 20, 17, 23, 8,
                              fill="#ffffff", outline="")

    @staticmethod
    def _draw_sun(canvas, cx, cy, colour):
        canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=colour, outline="")
        for dx, dy in ((0, -8), (0, 8), (-8, 0), (8, 0),
                       (-6, -6), (6, 6), (-6, 6), (6, -6)):
            canvas.create_line(cx + dx * 0.72, cy + dy * 0.72,
                               cx + dx, cy + dy, fill=colour, width=2,
                               capstyle="round")

    @staticmethod
    def _draw_moon(canvas, cx, cy, colour, behind):
        canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill=colour, outline="")
        canvas.create_oval(cx - 11, cy - 9, cx + 3, cy + 5, fill=behind, outline="")

    def _draw_theme_btn(self):
        """Two halves, sun and moon, with the active one filled - the same
        shape as every other choice on the window, so it reads as a switch."""
        canvas = self.w["theme_btn"]
        canvas.delete("all")
        canvas.configure(bg=self._c("bg"))
        track = self._c("surface_alt")
        round_rect(canvas, 0, 0, 64, 30, 15, fill=track, outline="")

        dark = self.theme == "dark"
        accent = self._c("accent")
        if dark:
            round_rect(canvas, 33, 2, 62, 28, 13, fill=accent, outline="")
        else:
            round_rect(canvas, 2, 2, 31, 28, 13, fill=accent, outline="")

        self._draw_sun(canvas, 16, 15,
                       self._c("on_accent") if not dark else self._c("text_faint"))
        self._draw_moon(canvas, 48, 15,
                        self._c("on_accent") if dark else self._c("text_faint"),
                        accent if dark else track)

    # --- Mode tabs ------------------------------------------------------------

    MODE_CARDS = {"clicker": ("int_outer", "set_outer"),
                  "pattern": ("pat_outer", "rep_outer")}

    def _build_mode_tabs(self):
        self.w["mode_seg"] = Segmented(
            self.w["main"], self.v_mode,
            [("clicker", self._t("mode_clicker")), ("pattern", self._t("mode_pattern"))],
            self._c, font=(self.FONT, 10, "bold"), height=36, ground="bg")
        self.w["mode_seg"].pack(fill="x", pady=(0, 12))

    def _style_mode_tabs(self):
        self.w["mode_seg"].redraw()

    def _on_mode_var(self):
        wanted = self.v_mode.get()
        if wanted == self.mode:
            return
        if self.clicking or self.recording:
            self.v_mode.set(self.mode)        # refused, put the tab back
            return
        self._set_mode(wanted)

    def _set_mode(self, mode):
        """Swap which pair of cards is on screen. Not while something runs."""
        if self.clicking or self.recording:
            return
        self.mode = mode
        if self.v_mode.get() != mode:
            self.v_mode.set(mode)
        for keys in self.MODE_CARDS.values():
            for key in keys:
                self.w[key].pack_forget()
        for key in self.MODE_CARDS[mode]:
            self.w[key].pack(fill="x", pady=(0, 10), before=self.w["hk_row"])
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

    # --- Interval card --------------------------------------------------------

    def _build_interval(self):
        card = self._card("int_outer")
        self._section(card, "int_title", self._t("interval_title"))

        row = tk.Frame(card)
        row.pack(fill="x")
        self.w["int_row"] = row
        for key, var in (("hours", self.v_hours), ("minutes", self.v_min),
                         ("seconds", self.v_sec), ("milliseconds", self.v_ms)):
            field = self._field(row, key, var, self._t(key))
            field.pack(side="left", expand=True, fill="x", padx=3)

    # --- Click settings card --------------------------------------------------

    def _build_settings(self):
        card = self._card("set_outer")
        self._section(card, "set_title", self._t("settings_title"))

        self.w["ct_seg"] = Segmented(
            card, self.v_click_type,
            [(key, self._t(key)) for key in CLICK_KEYS], self._c,
            font=(self.FONT, 9, "bold"), height=32)
        self.w["ct_seg"].pack(fill="x")

        self.w["mb_seg"] = Segmented(
            card, self.v_mbtn,
            [(key, self._t(key)) for key in MBTN_KEYS], self._c,
            font=(self.FONT, 9, "bold"), height=32)
        self.w["mb_seg"].pack(fill="x", pady=(8, 0))

    # --- Pattern card ---------------------------------------------------------

    def _build_pattern(self):
        card = self._card("pat_outer")

        head = tk.Frame(card)
        head.pack(fill="x", pady=(0, 9))
        self.w["pat_head"] = head
        self.w["pat_title"] = tk.Label(head, text=self._upper(self._t("pattern_title")),
                                       font=(self.FONT, 8, "bold"))
        self.w["pat_title"].pack(side="left")
        self.w["pat_count"] = tk.Label(head, text="", font=(self.FONT, 8, "bold"))
        self.w["pat_count"].pack(side="right")

        row = tk.Frame(card)
        row.pack(fill="x")
        self.w["pat_row"] = row
        self._soft_button(row, "rec_btn", self._t("record"), self._toggle_recording,
                          width=13, accent=True).pack(side="left", ipady=4)
        self._soft_button(row, "clr_btn", self._t("clear"),
                          self._clear_pattern).pack(side="right", ipady=4)
        self._soft_button(row, "undo_btn", self._t("undo"),
                          self._undo_step).pack(side="right", padx=(0, 6), ipady=4)

        self.w["pat_hint"] = tk.Label(card, text=self._t("pattern_hint"),
                                      font=(self.FONT, 8), anchor="w",
                                      justify="left", wraplength=352)
        self.w["pat_hint"].pack(fill="x", pady=(10, 9))

        self.w["pat_list"] = tk.Listbox(card, height=5, font=(self.MONO, 8),
                                        relief="flat", highlightthickness=0, bd=0,
                                        activestyle="none", selectmode="none")
        self.w["pat_list"].pack(fill="x")

    # --- Repeat card ----------------------------------------------------------

    def _build_repeat(self):
        card = self._card("rep_outer")
        self._section(card, "rep_title", self._t("repeat_title"))

        self.w["rep_seg"] = Segmented(
            card, self.v_repeat,
            [("forever", self._t("repeat_forever")),
             ("duration", self._t("repeat_duration"))],
            self._c, font=(self.FONT, 9, "bold"), height=32)
        self.w["rep_seg"].pack(fill="x")

        row = tk.Frame(card)
        row.pack(fill="x", pady=(10, 0))
        self.w["rep_row"] = row
        for key, var in (("hours", self.v_dur_h), ("minutes", self.v_dur_m),
                         ("seconds", self.v_dur_s)):
            field = self._field(row, f"dur_{key}", var, self._t(key), width=4, size=11)
            field.pack(side="left", expand=True, fill="x", padx=3)

        # the gap between passes belongs to both repeat modes, not to the
        # duration next to it, so it gets its own line
        gap_row = tk.Frame(card)
        gap_row.pack(fill="x", pady=(13, 0))
        self.w["gap_row"] = gap_row
        self.w["gap_lbl"] = tk.Label(gap_row, text=self._t("repeat_gap"),
                                     font=(self.FONT, 9))
        self.w["gap_lbl"].pack(side="left")
        self.w["l_gap"] = tk.Label(gap_row, text=self._t("milliseconds"),
                                   font=(self.FONT, 8))
        self.w["l_gap"].pack(side="right", padx=(7, 0))
        ring = tk.Frame(gap_row, padx=1, pady=1)
        ring.pack(side="right")
        self.w["ring_gap"] = ring
        self.w["e_gap"] = tk.Entry(ring, textvariable=self.v_gap, width=6,
                                   relief="flat", justify="center", bd=0,
                                   highlightthickness=0,
                                   font=(self.MONO, 10, "bold"),
                                   validate="key", validatecommand=self._vcmd)
        self.w["e_gap"].pack(ipady=4)
        self.w["e_gap"].bind("<FocusIn>",
                             lambda _e: self.w["ring_gap"].configure(bg=self._c("accent")))
        self.w["e_gap"].bind("<FocusOut>",
                             lambda _e: self.w["ring_gap"].configure(bg=self._c("border")))

    def _sync_repeat_fields(self):
        """Grey the duration boxes out while the pattern repeats forever."""
        live = self.v_repeat.get() == "duration"
        for key in ("dur_hours", "dur_minutes", "dur_seconds"):
            self.w[f"e_{key}"].configure(state="normal" if live else "disabled")
            self.w[f"l_{key}"].configure(
                fg=self._c("text_faint") if live else self._c("border"))
            self.w[f"ring_{key}"].configure(
                bg=self._c("border") if live else self._c("surface_alt"))

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
        self.w["st_lbl"].config(text=self._t("recording"), fg=self._c("warn"))
        self._refresh_pattern_ui()

    def _stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        self.rec_border.hide()
        self._sync_mouse_listener()
        self.w["st_lbl"].config(text=self._t("stopped"), fg=self._c("text_dim"))
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
            box.insert("end", f" {index:>3}.  {step.x:>5} , {step.y:<5}  "
                              f"{self._t(step.button):<7} +{step.delay:.2f}s")
        box.see("end")
        self.w["pat_count"].config(text=f"{len(steps)} {self._t('steps')}")
        self.w["rec_btn"].config(
            text=self._t("stop_record") if self.recording else self._t("record"),
            bg=self._c("danger") if self.recording else self._c("accent"))

    # --- Hotkey row -----------------------------------------------------------

    def _build_hotkeys(self):
        """Both hotkeys live here rather than inside a mode card: they work in
        either mode, so they have to be reachable from either one."""
        row = tk.Frame(self.w["main"])
        row.pack(fill="x", pady=(2, 12))
        self.w["hk_row"] = row

        left = tk.Frame(row)
        left.pack(side="left")
        self.w["hk_left"] = left
        self.w["hk_lbl"] = tk.Label(left, text=self._t("hotkey"), font=(self.FONT, 8))
        self.w["hk_lbl"].pack(side="left", padx=(0, 7))
        self.w["hk_btn"] = tk.Button(left, text=self.v_hotkey_str,
                                     font=(self.MONO, 9, "bold"), relief="flat",
                                     bd=0, width=9, cursor="hand2",
                                     command=lambda: self._start_binding("main"))
        self.w["hk_btn"].pack(side="left", ipady=3)

        # packed only in pattern mode, where recording exists
        right = tk.Frame(row)
        self.w["hk_right"] = right
        self.w["rec_hk_lbl"] = tk.Label(right, text=self._t("rec_hotkey"),
                                        font=(self.FONT, 8))
        self.w["rec_hk_lbl"].pack(side="left", padx=(0, 7))
        self.w["rec_hk_btn"] = tk.Button(right, text=self.v_rec_hotkey_str,
                                         font=(self.MONO, 9, "bold"), relief="flat",
                                         bd=0, width=9, cursor="hand2",
                                         command=lambda: self._start_binding("record"))
        self.w["rec_hk_btn"].pack(side="left", ipady=3)

    # --- Start button ---------------------------------------------------------

    def _build_button(self):
        frame = tk.Frame(self.w["main"])
        frame.pack(fill="x", pady=(0, 10))
        self.w["bf"] = frame

        self.w["btn"] = tk.Canvas(frame, height=52, highlightthickness=0, bd=0,
                                  cursor="hand2")
        self.w["btn"].pack(fill="x")
        self.w["btn"].bind("<Button-1>", lambda _e: self._toggle())
        self.w["btn"].bind("<Enter>", lambda _e: self._draw_btn(hover=True))
        self.w["btn"].bind("<Leave>", lambda _e: self._draw_btn(hover=False))
        self.w["btn"].bind("<Configure>", lambda _e: self._draw_btn())

    def _draw_btn(self, hover=False):
        canvas = self.w["btn"]
        canvas.delete("all")
        canvas.configure(bg=self._c("bg"))
        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), 1)

        if self.clicking:
            fill = self._c("danger")
        else:
            fill = self._c("accent_hover") if hover else self._c("accent")
        round_rect(canvas, 0, 0, width, height, 13, fill=fill, outline="")

        label = self._t("stop") if self.clicking else self._t("start")
        canvas.create_text(width / 2, height / 2 + 1, text=label,
                           font=(self.FONT, 13, "bold"), fill="#ffffff")
        canvas.create_text(width - 16, height / 2 + 1, text=self.v_hotkey_str,
                           anchor="e", font=(self.MONO, 9, "bold"),
                           fill=self._c("on_accent_dim"))

    # --- Status ---------------------------------------------------------------

    def _build_status(self):
        card = self._card("st_outer")
        card.configure(pady=11)
        card.pack(fill="x", pady=(0, 10))

        left = tk.Frame(card)
        left.pack(side="left")
        self.w["st_left"] = left
        self.w["st_dot"] = tk.Canvas(left, width=10, height=10, bd=0,
                                     highlightthickness=0)
        self.w["st_dot"].pack(side="left", padx=(0, 9), pady=2)
        self.w["st_lbl"] = tk.Label(left, text=self._t("stopped"),
                                    font=(self.FONT, 9, "bold"))
        self.w["st_lbl"].pack(side="left")

        right = tk.Frame(card)
        right.pack(side="right")
        self.w["st_right"] = right
        self.w["cnt_val"] = tk.Label(right, text="0", font=(self.MONO, 12, "bold"))
        self.w["cnt_val"].pack(side="right")
        self.w["cnt_lbl"] = tk.Label(right, text=self._t("clicks"),
                                     font=(self.FONT, 8))
        self.w["cnt_lbl"].pack(side="right", padx=(0, 7))

    def _draw_st_dot(self):
        dot = self.w["st_dot"]
        dot.delete("all")
        dot.configure(bg=self._c("surface"))
        colour = self._c("success") if self.clicking else self._c("text_faint")
        dot.create_oval(0, 0, 10, 10, fill=colour, outline="")

    # =========================================================================
    #  THEME
    # =========================================================================

    def _apply_theme(self):
        bg = self._c("bg")
        surface = self._c("surface")
        field = self._c("surface_alt")
        border = self._c("border")
        text = self._c("text")
        dim = self._c("text_dim")
        accent = self._c("accent")

        self.root.configure(bg=bg)
        self.w["top_line"].configure(bg=accent)
        self.w["main"].configure(bg=bg)

        # Header
        for key in ("hdr", "hdr_titles", "hdr_row"):
            self.w[key].configure(bg=bg)
        self.w["t1"].configure(bg=bg, fg=text)
        self.w["t2"].configure(bg=bg, fg=accent)
        self.w["sub"].configure(bg=bg, fg=dim)
        self._draw_logo()
        self._draw_theme_btn()
        self.w["lang_seg"].redraw()
        self.w["mode_seg"].redraw()

        # Cards
        for key in ("int_outer", "set_outer", "pat_outer", "rep_outer",
                    "st_outer"):
            self.w[key].configure(bg=surface)
        for key in ("int_row", "rep_row", "pat_head", "pat_row", "gap_row",
                    "st_left", "st_right"):
            self.w[key].configure(bg=surface)
        for key in ("int_title", "set_title", "rep_title"):
            self.w[key].configure(bg=surface, fg=dim)

        # Number fields
        for key in ("hours", "minutes", "seconds", "milliseconds",
                    "dur_hours", "dur_minutes", "dur_seconds"):
            self.w[f"holder_{key}"].configure(bg=surface)
            self.w[f"ring_{key}"].configure(bg=border)
            self.w[f"e_{key}"].configure(bg=field, fg=text, insertbackground=accent,
                                         disabledbackground=field,
                                         disabledforeground=self._c("text_faint"))
            self.w[f"l_{key}"].configure(bg=surface, fg=self._c("text_faint"))

        self.w["gap_row"].configure(bg=surface)
        self.w["gap_lbl"].configure(bg=surface, fg=dim)
        self.w["l_gap"].configure(bg=surface, fg=self._c("text_faint"))
        self.w["ring_gap"].configure(bg=border)
        self.w["e_gap"].configure(bg=field, fg=text, insertbackground=accent)

        for key in ("ct_seg", "mb_seg", "rep_seg"):
            self.w[key].redraw()

        # Pattern card
        self.w["pat_title"].configure(bg=surface, fg=dim)
        self.w["pat_count"].configure(bg=surface, fg=accent)
        self.w["pat_hint"].configure(bg=surface, fg=self._c("text_faint"))
        self.w["pat_list"].configure(bg=field, fg=dim, selectbackground=field,
                                     selectforeground=dim)

        # Buttons that are not the big one
        for key in ("rec_btn", "clr_btn", "undo_btn"):
            button = self.w[key]
            on_accent = key in self.w.get("_accent_buttons", ())
            button.configure(bg=accent if on_accent else field,
                             fg=self._c("on_accent") if on_accent else dim,
                             activebackground=self._c("accent_hover"),
                             activeforeground=self._c("on_accent"))

        # Hotkeys
        for key in ("hk_row", "hk_left", "hk_right"):
            self.w[key].configure(bg=bg)
        for key in ("hk_lbl", "rec_hk_lbl"):
            self.w[key].configure(bg=bg, fg=dim)
        for key in ("hk_btn", "rec_hk_btn"):
            self.w[key].configure(bg=field, fg=accent,
                                  activebackground=accent,
                                  activeforeground=self._c("on_accent"))

        # Start button
        self.w["bf"].configure(bg=bg)
        self._draw_btn()

        # Status
        self._draw_st_dot()
        self.w["st_lbl"].configure(
            bg=surface,
            fg=self._c("success") if self.clicking else dim)
        self.w["cnt_lbl"].configure(bg=surface, fg=self._c("text_faint"))
        self.w["cnt_val"].configure(bg=surface, fg=text)

        self._sync_repeat_fields()
        self._refresh_pattern_ui()

    # =========================================================================
    #  LANGUAGE & THEME SWITCHING
    # =========================================================================

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme()

    def _on_lang_var(self):
        self._set_lang(self.v_lang.get())

    def _set_lang(self, code):
        if code == self.lang:
            return
        self.lang = code
        if self.v_lang.get() != code:
            self.v_lang.set(code)

        self.w["sub"].config(text=self._t("subtitle"))
        self.w["int_title"].config(text=self._upper(self._t("interval_title")))
        self.w["set_title"].config(text=self._upper(self._t("settings_title")))
        self.w["rep_title"].config(text=self._upper(self._t("repeat_title")))
        self.w["pat_title"].config(text=self._upper(self._t("pattern_title")))
        self.w["pat_hint"].config(text=self._t("pattern_hint"))
        self.w["clr_btn"].config(text=self._t("clear"))
        self.w["undo_btn"].config(text=self._t("undo"))
        self.w["hk_lbl"].config(text=self._t("hotkey"))
        self.w["rec_hk_lbl"].config(text=self._t("rec_hotkey"))
        self.w["cnt_lbl"].config(text=self._t("clicks"))

        for key in ("hours", "minutes", "seconds", "milliseconds"):
            self.w[f"l_{key}"].config(text=self._t(key))
        for key in ("hours", "minutes", "seconds"):
            self.w[f"l_dur_{key}"].config(text=self._t(key))
        self.w["gap_lbl"].config(text=self._t("repeat_gap"))
        self.w["l_gap"].config(text=self._t("milliseconds"))

        self.w["mode_seg"].set_options(
            [("clicker", self._t("mode_clicker")), ("pattern", self._t("mode_pattern"))])
        self.w["ct_seg"].set_options([(key, self._t(key)) for key in CLICK_KEYS])
        self.w["mb_seg"].set_options([(key, self._t(key)) for key in MBTN_KEYS])
        self.w["rep_seg"].set_options(
            [("forever", self._t("repeat_forever")),
             ("duration", self._t("repeat_duration"))])

        self._draw_btn()
        if self.clicking:
            key = "pattern_running" if self.mode == "pattern" else "running"
            self.w["st_lbl"].config(text=self._t(key))
        elif self.recording:
            self.w["st_lbl"].config(text=self._t("recording"))
        else:
            self.w["st_lbl"].config(text=self._t("stopped"))

        self._refresh_pattern_ui()
        self._fit_window()

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
