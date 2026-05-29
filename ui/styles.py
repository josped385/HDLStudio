from themes.theme_manager import ThemeManager


def build_stylesheet():
    c = ThemeManager.colors()

    return f"""
QMainWindow {{
    background-color: {c["main_bg"]};
}}

QMenuBar {{
    background-color: {c["panel_bg"]};
    color: {c["text"]};
}}

QMenuBar::item:selected {{
    background: {c["panel_hover"]};
}}

QMenu {{
    background-color: {c["panel_bg"]};
    color: {c["text"]};
}}

QMenu::item:selected {{
    background: {c["panel_hover"]};
}}

QToolBar {{
    background-color: {c["panel_bg"]};
    spacing: 6px;
    border: none;
}}

QToolTip {{
    background-color: {c["panel_bg"]};
    color: {c["text"]};
    border: 1px solid {c["panel_hover"]};
}}

QDockWidget {{
    color: {c["text"]};
    titlebar-close-icon: none;
}}

QDockWidget::title {{
    background: {c["panel_bg"]};
    padding: 6px;
}}

QStatusBar {{
    background-color: {c["panel_bg"]};
    color: {c["text_secondary"]};
}}

QTabWidget::pane {{
    border: none;
}}

QTabBar::tab {{
    background: {c["panel_bg"]};
    color: {c["text"]};
    padding: 6px 14px;
    border: none;
}}

QTabBar::tab:selected {{
    background: {c["editor_bg"]};
    border-bottom: 2px solid {c["accent"]};
}}

QTabBar::tab:hover:!selected {{
    background: {c["panel_hover"]};
}}

QTreeView {{
    background-color: {c["main_bg"]};
    color: {c["text"]};
    border: none;
}}

QTreeView::item:hover {{
    background: {c["panel_hover"]};
}}

QTreeView::item:selected {{
    background: {c["accent"]};
    color: {c["text"]};
}}

QLineEdit {{
    background-color: {c["editor_bg"]};
    color: {c["text"]};
    border: 1px solid {c["panel_hover"]};
    padding: 4px;
}}

QComboBox {{
    background-color: {c["editor_bg"]};
    color: {c["text"]};
    border: 1px solid {c["panel_hover"]};
    padding: 3px 6px;
    min-height: 22px;
}}

QComboBox::drop-down {{
    border: none;
    background: {c["panel_hover"]};
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
}}

QComboBox QAbstractItemView {{
    background-color: {c["panel_bg"]};
    color: {c["text"]};
    selection-background-color: {c["accent"]};
    border: 1px solid {c["panel_hover"]};
}}

QTextEdit {{
    background-color: {c["terminal_bg"]};
    color: {c["terminal_text"]};
    border: none;
}}
"""


MAIN_STYLE = build_stylesheet()