import os

from themes.dark import COLORS as DARK
from themes.light import COLORS as LIGHT


HDLSTUDIO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ThemeManager:

    THEMES = {
        "dark": DARK,
        "light": LIGHT
    }

    current_theme = "dark"

    @classmethod
    def colors(cls):
        return cls.THEMES[cls.current_theme]

    @classmethod
    def set_theme(cls, theme_name):
        if theme_name in cls.THEMES:
            cls.current_theme = theme_name

    @classmethod
    def icon(cls, name):
        suffix = "_dark" if cls.current_theme == "light" else ""
        return os.path.join(HDLSTUDIO_ROOT, "assets", "icons", f"{name}{suffix}.svg")