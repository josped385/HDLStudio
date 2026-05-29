from PyQt6.QtWidgets import QTextEdit


class TerminalWidget(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)
        self.setPlainText("HDLStudio terminal initialized...\n")

        from themes.theme_manager import ThemeManager
        self.apply_theme(ThemeManager.colors())

    def apply_theme(self, colors):
        self.setStyleSheet(f"""
            background-color: {colors["terminal_bg"]};
            color: {colors["terminal_text"]};
            border: none;
        """)

    def write(self, text):
        self.append(text)
