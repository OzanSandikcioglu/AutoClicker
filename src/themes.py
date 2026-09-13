"""
AutoClicker - Color Themes

One accent, a neutral scale, and semantic colours kept for status only. The
older names are aliases onto the same values so nothing that reads a colour
has to know the palette was reworked.
"""

_DARK = {
    "bg":           "#0e1014",
    "surface":      "#161a21",
    "surface_alt":  "#1e232d",
    "border":       "#262c38",
    "accent":       "#6366f1",
    "accent_hover": "#7c7ef5",
    "accent_soft":  "#1d2039",
    "on_accent":    "#ffffff",
    "on_accent_dim": "#c8caf8",
    "text":         "#e7eaf0",
    "text_dim":     "#8b93a6",
    "text_faint":   "#5c6575",
    "success":      "#22c55e",
    "danger":       "#f05252",
    "warn":         "#f5a524",
    "info":         "#2dd4bf",
}

_LIGHT = {
    "bg":           "#f4f6fa",
    "surface":      "#ffffff",
    "surface_alt":  "#edf0f6",
    "border":       "#e0e5ee",
    "accent":       "#5a5ce0",
    "accent_hover": "#4a4cd4",
    "accent_soft":  "#eceefe",
    "on_accent":    "#ffffff",
    "on_accent_dim": "#cdcef5",
    "text":         "#141720",
    "text_dim":     "#6b7484",
    "text_faint":   "#9aa2b1",
    "success":      "#16a34a",
    "danger":       "#dc2626",
    "warn":         "#d97706",
    "info":         "#0d9488",
}

#: Names used before the palette was reworked, mapped onto the current one.
_ALIASES = {
    "bg_main": "bg",
    "bg_card": "surface",
    "bg_card_alt": "surface_alt",
    "bg_input": "surface_alt",
    "accent2": "info",
    "accent_gold": "warn",
    "green": "success",
    "red": "danger",
    "text_primary": "text",
    "text_secondary": "text_dim",
    "text_label": "text_dim",
    "btn_bg": "accent",
    "btn_hover": "accent_hover",
    "btn_active": "success",
    "btn_active_hov": "success",
}


def _with_aliases(palette):
    full = dict(palette)
    full.update({old: palette[new] for old, new in _ALIASES.items()})
    return full


THEMES = {
    "dark": _with_aliases(_DARK),
    "light": _with_aliases(_LIGHT),
}
