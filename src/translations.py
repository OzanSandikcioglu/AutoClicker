"""
AutoClicker - UI Translations
Supports: English, Türkçe, Deutsch, Español, Français, 中文
"""

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

# Click type keys used for radio buttons and translation lookups
CLICK_KEYS = ["single", "double", "hold"]

# Mouse button keys used for radio buttons and translation lookups
MBTN_KEYS = ["left", "right", "mid"]

# Language display order in the toolbar
LANG_ORDER = ["EN", "TR", "DE", "ES", "FR", "ZH"]
