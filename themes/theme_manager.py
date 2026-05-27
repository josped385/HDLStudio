from themes.dark import COLORS as DARK
from themes.light import COLORS as LIGHT


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