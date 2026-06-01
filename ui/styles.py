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
    min-width: 240px;
}}

QMenu::item:selected {{
    background: {c["panel_hover"]};
}}

QToolBar {{
    background-color: {c["panel_bg"]};
    spacing: 6px;
    border-bottom: 1px solid {c.get("border", c["panel_hover"])};
}}

QToolTip {{
    background-color: {c["panel_bg"]};
    color: {c["text"]};
    border: 1px solid {c["panel_hover"]};
}}

QDockWidget {{
    color: {c["text"]};
    border-left: 1px solid {c.get("border", c["panel_hover"])};
}}

QDockWidget::title {{
    background: {c["panel_bg"]};
    color: {c["text"]};
    padding: 6px;
    text-align: left;
    border-bottom: 1px solid {c.get("border", c["panel_hover"])};
}}

QStatusBar {{
    background-color: {c["panel_bg"]};
    color: {c["text_secondary"]};
    border-top: 1px solid {c.get("border", c["panel_hover"])};
}}

QTabWidget::pane {{
    border: none;
    border-top: 1px solid {c.get("border", c["panel_hover"])};
    background: transparent;
}}

QTabBar {{
    background: {c["panel_bg"]};
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
    border-top: 1px solid {c.get("border", c["panel_hover"])};
}}

QTreeView::item:hover {{
    background: {c["panel_hover"]};
}}

QTreeView::item:selected {{
    background: {c["accent"]};
    color: {c["text"]};
}}

QHeaderView {{
    background-color: {c["panel_bg"]};
    color: {c["text_secondary"]};
}}

QHeaderView::section {{
    background-color: {c["panel_bg"]};
    color: {c["text_secondary"]};
    padding: 4px 8px;
    border: none;
    font-weight: bold;
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

QScrollBar:vertical {{
    background: {c["panel_bg"]};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {c["panel_hover"]};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {c["text_secondary"]};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {c["panel_bg"]};
    height: 10px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {c["panel_hover"]};
    min-width: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {c["text_secondary"]};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}
"""


MAIN_STYLE = build_stylesheet()
