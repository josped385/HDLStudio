from PyQt6.QtWidgets import QTextEdit


class TerminalDock(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setReadOnly(True)

        self.setPlainText(
            "HDLStudio terminal initialized...\n"
        )

        self.setStyleSheet("""
            background-color: #111111;
            color: #00ff88;
            border: none;
        """)