"""
AutoClicker - Custom Widgets

Tk's own Radiobutton is the most dated thing that can sit on a window, so the
choices here are drawn instead: a segmented control, the kind of pill row a
modern app uses, painted on a Canvas.
"""

import tkinter as tk


def round_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """A rounded rectangle, as a smoothed polygon - Tk has no such shape."""
    radius = max(0, min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2))
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1,
              x2, y1 + radius, x2, y2 - radius, x2, y2,
              x2 - radius, y2, x1 + radius, y2, x1, y2,
              x1, y2 - radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class Segmented(tk.Canvas):
    """A row of pills that behaves like a group of radio buttons.

    `palette` is a callable taking a colour name, so the control repaints
    itself correctly when the theme changes without holding stale colours.
    """

    INSET = 3

    def __init__(self, parent, variable, options, palette, *,
                 font=("Segoe UI", 9, "bold"), height=32, track="surface_alt",
                 ground="surface"):
        super().__init__(parent, height=height, highlightthickness=0, bd=0,
                         takefocus=0)
        self.var = variable
        self.options = list(options)
        self.palette = palette
        self.font = font
        self.track = track
        self.ground = ground
        self._hover = None

        self.bind("<Configure>", lambda _e: self.redraw())
        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", lambda _e: self._set_hover(None))
        variable.trace_add("write", lambda *_a: self.redraw())

    def set_options(self, options):
        """Replace the labels, keeping the values - used on a language switch."""
        self.options = list(options)
        self.redraw()

    # --- interaction ----------------------------------------------------------

    def _index_at(self, x):
        if not self.options:
            return None
        width = max(self.winfo_width(), 1)
        index = int(x // (width / len(self.options)))
        return min(max(index, 0), len(self.options) - 1)

    def _on_click(self, event):
        index = self._index_at(event.x)
        if index is not None:
            self.var.set(self.options[index][0])

    def _on_motion(self, event):
        self._set_hover(self._index_at(event.x))

    def _set_hover(self, index):
        if index != self._hover:
            self._hover = index
            self.configure(cursor="hand2" if index is not None else "")
            self.redraw()

    # --- painting -------------------------------------------------------------

    def redraw(self):
        self.delete("all")
        colour = self.palette
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        self.configure(bg=colour(self.ground))
        round_rect(self, 0, 0, width, height, height / 2,
                   fill=colour(self.track), outline="")
        if not self.options:
            return

        step = width / len(self.options)
        current = self.var.get()
        for index, (value, label) in enumerate(self.options):
            left, right = index * step, (index + 1) * step
            if value == current:
                round_rect(self, left + self.INSET, self.INSET,
                           right - self.INSET, height - self.INSET,
                           (height - 2 * self.INSET) / 2,
                           fill=colour("accent"), outline="")
                fill = colour("on_accent")
            elif index == self._hover:
                fill = colour("text")
            else:
                fill = colour("text_dim")
            self.create_text((left + right) / 2, height / 2, text=label,
                             font=self.font, fill=fill)
